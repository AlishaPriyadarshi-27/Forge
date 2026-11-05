import React, { useEffect, useMemo, useRef, useState } from "react";
import "./NativeVisualLearn.css";

const API = import.meta.env.VITE_FORGE_API_BASE || "http://localhost:8000";

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

function readNumber(value, fallback = null) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function normalizeValues(arrayVisual, visuals) {
  const candidates = [
    arrayVisual?.values,
    arrayVisual?.data,
    arrayVisual?.items,
    arrayVisual?.elements,
    visuals.find(v => v?.type === "sequence")?.values,
    visuals.find(v => v?.type === "sequence")?.data,
  ];

  for (const candidate of candidates) {
    if (Array.isArray(candidate) && candidate.length) {
      return candidate.map((x, i) => {
        if (typeof x === "object" && x !== null) {
          return x.value ?? x.label ?? x.name ?? i;
        }
        return x;
      });
    }
  }

  return [];
}

function inferTarget(scene, values) {
  const text = `${scene?.title || ""} ${scene?.narration || ""}`;
  const matches = text.match(/\b(?:target(?:\s+value)?|value|find|looking\s+for)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)/i);
  if (matches) return matches[1];

  const allNums = text.match(/\b-?\d+(?:\.\d+)?\b/g)?.map(Number) || [];
  const candidate = allNums.find(n => values.some(v => Number(v) === n));
  return candidate ?? null;
}

function getPointerIndex(pointer, values) {
  const direct = [
    pointer?.index,
    pointer?.position,
    pointer?.array_index,
    pointer?.current_index,
  ];

  for (const value of direct) {
    const n = readNumber(value);
    if (n !== null) return clamp(Math.round(n), 0, Math.max(values.length - 1, 0));
  }

  const pointerValue = pointer?.value ?? pointer?.target_value;
  if (pointerValue !== undefined) {
    const idx = values.findIndex(v => String(v) === String(pointerValue));
    if (idx >= 0) return idx;
  }

  return 0;
}

function derivePointerIndex(label, scene, values, fallback) {
  const text = `${scene?.title || ""} ${scene?.narration || ""}`.toLowerCase();
  const nums = text.match(/\b-?\d+(?:\.\d+)?\b/g)?.map(Number) || [];

  if (label === "low") {
    if (/\blow\b.*?\b0\b/.test(text) || /\bbeginning\b/.test(text)) return 0;
  }

  if (label === "high") {
    if (/\bhigh\b.*?\bend\b/.test(text)) return values.length - 1;
    if (/\bhigh\b.*?\b7\b/.test(text) && values.length >= 8) return 7;
  }

  if (label === "mid") {
    const explicit = text.match(/\bmid(?:point)?\b.*?\bindex\s+(\d+)\b/i);
    if (explicit) return clamp(Number(explicit[1]), 0, values.length - 1);
    const n = nums.find(x => x >= 0 && x < values.length);
    if (n !== undefined && /mid/.test(text)) return n;
  }

  return fallback;
}


function normalizeBinarySearchValues(values, scene) {
  const next = [...values];
  const text = `${scene?.title || ""} ${scene?.narration || ""}`;

  // Gemini can occasionally describe a value at a specific index while its
  // visual payload contains a stale value. Prefer the explicit scene statement.
  const explicitPairs = [
    ...text.matchAll(
      /\b(?:index|position)\s*(\d+)[^.\n]{0,55}?\b(?:contains|has|holds|value\s+is)\s*(?:the\s+)?value\s*(-?\d+(?:\.\d+)?)/gi
    ),
  ];

  for (const match of explicitPairs) {
    const index = Number(match[1]);
    const value = match[2];
    if (Number.isInteger(index) && index >= 0 && index < next.length) {
      next[index] = value;
    }
  }

  // Also handle phrasing such as "mid index is 4, which contains the value 37".
  const midMatch = text.match(
    /\bmid(?:dle)?\s+index\s+(?:is\s+)?(\d+)[^.\n]{0,50}?\b(?:contains|has|holds)\s+(?:the\s+)?(?:value\s+)?(-?\d+(?:\.\d+)?)/i
  );
  if (midMatch) {
    const index = Number(midMatch[1]);
    if (Number.isInteger(index) && index >= 0 && index < next.length) {
      next[index] = midMatch[2];
    }
  }

  return next;
}

