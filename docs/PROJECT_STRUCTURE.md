# LockIn AI Project Structure and API Reference

## Project Tree

```
Lockin-Ai/
├── LICENSE                          # MIT License
├── README.md                        # Project overview and documentation
├── pyproject.toml                   # Project metadata and dependencies
├── requirements.txt                 # Core dependencies
├── requirements-dev.txt             # Development dependencies
├── main.py                          # Main entry point
├── docs/
│   └── architecture.md              # Architecture documentation
├── focusai/                         # Main package
│   ├── __init__.py                  # Package initialization (version)
│   ├── models.py                    # Shared dataclasses
│   ├── config.py                    # Configuration management
│   ├── logging_setup.py             # Logging configuration
│   ├── capture/                     # Camera frame capture module
│   │   ├── __init__.py
│   │   └── camera.py                # Camera capture implementation
│   ├── preprocess/                  # Frame preprocessing module
│   │   ├── __init__.py
│   │   ├── processor.py             # Frame preprocessing
│   │   └── features.py              # Feature extraction
│   ├── inference/                   # Focus detection inference module
│   │   ├── __init__.py
│   │   └── detector.py              # Focus detection model
│   └── ui/                          # User interface module
│       ├── __init__.py
│       └── monitor.py               # Live monitoring UI
└── tests/                           # Test suite
    ├── __init__.py
    ├── test_capture.py              # Tests for capture module
    ├── test_preprocess.py           # Tests for preprocess module
    ├── test_inference.py            # Tests for inference module
    ├── test_ui.py                   # Tests for UI module
    ├── test_config.py               # Tests for configuration
    └── test_models.py               # Tests for data models
```

## Module Overview and Function Signatures

### 1. Shared Models (`focusai/models.py`)

**Purpose**: Define shared data structures used across the system.

**Key Classes**:

```python
class FocusState(Enum):
    """Enumeration of possible focus states."""
    FOCUSED = "focused"
    UNFOCUSED = "unfocused"
    UNCERTAIN = "uncertain"

@dataclass
class Frame:
    """Raw camera frame data."""
    timestamp: float         # Timestamp when frame was captured
    data: np.ndarray        # Raw frame data (H, W, C)
    frame_id: int           # Unique frame identifier

@dataclass
class ProcessedFrame:
    """Preprocessed frame ready for inference."""
    timestamp: float
    frame_id: int
    features: np.ndarray           # Extracted features
    preprocessed_data: np.ndarray  # Normalized/processed data
    metadata: dict                 # Additional metadata

@dataclass
class FocusResult:
    """Result of focus detection inference."""
    timestamp: float
    frame_id: int
    state: FocusState      # Detected focus state
    confidence: float      # Confidence score (0.0 to 1.0)
    details: dict          # Additional inference details

@dataclass
class UIState:
    """State information for UI rendering."""
    focus_result: FocusResult
    history: list[FocusResult]
    alert_active: bool
    message: Optional[str]
```

### 2. Configuration (`focusai/config.py`)

**Purpose**: Manage system configuration.

**Key Functions**:

```python
def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file or use defaults."""

def save_config(config: Config, config_path: str) -> None:
    """Save configuration to file."""
```

**Configuration Classes**:

```python
@dataclass
class CaptureConfig:
    camera_id: int = 0
    fps: int = 30
    width: int = 640
    height: int = 480

@dataclass
class PreprocessConfig:
    target_size: tuple[int, int] = (224, 224)
    normalize: bool = True
    extract_faces: bool = True
    feature_extraction_method: str = "basic"

@dataclass
class InferenceConfig:
    model_path: Optional[str] = None
    confidence_threshold: float = 0.7
    batch_size: int = 1
    device: str = "cpu"

@dataclass
class UIConfig:
    window_title: str = "LockIn AI Monitor"
    refresh_rate: int = 30
    show_confidence: bool = True
    alert_threshold: float = 0.5
    history_length: int = 100

@dataclass
class Config:
    capture: CaptureConfig
    preprocess: PreprocessConfig
    inference: InferenceConfig
    ui: UIConfig
    log_level: str = "INFO"
```

### 3. Logging Setup (`focusai/logging_setup.py`)

**Purpose**: Configure structured logging for all components.

**Key Functions**:

```python
def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """Configure logging for the application."""

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
```

### 4. Capture Module (`focusai/capture/camera.py`)

**Purpose**: Capture video frames from camera devices.

**Key Class**:

```python
class CameraCapture:
    def __init__(self, config: CaptureConfig):
        """Initialize camera capture."""
    
    def start(self) -> None:
        """Start the camera and prepare for capture."""
    
    def stop(self) -> None:
        """Stop the camera and release resources."""
    
    def capture_frame(self) -> Optional[Frame]:
        """Capture a single frame from the camera."""
    
    def stream_frames(self) -> Generator[Frame, None, None]:
        """Continuously stream frames from the camera."""
    
    def __enter__(self) / __exit__(self, ...):
        """Context manager support."""
```

