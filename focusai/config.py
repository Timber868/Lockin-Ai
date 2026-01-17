"""Configuration management for LockIn AI system.

This module handles loading and managing configuration settings from
files and environment variables.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class CaptureConfig:
    """Configuration for camera capture.
    
    Attributes:
        camera_id: Camera device ID (0 for default)
        fps: Target frames per second
        width: Frame width in pixels
        height: Frame height in pixels
    """
    camera_id: int = 0
    fps: int = 30
    width: int = 640
    height: int = 480


@dataclass
class PreprocessConfig:
    """Configuration for preprocessing pipeline.
    
    Attributes:
        target_size: Target size for frame resizing (width, height)
        normalize: Whether to normalize pixel values
        extract_faces: Whether to extract face regions
        feature_extraction_method: Method for feature extraction
    """
    target_size: tuple[int, int] = (224, 224)
    normalize: bool = True
    extract_faces: bool = True
    feature_extraction_method: str = "basic"


@dataclass
class InferenceConfig:
    """Configuration for inference engine.
    
    Attributes:
        model_path: Path to the trained model file
        confidence_threshold: Minimum confidence for focus detection
        batch_size: Batch size for inference
        device: Device to run inference on ('cpu' or 'cuda')
    """
    model_path: Optional[str] = None
    confidence_threshold: float = 0.7
    batch_size: int = 1
    device: str = "cpu"


@dataclass
class UIConfig:
    """Configuration for user interface.
    
    Attributes:
        window_title: Title of the UI window
        refresh_rate: UI refresh rate in Hz
        show_confidence: Whether to display confidence scores
        alert_threshold: Focus confidence below which to alert
        history_length: Number of historical results to maintain
    """
    window_title: str = "LockIn AI Monitor"
    refresh_rate: int = 30
    show_confidence: bool = True
    alert_threshold: float = 0.5
    history_length: int = 100


@dataclass
class Config:
    """Main configuration container.
    
    Attributes:
        capture: Camera capture configuration
        preprocess: Preprocessing configuration
        inference: Inference configuration
        ui: User interface configuration
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    capture: CaptureConfig
    preprocess: PreprocessConfig
    inference: InferenceConfig
    ui: UIConfig
    log_level: str = "INFO"


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or use defaults.
    
    Args:
        config_path: Optional path to configuration file (JSON/YAML)
    
    Returns:
        Config object with loaded or default settings
    """
    # TODO: Implement config file loading
    # For now, return default configuration
    return Config(
        capture=CaptureConfig(),
        preprocess=PreprocessConfig(),
        inference=InferenceConfig(),
        ui=UIConfig(),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )


def save_config(config: Config, config_path: str) -> None:
    """Save configuration to file.
    
    Args:
        config: Configuration object to save
        config_path: Path where configuration should be saved
    """
    # TODO: Implement config file saving
    pass

