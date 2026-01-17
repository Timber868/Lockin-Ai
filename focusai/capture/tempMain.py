from focus_tracker import FocusTracker
import cv2

tracker = FocusTracker(camera_index=1)

print("Starting... Press 'q' to quit.")

while True:
    # EXAMPLE 1: Standard Run (Defaults)
    state, metrics, frame = tracker.get_frame_analysis()

    # EXAMPLE 2: "Strict Mode" (Tighter thresholds)
    # state, metrics, frame = tracker.get_frame_analysis(
    #     ear_threshold=0.40,          # Eyes must be wider open
    #     h_thresholds=(0.40, 0.60)    # Must look DEAD center
    # )

    # EXAMPLE 3: "Power Saver" (Turn off YOLO object detection)
    #state, metrics, frame = tracker.get_frame_analysis(
    #     enable_object_detection=False,
    #     enable_face_orientation=True,
    #     ear_threshold=0.3
    # )

    if frame is not None:
        print(f"ALERT: {state} | Metrics: {metrics}")
        cv2.putText(frame, f"State: {state}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        cv2.imshow("Hackathon App", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

tracker.cleanup()