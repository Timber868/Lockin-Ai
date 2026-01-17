# LockIn AI System Architecture

This document describes the architecture and design of the LockIn AI focus detection system.

## System Overview

LockIn AI is a real-time focus detection system that processes video frames through a multi-stage pipeline to determine whether a user is focused on their task. The system provides immediate visual feedback to help users maintain attention.

## Architecture Diagram

```
┌─────────────┐
│   Camera    │
└──────┬──────┘
       │ Raw Frames
       ▼
┌─────────────┐
│   Capture   │ ← CaptureConfig
└──────┬──────┘
       │ Frame
       ▼
┌─────────────┐
│ Preprocess  │ ← PreprocessConfig
└──────┬──────┘
       │ ProcessedFrame
       ▼
┌─────────────┐
│  Features   │
└──────┬──────┘
       │ ProcessedFrame + Features
       ▼
┌─────────────┐
│  Inference  │ ← InferenceConfig
└──────┬──────┘
       │ FocusResult
       ▼
┌─────────────┐
│     UI      │ ← UIConfig
└─────────────┘
```

## Components

### 1. Capture Module (`focusai/capture/`)

**Purpose**: Capture video frames from camera devices.

**Key Classes**:
- `CameraCapture`: Manages camera initialization and frame streaming

**Responsibilities**:
- Initialize and configure camera device
- Capture frames at specified FPS
- Provide continuous frame stream
- Handle camera resource management

**Outputs**: `Frame` objects containing:
- Timestamp
- Raw frame data (numpy array)
- Frame ID

**Configuration**: `CaptureConfig`
- Camera device ID
- Target FPS
- Frame dimensions

### 2. Preprocess Module (`focusai/preprocess/`)

**Purpose**: Prepare raw frames for inference by normalizing and extracting regions of interest.

**Key Classes**:
- `FramePreprocessor`: Handles frame normalization and resizing
- `FeatureExtractor`: Extracts facial features and indicators

**Responsibilities**:
- Resize frames to target dimensions
- Normalize pixel values
- Detect and extract face regions
- Extract facial landmarks
- Estimate gaze direction
- Estimate head pose

**Outputs**: `ProcessedFrame` objects containing:
- Original timestamp and frame ID
- Preprocessed frame data
- Extracted features (landmarks, gaze, pose)
- Preprocessing metadata

**Configuration**: `PreprocessConfig`
- Target frame size
- Normalization settings
- Face extraction enable/disable
- Feature extraction method

### 3. Inference Module (`focusai/inference/`)

**Purpose**: Determine focus state using machine learning models.

**Key Classes**:
- `FocusDetector`: Runs inference on processed frames

**Responsibilities**:
- Load trained ML model
- Prepare features for model input
- Run inference to classify focus state
- Apply confidence thresholds
- Provide detailed inference results

**Outputs**: `FocusResult` objects containing:
- Timestamp and frame ID
- Focus state (FOCUSED/UNFOCUSED/UNCERTAIN)
- Confidence score (0.0 to 1.0)
- Additional inference details

**Configuration**: `InferenceConfig`
- Model file path
- Confidence threshold
- Batch size
- Device (CPU/GPU)

### 4. UI Module (`focusai/ui/`)

**Purpose**: Display real-time focus detection results to the user.

**Key Classes**:
- `FocusMonitorUI`: Manages the user interface and visualization

**Responsibilities**:
- Display current focus state
- Show confidence scores
- Visualize historical focus data
- Trigger alerts when focus drops
- Maintain history of recent results

**Outputs**: Visual display with:
- Focus state indicator
- Confidence meter
- Historical graph
- Alert messages

**Configuration**: `UIConfig`
- Window title and size
- Refresh rate
- Display options (show confidence, etc.)
- Alert threshold
- History length

## Data Models

### Core Data Classes

```python
@dataclass
class Frame:
    """Raw camera frame"""
    timestamp: float
    data: np.ndarray
    frame_id: int

@dataclass
class ProcessedFrame:
    """Preprocessed frame with features"""
    timestamp: float
    frame_id: int
    features: np.ndarray
    preprocessed_data: np.ndarray
    metadata: dict

@dataclass
class FocusResult:
    """Focus detection result"""
    timestamp: float
    frame_id: int
    state: FocusState
    confidence: float
    details: dict

@dataclass
class UIState:
    """UI rendering state"""
    focus_result: FocusResult
    history: list[FocusResult]
    alert_active: bool
    message: Optional[str]
```

