"""
Step 2.5: Smart Snapper - Refines clip boundaries using SRT context
"""
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import math

from app.utils.llm.factory import LLMFactory
from app.utils.text_processor import TextProcessor
from app.config import PROJECT_ROOT, METADATA_DIR

logger = logging.getLogger(__name__)

class SmartSnapper:
    """Refines timestamps by analyzing surrounding context"""
    
    def __init__(self, metadata_dir: Path = None):
        # Use Grok for semantic smart snapping
        self.llm_client = LLMFactory.create_client(provider="grok")
        self.text_processor = TextProcessor()
        
        if metadata_dir is None:
            metadata_dir = METADATA_DIR
        self.metadata_dir = metadata_dir
        
        # Load prompt
        prompt_path = PROJECT_ROOT / "prompts" / "en" / "snapper.txt"
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.snapper_prompt = f.read()
            
        self.snapper_output_dir = self.metadata_dir / "step2_5_snapper_output"
        self.snapper_debug_dir = self.metadata_dir / "step2_5_debug"

    def refine_timeline(self, timeline_data: List[Dict], project_id: str) -> List[Dict]:
        """
        Refine the start and end times of each clip in the timeline.
        """
        logger.info("Step 2.5: Starting Smart Snapping refinement...")
        
        if not timeline_data:
            logger.warning("Timeline data is empty, skipping snapper.")
            return []

        self.snapper_output_dir.mkdir(parents=True, exist_ok=True)
        self.snapper_debug_dir.mkdir(parents=True, exist_ok=True)
        
        # Load all SRT chunks to have full context available
        srt_chunks_dir = self.metadata_dir / "step1_srt_chunks"
        all_srt_entries = []
        
        try:
            # We need to load ALL chunks to handle cross-chunk boundary context
            # Assuming chunks are named chunk_0.json, chunk_1.json, etc.
            chunk_files = sorted(srt_chunks_dir.glob("chunk_*.json"), key=lambda x: int(x.stem.split('_')[1]))
            for cf in chunk_files:
                with open(cf, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    all_srt_entries.extend(chunk_data)
            
            # Sort full SRT by start time just in case
            all_srt_entries.sort(key=lambda x: self.text_processor.time_to_seconds(x['start_time']))
            logger.info(f"Loaded {len(all_srt_entries)} total SRT entries for context lookups.")
            
        except Exception as e:
            logger.error(f"Failed to load SRT chunks for context: {e}")
            return timeline_data  # Return original if we fails

        refined_timeline = []
        
        for i, clip in enumerate(timeline_data):
            logger.info(f"Snapping Clip {i+1}/{len(timeline_data)}: {clip.get('outline', 'Unknown')}")
            
            try:
                refined_clip = self._snap_single_clip(clip, all_srt_entries, i)
                refined_timeline.append(refined_clip)
            except Exception as e:
                logger.error(f"Failed to snap clip {i+1}: {e}")
                refined_timeline.append(clip) # Fallback to original
                
        # Save results
        output_file = self.snapper_output_dir / "refined_timeline.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(refined_timeline, f, ensure_ascii=False, indent=2)
            
        return refined_timeline

    def _snap_single_clip(self, clip: Dict, all_srt_entries: List[Dict], index: int) -> Dict:
        """Process a single clip"""
        start_time = clip['start_time']
        end_time = clip['end_time']
        
        start_sec = self.text_processor.time_to_seconds(start_time)
        end_sec = self.text_processor.time_to_seconds(end_time)
        
        # Define context window: +20s before and after (approx)
        context_start_sec = max(0, start_sec - 20)
        context_end_sec = end_sec + 20
        
        # Extract SRT entries within this window
        context_entries = [
            sub for sub in all_srt_entries 
            if self.text_processor.time_to_seconds(sub['end_time']) >= context_start_sec 
            and self.text_processor.time_to_seconds(sub['start_time']) <= context_end_sec
        ]
        
        if not context_entries:
            logger.warning(f"  > No context found for clip {index+1}, keeping original.")
            return clip
            
        # Format SRT context for LLM
        context_srt_text = ""
        for sub in context_entries:
            context_srt_text += f"{sub['index']}\\n{sub['start_time']} --> {sub['end_time']}\\n{sub['text']}\\n\\n"
            
        # Prepare LLM input
        llm_input = {
            "rough_start_time": start_time,
            "rough_end_time": end_time,
            "context_srt": context_srt_text
        }
        
        # Call LLM
        response = self.llm_client.call_with_retry(self.snapper_prompt, llm_input)
        
        # Save debug
        debug_file = self.snapper_debug_dir / f"clip_{index+1}_snap.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f"INPUT:\n{json.dumps(llm_input, indent=2)}\n\nRESPONSE:\n{response}")

        # Parse output
        try:
            parsed = self.llm_client.parse_json_response(response)
            
            # handling list return which sometimes happens with some LLMs
            if isinstance(parsed, list) and len(parsed) > 0:
                parsed = parsed[0]
                
            if 'refined_start_time' in parsed and 'refined_end_time' in parsed:
                # Validate format
                if self._validate_time(parsed['refined_start_time']) and self._validate_time(parsed['refined_end_time']):
                     # Update clip
                    new_clip = clip.copy()
                    new_clip['start_time'] = parsed['refined_start_time']
                    new_clip['end_time'] = parsed['refined_end_time']
                    new_clip['snapped'] = True
                    new_clip['snap_reason'] = parsed.get('reasoning', '')
                    
                    logger.info(f"  > Snapped! {start_time}->{new_clip['start_time']} / {end_time}->{new_clip['end_time']}")
                    return new_clip
            
            logger.warning(f"  > Invalid snapper response keys: {parsed.keys()}")
            return clip
            
        except Exception as e:
            logger.error(f"  > Snapper parse error: {e}")
            return clip

    def _validate_time(self, time_str: str) -> bool:
        import re
        return bool(re.match(r'^\d{2}:\d{2}:\d{2},\d{3}$', time_str))

def run_step2_5_snapper(
    timeline_path: Path,
    metadata_dir: Path,
    output_path: Path,
    project_id: str
):
    """
    Run Step 2.5: Smart Snapper
    
    Args:
        timeline_path: Path to Step 2 timeline JSON
        metadata_dir: Directory containing metadata (for loading SRT chunks)
        output_path: Where to save refined timeline
        project_id: Project ID
    """
    try:
        with open(timeline_path, 'r', encoding='utf-8') as f:
            timeline_data = json.load(f)
            
        snapper = SmartSnapper(metadata_dir=metadata_dir)
        refined_data = snapper.refine_timeline(timeline_data, project_id)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(refined_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Step 2.5 completed. Refined timeline saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Step 2.5 failed: {e}")
        # In case of catastrophic failure, just copy the input to output to not break pipeline
        if timeline_path.exists():
            import shutil
            shutil.copy2(timeline_path, output_path)
            logger.warning("Copied original timeline to output due to snapper failure.")
