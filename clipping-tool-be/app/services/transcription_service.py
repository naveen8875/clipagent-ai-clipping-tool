"""
Transcription Service
Handles automatic SRT generation using OpenAI Whisper.
"""
import logging
import ssl
from pathlib import Path
import whisper
from whisper.utils import get_writer

logger = logging.getLogger(__name__)

# Fix for SSL errors on some environments when downloading models
ssl._create_default_https_context = ssl._create_unverified_context

class TranscriptionService:
    def __init__(self, model_size: str = "base"):
        """
        Initialize TranscriptionService.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large). 
                        'base' is a good trade-off for speed/accuracy.
        """
        self.model_size = model_size
        self.model = None

    def load_model(self):
        """Lazy load the model"""
        if not self.model:
            logger.info(f"Loading Whisper model: {self.model_size}...")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded.")

    def ensure_srt(self, video_path: Path, srt_path: Path) -> Path:
        """
        Ensures an SRT file exists for the video.
        If srt_path exists, returns it.
        If not, generates it from video_path.
        
        Args:
            video_path: Path to the input video file.
            srt_path: Desired path for the output SRT file.
            
        Returns:
            Path to the SRT file.
        """
        if srt_path.exists():
            logger.info(f"SRT file already exists: {srt_path}")
            return srt_path
        
        return self._generate_srt(video_path, srt_path)

    def _generate_srt(self, video_path: Path, output_path: Path) -> Path:
        """Generates SRT from video using Whisper"""
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        self.load_model()
        
        logger.info(f"Transcribing {video_path}...")
        # Whisper internally uses ffmpeg to load audio from the video file
        # verbose=False reduces noise in logs
        result = self.model.transcribe(str(video_path), verbose=False)
        
        # Prepare output directory
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Use Whisper's built-in SRT writer
        # We pass the Stem of the desired output path as the 'audio_path' argument
        # because the writer uses os.path.basename(audio_path) to name the file.
        writer = get_writer("srt", str(output_dir))
        
        # result: the transcription result
        # tmp_filename: just a string used for naming the output file. 
        # If we want output.srt, we pass "output"
        writer(result, output_path.stem, {"max_line_width": None, "max_line_count": None, "highlight_words": False})
        
        logger.info(f"Transcription saved to {output_path}")
        return output_path

# Global instance
transcription_service = TranscriptionService()
