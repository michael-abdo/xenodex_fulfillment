"""Shared utility functions for all API integrations"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up logging based on configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Logger instance
    """
    logging_config = config.get('logging', {})
    level = logging_config.get('level', 'INFO')
    format_str = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.basicConfig(
        level=getattr(logging, level),
        format=format_str
    )
    
    return logging.getLogger('xenodx_fulfillment')


def validate_file(file_path: str) -> Path:
    """
    Validate that file exists and has supported extension
    
    Args:
        file_path: Path to file
        
    Returns:
        Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type not supported
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    # Supported extensions
    supported_extensions = {'.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg'}
    
    if path.suffix.lower() not in supported_extensions:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    
    return path


def get_file_duration(file_path: Path) -> Optional[float]:
    """
    Get duration of audio/video file
    
    Args:
        file_path: Path to media file
        
    Returns:
        Duration in seconds or None if cannot determine
    """
    # This is a placeholder - actual implementation would use
    # a library like mutagen or ffprobe
    return None