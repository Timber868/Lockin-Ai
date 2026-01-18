import cv2
import mediapipe as mp
import time
import os
import numpy as np
import sounddevice as sd


def _open_camera(camera_index: int) -> cv2.VideoCapture:
    """
    Try common OpenCV backends for more reliable camera access on Windows.
    """
    backends = []
    if os.name == "nt":
        backends.extend([cv2.CAP_DSHOW, cv2.CAP_MSMF])
    backends.append(cv2.CAP_ANY)

    for backend in backends:
        cap = cv2.VideoCapture(camera_index, backend)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return cap
        cap.release()
    return cv2.VideoCapture(camera_index)

class FocusTracker:
    def __init__(self, camera_index=1, model_name='yolov8n.pt'):
        # --- INIT ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        face_model_path = os.path.join(self.script_dir, 'face_landmarker.task')

        # 1. MediaPipe Setup
        self.options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=face_model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO)
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(self.options)

        # 2. YOLO Setup (lazy-load to avoid long startup stalls)
        self.yolo_available = True
        self.yolo_model = None
        self.yolo_model_name = model_name
        self.yolo_loaded = False
        self.distraction_classes = [67, 73] # Cell phone, Book

        # 3. Audio Setup (Non-blocking)
        self.current_volume = 0.0
        self.audio_stream = None
        try:
            # Start a background stream that updates self.current_volume automatically
            self.audio_stream = sd.InputStream(callback=self._audio_callback)
            self.audio_stream.start()
            print("Microphone listening...")
        except Exception as e:
            print(f"Warning: Mic not found or error: {e}")

        # 4. Camera Setup
        self.cap = _open_camera(camera_index)
        if not self.cap or not self.cap.isOpened():
            raise RuntimeError(f"Unable to open camera {camera_index}")
        print(f"Camera ready (index {camera_index})")
        
    def _audio_callback(self, indata, frames, time, status):
        """Calculates volume (RMS) from the microphone input stream."""
        if status:
            print(status)
        # Calculate Root Mean Square (volume)
        self.current_volume = np.linalg.norm(indata) * 10

    def get_frame_analysis(self, 
                           # Feature Toggles
                           enable_face_orientation=True,
                           enable_eye_detection=True,
                           enable_object_detection=True,
                           enable_audio_detection=True,
                           # Threshold Overrides
                           h_thresholds=(0.20, 0.80),
                           v_thresholds=(0.39, 0.70),
                           ear_threshold=0.25,
                           conf_threshold=0.5,
                           audio_threshold=1.5): # Adjust this based on room noise
        
        """
        Returns: (state_string, metrics_dict, annotated_frame)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None

        state = "Focused"
        metrics = {"volume": round(self.current_volume, 4)}
        
        # --- 1. FACE & EYE TRACKING ---
        if enable_face_orientation or enable_eye_detection:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            face_result = self.landmarker.detect_for_video(mp_image, int(time.time() * 1000))
            
            if face_result.face_landmarks:
                face_state, face_metrics = self._process_face(
                    face_result.face_landmarks[0], 
                    enable_face_orientation,
                    enable_eye_detection,
                    h_thresholds,
                    v_thresholds,
                    ear_threshold
                )
                if face_state != "Focused":
                    state = face_state
                metrics.update(face_metrics)
            else:
                state = "No Face Detected"

        # --- 2. AUDIO DETECTION  ---
        if enable_audio_detection:
            if self.current_volume > audio_threshold:
                if "DETECTED" not in state: 
                    state = "TALKING"
                
        # --- 3. OBJECT DETECTION (YOLO) ---
        if enable_object_detection and self.yolo_available:
            if not self.yolo_loaded:
                try:
                    from ultralytics import YOLO
                    self.yolo_model = YOLO(self.yolo_model_name)
                    self.yolo_loaded = True
                    print("YOLO model loaded.")
                except Exception as exc:
                    self.yolo_available = False
                    print(f"Warning: YOLO unavailable ({exc}). Object detection disabled.")
            if self.yolo_model is not None:
                yolo_results = self.yolo_model(frame, stream=True, verbose=False)
            for r in yolo_results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    if cls_id in self.distraction_classes and conf > conf_threshold:
                        if cls_id == 67: state = "PHONE DETECTED"
                        elif cls_id == 73: state = "BOOK DETECTED"
                        else: state = "DISTRACTION DETECTED"
                        
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        label = f"{state.split(' ')[0]} ({conf:.2f})"

        return state, metrics, frame

    def _process_face(self, face, check_orientation, check_eyes, h_thresh, v_thresh, ear_thresh):
        """Internal helper for Face/Eye logic"""
        state = "Focused"
        metrics = {}

        if check_orientation:
            total_width = abs(face[454].x - face[234].x)
            h_ratio = abs(face[4].x - face[234].x) / total_width if total_width != 0 else 0.5
            
            total_height = abs(face[152].y - face[10].y)
            v_ratio = abs(face[4].y - face[10].y) / total_height if total_height != 0 else 0.5

            metrics["h_ratio"] = round(h_ratio, 3)
            metrics["v_ratio"] = round(v_ratio, 3)

            if h_ratio < h_thresh[0]: state = "Looking Left"
            elif h_ratio > h_thresh[1]: state = "Looking Right"
            elif v_ratio < v_thresh[0]: state = "Looking Up"
            elif v_ratio > v_thresh[1]: state = "Looking Down"

        if check_eyes:
            v1 = abs(face[160].y - face[144].y)
            v2 = abs(face[158].y - face[153].y)
            h = abs(face[33].x - face[133].x)
            left_ear = (v1 + v2) / (2.0 * h) if h != 0 else 0.0
            
            metrics["ear"] = round(left_ear, 3)
            if left_ear < ear_thresh:
                state = "Eyes Closed / Looking Down"

        return state, metrics

    def cleanup(self):
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
        self.cap.release()
        cv2.destroyAllWindows()