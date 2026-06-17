"""
Step 3: Clip scoring - rate each topic clip across multiple dimensions.
"""
import json
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import defaultdict

from app.utils.llm.factory import LLMFactory
from app.utils.text_processor import TextProcessor
from app.config import PROMPT_FILES, METADATA_DIR, MIN_SCORE_THRESHOLD

logger = logging.getLogger(__name__)

class ClipScorer:
    """Clip scorer."""
    
    def __init__(self, prompt_files: Dict = None):
        # Use Grok specifically for clip scoring (engagement evaluation)
        self.llm_client = LLMFactory.create_client(provider="grok")
        self.text_processor = TextProcessor()
        
        # Load prompts
        prompt_files_to_use = prompt_files if prompt_files is not None else PROMPT_FILES
        with open(prompt_files_to_use['recommendation'], 'r', encoding='utf-8') as f:
            self.recommendation_prompt = f.read()
    
    def score_clips(self, timeline_data: List[Dict]) -> List[Dict]:
        """
        Score clips in batches by chunk using the LLM for holistic evaluation.
        """
        if not timeline_data:
            logger.warning("Timeline data is empty; scoring cannot proceed.")
            return []
            
        logger.info(f"Starting batch scoring for {len(timeline_data)} clips...")
        
        # 1. Group timeline data by chunk_index
        timeline_by_chunk = defaultdict(list)
        for item in timeline_data:
            chunk_index = item.get('chunk_index')
            if chunk_index is not None:
                timeline_by_chunk[chunk_index].append(item)
            else:
                logger.warning(f"  > Topic '{item.get('outline', 'unknown')}' is missing chunk_index and will be skipped.")
        
        all_scored_clips = []
        # 2. Process all topics in each chunk as a batch
        for chunk_index, chunk_items in timeline_by_chunk.items():
            logger.info(f"Processing chunk {chunk_index} with {len(chunk_items)} topics...")
            try:
                # 3. Run batch evaluation with the LLM
                scored_chunk_items = self._get_llm_evaluation(chunk_items)
                
                if scored_chunk_items:
                    all_scored_clips.extend(scored_chunk_items)
                else:
                    logger.warning(f"Chunk {chunk_index} returned an empty LLM evaluation and will be skipped.")

            except Exception as e:
                logger.error(f"  > Error while scoring chunk {chunk_index}: {str(e)}")
                continue

        # 4. Sort results by final score
        if all_scored_clips:
            all_scored_clips.sort(key=lambda x: x.get('final_score', 0), reverse=True)
            # Keep the stable IDs assigned in Step 2.
            logger.info("Sorting by score complete; keeping the original fixed IDs.")
            
            # Finally sort by ID to preserve chronological consistency.
            all_scored_clips.sort(key=lambda x: int(x.get('id', 0)))
            logger.info("Sorting by ID complete; chronological order preserved.")
                
        logger.info("Finished scoring all clips.")
        return all_scored_clips
    
    def _get_llm_evaluation(self, clips: List[Dict]) -> List[Dict]:
        """
        Batch-evaluate clips with the LLM and add final_score and recommend_reason.
        """
        try:
            # Send only the fields the LLM needs.
            input_for_llm = [
                {
                    "outline": clip.get('outline'), 
                    "content": clip.get('content'),
                    "start_time": clip.get('start_time'),
                    "end_time": clip.get('end_time'),
                } for clip in clips
            ]
            
            response = self.llm_client.call_with_retry(self.recommendation_prompt, input_for_llm)
            parsed_list = self.llm_client.parse_json_response(response)
            
            if not isinstance(parsed_list, list) or len(parsed_list) != len(clips):
                logger.error(f"LLM returned a mismatched number of results. Input: {len(clips)}, Output: {len(parsed_list)}")
                return []
                
            # Merge the scoring results back into the original clips.
            for original_clip, llm_result in zip(clips, parsed_list):
                score = llm_result.get('final_score')
                reason = llm_result.get('recommend_reason')
                
                if score is None or reason is None:
                    logger.warning(f"An LLM result is missing score or reason: {llm_result}")
                    original_clip['final_score'] = 0.0
                    original_clip['recommend_reason'] = "Evaluation failed"
                else:
                    original_clip['final_score'] = round(float(score), 2)
                    original_clip['recommend_reason'] = reason
                    logger.info(f"  > Scored successfully: {original_clip.get('outline', '')[:20]}... [score: {score}]")

            return clips

        except Exception as e:
            logger.error(f"LLM batch evaluation failed: {e}")
            # If batch evaluation fails, mark every clip as failed.
            for clip in clips:
                clip['final_score'] = 0.0
                clip['recommend_reason'] = "Batch evaluation failed"
            return clips

    def save_scores(self, scored_clips: List[Dict], output_path: Path):
        """Save scoring results."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(scored_clips, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved scoring results to: {output_path}")

def run_step3_scoring(timeline_path: Path, metadata_dir: Path = None, output_path: Optional[Path] = None, prompt_files: Dict = None) -> List[Dict]:
    """
    Run Step 3: score and filter content clips.
    
    Args:
        timeline_path: Path to the timeline file.
        output_path: Output file path.
        prompt_files: Custom prompt files.
        
    Returns:
        List of high-scoring clips.
    """
    # Load timeline data.
    with open(timeline_path, 'r', encoding='utf-8') as f:
        timeline_data = json.load(f)
    
    # Create the scorer.
    scorer = ClipScorer(prompt_files)
    
    # Score clips.
    scored_clips = scorer.score_clips(timeline_data)
    
    # Filter high-scoring clips.
    high_score_clips = [clip for clip in scored_clips if clip['final_score'] >= MIN_SCORE_THRESHOLD]
    
    # Save results.
    if metadata_dir is None:
        metadata_dir = METADATA_DIR
    
    # Save all scored clips for debugging and analysis.
    all_scored_path = metadata_dir / "step3_all_scored.json"
    scorer.save_scores(scored_clips, all_scored_path)
    
    # Save filtered high-scoring clips for downstream steps.
    if output_path is None:
        output_path = metadata_dir / "step3_high_score_clips.json"
        
    scorer.save_scores(high_score_clips, output_path)
    
    return high_score_clips
