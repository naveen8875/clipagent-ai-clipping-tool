"""
Step 1: Outline extraction - pull a structured outline from transcript text.
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.utils.llm.factory import LLMFactory
from app.utils.text_processor import TextProcessor
from app.config import PROMPT_FILES, METADATA_DIR

logger = logging.getLogger(__name__)

class OutlineExtractor:
    """Outline extractor."""
    
    def __init__(self, metadata_dir: Path = None, prompt_files: Dict = None):
        self.llm_client = LLMFactory.get_default_client()
        self.text_processor = TextProcessor()
        
        # Use the provided metadata_dir or fall back to the default.
        if metadata_dir is None:
            metadata_dir = METADATA_DIR
        self.metadata_dir = metadata_dir
        
        # Use the provided prompt_files or fall back to defaults.
        if prompt_files is None:
            prompt_files = PROMPT_FILES
        
        # Load prompts.
        with open(prompt_files['outline'], 'r', encoding='utf-8') as f:
            self.outline_prompt = f.read()
            
        # Create a directory for intermediate text chunks.
        self.chunks_dir = self.metadata_dir / "step1_chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        # Create a directory for intermediate SRT chunks.
        self.srt_chunks_dir = self.metadata_dir / "step1_srt_chunks"
        self.srt_chunks_dir.mkdir(parents=True, exist_ok=True)

    def extract_outline(self, srt_path: Path) -> List[Dict]:
        """
        Extract a video outline from an SRT file.
        
        Args:
            srt_path: Path to the SRT file.
            
        Returns:
            List of extracted outline entries.
        """
        logger.info("Starting video outline extraction...")
        
        # 1. Parse the SRT file.
        try:
            srt_data = self.text_processor.parse_srt(srt_path)
            if not srt_data:
                logger.warning("SRT file is empty or failed to parse.")
                return []
        except Exception as e:
            logger.error(f"Failed to parse SRT file: {e}")
            return []
            
        # 2. Split into time-based chunks.
        chunks = self.text_processor.chunk_srt_data(srt_data, interval_minutes=30)
        logger.info(f"Transcript split into ~30-minute chunks: {len(chunks)} total chunks.")
        
        # 3. Save text chunks and SRT chunks to intermediate files.
        chunk_files = self._save_chunks_to_files(chunks)
        self._save_srt_chunks(chunks)
        
        all_outlines = []
        
        # 4. Process each chunk file one by one.
        for i, chunk_file in enumerate(chunk_files):
            logger.info(f"Processing text chunk {i+1}/{len(chunks)}: {chunk_file.name}")
            try:
                # Read the chunk text.
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    chunk_text = f.read()
                
                # Call the LLM for each chunk.
                input_data = {"text": chunk_text}
                response = self.llm_client.call_with_retry(self.outline_prompt, input_data)
                
                if response:
                    # Parse the response and attach the originating chunk index.
                    parsed_outlines = self._parse_outline_response(response, i)
                    all_outlines.extend(parsed_outlines)
                else:
                    logger.warning(f"Chunk {i+1} returned an empty response.")
            except Exception as e:
                logger.error(f"Failed to process text chunk {i+1}: {e}")
                continue
        
        # 5. Merge and deduplicate.
        final_outlines = self._merge_outlines(all_outlines)
        
        logger.info(f"Outline extraction complete: {len(final_outlines)} topics found.")
        return final_outlines

    def _save_chunks_to_files(self, chunks: List[Dict]) -> List[Path]:
        """Save text chunks as individual `.txt` files."""
        chunk_files = []
        for chunk in chunks:
            chunk_index = chunk['chunk_index']
            text_content = chunk['text']
            file_path = self.chunks_dir / f"chunk_{chunk_index}.txt"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            chunk_files.append(file_path)
        
        logger.info(f"Saved all text chunks to: {self.chunks_dir}")
        return chunk_files

    def _save_srt_chunks(self, chunks: List[Dict]):
        """Save SRT chunk data as individual `.json` files."""
        for chunk in chunks:
            chunk_index = chunk['chunk_index']
            srt_entries = chunk['srt_entries']
            file_path = self.srt_chunks_dir / f"chunk_{chunk_index}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(srt_entries, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved all SRT chunks to: {self.srt_chunks_dir}")

    def _parse_outline_response(self, response: str, chunk_index: int) -> List[Dict]:
        """
        Parse the outline response from the model.
        
        Args:
            response: Model response text.
            chunk_index: Index of the current chunk.
            
        Returns:
            Parsed outline structure.
        """
        outlines = []
        lines = response.split('\n')
        current_outline = None
        
        for line in lines:
            line = line.strip()
            
            if re.match(r'^\d+\.\s*\*\*', line):
                if current_outline:
                    outlines.append(current_outline)
                
                topic_name = line.split('**')[1] if '**' in line else line.split('.', 1)[1].strip()
                current_outline = {
                    'title': topic_name,
                    'subtopics': [],
                    'chunk_index': chunk_index
                }
            
            elif line.startswith('-') and current_outline:
                subtopic = line[1:].strip()
                if subtopic and len(subtopic) <= 200:
                    current_outline['subtopics'].append(subtopic)
        
        if current_outline:
            outlines.append(current_outline)
        
        return outlines
    
    def _merge_outlines(self, outlines: List[Dict]) -> List[Dict]:
        """
        Merge and deduplicate outlines, keeping the earliest occurrence.
        """
        unique_outlines = {}
        for outline in outlines:
            title = outline['title']
            if title not in unique_outlines:
                unique_outlines[title] = outline
        return list(unique_outlines.values())
    
    def save_outline(self, outlines: List[Dict], output_path: Optional[Path] = None) -> Path:
        """
        Save outlines to a file.
        """
        if output_path is None:
            output_path = METADATA_DIR / "step1_outline.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(outlines, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Outline saved to: {output_path}")
        return output_path
    
    def load_outline(self, input_path: Path) -> List[Dict]:
        """
        Load outlines from a file.
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)

def run_step1_outline(srt_path: Path, metadata_dir: Path = None, output_path: Optional[Path] = None, prompt_files: Dict = None) -> List[Dict]:
    """
    Run Step 1: outline extraction.
    """
    if metadata_dir is None:
        metadata_dir = METADATA_DIR
        
    extractor = OutlineExtractor(metadata_dir, prompt_files)
    outlines = extractor.extract_outline(srt_path)
    
    if output_path is None:
        output_path = metadata_dir / "step1_outline.json"
        
    extractor.save_outline(outlines, output_path)
    
    return outlines
