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
  const [visionStatus, setVisionStatus] = useState("idle");
  const [visionState, setVisionState] = useState("");
  const [visionFrame, setVisionFrame] = useState("");
  const [visionVolume, setVisionVolume] = useState(null);
  const [backendConfig, setBackendConfig] = useState(null);
  const [lastConfigSentAt, setLastConfigSentAt] = useState(null);
  const [distractorReason, setDistractorReason] = useState("");
  const lastPayloadRef = useRef(null);
  const recentStatesRef = useRef([]);
  const socketRef = useRef(null);
  const alertVideoRef = useRef(null);
  const alertTimeoutRef = useRef(null);
  const alertQueuedRef = useRef(false);
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
  const [visionConfig, setVisionConfig] = useState({
    hMin: 0.35,
    hMax: 0.65,
    vMin: 0.35,
    vMax: 0.6,
    earThreshold: 0.3,
    audioThreshold: 1.5,
    includeTalking: true,
    includeObjects: true
  });
  const [characterChoice, setCharacterChoice] = useState("cop");
  const [alertQueue, setAlertQueue] = useState([]);
  const [activeAlert, setActiveAlert] = useState("");

  const statusText = useMemo(() => {
    if (!trackingEnabled) {
      return "Offline";
    }
    return currentState === "focused" ? "Focused" : "Distracted";
  }, [trackingEnabled, currentState]);

  const toggleTracking = () => {
    setTrackingEnabled((prev) => !prev);
  };

  const sendVisionConfig = (config) => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }
    const payload = {
      type: "config",
      h_min: config.hMin,
      h_max: config.hMax,
      v_min: config.vMin,
      v_max: config.vMax,
      ear_threshold: config.earThreshold,
      audio_threshold: config.audioThreshold,
      include_talking: config.includeTalking,
      include_objects: config.includeObjects
    };
    socket.send(JSON.stringify(payload));
    setLastConfigSentAt(Date.now());
    console.log("[LockIn AI] Sent vision config", payload);
  };

  const normalizeState = (value) =>
    String(value || "").trim().toLowerCase();
  const isFocusedState = (value) =>
    value === "focused" || value === "at screen";
  const computeMostCommonDistractor = (states, includeTalking) => {
    const counts = {};
    const labels = {};
    states.forEach((state) => {
      const normalized = normalizeState(state);
      if (!normalized || isFocusedState(normalized)) {
        return;
      }
      if (!includeTalking && normalized.includes("talking")) {
        return;
      }
      counts[normalized] = (counts[normalized] || 0) + 1;
      if (!labels[normalized]) {
        labels[normalized] = String(state);
      }
    });

    let bestKey = "";
    let bestCount = 0;
    Object.entries(counts).forEach(([key, count]) => {
      if (count > bestCount) {
        bestKey = key;
        bestCount = count;
      }
    });

    return bestKey ? labels[bestKey] : "";
  };

  const focusPercent = Math.round(focusLevel * 100);
  const focusMeterColor =
    focusLevel >= 0.7
      ? "var(--success)"
      : focusLevel >= 0.4
      ? "var(--warning)"
      : "#ef4444";
  const statusColor = trackingEnabled ? focusMeterColor : statusColors.offline;
  const effectiveIncludeTalking =
    backendConfig?.include_talking ?? visionConfig.includeTalking;

  const characterAssets = {
    cop: {
      label: "Cop",
      filler: "/videos/cop/cop-filler.mp4",
      side: "/videos/cop/Cop-side.mp4",
      up: "/videos/cop/Cop-up.mp4",
      phone: "/videos/cop/Cop-phone.mp4",
      talking: "/videos/cop/Cop-talking.mp4"
    },
    animegirl: {
      label: "Anime Girl",
      filler: "/videos/animegirl/animegirl-filler.mp4",
      side: "/videos/animegirl/animegirl-side.mp4",
      up: "/videos/animegirl/animegirl-up.mp4",
      phone: "/videos/animegirl/animegirl-phone.mp4",
      talking: "/videos/animegirl/animegirl-talking.mp4"
    }
  };

  const normalizedStateLabel = (value) => normalizeState(value);
  const alertKeyForState = (value) => {
    const normalized = normalizedStateLabel(value);
    if (!normalized) {
      return "";
    }
    if (normalized.includes("left") || normalized.includes("right")) {
      return "side";
    }
    if (normalized.includes("up")) {
      return "up";
    }
    if (
      normalized.includes("phone") ||
      normalized.includes("book") ||
      normalized.includes("down")
    ) {
      return "phone";
    }
    if (normalized.includes("eyes closed")) {
      return "up";
    }
    if (normalized.includes("talking")) {
      return effectiveIncludeTalking ? "talking" : "";
    }
    return "";
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

  const previewEnabled = false;

  useEffect(() => {
    let stream;
    const enableCamera = async () => {
      if (!previewEnabled) {
        setCameraReady(false);
        if (visionStatus === "connected") {
          setCameraError("Preview paused while vision backend is connected.");
        }
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
  }, [previewEnabled, visionStatus]);

  const evaluateFocus = (visionData) => {
    const {
      h_ratio: hRatio,
      v_ratio: vRatio,
      left_ear: leftEar,
      state,
      objects,
      volume
    } = visionData || {};

    const normalizedState = String(state || "").toLowerCase();
    const normalizedObjects = (objects || []).map((item) =>
      String(item).toLowerCase()
    );

    const distractedObjects = ["phone", "cell phone", "tablet", "ipad", "book"];
    const hasDistractor = normalizedObjects.some((item) =>
      distractedObjects.includes(item)
    );

    if (hasDistractor) {
      return { focused: false, reason: "distractor" };
    }

    if (normalizedState.includes("phone") || normalizedState.includes("book")) {
      return { focused: false, reason: "distractor" };
    }

    if (effectiveIncludeTalking && normalizedState.includes("talking")) {
      return { focused: false, reason: "audio" };
    }

    if (normalizedState.includes("no face")) {
      return { focused: false, reason: "no-face" };
    }

    if (typeof leftEar === "number" && leftEar < visionConfig.earThreshold) {
      return { focused: false, reason: "eyes-closed" };
    }

    if (normalizedState === "focused" || normalizedState === "at screen") {
      return { focused: true, reason: "state" };
    }

    if (
      typeof hRatio === "number" &&
      typeof vRatio === "number" &&
      hRatio >= visionConfig.hMin &&
      hRatio <= visionConfig.hMax &&
      vRatio >= visionConfig.vMin &&
      vRatio <= visionConfig.vMax
    ) {
      return { focused: true, reason: "centered" };
    }

    return { focused: false, reason: "off-center" };
  };

  const pushFocusResult = (isFocused) => {
    setFocusResults((prevResults) => {
      const nextResults = [...prevResults, isFocused ? 1 : 0].slice(-60);
      const average =
        nextResults.reduce((sum, value) => sum + value, 0) /
        nextResults.length;
      setFocusLevel(average);
      setCurrentState(average >= 0.7 ? "focused" : "distracted");
      console.log(
        "[LockIn AI] Focus update",
        `level=${Math.round(average * 100)}%`,
        `samples=${nextResults.length}`,
        `latest=${isFocused ? "focused" : "distracted"}`
      );
      return nextResults;
    });
  };

  useEffect(() => {
    if (!trackingEnabled) {
      setVisionStatus("idle");
      return;
    }

    const socket = new WebSocket("ws://localhost:8765");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("[LockIn AI] Vision socket connected");
      setVisionStatus("connected");
      setCameraReady(false);
      sendVisionConfig(visionConfig);
    };

    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        lastPayloadRef.current = payload;
        const incomingState = payload?.state ? String(payload.state) : "";
        if (!effectiveIncludeTalking && incomingState.toLowerCase().includes("talking")) {
          setVisionState("Focused");
        } else {
          setVisionState(incomingState);
        }
        if (payload?.config) {
          setBackendConfig(payload.config);
        }
        if (payload?.preview_jpeg) {
          setVisionFrame(payload.preview_jpeg);
          setCameraReady(true);
        }
        if (typeof payload?.volume === "number") {
          setVisionVolume(payload.volume);
        }
        if (payload?.state) {
          const nextStates = [...recentStatesRef.current, payload.state].slice(
            -60
          );
          recentStatesRef.current = nextStates;
          setDistractorReason(
            computeMostCommonDistractor(nextStates, effectiveIncludeTalking)
          );
        }
        if (payload?.state === "camera-error") {
          setCameraError("Vision backend cannot read the camera.");
        } else {
          setCameraError("");
        }
        console.log("[LockIn AI] Vision payload", payload);
        const result = evaluateFocus(payload);
        pushFocusResult(result.focused);
      } catch (error) {
        console.warn("[LockIn AI] Invalid vision payload", event.data);
      }
    };

    socket.onerror = (event) => {
      console.warn("[LockIn AI] Vision socket error", event);
      setVisionStatus("error");
      setCameraError("Vision backend connection error.");
      setCameraReady(false);
    };

    socket.onclose = () => {
      console.log("[LockIn AI] Vision socket disconnected");
      setVisionStatus("disconnected");
      setVisionFrame("");
      setVisionState("");
      setCameraReady(false);
      setCameraError("Vision backend disconnected.");
      socketRef.current = null;
    };

    return () => {
      socket.close();
    };
  }, [trackingEnabled]);

  useEffect(() => {
    sendVisionConfig(visionConfig);
  }, [visionConfig]);

  useEffect(() => {
    const interval = setInterval(() => {
      sendVisionConfig(visionConfig);
    }, 2000);
    return () => clearInterval(interval);
  }, [visionConfig]);

  const focusWarningActive = focusLevel < 0.7;

  useEffect(() => {
    if (!lessonStarted) {
      return;
    }
    if (!focusWarningActive) {
      if (alertTimeoutRef.current) {
        clearTimeout(alertTimeoutRef.current);
        alertTimeoutRef.current = null;
      }
      alertQueuedRef.current = false;
      return;
    }
    if (alertQueuedRef.current) {
      return;
    }
    const startTime = distractedStartRef.current || Date.now();
    const elapsed = Date.now() - startTime;
    const remaining = Math.max(4000 - elapsed, 0);
    alertTimeoutRef.current = setTimeout(() => {
      if (!focusWarningActive || alertQueuedRef.current) {
        return;
      }
      const stateCandidate = distractorReason || visionState;
      const alertKey = alertKeyForState(stateCandidate);
      if (!alertKey) {
        return;
      }
      const asset = characterAssets[characterChoice]?.[alertKey];
      if (!asset) {
        return;
      }
      alertQueuedRef.current = true;
      setAlertQueue((prev) => [...prev, asset]);
    }, remaining);

    return () => {
      if (alertTimeoutRef.current) {
        clearTimeout(alertTimeoutRef.current);
        alertTimeoutRef.current = null;
      }
    };
  }, [
    focusWarningActive,
    lessonStarted,
    distractorReason,
    visionState,
    characterChoice,
    effectiveIncludeTalking
  ]);

  useEffect(() => {
    if (activeAlert || !alertQueue.length) {
      return;
    }
    const next = alertQueue[0];
    setAlertQueue((prev) => prev.slice(1));
    setActiveAlert(next);
  }, [activeAlert, alertQueue]);

  useEffect(() => {
    if (!activeAlert || !alertVideoRef.current) {
      return;
    }
    alertVideoRef.current.currentTime = 0;
    alertVideoRef.current.play().catch(() => {});
  }, [activeAlert]);

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
      const label = distractorReason || "distracted";
      setSessionTimeline((prev) => [
        ...prev,
        { elapsedSeconds, state: "distracted", label }
      ]);
    }
    if (!focusWarningActive && distractedStartRef.current) {
      distractedTotalRef.current += Math.round(
        (now - distractedStartRef.current) / 1000
      );
      distractedStartRef.current = null;
      setSessionTimeline((prev) => [
        ...prev,
        { elapsedSeconds, state: "focused", label: "focused" }
      ]);
    }
  }, [focusWarningActive, lessonStarted, distractorReason]);

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
            <video
              className="session-video"
              src={characterAssets[characterChoice]?.filler}
              autoPlay
              muted
              loop
              playsInline
            />
            {activeAlert && (
              <video
                ref={alertVideoRef}
                className="session-video alert-video"
                src={activeAlert}
                autoPlay
                playsInline
                onEnded={() => setActiveAlert("")}
              />
            )}
          </div>
          {focusWarningActive && (
            <div className="session-alert">
              YOU'RE NOT FOCUSED
              {distractorReason ? ` - ${distractorReason}` : ""}
            </div>
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
            {previewEnabled ? (
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
            ) : visionFrame ? (
              <img
                className="camera-video"
                src={`data:image/jpeg;base64,${visionFrame}`}
                alt="Vision preview"
              />
            ) : null}
              {visionState && (
                <div className="camera-state">State: {visionState}</div>
              )}
              {(cameraError || !cameraReady) && (
                <div className="camera-overlay">
                  <div className="camera-ring" />
                  <div>
                    <p className="camera-title">Live stream</p>
                    <p className="subtle">
                      {cameraError
                        ? cameraError
                        : previewEnabled
                        ? "Allow camera access to see the live feed."
                        : "Waiting for vision backend preview..."}
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
                  Focus level {focusPercent}%
                </p>
                <div className="focus-meter">
                  <div className="meter">
                    <div
                      className="meter-fill"
                      style={{
                        width: `${focusPercent}%`,
                        background: focusMeterColor
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div>
              <p className="footer-label">Vision</p>
              <p className="footer-subtle">{visionStatus}</p>
              {visionState && (
                <p className="footer-subtle">State: {visionState}</p>
              )}
              <p className="footer-subtle">
                Talking: {visionConfig.includeTalking ? "on" : "off"}
              </p>
              <p className="footer-subtle">
                Audio {visionVolume !== null ? visionVolume.toFixed(2) : "--"} /
                {` ${visionConfig.audioThreshold}`}
              </p>
              {backendConfig && (
                <p className="footer-subtle">
                  Backend talking: {backendConfig.include_talking ? "on" : "off"}
                </p>
              )}
              <p className="footer-subtle">
                Config sent:{" "}
                {lastConfigSentAt
                  ? `${Math.round((Date.now() - lastConfigSentAt) / 1000)}s ago`
                  : "never"}
              </p>
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
              {previewEnabled ? (
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
              ) : visionFrame ? (
                <img
                  className="camera-video"
                  src={`data:image/jpeg;base64,${visionFrame}`}
                  alt="Vision preview"
                />
              ) : null}
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
                <span>Accountability character</span>
                <select
                  value={characterChoice}
                  onChange={(event) => setCharacterChoice(event.target.value)}
                >
                  {Object.entries(characterAssets).map(([key, value]) => (
                    <option value={key} key={key}>
                      {value.label}
                    </option>
                  ))}
                </select>
              </label>
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
              <button className="primary" type="submit">
                Start session
              </button>
            </form>
            <div className="settings-block">
              <p className="subtle">Detection settings</p>
              <div className="settings-grid">
                <label className="field">
                  <span>Horizontal min</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={visionConfig.hMin}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        hMin: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Horizontal max</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={visionConfig.hMax}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        hMax: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Vertical min</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={visionConfig.vMin}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        vMin: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Vertical max</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={visionConfig.vMax}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        vMax: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Eye threshold</span>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={visionConfig.earThreshold}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        earThreshold: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Audio threshold</span>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    value={visionConfig.audioThreshold}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        audioThreshold: Number(event.target.value)
                      }))
                    }
                  />
                </label>
                <label className="field checkbox-field">
                  <span>Include talking</span>
                  <input
                    type="checkbox"
                    checked={visionConfig.includeTalking}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        includeTalking: event.target.checked
                      }))
                    }
                  />
                </label>
                <label className="field checkbox-field">
                  <span>Include objects</span>
                  <input
                    type="checkbox"
                    checked={visionConfig.includeObjects}
                    onChange={(event) =>
                      setVisionConfig((prev) => ({
                        ...prev,
                        includeObjects: event.target.checked
                      }))
                    }
                  />
                </label>
              </div>
            </div>
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
                          {entry.label || entry.state}
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
              </>
            )}
          </section>
        </main>
      )}
    </div>
  );
}