**Factory Function**:

```python
def create_capture(config: CaptureConfig) -> CameraCapture:
    """Factory function to create a camera capture instance."""
```

### 5. Preprocess Module (`focusai/preprocess/processor.py`)

**Purpose**: Preprocess raw camera frames.

**Key Class**:

```python
class FramePreprocessor:
    def __init__(self, config: PreprocessConfig):
        """Initialize the preprocessor."""
    
    def resize_frame(self, frame_data: np.ndarray) -> np.ndarray:
        """Resize frame to target dimensions."""
    
    def normalize_frame(self, frame_data: np.ndarray) -> np.ndarray:
        """Normalize pixel values to [0, 1] range."""
    
    def extract_face_region(self, frame_data: np.ndarray) -> Optional[np.ndarray]:
        """Extract face region from frame."""
    
    def preprocess(self, frame: Frame) -> ProcessedFrame:
        """Apply full preprocessing pipeline to a frame."""
```

**Factory Function**:

```python
def create_preprocessor(config: PreprocessConfig) -> FramePreprocessor:
    """Factory function to create a preprocessor instance."""
```

### 6. Feature Extraction (`focusai/preprocess/features.py`)

**Purpose**: Extract features from preprocessed frames.

**Key Class**:

```python
class FeatureExtractor:
    def __init__(self, config: PreprocessConfig):
        """Initialize the feature extractor."""
    
    def extract_facial_landmarks(self, frame_data: np.ndarray) -> np.ndarray:
        """Extract facial landmark points."""
    
    def extract_gaze_features(self, frame_data: np.ndarray) -> np.ndarray:
        """Extract gaze direction features."""
    
    def extract_head_pose(self, frame_data: np.ndarray) -> np.ndarray:
        """Extract head pose estimation."""
    
    def extract(self, processed_frame: ProcessedFrame) -> ProcessedFrame:
        """Extract all configured features from frame."""
```

**Factory Function**:

```python
def create_feature_extractor(config: PreprocessConfig) -> FeatureExtractor:
    """Factory function to create a feature extractor instance."""
```

### 7. Inference Module (`focusai/inference/detector.py`)

**Purpose**: Detect focus state using machine learning models.

**Key Class**:

```python
class FocusDetector:
    def __init__(self, config: InferenceConfig):
        """Initialize the focus detector."""
    
    def load_model(self, model_path: Optional[str] = None) -> None:
        """Load the focus detection model."""
    
    def preprocess_for_inference(self, processed_frame: ProcessedFrame):
        """Prepare processed frame for model inference."""
    
    def run_inference(self, model_input) -> tuple[FocusState, float, dict]:
        """Run model inference on prepared input."""
    
    def postprocess_result(
        self, state: FocusState, confidence: float,
        details: dict, frame_id: int
    ) -> FocusResult:
        """Postprocess inference results."""
    
    def detect(self, processed_frame: ProcessedFrame) -> FocusResult:
        """Detect focus state from a processed frame."""
    
    def batch_detect(
        self, processed_frames: list[ProcessedFrame]
    ) -> list[FocusResult]:
        """Detect focus state for multiple frames in batch."""
```

**Factory Function**:

```python
def create_detector(config: InferenceConfig) -> FocusDetector:
    """Factory function to create a focus detector instance."""
```

### 8. UI Module (`focusai/ui/monitor.py`)

**Purpose**: Display real-time focus detection results.

**Key Class**:

```python
class FocusMonitorUI:
    def __init__(self, config: UIConfig):
        """Initialize the UI."""
    
    def initialize_window(self) -> None:
        """Initialize the display window."""
    
    def close_window(self) -> None:
        """Close and cleanup the display window."""
    
    def should_alert(self, result: FocusResult) -> bool:
        """Determine if an alert should be shown."""
    
    def render_focus_indicator(self, state: FocusState, confidence: float) -> None:
        """Render the main focus state indicator."""
    
    def render_confidence_meter(self, confidence: float) -> None:
        """Render confidence score meter."""
    
    def render_history_graph(self) -> None:
        """Render historical focus data as a graph."""
    
    def render_alert(self, message: str) -> None:
        """Render an alert message to the user."""
    
    def update(self, result: FocusResult) -> None:
        """Update UI with new focus detection result."""
    
    def start(self) -> None:
        """Start the UI event loop."""
    
    def stop(self) -> None:
        """Stop the UI and cleanup."""
    
    def __enter__(self) / __exit__(self, ...):
        """Context manager support."""
```

**Factory Function**:

```python
def create_ui(config: UIConfig) -> FocusMonitorUI:
    """Factory function to create a UI instance."""
```

### 9. Main Entry Point (`main.py`)

