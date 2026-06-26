"""
Config file - Manage API keys, file paths and other configuration
Supports new configuration management system with backward compatibility
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, field_validator
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Video Category Enum
class VideoCategory(str, Enum):
    DEFAULT = "default"
    KNOWLEDGE = "knowledge"
    BUSINESS = "business"
    OPINION = "opinion"
    EXPERIENCE = "experience"
    SPEECH = "speech"
    CONTENT_REVIEW = "content_review"
    ENTERTAINMENT = "entertainment"
    PODCAST = "podcast"

# Video Category Configuration
VIDEO_CATEGORIES_CONFIG = {
    VideoCategory.DEFAULT: {
        "name": "Default",
        "description": "General video content, suitable for most scenarios",
        "icon": "🎬",
        "color": "#4facfe"
    },
    VideoCategory.KNOWLEDGE: {
        "name": "Knowledge",
        "description": "Educational, science, and tech content",
        "icon": "📚",
        "color": "#52c41a"
    },
    VideoCategory.BUSINESS: {
        "name": "Business",
        "description": "Business analysis, finance, and investment",
        "icon": "💼",
        "color": "#faad14"
    },
    VideoCategory.OPINION: {
        "name": "Opinion",
        "description": "Commentary, analysis, and debate",
        "icon": "💭",
        "color": "#722ed1"
    },
    VideoCategory.EXPERIENCE: {
        "name": "Experience",
        "description": "Life tips, tutorials, and practical advice",
        "icon": "🌟",
        "color": "#13c2c2"
    },
    VideoCategory.SPEECH: {
        "name": "Speech",
        "description": "Speeches, talk shows, podcasts, and interviews",
        "icon": "🎤",
        "color": "#eb2f96"
    },
    VideoCategory.CONTENT_REVIEW: {
        "name": "Review",
        "description": "Movie reviews, game commentary, reactions",
        "icon": "🎭",
        "color": "#f5222d"
    },
    VideoCategory.ENTERTAINMENT: {
        "name": "Entertainment",
        "description": "Variety shows, performances, fun content",
        "icon": "🎪",
        "color": "#fa8c16"
    },
    VideoCategory.PODCAST: {
        "name": "Podcast",
        "description": "Engaging podcast clips with strong hooks and payoffs",
        "icon": "🎙️",
        "color": "#7B1FA2"
    }
}

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Input file paths
INPUT_DIR = PROJECT_ROOT / "input"
INPUT_VIDEO = INPUT_DIR / "input.mp4"
INPUT_SRT = INPUT_DIR / "input.srt"
INPUT_TXT = INPUT_DIR / "input.txt"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "output"
CLIPS_DIR = OUTPUT_DIR / "clips"
COLLECTIONS_DIR = OUTPUT_DIR / "collections"
METADATA_DIR = OUTPUT_DIR / "metadata"

# Prompt file paths - Using English prompts
PROMPT_DIR = PROJECT_ROOT / "prompts" / "en"
PROMPT_FILES = {
    "outline": PROMPT_DIR / "outline.txt",
    "timeline": PROMPT_DIR / "timeline.txt", 
    "recommendation": PROMPT_DIR / "recommendation.txt",
    "title": PROMPT_DIR / "title_generation.txt",
    "clustering": PROMPT_DIR / "clustering.txt"
}

# API Configuration
MODEL_NAME = "grok-3-mini"

# Processing parameters
CHUNK_SIZE = 5000  # Text chunk size
MIN_SCORE_THRESHOLD = 0.7  # Minimum score threshold
MAX_CLIPS_PER_COLLECTION = 5  # Maximum clips per collection

# Short-form clip duration settings (in minutes, use fractions for seconds)
MIN_TOPIC_DURATION_MINUTES = 0.5  # Minimum clip duration (30 seconds)
MAX_TOPIC_DURATION_MINUTES = 1.5  # Maximum clip duration (90 seconds)
TARGET_TOPIC_DURATION_MINUTES = 1  # Target clip duration (60 seconds)
MIN_TOPICS_PER_CHUNK = 5  # Minimum topics per chunk (more clips for short-form)
MAX_TOPICS_PER_CHUNK = 15  # Maximum topics per chunk

# Ensure output directories exist
for dir_path in [CLIPS_DIR, COLLECTIONS_DIR, METADATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Configuration management system
class Settings(BaseModel):
    """System settings"""
    openrouter_api_key: Optional[str] = ""  # OpenRouter API key
    xai_api_key: Optional[str] = ""  # xAI (Grok) API key
    api_provider: str = "grok"  # API provider: openrouter or grok
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"  # OpenRouter model
    grok_model: str = "grok-3-mini"  # Grok model for highlight detection
    chunk_size: int = 5000
    min_score_threshold: float = 0.7
    max_clips_per_collection: int = 5
    max_retries: int = 3
    timeout_seconds: int = 30
    # Short-form clip duration settings (in minutes, use fractions for seconds)
    min_topic_duration_minutes: float = 0.5  # 30 seconds
    max_topic_duration_minutes: float = 1.5  # 90 seconds
    target_topic_duration_minutes: float = 1  # 60 seconds
    min_topics_per_chunk: int = 5
    max_topics_per_chunk: int = 15
    def __init__(self, **data):
        # Load configuration from environment variables
        env_mappings = {
            'openrouter_api_key': 'OPENROUTER_API_KEY',
            'xai_api_key': 'XAI_API_KEY',
            'api_provider': 'API_PROVIDER',
            'openrouter_model': 'OPENROUTER_MODEL',
            'grok_model': 'GROK_MODEL',
            'chunk_size': 'CHUNK_SIZE',
            'min_score_threshold': 'MIN_SCORE_THRESHOLD'
        }
        
        for field, env_var in env_mappings.items():
            if field not in data and os.getenv(env_var):
                env_value = os.getenv(env_var)
                if env_value is not None:
                    # Type conversion
                    if field == 'chunk_size':
                        data[field] = int(env_value)
                    elif field == 'min_score_threshold':
                        data[field] = float(env_value)
                    else:
                        data[field] = env_value
        
        super().__init__(**data)
    
    @field_validator('min_score_threshold')
    @classmethod
    def validate_score_threshold(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Score threshold must be between 0 and 1')
        return v
    
    @field_validator('chunk_size')
    @classmethod
    def validate_chunk_size(cls, v):
        if v <= 0:
            raise ValueError('Chunk size must be greater than 0')
        return v

@dataclass
class APIConfig:
    """API Configuration"""
    provider: str = "grok"  # openrouter or grok
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    grok_model: str = "grok-3-mini"
    openrouter_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    xai_base_url: str = "https://api.x.ai/v1"
    max_tokens: int = 4096

@dataclass
class ProcessingConfig:
    """Processing configuration."""
    chunk_size: int = 5000
    min_score_threshold: float = 0.7
    max_clips_per_collection: int = 5
    max_retries: int = 3
    timeout_seconds: int = 30

@dataclass
class PathConfig:
    """Filesystem path configuration."""
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    uploads_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "uploads")
    output_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "output")
    prompt_dir: Path = field(default_factory=lambda: PROMPT_DIR)
    temp_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "temp")

class ConfigManager:
    """Application configuration manager."""
    
    def __init__(self):
        self.settings = Settings()
        self._load_settings()
        self._setup_prompt_files()
    
    def _load_settings(self):
        """Load settings from disk, then let environment variables override them."""
        config_file = PROJECT_ROOT / "data" / "settings.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
            except Exception as e:
                print(f"Failed to load config file: {e}")

        self._apply_environment_overrides()

    def _apply_environment_overrides(self):
        """Apply environment variable overrides to the current settings."""
        env_mappings = {
            "openrouter_api_key": "OPENROUTER_API_KEY",
            "xai_api_key": "XAI_API_KEY",
            "api_provider": "API_PROVIDER",
            "openrouter_model": "OPENROUTER_MODEL",
            "grok_model": "GROK_MODEL",
        }

        for field, env_var in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                setattr(self.settings, field, env_value)

    def _sync_environment_from_settings(self):
        """Mirror active settings into process environment variables."""
        os.environ["OPENROUTER_API_KEY"] = self.settings.openrouter_api_key or ""
        os.environ["XAI_API_KEY"] = self.settings.xai_api_key or ""
        os.environ["API_PROVIDER"] = self.settings.api_provider
        os.environ["OPENROUTER_MODEL"] = self.settings.openrouter_model
        os.environ["GROK_MODEL"] = self.settings.grok_model
    
    def _setup_prompt_files(self):
        """Ensure the default English prompt directory exists."""
        self.prompt_files = PROMPT_FILES.copy()
        PROMPT_DIR.mkdir(exist_ok=True)
    
    def get_api_config(self) -> APIConfig:
        """Return API provider configuration."""
        return APIConfig(
            provider=self.settings.api_provider,
            openrouter_model=self.settings.openrouter_model,
            grok_model=self.settings.grok_model,
            openrouter_api_key=self.settings.openrouter_api_key,
            xai_api_key=self.settings.xai_api_key
        )
    
    def get_processing_config(self) -> ProcessingConfig:
        """Return processing configuration."""
        return ProcessingConfig(
            chunk_size=self.settings.chunk_size,
            min_score_threshold=self.settings.min_score_threshold,
            max_clips_per_collection=self.settings.max_clips_per_collection,
            max_retries=self.settings.max_retries,
            timeout_seconds=self.settings.timeout_seconds
        )
    
    def get_path_config(self) -> PathConfig:
        """Return path configuration."""
        return PathConfig()
    
    def ensure_project_directories(self, project_id: str):
        """Ensure the project directory structure exists."""
        paths = self.get_project_paths(project_id)
        
        for path in paths.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
    
    def get_project_paths(self, project_id: str) -> Dict[str, Path]:
        """Return the path layout for a project."""
        uploads_dir = self.get_path_config().uploads_dir
        project_base = uploads_dir / project_id
        
        return {
            "project_base": project_base,
            "input_dir": project_base / "input",
            "output_dir": project_base / "output",
            "clips_dir": project_base / "output" / "clips",
            "collections_dir": project_base / "output" / "collections",
            "metadata_dir": project_base / "output" / "metadata",
            "logs_dir": project_base / "logs",
            "temp_dir": project_base / "temp"
        }
    
    def update_api_key(self, api_key: str, provider: str = "openrouter"):
        """Update the configured API key for a provider."""
        if provider == "openrouter":
            self.settings.openrouter_api_key = api_key
            os.environ["OPENROUTER_API_KEY"] = api_key
        elif provider == "grok":
            self.settings.xai_api_key = api_key
            os.environ["XAI_API_KEY"] = api_key
        
        self._save_settings()
    
    def update_settings(self, **kwargs):
        """Update settings in memory and persist them."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._sync_environment_from_settings()
        self._save_settings()
    
    def _save_settings(self):
        """Persist settings to the local config file."""
        config_file = PROJECT_ROOT / "data" / "settings.json"
        config_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.model_dump(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save config file: {e}")
    
    def export_config(self) -> Dict[str, Any]:
        """Export the current configuration."""
        return {
            "api_config": {
                "provider": self.settings.api_provider,
                "openrouter_model": self.settings.openrouter_model,
                "grok_model": self.settings.grok_model,
                "openrouter_api_key": self.settings.openrouter_api_key[:8] + "..." if self.settings.openrouter_api_key else None,
                "xai_api_key": self.settings.xai_api_key[:8] + "..." if self.settings.xai_api_key else None
            },
            "processing_config": {
                "chunk_size": self.settings.chunk_size,
                "min_score_threshold": self.settings.min_score_threshold,
                "max_clips_per_collection": self.settings.max_clips_per_collection,
                "max_retries": self.settings.max_retries,
                "timeout_seconds": self.settings.timeout_seconds
            },
            "paths": {
                "project_root": str(self.get_path_config().project_root),
                "data_dir": str(self.get_path_config().data_dir),
                "uploads_dir": str(self.get_path_config().uploads_dir),
                "output_dir": str(self.get_path_config().output_dir),
                "prompt_dir": str(self.get_path_config().prompt_dir)
            }
        }

def get_prompt_files(video_category: str = VideoCategory.DEFAULT) -> Dict[str, Path]:
    """
    Return category-specific prompt files when present.
    Fall back to the default English prompts otherwise.
    """
    category_prompt_dir = PROMPT_DIR / video_category
    default_prompt_files = PROMPT_FILES.copy()
    
    if category_prompt_dir.exists():
        category_prompt_files = {}
        for key, default_path in default_prompt_files.items():
            category_file = category_prompt_dir / default_path.name
            if category_file.exists():
                category_prompt_files[key] = category_file
            else:
                category_prompt_files[key] = default_path
        return category_prompt_files
    
    return default_prompt_files

config_manager = ConfigManager()

def get_legacy_config() -> Dict[str, Any]:
    """Return a backwards-compatible configuration mapping."""
    return {
        'PROJECT_ROOT': PROJECT_ROOT,
        'INPUT_DIR': INPUT_DIR,
        'INPUT_VIDEO': INPUT_VIDEO,
        'INPUT_SRT': INPUT_SRT,
        'INPUT_TXT': INPUT_TXT,
        'OUTPUT_DIR': OUTPUT_DIR,
        'CLIPS_DIR': CLIPS_DIR,
        'COLLECTIONS_DIR': COLLECTIONS_DIR,
        'METADATA_DIR': METADATA_DIR,
        'PROMPT_DIR': PROMPT_DIR,
        'PROMPT_FILES': PROMPT_FILES,
        'MODEL_NAME': MODEL_NAME,
        'CHUNK_SIZE': CHUNK_SIZE,
        'MIN_SCORE_THRESHOLD': MIN_SCORE_THRESHOLD,
        'MAX_CLIPS_PER_COLLECTION': MAX_CLIPS_PER_COLLECTION,
        'MIN_TOPIC_DURATION_MINUTES': MIN_TOPIC_DURATION_MINUTES,
        'MAX_TOPIC_DURATION_MINUTES': MAX_TOPIC_DURATION_MINUTES,
        'TARGET_TOPIC_DURATION_MINUTES': TARGET_TOPIC_DURATION_MINUTES,
        'MIN_TOPICS_PER_CHUNK': MIN_TOPICS_PER_CHUNK,
        'MAX_TOPICS_PER_CHUNK': MAX_TOPICS_PER_CHUNK
    }
