import cv2
import mediapipe as mp
import time
import os

def get_focus_data(face_landmarks):
    """
    Analyzes face landmarks and returns (status, metrics_dict)
    """
    face = face_landmarks
    
    # --- 1. COORDINATE EXTRACTION ---
    # Head Pose Points
    nose = face[4]
    left_edge = face[234]
    right_edge = face[454]
    top_edge = face[10]
    bottom_edge = face[152]
    
    # Eye Points (for EAR)
    # Left Eye: Horizontal [33, 133], Vertical [160, 144] & [158, 153]
    l_ear_points = [33, 160, 158, 133, 153, 144]
    
    # --- 2. METRIC CALCULATIONS ---
    # Horizontal Ratio (Yaw)
    total_width = abs(right_edge.x - left_edge.x)
    h_ratio = abs(nose.x - left_edge.x) / total_width if total_width != 0 else 0.5

    # Vertical Ratio (Pitch)
    total_height = abs(bottom_edge.y - top_edge.y)
    v_ratio = abs(nose.y - top_edge.y) / total_height if total_height != 0 else 0.5
    
    # Eye Aspect Ratio (EAR)
    v1 = abs(face[l_ear_points[1]].y - face[l_ear_points[5]].y)
    v2 = abs(face[l_ear_points[2]].y - face[l_ear_points[4]].y)
    h = abs(face[l_ear_points[0]].x - face[l_ear_points[3]].x)
    left_ear = (v1 + v2) / (2.0 * h) if h != 0 else 0.0

    # --- 3. STATE LOGIC ---
    EAR_THRESHOLD = 0.3 # Your tuned value
    
    state = "Focused"
    if left_ear < EAR_THRESHOLD:
        state = "Eyes Closed / Looking Deep Down"
    elif h_ratio < 0.35:
        state = "Looking Left"
    elif h_ratio > 0.65:
        state = "Looking Right"
    elif v_ratio < 0.35:
        state = "Looking Up"
    elif v_ratio > 0.60:
        state = "Looking Down"

    # --- 4. RETURN DATA ---
    metrics = {
        "h_ratio": round(h_ratio, 3),
        "v_ratio": round(v_ratio, 3),
        "left_ear": round(left_ear, 3)
    }
    
    return state, metrics

# Setup Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(SCRIPT_DIR, 'face_landmarker.task')

# MediaPipe Setup
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO)

cap = cv2.VideoCapture(1) # Change to 0 if on Windows later

with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = landmarker.detect_for_video(mp_image, int(time.time() * 1000))

        status = "Looking at Screen"

        if result.face_landmarks:
            state, stats = get_focus_data(result.face_landmarks[0])
            print(f"Current State: {state} | Stats: {stats}")
            
        cv2.imshow('Focus AI Debugger', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()

def get_focus_data(face_landmarks):
    """
    Analyzes face landmarks and returns (status, metrics_dict)
    """
    face = face_landmarks
    
    # --- 1. COORDINATE EXTRACTION ---
    # Head Pose Points
    nose = face[4]
    left_edge = face[234]
    right_edge = face[454]
    top_edge = face[10]
    bottom_edge = face[152]
    
    # Eye Points (for EAR)
    # Left Eye: Horizontal [33, 133], Vertical [160, 144] & [158, 153]
    l_ear_points = [33, 160, 158, 133, 153, 144]
    
    # --- 2. METRIC CALCULATIONS ---
    # Horizontal Ratio (Yaw)
    total_width = abs(right_edge.x - left_edge.x)
    h_ratio = abs(nose.x - left_edge.x) / total_width if total_width != 0 else 0.5

    # Vertical Ratio (Pitch)
    total_height = abs(bottom_edge.y - top_edge.y)
    v_ratio = abs(nose.y - top_edge.y) / total_height if total_height != 0 else 0.5
    
    # Eye Aspect Ratio (EAR)
    v1 = abs(face[l_ear_points[1]].y - face[l_ear_points[5]].y)
    v2 = abs(face[l_ear_points[2]].y - face[l_ear_points[4]].y)
    h = abs(face[l_ear_points[0]].x - face[l_ear_points[3]].x)
    left_ear = (v1 + v2) / (2.0 * h) if h != 0 else 0.0

    # --- 3. STATE LOGIC ---
    EAR_THRESHOLD = 0.3 # Your tuned value
    
    state = "Focused"
    if left_ear < EAR_THRESHOLD:
        state = "Eyes Closed / Looking Deep Down"
    elif h_ratio < 0.35:
        state = "Looking Left"
    elif h_ratio > 0.65:
        state = "Looking Right"
    elif v_ratio < 0.35:
        state = "Looking Up"
    elif v_ratio > 0.60:
        state = "Looking Down"

    # --- 4. RETURN DATA ---
    metrics = {
        "h_ratio": round(h_ratio, 3),
        "v_ratio": round(v_ratio, 3),
        "left_ear": round(left_ear, 3)
    }
    
    return state, metrics

# --- MAIN LOOP SNIPPET ---
# Inside your while loop, where you get 'result.face_landmarks':
# if result.face_landmarks:
#     state, stats = get_focus_data(result.face_landmarks[0])
#     print(f"Current State: {state} | Stats: {stats}")