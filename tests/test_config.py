"""Tests for configuration module."""

import unittest
from focusai.config import (
    Config, CaptureConfig, PreprocessConfig,
    InferenceConfig, UIConfig, load_config
)


class TestConfig(unittest.TestCase):
    """Test cases for configuration management."""
    
    def test_load_default_config(self):
        """Test loading default configuration."""
        config = load_config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config.capture, CaptureConfig)
        self.assertIsInstance(config.preprocess, PreprocessConfig)
        self.assertIsInstance(config.inference, InferenceConfig)
        self.assertIsInstance(config.ui, UIConfig)
    
    def test_capture_config_defaults(self):
        """Test CaptureConfig default values."""
        config = CaptureConfig()
        self.assertEqual(config.camera_id, 0)
        self.assertEqual(config.fps, 30)
        self.assertEqual(config.width, 640)
        self.assertEqual(config.height, 480)
    
    def test_preprocess_config_defaults(self):
        """Test PreprocessConfig default values."""
        config = PreprocessConfig()
        self.assertEqual(config.target_size, (224, 224))
        self.assertTrue(config.normalize)
        self.assertTrue(config.extract_faces)
    
    def test_inference_config_defaults(self):
        """Test InferenceConfig default values."""
        config = InferenceConfig()
        self.assertEqual(config.confidence_threshold, 0.7)
        self.assertEqual(config.device, "cpu")
    
    def test_ui_config_defaults(self):
        """Test UIConfig default values."""
        config = UIConfig()
        self.assertEqual(config.window_title, "LockIn AI Monitor")
        self.assertEqual(config.refresh_rate, 30)
        self.assertTrue(config.show_confidence)


if __name__ == "__main__":
    unittest.main()

