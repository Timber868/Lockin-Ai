import { useEffect, useMemo, useRef, useState } from "react";

const statusColors = {
  focused: "var(--success)",
  distracted: "var(--warning)",
  offline: "var(--muted)"
};

const sampleTimeline = [
  { label: "09:40", state: "focused" },
  { label: "09:45", state: "focused" },
  { label: "09:50", state: "distracted" },
  { label: "09:55", state: "focused" },
  { label: "10:00", state: "focused" }
];

export default function App() {
  const [lessonMinutes, setLessonMinutes] = useState("45");
  const [workMode, setWorkMode] = useState("laptop");
  const [accountabilityCharacter, setAccountabilityCharacter] = useState("");
  const [lessonStarted, setLessonStarted] = useState(false);
  const [trackingEnabled, setTrackingEnabled] = useState(true);
  const [confidence, setConfidence] = useState(0.82);
  const [currentState, setCurrentState] = useState("focused");
  const [remainingSeconds, setRemainingSeconds] = useState(0);
  const [cameraError, setCameraError] = useState("");
  const [cameraReady, setCameraReady] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const sessionRef = useRef(null);
  const [cameraPosition, setCameraPosition] = useState({ x: 24, y: 24 });
  const dragState = useRef(null);

  const statusText = useMemo(() => {
    if (!trackingEnabled) {
      return "Offline";
    }
    return currentState === "focused" ? "Focused" : "Distracted";
  }, [trackingEnabled, currentState]);

  const statusColor = trackingEnabled
    ? statusColors[currentState]
    : statusColors.offline;

  const toggleTracking = () => {
    setTrackingEnabled((prev) => !prev);
  };

  const simulateState = () => {
    setCurrentState((prev) => (prev === "focused" ? "distracted" : "focused"));
    setConfidence((prev) => (prev > 0.6 ? 0.48 : 0.86));
  };

  const startLesson = (event) => {
    event.preventDefault();
    if (!lessonMinutes.trim()) {
      return;
    }
    const minutes = Number(lessonMinutes);
    if (!Number.isFinite(minutes) || minutes <= 0) {
      return;
    }
    setRemainingSeconds(Math.round(minutes * 60));
    setLessonStarted(true);
  };

  useEffect(() => {
    const handleMove = (event) => {
      if (!dragState.current || !sessionRef.current) {
        return;
      }
      const { offsetX, offsetY } = dragState.current;
      const bounds = sessionRef.current.getBoundingClientRect();
      const nextX = Math.min(
        Math.max(event.clientX - bounds.left - offsetX, 16),
        bounds.width - 200
      );
      const nextY = Math.min(
        Math.max(event.clientY - bounds.top - offsetY, 16),
        bounds.height - 140
      );
      setCameraPosition({ x: nextX, y: nextY });
    };

    const stopDrag = () => {
      dragState.current = null;
    };

    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", stopDrag);

    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", stopDrag);
    };
  }, []);

  useEffect(() => {
    let stream;
    const enableCamera = async () => {
      if (!trackingEnabled) {
        setCameraReady(false);
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
        return;
      }
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraError("");
          await videoRef.current.play();
        }
      } catch (error) {
        setCameraError("Camera access was denied or unavailable.");
        setCameraReady(false);
      }
    };

    enableCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
      streamRef.current = null;
    };
  }, [trackingEnabled]);

  useEffect(() => {
    if (!streamRef.current || !videoRef.current) {
      return;
    }
    setCameraReady(false);
    videoRef.current.srcObject = streamRef.current;
    videoRef.current
      .play()
      .then(() => setCameraReady(true))
      .catch(() => {
        setCameraError("Camera preview failed to start.");
        setCameraReady(false);
      });
  }, [lessonStarted]);

  useEffect(() => {
    if (!lessonStarted || remainingSeconds <= 0) {
      return;
    }
    const timer = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [lessonStarted, remainingSeconds]);

  const formattedTime = useMemo(() => {
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  }, [remainingSeconds]);

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">FocusAI Web</p>
          <h1>Real-time focus monitoring</h1>
          <p className="subtle">
            React dashboard prototype for the FocusAI pipeline. Backend wiring
            can be added later via WebSocket or REST.
          </p>
        </div>
        {lessonStarted && (
          <div className="header-actions">
            <button className="ghost" onClick={simulateState} type="button">
              Simulate state
            </button>
            <button className="primary" onClick={toggleTracking} type="button">
              {trackingEnabled ? "Stop tracking" : "Start tracking"}
            </button>
          </div>
        )}
      </header>

      {lessonStarted ? (
        <main className="session-view" ref={sessionRef}>
          <div className="session-background">
            <p className="session-message">Session running</p>
            <p className="subtle">
              Your AI character will appear here later. For now, this is a
              placeholder background.
            </p>
          </div>
          <div
            className="floating-camera"
            onMouseDown={(event) => {
              const bounds = event.currentTarget.getBoundingClientRect();
              dragState.current = {
                offsetX: event.clientX - bounds.left,
                offsetY: event.clientY - bounds.top
              };
            }}
            style={{
              transform: `translate(${cameraPosition.x}px, ${cameraPosition.y}px)`
            }}
          >
            <div className="camera-frame">
              <video
                ref={videoRef}
                className="camera-video"
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => setCameraReady(true)}
              />
              {(cameraError || !cameraReady) && (
                <div className="camera-overlay">
                  <div className="camera-ring" />
                  <div>
                    <p className="camera-title">Live stream</p>
                    <p className="subtle">
                      {cameraError
                        ? cameraError
                        : "Allow camera access to see the live feed."}
                    </p>
                  </div>
                </div>
              )}
            </div>
            <p className="camera-hint">Drag to move</p>
          </div>
          <div className="session-footer">
            <div>
              <p className="footer-label">Time remaining</p>
              <p className="footer-value">{formattedTime}</p>
            </div>
            <div className="footer-status">
              <span
                className="status-dot"
                style={{ backgroundColor: statusColor }}
              />
              <div>
                <p className="footer-label">{statusText}</p>
                <p className="footer-subtle">
                  Confidence {Math.round(confidence * 100)}%
                </p>
              </div>
            </div>
          </div>
        </main>
      ) : (
        <main className="grid">
          <section className="card camera-card">
            <div className="card-header">
              <h2>Camera preview</h2>
              <span className="chip">Device 0</span>
            </div>
            <div className="camera-placeholder">
              <video
                ref={videoRef}
                className="camera-video"
                autoPlay
                playsInline
                muted
                onLoadedMetadata={() => setCameraReady(true)}
              />
              {(cameraError || !cameraReady) && (
                <div className="camera-overlay">
                  <div className="camera-ring" />
                  <div>
                    <p className="camera-title">Live stream</p>
                    <p className="subtle">
                      {cameraError
                        ? cameraError
                        : "Allow camera access to see the live feed."}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </section>

          <section className="card status-card">
            <div className="card-header">
              <h2>Current status</h2>
              <span className="chip">Live</span>
            </div>
            <div className="status">
              <span
                className="status-dot"
                style={{ backgroundColor: statusColor }}
              />
              <div>
                <p className="status-label">{statusText}</p>
                <p className="subtle">
                  Confidence {Math.round(confidence * 100)}%
                </p>
              </div>
            </div>
            <div className="meter">
              <div
                className="meter-fill"
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
          </section>

          <section className="card lesson-card">
            <div className="card-header">
              <h2>Study session</h2>
            </div>
            <p className="subtle">
              Set how long you want to study for, then start the lesson.
            </p>
            <form className="intro-form" onSubmit={startLesson}>
              <label className="field">
                <span>Study length (minutes)</span>
                <input
                  type="number"
                  min="5"
                  max="240"
                  step="5"
                  value={lessonMinutes}
                  onChange={(event) => setLessonMinutes(event.target.value)}
                />
              </label>
              <label className="field">
                <span>Work setup</span>
                <select
                  value={workMode}
                  onChange={(event) => setWorkMode(event.target.value)}
                >
                  <option value="paper-ipad">Paper/iPad notes</option>
                  <option value="laptop">Working on laptop</option>
                  <option value="both">Both</option>
                </select>
              </label>
              <label className="field">
                <span>Accountability character</span>
                <input
                  type="text"
                  placeholder="e.g. Professor Oak"
                  value={accountabilityCharacter}
                  onChange={(event) =>
                    setAccountabilityCharacter(event.target.value)
                  }
                />
                <span className="helper">
                  They will be responsible for keeping you in check while you work.
                </span>
              </label>
              <button className="primary" type="submit">
                Start session
              </button>
            </form>
          </section>

          <section className="card timeline-card">
            <div className="card-header">
              <h2>Focus timeline</h2>
              <span className="chip">Last 25 minutes</span>
            </div>
            <div className="timeline">
              {sampleTimeline.map((entry) => (
                <div className="timeline-item" key={entry.label}>
                  <span className="timeline-time">{entry.label}</span>
                  <span
                    className="timeline-pill"
                    style={{ backgroundColor: statusColors[entry.state] }}
                  >
                    {entry.state}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="card insights-card">
            <div className="card-header">
              <h2>Session insights</h2>
            </div>
            <div className="insights">
              <div>
                <p className="insight-value">42m</p>
                <p className="subtle">Focused time</p>
              </div>
              <div>
                <p className="insight-value">6m</p>
                <p className="subtle">Distractions</p>
              </div>
              <div>
                <p className="insight-value">12</p>
                <p className="subtle">Alerts</p>
              </div>
            </div>
            <p className="subtle note">
              Replace these placeholders with real metrics from the inference
              pipeline.
            </p>
          </section>
        </main>
      )}
    </div>
  );
}
