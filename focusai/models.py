"""Shared data models for the FocusAI system.

This module defines dataclasses used across different components of the
focus detection pipeline.
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
from enum import Enum


class FocusState(Enum):
    """Enumeration of possible focus states."""
    FOCUSED = "focused"
    UNFOCUSED = "unfocused"
    UNCERTAIN = "uncertain"


@dataclass
class Frame:
    """Raw camera frame data.
    
    Attributes:
        timestamp: Timestamp when frame was captured (seconds since epoch)
        data: Raw frame data as numpy array (H, W, C)
        frame_id: Unique identifier for the frame
    """
    timestamp: float
    data: np.ndarray
    frame_id: int


@dataclass
class ProcessedFrame:
    """Preprocessed frame ready for inference.
    
    Attributes:
        timestamp: Original capture timestamp
        frame_id: Original frame identifier
        features: Extracted features as numpy array
        preprocessed_data: Normalized/processed frame data
        metadata: Additional preprocessing metadata
    """
    timestamp: float
    frame_id: int
    features: np.ndarray
    preprocessed_data: np.ndarray
    metadata: dict


@dataclass
class FocusResult:
    """Result of focus detection inference.
    
    Attributes:
        timestamp: Timestamp of the result
        frame_id: Frame identifier this result corresponds to
        state: Detected focus state
        confidence: Confidence score (0.0 to 1.0)
        details: Additional inference details (e.g., attention scores, gaze data)
    """
    timestamp: float
    frame_id: int
    state: FocusState
    confidence: float
    details: dict


@dataclass
class UIState:
    """State information for UI rendering.
    
    Attributes:
        focus_result: Latest focus detection result
        history: Recent history of focus states for visualization
        alert_active: Whether an alert should be displayed
        message: Optional message to display to user
    """
    focus_result: FocusResult
    history: list[FocusResult]
    alert_active: bool
    message: Optional[str] = None
