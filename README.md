# LockIn AI - Real-Time Focus Detection System

A Python-based real-time focus detection system that monitors user attention through camera input and provides live visual feedback. Built for McHacks 2026.

## Overview

LockIn AI uses computer vision and machine learning to detect whether a user is focused on their task. The system captures video frames from a camera, processes them to extract relevant features, runs inference to determine focus state, and displays real-time feedback through a user interface.

## Project Structure

```
Lockin-Ai/
├── focusai/                    # Main Python package
│   ├── __init__.py            # Package initialization
│   ├── models.py              # Shared dataclasses
│   ├── config.py              # Configuration management
│   ├── logging_setup.py       # Logging configuration
│   ├── vision_server.py       # WebSocket vision server (main backend)
│   ├── capture/               # Camera frame capture
│   │   ├── __init__.py
│   │   ├── focus_tracker.py   # Focus detection tracker
│   │   └── tempMain.py        # Temporary test scripts
│   ├── preprocess/            # Frame preprocessing
│   │   ├── __init__.py
│   │   ├── processor.py       # Frame preprocessing
│   │   └── features.py        # Feature extraction
│   ├── inference/             # Focus detection inference
│   │   ├── __init__.py
│   │   └── detector.py        # Focus detection model
│   ├── ui/                    # User interface
│   │   ├── __init__.py
│   │   └── monitor.py         # Live monitoring UI
│   └── videos/                # Character reaction videos
│       ├── animegirl/         # Anime girl character videos
│       ├── cop/               # Cop character videos
│       ├── drillsergeant/     # Drill sergeant videos
│       └── shrek/             # Shrek character videos
├── frontend/                  # React web frontend
│   ├── src/                   # React source code
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── vite.config.js         # Vite configuration
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
├── main.py                    # Legacy CLI entry point
├── pyproject.toml             # Project metadata
├── requirements.txt           # Python dependencies
├── requirements-dev.txt       # Development dependencies
├── .env.example               # Environment variables template
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

### Prerequisites

- **Python 3.9+** (3.12 recommended)
- **Node.js 18+** and npm (for frontend)
- **Virtual environment** (recommended)

### Python Backend Setup

```bash
# Clone the repository
git clone https://github.com/Timber868/Lockin-Ai.git
cd Lockin-Ai

# Create and activate virtual environment (recommended)
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Windows (Git Bash/Command Prompt):
source .venv/Scripts/activate

# On Linux/Mac:
source .venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root for API keys (if needed):

```bash
# .env file
ELEVENLABS_API_KEY=your_api_key_here
LOCKIN_CAMERA_ID=0
LOCKIN_VISION_PORT=8765
```


## Usage

### Running the Vision Server (Python Backend)

The vision server processes camera input and sends focus tracking data to the frontend via WebSocket.

```bash
# Make sure virtual environment is activated
# .\.venv\Scripts\Activate.ps1  (Windows PowerShell)

# Run the vision server
python -m focusai.vision_server

# Or with custom camera/port (via environment variables)
$env:LOCKIN_CAMERA_ID=0
$env:LOCKIN_VISION_PORT=8765
python -m focusai.vision_server
```

The vision server will start on `ws://localhost:8765` by default.

## Web Frontend (React)

This repo includes a React-based web dashboard that connects to the Python vision server via WebSocket.

### Frontend Prerequisites

- **Node.js 18+** and npm installed
- Check your Node version: `node --version`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

**Note:** The frontend connects to the Python vision server running on `ws://localhost:8765` by default.

### Project Status

✅ **Current Status**: Core functionality implemented

The project includes:
- ✅ Computer vision implementation with MediaPipe face detection
- ✅ Focus tracking with eye aspect ratio (EAR) and head pose detection
- ✅ WebSocket-based vision server for real-time data streaming
- ✅ React frontend with real-time focus visualization
- ✅ Character-based reaction system with video playback
- ✅ Configuration management and logging
- ✅ Test suite framework
- ✅ Complete documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Team

Built for McHacks 2026 by the Lockin-AI team:
- Tim Roma
- Marrec Bois
- Garrett Woodson