function getVisualPosition(v, index, total) {
  const p = v?.position || v?.pos || {};
  let x = Number(v?.x ?? p.x);
  let y = Number(v?.y ?? p.y);

  if (Number.isFinite(x) && Number.isFinite(y)) {
    return { x, y };
  }

  // Generic deterministic fallback layout. This is not topic logic:
  // it simply places an arbitrary visual object on the canvas.
  const cols = Math.max(1, Math.ceil(Math.sqrt(total)));
  const row = Math.floor(index / cols);
  const col = index % cols;

  return {
    x: 12 + (col * 76) / Math.max(cols - 1, 1),
    y: 18 + (row * 62) / Math.max(Math.ceil(total / cols) - 1, 1),
  };
}

function visualText(v) {
  if (v?.text != null) return String(v.text);
  if (v?.label != null) return String(v.label);
  if (v?.value != null && !Array.isArray(v.value)) return String(v.value);
  if (v?.name != null) return String(v.name);
  if (v?.title != null) return String(v.title);
  if (v?.content != null && typeof v.content !== "object") return String(v.content);
  return "";
}

function UniversalSceneRenderer({ visuals = [], actions = [] }) {
  const safeVisuals = Array.isArray(visuals) ? visuals : [];
  const nodes = new Map(
    safeVisuals
      .filter(v => v?.id != null)
      .map(v => [String(v.id), v])
  );

  const activeIds = new Set();
  const actionList = Array.isArray(actions) ? actions : [];

  actionList.forEach(action => {
    const type = String(action?.type || action?.action || "").toLowerCase();
    const targets = action?.targets ?? action?.target ?? action?.id;
    const list = Array.isArray(targets) ? targets : [targets];

    if (["highlight", "path"].includes(type)) {
      list.filter(Boolean).forEach(x => activeIds.add(String(x)));
    }
  });

  const pointFor = (v, index) => getVisualPosition(v, index, safeVisuals.length);

  return (
    <div className="nv-universal-canvas">
      <svg className="nv-edge-layer" viewBox="0 0 100 100" preserveAspectRatio="none">
        {safeVisuals
          .filter(v => String(v?.type || "").toLowerCase() === "edge")
          .map((edge, i) => {
            const from = nodes.get(String(edge?.from ?? edge?.source ?? ""));
            const to = nodes.get(String(edge?.to ?? edge?.target ?? ""));
            if (!from || !to) return null;

            const fromIndex = safeVisuals.indexOf(from);
            const toIndex = safeVisuals.indexOf(to);
            const a = pointFor(from, fromIndex);
            const b = pointFor(to, toIndex);
            const active = activeIds.has(String(edge?.id));

            return (
              <g key={edge?.id || `edge-${i}`}>
                <line
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  className={active ? "nv-edge active" : "nv-edge"}
                />
                {edge?.directed !== false && (
                  <circle
                    cx={b.x}
                    cy={b.y}
                    r="0.9"
                    className={active ? "nv-edge-arrow active" : "nv-edge-arrow"}
                  />
                )}
                {edge?.weight != null && (
                  <text
                    x={(a.x + b.x) / 2}
                    y={(a.y + b.y) / 2 - 2}
                    className="nv-edge-weight"
                  >
                    {String(edge.weight)}
                  </text>
                )}
              </g>
            );
          })}
      </svg>

      <div className="nv-scene-layer">
        {safeVisuals.map((v, i) => {
          const type = String(v?.type || "text").toLowerCase();
          if (type === "edge") return null;

          const { x, y } = pointFor(v, i);
          const active = activeIds.has(String(v?.id));
          const width = Number(v?.width);
          const height = Number(v?.height);

          const style = {
            left: `${x}%`,
            top: `${y}%`,
            ...(Number.isFinite(width) ? { width: `${width}%` } : {}),
            ...(Number.isFinite(height) ? { height: `${height}%` } : {}),
          };

          const rawItems = v?.values ?? v?.items ?? v?.data;
          const items = Array.isArray(rawItems) ? rawItems : null;

          if (type === "array" && items) {
            return (
              <div
                key={v?.id || i}
                className={`nv-object nv-object-array ${active ? "active" : ""}`}
                style={style}
              >
                {items.map((item, j) => (
                  <div className="nv-object-array-item" key={j}>
                    <strong>
                      {typeof item === "object"
                        ? item?.value ?? item?.label ?? item?.name ?? ""
                        : String(item)}
                    </strong>
                    <small>{j}</small>
                  </div>
                ))}
              </div>
            );
          }

          if (type === "table" && items) {
            const rows = items.map(row => Array.isArray(row) ? row : [row]);
            return (
              <div
                key={v?.id || i}
                className={`nv-object nv-object-table ${active ? "active" : ""}`}
                style={style}
              >
                {rows.map((row, r) => (
                  <div className="nv-table-row" key={r}>
                    {row.map((cell, c) => (
                      <span key={c}>{typeof cell === "object" ? JSON.stringify(cell) : String(cell)}</span>
                    ))}
                  </div>
                ))}
              </div>
            );
          }

          if (type === "stack" && items) {
            return (
              <div
                key={v?.id || i}
                className={`nv-object nv-object-stack ${active ? "active" : ""}`}
                style={style}
              >
                {items.map((item, j) => (
                  <div key={j}>{typeof item === "object" ? item?.value ?? item?.label ?? "" : String(item)}</div>
                ))}
              </div>
            );
          }

          const className = [
            "nv-object",
            `nv-object-${type}`,
            active ? "active" : "",
          ].join(" ");

          return (
            <div key={v?.id || i} className={className} style={style}>
              <span>{visualText(v)}</span>
              {v?.subtext != null && <small>{String(v.subtext)}</small>}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function NativeVisualLearn({
  topic = "Binary Search",
  difficulty = "intermediate",
}) {
  const [lesson, setLesson] = useState(null);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [voiceRate, setVoiceRate] = useState(1);
  const [speaking, setSpeaking] = useState(false);

  const timer = useRef(null);
  const utteranceRef = useRef(null);
  const autoLoadedTopicRef = useRef("");

  const scene = lesson?.scenes?.[sceneIndex] || null;

  const progress = useMemo(() => {
    if (!lesson?.scenes?.length) return 0;
    return ((sceneIndex + 1) / lesson.scenes.length) * 100;
  }, [lesson, sceneIndex]);

  const stopVoice = () => {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    utteranceRef.current = null;
    setSpeaking(false);
  };

  const speakScene = (currentScene) => {
    if (
      !voiceEnabled ||
      !currentScene?.narration ||
      !("speechSynthesis" in window)
    ) return;

    stopVoice();

    const utterance = new SpeechSynthesisUtterance(
      String(currentScene.narration).replace(/\s+/g, " ").trim()
    );

    utterance.rate = voiceRate;
    utterance.pitch = 1;
    utterance.volume = 1;
    utterance.lang = "en-US";

    const voices = window.speechSynthesis.getVoices();
    const preferred =
      voices.find(
        v =>
          /en-US/i.test(v.lang) &&
          /Google|Microsoft|Samantha|Natural/i.test(v.name)
      ) ||
      voices.find(v => /en-US/i.test(v.lang)) ||
      voices.find(v => /^en/i.test(v.lang));

    if (preferred) utterance.voice = preferred;

    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => {
      utteranceRef.current = null;
      setSpeaking(false);
    };
    utterance.onerror = () => {
      utteranceRef.current = null;
      setSpeaking(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  async function loadLesson() {
    stopVoice();
    setLoading(true);
    setError("");
    setLesson(null);
    setSceneIndex(0);

    try {
      const res = await fetch(`${API}/api/student/native-visual-lesson`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, difficulty }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.detail || "Could not create visual lesson.");
      }

      setLesson(data.lesson);
    } catch (e) {
      setError(e?.message || "Visual lesson failed.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const key = `${topic}::${difficulty}`;
    if (!topic || autoLoadedTopicRef.current === key) return;
    autoLoadedTopicRef.current = key;
    loadLesson();
  }, [topic, difficulty]);

  useEffect(() => {
    if (!scene) return;

    clearTimeout(timer.current);

    const voiceTimer = window.setTimeout(() => {
      speakScene(scene);
    }, 200);

    timer.current = window.setTimeout(() => {
      setSceneIndex(i =>
        i + 1 < (lesson?.scenes?.length || 0) ? i + 1 : i
      );
    }, Math.max(4500, Number(scene.duration || 5) * 1000));

    return () => {
      clearTimeout(timer.current);
      clearTimeout(voiceTimer);
    };
  }, [sceneIndex, lesson]);

  useEffect(() => {
    if (scene && voiceEnabled) speakScene(scene);
    if (!voiceEnabled) stopVoice();
  }, [voiceRate, voiceEnabled]);

  useEffect(() => {
    return () => {
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
      clearTimeout(timer.current);
    };
  }, []);

  const goToScene = index => {
    stopVoice();
    setSceneIndex(clamp(index, 0, (lesson?.scenes?.length || 1) - 1));
  };

  return (
    <section className="native-visual-learn">
      <div className="nv-header">
        <div>
          <span className="nv-kicker">FORGE · VISUAL LEARN</span>
          <h2>{lesson?.title || topic}</h2>
          <p>
            {lesson
              ? `Scene ${sceneIndex + 1} of ${lesson.scenes.length}`
              : "Topic-specific browser animation + voice narration"}
          </p>
        </div>

        <div className="nv-header-actions">
          {lesson && (
            <div className="nv-voice-controls">
              <button
                className={`nv-voice-btn ${voiceEnabled ? "active" : ""}`}
                onClick={() => setVoiceEnabled(v => !v)}
              >
                {voiceEnabled ? "🔊 Voice ON" : "🔇 Voice OFF"}
              </button>

              <select
                className="nv-rate"
                value={voiceRate}
                onChange={e => setVoiceRate(Number(e.target.value))}
                aria-label="Voice speed"
              >
                <option value="0.85">0.85×</option>
                <option value="1">1× Normal</option>
                <option value="1.1">1.1×</option>
              </select>

              {speaking && (
                <button className="nv-stop-btn" onClick={stopVoice}>
                  Stop
                </button>
              )}
            </div>
          )}

          <button className="nv-start" onClick={loadLesson} disabled={loading}>
            {loading
              ? "Building lesson…"
              : lesson
                ? "Regenerate"
                : "Build Full Explanation"}
          </button>
        </div>
      </div>

      {error && <div className="nv-error">{error}</div>}

      {loading && (
        <div className="nv-loading">
          <div className="nv-spinner" />
          <strong>Gemini is designing the visual grammar…</strong>
          <span>
            No MP4 rendering. The lesson will animate directly in the browser.
          </span>
        </div>
      )}

      {scene && (
        <div className="nv-lesson">
          <div className="nv-scene-title">
            <span>{sceneIndex + 1}</span>
            <div>
              <h3>{scene.title}</h3>
              <p>{scene.narration}</p>
            </div>
          </div>

          <UniversalSceneRenderer
            visuals={Array.isArray(scene.visuals) ? scene.visuals : []}
            actions={Array.isArray(scene.actions) ? scene.actions : []}
          />

          <div className="nv-controls">
            <button
              onClick={() => goToScene(sceneIndex - 1)}
              disabled={sceneIndex === 0}
            >
              ← Previous
            </button>

            <div className="nv-dots">
              {lesson.scenes.map((_, i) => (
                <button
                  key={i}
                  aria-label={`Scene ${i + 1}`}
                  className={i === sceneIndex ? "active" : ""}
                  onClick={() => goToScene(i)}
                />
              ))}
            </div>

            <button
              onClick={() => goToScene(sceneIndex + 1)}
              disabled={sceneIndex === lesson.scenes.length - 1}
            >
              Next →
            </button>
          </div>

          <div className="nv-voice-status">
            <span className="nv-voice-wave">
              {speaking ? "● ● ●" : "●"}
            </span>
            <span>
              {voiceEnabled
                ? speaking
                  ? "FORGE is narrating this scene at normal speed"
                  : "Voice narration ready"
                : "Voice narration muted"}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