**Purpose**: Wire together all components and run the system.

**Key Class**:

```python
class LockInAISystem:
    def __init__(self, config: Config):
        """Initialize the LockIn AI system."""
    
    def initialize_components(self) -> None:
        """Initialize all system components."""
    
    def process_frame(self, frame) -> None:
        """Process a single frame through the pipeline."""
    
    def run(self) -> None:
        """Run the main focus detection loop."""
    
    def shutdown(self) -> None:
        """Cleanly shutdown all system components."""
```

**Key Functions**:

```python
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

def main() -> int:
    """Main entry point."""
```

**Command Line Usage**:

```bash
python main.py [OPTIONS]

Options:
  --config PATH          Path to configuration file
  --log-level LEVEL      Logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
  --log-file PATH        Path to log file
  --camera ID            Camera device ID (default: 0)
```

## Data Flow

```
Camera
  ↓ (raw frames)
CameraCapture.capture_frame()
  ↓ Frame
FramePreprocessor.preprocess()
  ↓ ProcessedFrame (partial)
FeatureExtractor.extract()
  ↓ ProcessedFrame (with features)
FocusDetector.detect()
  ↓ FocusResult
FocusMonitorUI.update()
  ↓ (visual display)
User
```

## Implementation Status

### ✅ Complete
- Module structure and organization
- Data models and types
- Configuration system
- Logging setup
- Function signatures and interfaces
- Basic unit tests
- Documentation (README, architecture)
- Project metadata (pyproject.toml)

### ❌ To Be Implemented
- Actual camera capture (OpenCV integration)
- Face detection and extraction
- Feature extraction (landmarks, gaze, pose)
- ML model training and integration
- Model inference implementation
- UI rendering (pygame/tkinter/OpenCV)
- Comprehensive testing with real data
- Performance optimization

## Usage Examples

### Basic Usage

```python
from focusai.config import load_config
from main import LockInAISystem

# Load configuration
config = load_config()

# Create and run system
system = LockInAISystem(config)
system.initialize_components()
system.run()
```

### Custom Configuration

```python
from focusai.config import Config, CaptureConfig, InferenceConfig

# Create custom configuration
config = Config(
    capture=CaptureConfig(camera_id=1, fps=60),
    inference=InferenceConfig(device="cuda"),
    log_level="DEBUG"
)

# Use custom config
system = LockInAISystem(config)
```

### Processing Single Frame

```python
from focusai.capture.camera import create_capture
from focusai.preprocess.processor import create_preprocessor
from focusai.preprocess.features import create_feature_extractor
from focusai.inference.detector import create_detector

# Initialize components
capture = create_capture(config.capture)
preprocessor = create_preprocessor(config.preprocess)
extractor = create_feature_extractor(config.preprocess)
detector = create_detector(config.inference)

# Process frame
frame = capture.capture_frame()
processed = preprocessor.preprocess(frame)
processed = extractor.extract(processed)
result = detector.detect(processed)

print(f"Focus: {result.state.value}, Confidence: {result.confidence:.2f}")
```

## Development Notes

### Adding New Features

1. **New Preprocessing Method**: Extend `FramePreprocessor` or `FeatureExtractor`
2. **New Model**: Modify `FocusDetector.load_model()` and `run_inference()`
3. **New UI Component**: Add methods to `FocusMonitorUI`
4. **New Configuration**: Add to appropriate config dataclass

### Testing

All modules have corresponding test files in `tests/`:
- `test_capture.py` - Camera capture tests
- `test_preprocess.py` - Preprocessing tests
- `test_inference.py` - Inference tests
- `test_ui.py` - UI tests
- `test_config.py` - Configuration tests
- `test_models.py` - Data model tests

### Code Style

Follow Python best practices:
- Type hints for all function signatures
- Docstrings for all public APIs
- PEP 8 style guide (enforced by black)
- Comprehensive error handling
- Structured logging

## Next Steps for Implementation

1. **Phase 1 - Camera Capture**
   - Integrate OpenCV for camera access
   - Implement frame capture and streaming
   - Add camera error handling

2. **Phase 2 - Preprocessing**
   - Implement face detection (MediaPipe/dlib)
   - Add frame normalization and resizing
   - Extract facial landmarks

3. **Phase 3 - Feature Engineering**
   - Implement gaze estimation
   - Add head pose detection
   - Create feature vectors

4. **Phase 4 - Model Development**
   - Collect/prepare training data
   - Train focus detection model
   - Export model for inference

5. **Phase 5 - Inference**
   - Load trained model
   - Implement inference pipeline
   - Add confidence calibration

6. **Phase 6 - UI Development**
   - Create visual indicators
   - Add real-time graphs
   - Implement alert system

7. **Phase 7 - Testing & Optimization**
   - Add comprehensive tests
   - Profile and optimize
   - Ensure real-time performance

