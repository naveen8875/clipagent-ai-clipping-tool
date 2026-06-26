"""
Video processing helpers for FFmpeg-based clip extraction and concatenation.
"""
import subprocess
import json
import logging
import re
from typing import List, Dict, Optional
from pathlib import Path

from app.config import CLIPS_DIR, COLLECTIONS_DIR

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Utility wrapper around FFmpeg for clip extraction and concatenation."""
    
    def __init__(self, clips_dir: Optional[str] = None, collections_dir: Optional[str] = None):
        self.clips_dir = Path(clips_dir) if clips_dir else CLIPS_DIR
        self.collections_dir = Path(collections_dir) if collections_dir else COLLECTIONS_DIR
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Remove or replace filesystem-invalid characters from a filename.
        """
        # Replace characters that are invalid on common filesystems.
        sanitized = re.sub(r'[<>:"|?*\\/]', '_', filename)
        
        # Remove trailing spaces and dots.
        sanitized = sanitized.strip(' .')
        
        # Keep filenames reasonably short.
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        # Ensure the filename is not empty.
        if not sanitized:
            sanitized = "untitled"
            
        return sanitized
    
    @staticmethod
    def convert_srt_time_to_ffmpeg_time(srt_time: str) -> str:
        """
        Convert SRT timestamps like ``00:00:06,140`` to FFmpeg timestamps.
        """
        return srt_time.replace(',', '.')
    
    @staticmethod
    def extract_clip(input_video: Path, output_path: Path, 
                    start_time: str, end_time: str) -> bool:
        """
        Extract a clip from ``input_video`` into ``output_path``.
        """
        try:
            # Ensure the output directory exists.
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            ffmpeg_start_time = VideoProcessor.convert_srt_time_to_ffmpeg_time(start_time)
            ffmpeg_end_time = VideoProcessor.convert_srt_time_to_ffmpeg_time(end_time)
            
            def time_to_seconds(time_str: str) -> float:
                """Convert a timestamp string to seconds."""
                h, m, s = time_str.split(':')
                s, ms = s.split('.')
                return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
            
            start_seconds = time_to_seconds(ffmpeg_start_time)
            end_seconds = time_to_seconds(ffmpeg_end_time)
            duration = end_seconds - start_seconds
            
            cmd = [
                'ffmpeg',
                '-ss', ffmpeg_start_time,
                '-i', str(input_video),
                '-t', str(duration),
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-avoid_negative_ts', 'make_zero',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                logger.info(
                    "Extracted clip: %s (%s -> %s, duration: %.2fs)",
                    output_path,
                    ffmpeg_start_time,
                    ffmpeg_end_time,
                    duration,
                )
                return True
            else:
                logger.error("Failed to extract clip: %s", result.stderr)
                return False
                
        except Exception as e:
            logger.error("Video processing error: %s", str(e))
            return False
    
    @staticmethod
    def create_collection(clips_list: List[Path], output_path: Path) -> bool:
        """
        Concatenate multiple clips into a single collection video.
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            concat_file = output_path.parent / "concat_list.txt"
            
            with open(concat_file, 'w', encoding='utf-8') as f:
                for clip_path in clips_list:
                    f.write(f"file '{clip_path.absolute()}'\n")
            
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                '-y',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            concat_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                logger.info("Created collection: %s", output_path)
                return True
            else:
                logger.error("Failed to create collection: %s", result.stderr)
                return False
                
        except Exception as e:
            logger.error("Collection creation error: %s", str(e))
            return False
    
    @staticmethod
    def get_video_info(video_path: Path) -> Dict:
        """
        Inspect a video file using ``ffprobe``.
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return {
                    'duration': float(info['format']['duration']),
                    'size': int(info['format']['size']),
                    'bitrate': int(info['format']['bit_rate']),
                    'streams': info['streams']
                }
            else:
                logger.error("Failed to read video info: %s", result.stderr)
                return {}
                
        except Exception as e:
            logger.error("Video info inspection error: %s", str(e))
            return {}
    
    def batch_extract_clips(self, input_video: Path, clips_data: List[Dict]) -> List[Path]:
        """
        Batch-extract clips from the source video.
        """
        successful_clips = []
        
        for clip_data in clips_data:
            clip_id = clip_data['id']
            title = clip_data.get('title', f"clip_{clip_id}")
            start_time = clip_data['start_time']
            end_time = clip_data['end_time']
            
            safe_title = VideoProcessor.sanitize_filename(title)
            output_path = self.clips_dir / f"{clip_id}_{safe_title}.mp4"
            
            if VideoProcessor.extract_clip(input_video, output_path, start_time, end_time):
                successful_clips.append(output_path)
        
        return successful_clips
    
    def create_collections_from_metadata(self, collections_data: List[Dict]) -> List[Path]:
        """
        Create collection videos based on collection metadata.
        """
        successful_collections = []
        
        for collection_data in collections_data:
            collection_id = collection_data['id']
            collection_title = collection_data.get('collection_title', f'collection_{collection_id}')
            clip_ids = collection_data['clip_ids']
            
            clips_list = []
            for clip_id in clip_ids:
                found_clips = list(self.clips_dir.glob(f"{clip_id}_*.mp4"))
                
                if found_clips:
                    found_clip = found_clips[0]
                    clips_list.append(found_clip)
                    logger.info("Found clip %s for collection %s", found_clip.name, collection_id)
                else:
                    logger.warning("Missing clip %s for collection %s", clip_id, collection_id)
            
            if clips_list:
                safe_title = VideoProcessor.sanitize_filename(collection_title)
                output_path = self.collections_dir / f"{safe_title}.mp4"
                
                if VideoProcessor.create_collection(clips_list, output_path):
                    successful_collections.append(output_path)
                    logger.info("Created collection %s: %s", collection_id, output_path)
            else:
                logger.warning("Collection %s has no valid source clips", collection_id)
        
        return successful_collections
