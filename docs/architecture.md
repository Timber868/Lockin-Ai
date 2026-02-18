# LockIn AI – Current Architecture

This document describes how the LockIn AI system works today: vision backend + React frontend.

## Overview

- **Backend**: Python vision server (`focusai.vision_server`) opens the camera once, runs focus detection (MediaPipe face/eyes + optional YOLO objects + audio), and streams JSON over WebSocket.
- **Frontend**: React app connects to the WebSocket, shows the backend’s camera preview and focus state, and triggers character reactions when the user is distracted.

## High-Level Flow

```
Camera (OpenCV) → FocusTracker (MediaPipe + YOLO + audio) → vision_server (WebSocket)
                                                                  ↓
React frontend ←──────────────────────────────────────────────────┘
  (preview, state, alerts, character videos)
```

## Backend

### Entry point

- Run: `python -m focusai.vision_server`
- Listens on `ws://localhost:8765` (or `LOCKIN_VISION_PORT`).

### Single shared pipeline

- **One** camera and **one** `FocusTracker` for all clients.
- When the first WebSocket client connects, the server starts a capture thread that:
  - Creates `FocusTracker(camera_index)` (opens camera, MediaPipe, optional YOLO, microphone).
  - In a loop: `get_frame_analysis()` → build JSON payload (state, metrics, optional `preview_jpeg`) → put on a queue.
- A broadcaster task reads from that queue and sends each payload to every connected client.
- When the last client disconnects, the capture thread is stopped and the tracker is cleaned up.

### FocusTracker (`focusai/capture/focus_tracker.py`)

- **Input**: Live frames from OpenCV `VideoCapture`.
- **Output**: `(state_string, metrics_dict, annotated_frame)` per frame.
- **Logic**:
  - **Face / eyes**: MediaPipe Face Landmarker (face mesh, eye aspect ratio, head pose).
  - **Objects** (optional): YOLO (e.g. phone, book) for distraction.
  - **Audio** (optional): `sounddevice` for “talking” detection.
- **States** (examples): `"Focused"`, `"No Face Detected"`, `"Looking Left/Right"`, `"Eyes Closed / Looking Down"`, `"PHONE DETECTED"`, `"BOOK DETECTED"`, `"TALKING"`.

### WebSocket payload (summary)

- `state`, `face_detected`, `h_ratio`, `v_ratio`, `left_ear`, `volume`, `objects`, `camera_id`, `timestamp_ms`, `frame_index`.
- `preview_jpeg`: base64 JPEG of the current frame (included on first payload and then at `LOCKIN_PREVIEW_FPS`).
- Clients can send `{ "type": "config", ... }` to update thresholds (e.g. `h_min`, `ear_threshold`, `include_talking`).

## Frontend

- Connects to `ws://localhost:8765` when tracking is enabled.
- Sends initial config and receives a stream of payloads.
- Renders:
  - Backend preview (when `previewEnabled` is false) or browser camera (when true; note: backend needs the camera for CV, so typically `previewEnabled` is false).
  - Focus state and metrics.
- Uses `evaluateFocus(payload)` to decide focused vs distracted and pushes results into a short history; `focusLevel` is a rolling average used for alerts.
- When the user is distracted long enough, it pushes character alert videos (e.g. phone, talking, gone) from `focusai/videos/`.

## Configuration (backend)

- **Env**: `LOCKIN_CAMERA_ID` (default `0`), `LOCKIN_VISION_PORT` (default `8765`), `LOCKIN_PREVIEW_FPS` (default `5`).
- **Runtime**: WebSocket `config` messages update thresholds and toggles (e.g. `include_talking`, `include_objects`) held in the shared config dict used by the capture thread.

## Project layout (relevant parts)

```
focusai/
├── vision_server.py    # WebSocket server, shared pipeline, broadcaster
└── capture/
    └── focus_tracker.py # Camera + MediaPipe + YOLO + audio → state/metrics/frame
```

Frontend lives in `frontend/` (React + Vite). Character assets live under `focusai/videos/` (e.g. drillsergeant, cop, shrek).
