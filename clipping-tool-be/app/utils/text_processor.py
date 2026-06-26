"""
Text processing utilities for chunking text and parsing SRT subtitles.
"""
import re
import json
from typing import List, Dict, Tuple
from pathlib import Path
import pysrt
import logging

from app.config import CHUNK_SIZE

logger = logging.getLogger(__name__)

class TextProcessor:
    """Utility helpers for transcript and subtitle text processing."""
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
        """
        Split long text into chunks of approximately ``chunk_size`` characters.
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraph first.
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            # Append the paragraph if it still fits in the current chunk.
            if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
                current_chunk += paragraph + '\n'
            else:
                # Flush the current chunk before starting a new one.
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Split very large paragraphs into sentence-like pieces.
                if len(paragraph) > chunk_size:
                    # Keep the Chinese punctuation split here because transcripts may include it.
                    sentences = re.split(r'[。！？]', paragraph)
                    temp_chunk = ""
                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) + 1 <= chunk_size:
                            temp_chunk += sentence + "。"
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sentence + "。"
                    current_chunk = temp_chunk
                else:
                    current_chunk = paragraph + '\n'
        
        # Flush the final chunk.
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_srt_data(self, srt_data: List[Dict], interval_minutes: int = 30, pause_threshold_ms: int = 1000) -> List[Dict]:
        """
        Split SRT entries into roughly equal time windows using pause-aware cuts.

        This avoids splitting in the middle of a conversation when a nearby
        pause can serve as a cleaner boundary.
        """
        if not srt_data:
            return []

        # Create a derived list with second-based timestamps instead of mutating
        # the original subtitle records.
        srt_data_with_seconds = []
        for sub in srt_data:
            entry = sub.copy()
            entry['start_seconds'] = self.time_to_seconds(sub['start_time'])
            entry['end_seconds'] = self.time_to_seconds(sub['end_time'])
            srt_data_with_seconds.append(entry)

        interval_seconds = interval_minutes * 60
        chunks = []
        current_chunk_start_index = 0
        chunk_index = 0
        
        last_cut_time = 0
        
        while current_chunk_start_index < len(srt_data_with_seconds):
            target_cut_time = last_cut_time + interval_seconds
            
            # Find the best cut near the target time.
            best_cut_index = -1
            
            # Search for a pause between 90% and 110% of the target position.
            search_start_index = current_chunk_start_index
            while search_start_index < len(srt_data_with_seconds) and srt_data_with_seconds[search_start_index]['start_seconds'] < target_cut_time * 0.9:
                search_start_index += 1

            # Look for the first pause that clears the threshold.
            for i in range(search_start_index, len(srt_data_with_seconds) - 1):
                current_sub = srt_data_with_seconds[i]
                next_sub = srt_data_with_seconds[i+1]
                
                # Stop once we move too far past the target time.
                if current_sub['start_seconds'] > target_cut_time * 1.1:
                    break
                
                # Measure the silence between adjacent subtitle entries.
                pause = next_sub['start_seconds'] - current_sub['end_seconds']
                if pause * 1000 >= pause_threshold_ms:
                    best_cut_index = i + 1
                    break
            
            # Fall back to the nearest target position if no clean pause exists.
            if best_cut_index == -1:
                # Find the subtitle entry closest to the target cut time.
                i = current_chunk_start_index
                while i < len(srt_data_with_seconds) and srt_data_with_seconds[i]['start_seconds'] < target_cut_time:
                    i += 1
                best_cut_index = i if i < len(srt_data_with_seconds) else len(srt_data_with_seconds)

            # If the cut point is invalid, consume the remaining entries.
            if best_cut_index <= current_chunk_start_index:
                 best_cut_index = len(srt_data_with_seconds)

            # Build the chunk payload.
            chunk_entries_with_seconds = srt_data_with_seconds[current_chunk_start_index:best_cut_index]
            if not chunk_entries_with_seconds:
                break

            # Drop the temporary helper fields before storing the final entries.
            chunk_entries = []
            for entry in chunk_entries_with_seconds:
                clean_entry = entry.copy()
                del clean_entry['start_seconds']
                del clean_entry['end_seconds']
                chunk_entries.append(clean_entry)
            
            start_time = chunk_entries[0]['start_time']
            end_time = chunk_entries[-1]['end_time']
            text = " ".join([entry['text'] for entry in chunk_entries])
            
            chunks.append({
                "chunk_index": chunk_index,
                "text": text,
                "start_time": start_time,
                "end_time": end_time,
                "srt_entries": chunk_entries
            })
            
            chunk_index += 1
            last_cut_time = chunk_entries_with_seconds[-1]['end_seconds']
            current_chunk_start_index = best_cut_index
            
        return chunks

    @staticmethod
    def parse_srt(srt_path: Path) -> List[Dict]:
        """
        Parse an SRT subtitle file into timestamped subtitle entries.
        """
        if not srt_path.exists():
            logger.error("SRT file does not exist: %s", srt_path)
            return []
        
        if srt_path.stat().st_size == 0:
            logger.warning("SRT file is empty: %s", srt_path)
            return []

        try:
            try:
                subs = pysrt.open(str(srt_path), encoding='utf-8')
            except UnicodeDecodeError:
                logger.warning("UTF-8 decoding failed, retrying with utf-8-sig...")
                subs = pysrt.open(str(srt_path), encoding='utf-8-sig')

            subtitles = []
            for sub in subs:
                subtitles.append({
                    'start_time': str(sub.start),
                    'end_time': str(sub.end),
                    'text': sub.text.strip(),
                    'index': sub.index
                })

            if not subtitles:
                logger.warning("Opened SRT file but parsed no subtitle content: %s", srt_path)
            
            return subtitles
        except Exception as e:
            logger.error("Unexpected error while parsing SRT file '%s': %s", srt_path, e, exc_info=True)
            return []
    
    @staticmethod
    def extract_text_by_time_range(text: str, srt_data: List[Dict], 
                                  start_time: str, end_time: str) -> str:
        """
        Extract transcript text that overlaps a given time range.
        """
        # Collect subtitles that overlap the requested window.
        target_subtitles = []
        
        for sub in srt_data:
            sub_start = sub['start_time']
            sub_end = sub['end_time']
            
            # Check for any overlap with the requested interval.
            if (sub_start <= end_time and sub_end >= start_time):
                target_subtitles.append(sub)
        
        # Join the text from all matching subtitles.
        extracted_text = ""
        for sub in target_subtitles:
            extracted_text += sub['text'] + " "
        
        return extracted_text.strip()
    
    @staticmethod
    def time_to_seconds(time_str: str) -> float:
        """
        Convert an SRT time string like ``HH:MM:SS,mmm`` into seconds.
        """
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        
        if len(parts) == 3:
            h = int(parts[0])
            m = int(parts[1])
            s_parts = parts[2].split('.')
            s = int(s_parts[0])
            ms = int(s_parts[1]) if len(s_parts) > 1 else 0
            return h * 3600 + m * 60 + s + ms / 1000.0
        
        raise ValueError(f"Invalid time format: {time_str}")
    
    @staticmethod
    def seconds_to_time(seconds: float) -> str:
        """
        Convert seconds into an ``HH:MM:SS`` time string.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}" 
