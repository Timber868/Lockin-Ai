import cv2
import mediapipe as mp
import time
import os
from ultralytics import YOLO

class FocusTracker:
    def __init__(self, camera_index=1, model_name='yolov8n.pt'):
        # --- INIT (Runs once) ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        face_model_path = os.path.join(self.script_dir, 'face_landmarker.task')

        # MediaPipe Setup
        self.options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=face_model_path),
            running_mode=mp.tasks.vision.RunningMode.VIDEO)
        self.landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(self.options)

        # YOLO Setup
        self.yolo_model = YOLO(model_name)
        self.distraction_classes = [67, 73] # Cell phone, Book

        # Camera Setup
        self.cap = cv2.VideoCapture(camera_index)
        
    def get_frame_analysis(self, 
                           # Feature Toggles
                           enable_face_orientation=True,
                           enable_eye_detection=True,
                           enable_object_detection=True,
                           # Threshold Overrides (Defaults)
                           h_thresholds=(0.20, 0.80), # (Left Limit, Right Limit)
                           v_thresholds=(0.39, 0.70), # (Up Limit, Down Limit)
                           ear_threshold=0.25,
                           conf_threshold=0.5):
        
        """
        Processes a frame with optional configuration arguments.
        Returns: (state_string, metrics_dict, annotated_frame)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None

        state = "Focused"
        metrics = {}
        
        # --- 1. FACE & EYE TRACKING (MediaPipe) ---
        # Only run MediaPipe if we need Face OR Eye data
        if enable_face_orientation or enable_eye_detection:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            face_result = self.landmarker.detect_for_video(mp_image, int(time.time() * 1000))
            
            if face_result.face_landmarks:
                # Pass the feature flags and thresholds to the helper function
                face_state, face_metrics = self._process_face(
                    face_result.face_landmarks[0], 
                    enable_face_orientation,
                    enable_eye_detection,
                    h_thresholds,
                    v_thresholds,
                    ear_threshold
                )
                
                # Update main state and metrics
                if face_state != "Focused":
                    state = face_state
                metrics.update(face_metrics)
            else:
                state = "No Face Detected"

# --- 2. OBJECT DETECTION (YOLO) ---
        if enable_object_detection:
            yolo_results = self.yolo_model(frame, stream=True, verbose=False)
            for r in yolo_results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    if cls_id in self.distraction_classes and conf > conf_threshold:
                        # Specific Logic for Distraction Type
                        if cls_id == 67:
                            state = "PHONE DETECTED"
                        elif cls_id == 73:
                            state = "BOOK DETECTED"
                        else:
                            state = "DISTRACTION DETECTED"
                        
                        # Visual annotation
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        # Red box for distraction
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        # Display the specific label on screen
                        label = f"{state.split(' ')[0]} ({conf:.2f})"
                        cv2.putText(frame, label, (x1, y1 - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return state, metrics, frame

    def _process_face(self, face, 
                      check_orientation, check_eyes, 
                      h_thresh, v_thresh, ear_thresh):
        """Internal helper to calculate ratios based on flags"""
        state = "Focused"
        metrics = {}

        # --- ORIENTATION LOGIC ---
        if check_orientation:
            # Horizontal (Yaw)
            total_width = abs(face[454].x - face[234].x)
            h_ratio = abs(face[4].x - face[234].x) / total_width if total_width != 0 else 0.5
            
            # Vertical (Pitch)
            total_height = abs(face[152].y - face[10].y)
            v_ratio = abs(face[4].y - face[10].y) / total_height if total_height != 0 else 0.5

            metrics["h_ratio"] = round(h_ratio, 3)
            metrics["v_ratio"] = round(v_ratio, 3)

            # Check Thresholds
            if h_ratio < h_thresh[0]: state = "Looking Left"
            elif h_ratio > h_thresh[1]: state = "Looking Right"
            elif v_ratio < v_thresh[0]: state = "Looking Up"
            elif v_ratio > v_thresh[1]: state = "Looking Down"

        # --- EYE LOGIC (EAR) ---
        if check_eyes:
            # EAR (Left Eye)
            v1 = abs(face[160].y - face[144].y)
            v2 = abs(face[158].y - face[153].y)
            h = abs(face[33].x - face[133].x)
            left_ear = (v1 + v2) / (2.0 * h) if h != 0 else 0.0
            
            metrics["ear"] = round(left_ear, 3)

            # Check Threshold
            if left_ear < ear_thresh:
                state = "Eyes Closed / Looking Down"

        return state, metrics

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()