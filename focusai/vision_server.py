import asyncio
import base64
import json
import logging
import os
import threading
import time

import cv2
import websockets

from focusai.capture.focus_tracker import FocusTracker

LOG = logging.getLogger("lockin.vision")


def _safe_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _start_stream(queue, loop, stop_event, camera_id):
    tracker = None
    try:
        try:
            tracker = FocusTracker(camera_index=camera_id)
        except Exception as exc:
            LOG.error("Vision camera init failed camera_id=%s error=%s", camera_id, exc)
            loop.call_soon_threadsafe(
                queue.put_nowait,
                {
                    "state": "camera-error",
                    "error": "camera-init-failed",
                    "camera_id": camera_id,
                    "timestamp_ms": int(time.time() * 1000),
                    "frame_index": 0,
                    "face_detected": False,
                    "objects": []
                }
            )
            return
        LOG.info("Vision capture started camera_id=%s", camera_id)
        frame_index = 0
        preview_fps = float(os.getenv("LOCKIN_PREVIEW_FPS", "5"))
        preview_interval = 1.0 / max(preview_fps, 0.1) if preview_fps > 0 else None
        last_preview_time = 0.0
        first_payload_logged = False
        while not stop_event.is_set():
            state, metrics, _frame = tracker.get_frame_analysis()
            if state is None and metrics is None:
                LOG.error("Vision camera read failed camera_id=%s", camera_id)
                loop.call_soon_threadsafe(
                    queue.put_nowait,
                    {
                        "state": "camera-error",
                        "error": "camera-read-failed",
                        "camera_id": camera_id,
                        "timestamp_ms": int(time.time() * 1000),
                        "frame_index": frame_index,
                        "face_detected": False,
                        "objects": []
                    }
                )
                break

            face_detected = state != "No Face Detected"
            objects = []
            normalized_state = (state or "").upper()
            if "PHONE" in normalized_state:
                objects.append("phone")
            if "BOOK" in normalized_state:
                objects.append("book")
            if "DISTRACTION" in normalized_state and not objects:
                objects.append("distractor")

            payload = {
                "state": state,
                "h_ratio": _safe_float(metrics.get("h_ratio")),
                "v_ratio": _safe_float(metrics.get("v_ratio")),
                "left_ear": _safe_float(metrics.get("ear")),
                "volume": _safe_float(metrics.get("volume")),
                "objects": objects,
                "camera_id": camera_id,
                "timestamp_ms": int(time.time() * 1000),
                "frame_index": frame_index,
                "face_detected": face_detected
            }
            if preview_interval and _frame is not None:
                now = time.time()
                if now - last_preview_time >= preview_interval:
                    last_preview_time = now
                    ok, buffer = cv2.imencode(".jpg", _frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                    if ok:
                        payload["preview_jpeg"] = base64.b64encode(buffer).decode("ascii")
            if not first_payload_logged:
                LOG.info(
                    "Vision first payload state=%s face=%s camera_id=%s",
                    state,
                    face_detected,
                    camera_id
                )
                first_payload_logged = True
            loop.call_soon_threadsafe(queue.put_nowait, payload)
            frame_index += 1
    finally:
        if tracker is not None:
            tracker.cleanup()
        loop.call_soon_threadsafe(queue.put_nowait, None)


async def handler(websocket):
    loop = asyncio.get_running_loop()
    queue = asyncio.Queue()
    stop_event = threading.Event()

    camera_id = int(os.getenv("LOCKIN_CAMERA_ID", "0"))
    log_every = int(os.getenv("LOCKIN_VISION_LOG_EVERY", "30"))
    thread = threading.Thread(
        target=_start_stream, args=(queue, loop, stop_event, camera_id), daemon=True
    )
    thread.start()
    client = getattr(websocket, "remote_address", None)
    LOG.info("Vision client connected camera_id=%s client=%s", camera_id, client)

    sent_count = 0
    last_log_time = time.time()
    try:
        while True:
            payload = await queue.get()
            if payload is None:
                break
            await websocket.send(json.dumps(payload))
            sent_count += 1
            if log_every > 0 and sent_count % log_every == 0:
                now = time.time()
                elapsed = max(now - last_log_time, 0.001)
                rate = round(log_every / elapsed, 2)
                last_log_time = now
                LOG.info(
                    "Vision payload state=%s face=%s rate=%s/s camera_id=%s",
                    payload.get("state"),
                    payload.get("face_detected"),
                    rate,
                    payload.get("camera_id")
                )
    except websockets.ConnectionClosed:
        LOG.info("Vision client disconnected client=%s", client)
    finally:
        stop_event.set()


async def main():
    port = int(os.getenv("LOCKIN_VISION_PORT", "8765"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    async with websockets.serve(handler, "0.0.0.0", port):
        LOG.info("Vision server listening on ws://localhost:%s", port)
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOG.info("Vision server stopped.")
