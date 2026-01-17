"""Tests for camera capture module."""

import unittest
from focusai.capture.camera import CameraCapture, create_capture
from focusai.config import CaptureConfig


class TestCameraCapture(unittest.TestCase):
    """Test cases for CameraCapture class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = CaptureConfig(camera_id=0, fps=30)
        self.capture = create_capture(self.config)
    
    def test_initialization(self):
        """Test camera capture initialization."""
        self.assertIsNotNone(self.capture)
        self.assertEqual(self.capture.config.camera_id, 0)
        self.assertFalse(self.capture.is_running)
    
    def test_start_stop(self):
        """Test starting and stopping camera."""
        self.capture.start()
        self.assertTrue(self.capture.is_running)
        
        self.capture.stop()
        self.assertFalse(self.capture.is_running)
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with create_capture(self.config) as capture:
            self.assertTrue(capture.is_running)
        # After context, should be stopped
        self.assertFalse(capture.is_running)
    
    # TODO: Add more comprehensive tests with mocked camera


if __name__ == "__main__":
    unittest.main()

