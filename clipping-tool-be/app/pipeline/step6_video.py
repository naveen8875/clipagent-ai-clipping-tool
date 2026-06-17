"""
Step 6: Video cutting - generate clip videos and collection videos.
"""
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from app.utils.video_processor import VideoProcessor
from app.config import METADATA_DIR, CLIPS_DIR, COLLECTIONS_DIR

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Video generator."""
    
    def __init__(self, clips_dir: Optional[str] = None, collections_dir: Optional[str] = None, metadata_dir: Optional[str] = None):
        self.clips_dir = Path(clips_dir) if clips_dir else CLIPS_DIR
        self.collections_dir = Path(collections_dir) if collections_dir else COLLECTIONS_DIR
        self.metadata_dir = Path(metadata_dir) if metadata_dir else METADATA_DIR
        self.video_processor = VideoProcessor(clips_dir=str(self.clips_dir), collections_dir=str(self.collections_dir))
    
    def generate_clips(self, clips_with_titles: List[Dict], input_video: Path) -> List[Path]:
        """
        Generate clip videos.
        
        Args:
            clips_with_titles: Clip data with generated titles.
            input_video: Input video path.
            
        Returns:
            List of generated clip video paths.
        """
        logger.info("Starting clip video generation...")
        
        # Prepare clip payloads.
        clips_data = []
        for clip in clips_with_titles:
            clips_data.append({
                'id': clip['id'],
                'title': clip.get('generated_title', f"clip_{clip['id']}"),
                'start_time': clip['start_time'],
                'end_time': clip['end_time']
            })
        
        # Generate clips in batch.
        successful_clips = self.video_processor.batch_extract_clips(input_video, clips_data)
        
        logger.info(f"Clip video generation complete: {len(successful_clips)} clips created.")
        return successful_clips
    
    def generate_collections(self, collections_data: List[Dict]) -> List[Path]:
        """
        Generate collection videos.
        
        Args:
            collections_data: Collection metadata.
            
        Returns:
            List of generated collection video paths.
        """
        logger.info("Starting collection video generation...")
        
        # Generate collection videos.
        successful_collections = self.video_processor.create_collections_from_metadata(collections_data)
        
        logger.info(f"Collection video generation complete: {len(successful_collections)} collections created.")
        return successful_collections
    
    def save_clip_metadata(self, clips_with_titles: List[Dict], output_path: Optional[Path] = None) -> Path:
        """
        Save final clip metadata to clips_metadata.json.
        
        Args:
            clips_with_titles: Clip data with generated titles from Step 4.
            output_path: Output path; defaults to clips_metadata.json.
            
        Returns:
            Saved file path.
            
        Note:
            This stores the final clip metadata, including the complete information
            available after video generation. Unlike step4_titles.json from Step 4,
            this file is the final dataset used for frontend display.
        """
        if output_path is None:
            output_path = self.metadata_dir / "clips_metadata.json"
        
        # Ensure the directory exists.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the data.
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clips_with_titles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Clip metadata saved to: {output_path}")
        return output_path
    
    def save_collection_metadata(self, collections_data: List[Dict], output_path: Optional[Path] = None) -> Path:
        """
        Save collection metadata.
        
        Args:
            collections_data: Collection metadata.
            output_path: Output path.
            
        Returns:
            Saved file path.
        """
        if output_path is None:
            output_path = self.metadata_dir / "collections_metadata.json"
        
        # Ensure the directory exists.
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the data.
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collections_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Collection metadata saved to: {output_path}")
        return output_path

def run_step6_video(clips_with_titles_path: Path, collections_path: Path, 
                   input_video: Path, output_dir: Optional[Path] = None, 
                   clips_dir: Optional[str] = None, collections_dir: Optional[str] = None, 
                   metadata_dir: Optional[str] = None) -> Dict:
    """
    Run Step 6: video cutting.
    
    Args:
        clips_with_titles_path: Path to the titled clips file.
        collections_path: Path to the collections file.
        input_video: Input video path.
        output_dir: Output directory.
        
    Returns:
        Generation result summary.
    """
    # Load data.
    with open(clips_with_titles_path, 'r', encoding='utf-8') as f:
        clips_with_titles = json.load(f)
    
    with open(collections_path, 'r', encoding='utf-8') as f:
        collections_data = json.load(f)
    
    # Create the video generator.
    generator = VideoGenerator(clips_dir=clips_dir, collections_dir=collections_dir, metadata_dir=metadata_dir)
    
    # Generate clip videos.
    successful_clips = generator.generate_clips(clips_with_titles, input_video)
    
    # Generate collection videos.
    successful_collections = generator.generate_collections(collections_data)
    
    # Save metadata.
    # clips_metadata.json is saved here and includes the final clip metadata,
    # including generated video paths and other post-processing information.
    # This differs from step4_titles.json, which only stores titled clip data.
    generator.save_clip_metadata(clips_with_titles)
    generator.save_collection_metadata(collections_data)
    
    # Return a result summary.
    result = {
        'clips_generated': len(successful_clips),
        'collections_generated': len(successful_collections),
        'clip_paths': [str(path) for path in successful_clips],
        'collection_paths': [str(path) for path in successful_collections]
    }
    
    logger.info(
        f"Video generation complete: {result['clips_generated']} clips, "
        f"{result['collections_generated']} collections."
    )
    
    return result