## Configuration System

The system uses a hierarchical configuration structure:

```
Config
├── CaptureConfig
├── PreprocessConfig
├── InferenceConfig
├── UIConfig
└── log_level
```

Configuration can be loaded from:
1. Configuration files (JSON/YAML)
2. Command-line arguments
3. Environment variables
4. Default values

## Logging

Structured logging is provided by the `logging_setup` module:
- Hierarchical logger names (`LockIn AI.module.submodule`)
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- Console and file output options
- Consistent log format with timestamps and context

## Pipeline Flow

### Main Loop

```python
while system.is_running:
    # 1. Capture
    frame = capture.capture_frame()
    
    # 2. Preprocess
    processed_frame = preprocessor.preprocess(frame)
    processed_frame = feature_extractor.extract(processed_frame)
    
    # 3. Inference
    focus_result = detector.detect(processed_frame)
    
    # 4. Update UI
    ui.update(focus_result)
```

### Data Flow

```
Camera → Frame → ProcessedFrame → FocusResult → UIState → Display
```

## Performance Considerations

### Real-Time Requirements
- Target: 30 FPS processing
- Latency: < 100ms end-to-end
- Frame drops: Acceptable under high load

### Optimization Strategies
1. **Batch Processing**: Process multiple frames together
2. **GPU Acceleration**: Use GPU for inference when available
3. **Frame Skipping**: Skip frames if processing falls behind
4. **Async Processing**: Pipeline stages can run concurrently
5. **Model Optimization**: Use quantized or pruned models

## Error Handling

### Failure Modes
- Camera not available
- Model file not found
- Inference errors
- UI display errors

### Recovery Strategies
- Graceful degradation
- Logging of all errors
- User-friendly error messages
- Automatic retry for transient failures

## Extension Points

The architecture supports extensions through:

1. **Custom Preprocessors**: Implement new preprocessing methods
2. **Feature Extractors**: Add new feature extraction techniques
3. **Models**: Swap or ensemble multiple models
4. **UI Implementations**: Different UI frameworks (pygame, tkinter, web)
5. **Alert Systems**: Additional notification methods (audio, desktop, etc.)

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock external dependencies (camera, models)
- Validate configuration handling

### Integration Tests
- Test pipeline end-to-end
- Use synthetic/recorded data
- Validate data flow between components

### Performance Tests
- Measure FPS and latency
- Profile bottlenecks
- Test under various conditions

## Future Enhancements

### Short Term
1. Implement actual CV and ML functionality
2. Train focus detection models
3. Build complete UI
4. Add comprehensive tests

### Long Term
1. Multi-user support
2. Cloud-based inference
3. Mobile app integration
4. Historical analytics and reports
5. Customizable alerts and notifications
6. Integration with productivity tools
7. Adaptive learning from user feedback

## Security and Privacy

### Considerations
- All processing happens locally by default
- No frame data sent to external servers
- Optional telemetry (opt-in only)
- Secure model storage
- User data encryption at rest

### Best Practices
- Minimize data retention
- Clear user consent for camera access
- Audit logs for security events
- Regular security updates

## Dependencies

### Core
- `numpy`: Array operations and data handling

### Optional (Computer Vision)
- `opencv-python`: Camera capture and image processing
- `mediapipe`: Face detection and feature extraction

### Optional (Machine Learning)
- `torch`/`torchvision`: Deep learning framework
- `onnxruntime`: Optimized inference runtime

### Optional (UI)
- `pygame`: Game engine for UI
- `tkinter`: Standard Python GUI toolkit

## Deployment

### Development
```bash
python main.py --log-level DEBUG
```

### Production
```bash
python main.py --config production.yaml --log-file /var/log/lockin-ai.log
```

### Docker (Future)
```bash
docker build -t lockin-ai .
docker run -it --device=/dev/video0 lockin-ai
```

## Conclusion

LockIn AI's modular architecture provides a clean separation of concerns while maintaining a straightforward data flow. The design emphasizes:
- **Modularity**: Each component is independent and replaceable
- **Testability**: Clear interfaces enable comprehensive testing
- **Extensibility**: New features can be added without major refactoring
- **Performance**: Architecture supports real-time processing requirements
- **Maintainability**: Well-documented code with consistent patterns

