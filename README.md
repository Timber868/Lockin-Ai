# FocusAI - Real-Time Focus Detection System

A Python-based real-time focus detection system that monitors user attention through camera input and provides live visual feedback. Built for McHacks 2026.

## Overview

FocusAI uses computer vision and machine learning to detect whether a user is focused on their task. The system captures video frames from a camera, processes them to extract relevant features, runs inference to determine focus state, and displays real-time feedback through a user interface.

## Project Structure

```
Lockin-Ai/
├── focusai/                    # Main package
│   ├── __init__.py            # Package initialization
│   ├── models.py              # Shared dataclasses
│   ├── config.py              # Configuration management
│   ├── logging_setup.py       # Logging configuration
│   ├── capture/               # Camera frame capture
│   │   ├── __init__.py
│   │   └── camera.py          # Camera capture implementation
│   ├── preprocess/            # Frame preprocessing
│   │   ├── __init__.py
│   │   ├── processor.py       # Frame preprocessing
│   │   └── features.py        # Feature extraction
│   ├── inference/             # Focus detection inference
│   │   ├── __init__.py
│   │   └── detector.py        # Focus detection model
│   └── ui/                    # User interface
│       ├── __init__.py
│       └── monitor.py         # Live monitoring UI
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_capture.py
│   ├── test_preprocess.py
│   ├── test_inference.py
│   ├── test_ui.py
│   ├── test_config.py
│   └── test_models.py
├── docs/                      # Documentation
│   └── architecture.md        # Architecture details
├── main.py                    # Main entry point
├── pyproject.toml             # Project metadata
├── requirements.txt           # Core dependencies
├── requirements-dev.txt       # Development dependencies
├── README.md                  # This file
├── LICENSE                    # MIT License
└── .gitignore                # Git ignore rules
```

## Features

- **Real-time camera capture**: Efficient video frame capture from camera devices
- **Preprocessing pipeline**: Frame normalization, resizing, and face detection
- **Feature extraction**: Extraction of facial landmarks, gaze direction, and head pose
- **Focus detection**: Machine learning-based inference for focus state classification
- **Live UI feedback**: Real-time visual feedback with alerts and confidence scores
- **Configurable**: Flexible configuration system for all components
- **Modular design**: Clean separation of concerns for easy development and testing

## Installation

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/Timber868/Lockin-Ai.git
cd Lockin-Ai

# Install core dependencies
pip install -r requirements.txt
```

### Full Installation (with all optional dependencies)

```bash
# Install with computer vision support
pip install -r requirements.txt opencv-python mediapipe

# Install with machine learning support
pip install torch torchvision onnxruntime

# Install with UI support
pip install pygame

# Or install everything using pyproject.toml
pip install -e ".[all]"
```

### Development Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Or use pyproject.toml
pip install -e ".[dev]"
```

## Usage

### Running the System

```bash
# Run with default settings
python main.py

# Specify camera device
python main.py --camera 0

# Set log level
python main.py --log-level DEBUG

# Use custom configuration file
python main.py --config config.yaml

# Save logs to file
python main.py --log-file focusai.log
```

## Web Frontend (React)

This repo now includes a React-based web dashboard under `frontend/`. It is a
standalone UI prototype that can be wired to the Python service later.

```bash
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`.

### Configuration

Configuration can be provided via:
1. Configuration file (JSON/YAML) - use `--config` flag
2. Command line arguments
3. Environment variables
4. Default values in code

Example configuration structure:
```python
from focusai.config import Config, CaptureConfig, PreprocessConfig, InferenceConfig, UIConfig

config = Config(
    capture=CaptureConfig(camera_id=0, fps=30, width=640, height=480),
    preprocess=PreprocessConfig(target_size=(224, 224), normalize=True),
    inference=InferenceConfig(confidence_threshold=0.7, device="cpu"),
    ui=UIConfig(alert_threshold=0.5, show_confidence=True),
    log_level="INFO"
)
```

## Architecture

The system follows a pipeline architecture with four main stages:

1. **Capture**: Camera frames are captured at a specified FPS
2. **Preprocess**: Frames are normalized, resized, and prepared for analysis
3. **Inference**: ML model determines focus state and confidence
4. **UI**: Results are displayed with visual feedback and alerts

See [docs/architecture.md](docs/architecture.md) for detailed architecture information.

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_capture.py

# Run with coverage
pytest --cov=focusai --cov-report=html

# Run specific test
pytest tests/test_config.py::TestConfig::test_load_default_config
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black focusai/ tests/

# Lint code
flake8 focusai/ tests/

# Type check
mypy focusai/
```

### Project Status

⚠️ **Current Status**: Project skeleton only - no CV/ML implementation yet

This is a skeleton project with:
- ✅ Complete module structure
- ✅ Function signatures and interfaces
- ✅ Configuration management
- ✅ Logging setup
- ✅ Basic tests
- ✅ Documentation
- ❌ Actual computer vision implementation (TODO)
- ❌ Trained ML models (TODO)
- ❌ UI rendering implementation (TODO)

## Next Steps

To implement the full system:

1. **Camera Capture**: Implement actual camera capture using OpenCV
2. **Preprocessing**: Add face detection, frame normalization, and resizing
3. **Feature Extraction**: Implement facial landmark detection, gaze tracking, head pose estimation
4. **Model Training**: Train or integrate a focus detection model
5. **Inference**: Load and run the trained model
6. **UI Implementation**: Build the actual UI using pygame/tkinter/OpenCV
7. **Testing**: Add comprehensive tests with mock data
8. **Optimization**: Profile and optimize for real-time performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Team

Built for McHacks 2026 by the Lockin-AI team.

## Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for face and pose detection
- PyTorch for machine learning framework 
