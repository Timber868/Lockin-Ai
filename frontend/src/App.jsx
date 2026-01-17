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
  const [focusResults, setFocusResults] = useState([]);
  const [focusLevel, setFocusLevel] = useState(1);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [sessionTimeline, setSessionTimeline] = useState([]);
  const [rightPanelView, setRightPanelView] = useState("timeline");
  const [cameraError, setCameraError] = useState("");
  const [cameraReady, setCameraReady] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const sessionRef = useRef(null);
  const sessionStartRef = useRef(null);
  const distractedStartRef = useRef(null);
  const distractedTotalRef = useRef(0);
  const distractedCountRef = useRef(0);
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
    setSessionSummary(null);
    setSessionTimeline([]);
    setFocusResults([]);
    setFocusLevel(1);
    sessionStartRef.current = Date.now();
    distractedStartRef.current = null;
    distractedTotalRef.current = 0;
    distractedCountRef.current = 0;
    setLessonStarted(true);
  };

  const endLesson = () => {
    const endTime = Date.now();
    const sessionStart = sessionStartRef.current;
    if (sessionStart) {
      if (distractedStartRef.current) {
        distractedTotalRef.current += Math.round(
          (endTime - distractedStartRef.current) / 1000
        );
        distractedStartRef.current = null;
      }

      const totalSeconds = Math.max(
        1,
        Math.round((endTime - sessionStart) / 1000)
      );
      const distractedSeconds = distractedTotalRef.current;
      const focusedSeconds = Math.max(totalSeconds - distractedSeconds, 0);

      setSessionSummary({
        totalSeconds,
        distractedSeconds,
        focusedSeconds,
        alerts: distractedCountRef.current
      });
    }
    setLessonStarted(false);
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

  const evaluateFocus = (visionData) => {
    const {
      h_ratio: hRatio,
      v_ratio: vRatio,
      left_ear: leftEar,
      state,
      objects
    } = visionData || {};

    const normalizedState = String(state || "").toLowerCase();
    const normalizedObjects = (objects || []).map((item) =>
      String(item).toLowerCase()
    );

    const distractedObjects = ["phone", "cell phone", "tablet", "ipad"];
    const hasDistractor = normalizedObjects.some((item) =>
      distractedObjects.includes(item)
    );

    if (hasDistractor) {
      return { focused: false, reason: "distractor" };
    }

    if (typeof leftEar === "number" && leftEar < 0.3) {
      return { focused: false, reason: "eyes-closed" };
    }

    if (normalizedState === "at screen") {
      return { focused: true, reason: "state" };
    }

    if (
      typeof hRatio === "number" &&
      typeof vRatio === "number" &&
      hRatio >= 0.35 &&
      hRatio <= 0.65 &&
      vRatio >= 0.35 &&
      vRatio <= 0.6
    ) {
      return { focused: true, reason: "centered" };
    }

    return { focused: false, reason: "off-center" };
  };

  const pushFocusResult = (isFocused) => {
    setFocusResults((prevResults) => {
      const nextResults = [...prevResults, isFocused ? 1 : 0].slice(-20);
      const average =
        nextResults.reduce((sum, value) => sum + value, 0) /
        nextResults.length;
      setFocusLevel(average);
      setCurrentState(average >= 0.7 ? "focused" : "distracted");
      return nextResults;
    });
  };

  useEffect(() => {
    if (!lessonStarted) {
      setFocusResults([]);
      setFocusLevel(1);
      return;
    }

    const interval = setInterval(() => {
      const focusBias = Math.random();
      const hRatio = focusBias < 0.7 ? 0.45 : 0.2 + Math.random() * 0.6;
      const vRatio = focusBias < 0.7 ? 0.5 : 0.2 + Math.random() * 0.6;
      const leftEar = Math.random() > 0.95 ? 0.2 : 0.35;
      const state =
        focusBias < 0.7 ? "at screen" : ["left", "right", "down"][
          Math.floor(Math.random() * 3)
        ];
      const objects = Math.random() > 0.97 ? ["phone"] : [];

      const result = evaluateFocus({
        h_ratio: hRatio,
        v_ratio: vRatio,
        left_ear: leftEar,
        state,
        objects
      });
      pushFocusResult(result.focused);
    }, 1500);

    return () => clearInterval(interval);
  }, [lessonStarted]);

  const focusWarningActive = focusLevel < 0.7;

  useEffect(() => {
    if (!lessonStarted || !sessionStartRef.current) {
      return;
    }
    const now = Date.now();
    const elapsedSeconds = Math.round(
      (now - sessionStartRef.current) / 1000
    );
    if (focusWarningActive && !distractedStartRef.current) {
      distractedStartRef.current = now;
      distractedCountRef.current += 1;
      setSessionTimeline((prev) => [
        ...prev,
        { elapsedSeconds, state: "distracted" }
      ]);
    }
    if (!focusWarningActive && distractedStartRef.current) {
      distractedTotalRef.current += Math.round(
        (now - distractedStartRef.current) / 1000
      );
      distractedStartRef.current = null;
      setSessionTimeline((prev) => [
        ...prev,
        { elapsedSeconds, state: "focused" }
      ]);
    }
  }, [focusWarningActive, lessonStarted]);

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

  const formatDuration = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}m ${seconds}s`;
  };

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="eyebrow">LockIn AI</p>
          <h1>Real-time focus monitoring</h1>
          <p className="subtle">
            React dashboard prototype for the LockIn AI pipeline. Backend wiring
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
          {focusWarningActive && (
            <div className="session-alert">YOU'RE NOT FOCUSED</div>
          )}
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
              onLoadedMetadata={() => {
                setCameraReady(true);
                setCameraError("");
              }}
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
                  Focus level {Math.round(focusLevel * 100)}%
                </p>
              </div>
            </div>
            <button className="ghost" type="button" onClick={endLesson}>
              End session
            </button>
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
                onLoadedMetadata={() => {
                  setCameraReady(true);
                  setCameraError("");
                }}
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
                  placeholder="e.g. Shrek"
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

          <section className="card right-panel-card">
            <div className="card-header">
              <h2>
                {rightPanelView === "timeline"
                  ? "Focus timeline"
                  : "Session insights"}
              </h2>
              <div className="tab-switch">
                <button
                  className={rightPanelView === "timeline" ? "active" : ""}
                  type="button"
                  onClick={() => setRightPanelView("timeline")}
                >
                  Timeline
                </button>
                <button
                  className={rightPanelView === "insights" ? "active" : ""}
                  type="button"
                  onClick={() => setRightPanelView("insights")}
                >
                  Insights
                </button>
              </div>
            </div>
            {rightPanelView === "timeline" ? (
              <>
                <p className="subtle note">
                  {sessionTimeline.length
                    ? "Session focus shifts"
                    : "No session data yet"}
                </p>
                {sessionTimeline.length ? (
                  <div className="timeline">
                    {sessionTimeline.slice(-8).map((entry, index) => (
                      <div className="timeline-item" key={`${entry.state}-${index}`}>
                        <span className="timeline-time">
                          {formatDuration(entry.elapsedSeconds)}
                        </span>
                        <span
                          className="timeline-pill"
                          style={{ backgroundColor: statusColors[entry.state] }}
                        >
                          {entry.state}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : null}
              </>
            ) : (
              <>
                <div className="insights">
                  <div>
                    <p className="insight-value">
                      {sessionSummary
                        ? formatDuration(sessionSummary.focusedSeconds)
                        : "0m 0s"}
                    </p>
                    <p className="subtle">Focused time</p>
                  </div>
                  <div>
                    <p className="insight-value">
                      {sessionSummary
                        ? formatDuration(sessionSummary.distractedSeconds)
                        : "0m 0s"}
                    </p>
                    <p className="subtle">Distractions</p>
                  </div>
                  <div>
                    <p className="insight-value">
                      {sessionSummary ? sessionSummary.alerts : 0}
                    </p>
                    <p className="subtle">Alerts</p>
                  </div>
                </div>
                <p className="subtle note">
                  Replace these placeholders with real metrics from the
                  inference pipeline.
                </p>
              </>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

