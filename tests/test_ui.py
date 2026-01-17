"""Tests for UI module."""

import unittest
from focusai.ui.monitor import FocusMonitorUI, create_ui
from focusai.config import UIConfig
from focusai.models import FocusResult, FocusState


class TestFocusMonitorUI(unittest.TestCase):
    """Test cases for FocusMonitorUI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = UIConfig(
            alert_threshold=0.5,
            history_length=100
        )
        self.ui = create_ui(self.config)
    
    def test_initialization(self):
        """Test UI initialization."""
        self.assertIsNotNone(self.ui)
        self.assertEqual(self.ui.config.history_length, 100)
        self.assertFalse(self.ui.is_running)
    
    def test_should_alert_unfocused(self):
        """Test alert triggering for unfocused state."""
        result = FocusResult(
            timestamp=0.0,
            frame_id=0,
            state=FocusState.UNFOCUSED,
            confidence=0.8,
            details={}
        )
        self.assertTrue(self.ui.should_alert(result))
    
    def test_should_alert_low_confidence(self):
        """Test alert triggering for low confidence."""
        result = FocusResult(
            timestamp=0.0,
            frame_id=0,
            state=FocusState.FOCUSED,
            confidence=0.3,
            details={}
        )
        self.assertTrue(self.ui.should_alert(result))
    
    # TODO: Add more comprehensive UI tests


if __name__ == "__main__":
    unittest.main()

