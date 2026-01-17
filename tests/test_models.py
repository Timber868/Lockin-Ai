"""Tests for data models."""

import unittest
import numpy as np
from focusai.models import (
    Frame, ProcessedFrame, FocusResult, UIState, FocusState
)


class TestModels(unittest.TestCase):
    """Test cases for data models."""
    
    def test_focus_state_enum(self):
        """Test FocusState enumeration."""
        self.assertEqual(FocusState.FOCUSED.value, "focused")
        self.assertEqual(FocusState.UNFOCUSED.value, "unfocused")
        self.assertEqual(FocusState.UNCERTAIN.value, "uncertain")
    
    def test_frame_creation(self):
        """Test Frame dataclass creation."""
        frame = Frame(
            timestamp=123.456,
            data=np.zeros((480, 640, 3)),
            frame_id=1
        )
        self.assertEqual(frame.timestamp, 123.456)
        self.assertEqual(frame.frame_id, 1)
        self.assertEqual(frame.data.shape, (480, 640, 3))
    
    def test_focus_result_creation(self):
        """Test FocusResult dataclass creation."""
        result = FocusResult(
            timestamp=123.456,
            frame_id=1,
            state=FocusState.FOCUSED,
            confidence=0.95,
            details={"test": "data"}
        )
        self.assertEqual(result.state, FocusState.FOCUSED)
        self.assertEqual(result.confidence, 0.95)
        self.assertIn("test", result.details)


if __name__ == "__main__":
    unittest.main()
