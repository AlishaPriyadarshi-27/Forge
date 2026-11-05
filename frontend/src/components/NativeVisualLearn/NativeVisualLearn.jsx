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

function DynamicSceneRenderer({ visuals = [], actions = [] }) {
  const list = Array.isArray(visuals) ? visuals : [];
  const actionList = Array.isArray(actions) ? actions : [];
  const active = new Set();

  actionList.forEach(a => {
    const t = String(a?.type || a?.action || "").toLowerCase();
    if (["highlight", "path"].includes(t)) {
      const ids = Array.isArray(a?.targets)
        ? a.targets
        : [a?.target ?? a?.id];
      ids.filter(Boolean).forEach(id => active.add(String(id)));
    }
  });

  const esc = value => String(value ?? "");

  return (
    <div className="nv-dynamic-canvas">
      <svg
        className="nv-dynamic-svg"
        viewBox="0 0 1000 600"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <marker
            id="nvArrow"
            markerWidth="8"
            markerHeight="8"
            refX="7"
            refY="4"
            orient="auto"
          >
            <path d="M0,0 L8,4 L0,8 z" fill="currentColor" />
          </marker>
        </defs>

        {list.map((v, i) => {
          const type = String(v?.type || "text").toLowerCase();
          const hot = active.has(String(v?.id));
          const cls = hot ? "nv-svg-item hot" : "nv-svg-item";

          const x = Number(v?.x ?? 50) * 10;
          const y = Number(v?.y ?? 50) * 6;
          const w = Number(v?.width ?? 18) * 10;
          const h = Number(v?.height ?? 10) * 6;

          if (type === "line" || type === "arrow") {
            const x1 = Number(v?.x1 ?? v?.x ?? 20) * 10;
            const y1 = Number(v?.y1 ?? v?.y ?? 20) * 6;
            const x2 = Number(v?.x2 ?? 70) * 10;
            const y2 = Number(v?.y2 ?? 70) * 6;

            return (
              <g key={v?.id || i} className={cls}>
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  className={type === "arrow" ? "nv-svg-arrow" : "nv-svg-line"}
                  stroke={type === "arrow" ? "#a98cff" : "#8aa9b8"}
                  strokeWidth="3"
                  fill="none"
                  markerEnd={type === "arrow" ? "url(#nvArrow)" : undefined}
                />
                {v?.label && (
                  <text x={(x1+x2)/2} y={(y1+y2)/2-8} className="nv-svg-label" fill="#f3f8fb">
                    {esc(v.label)}
                  </text>
                )}
              </g>
            );
          }

          if (type === "edge") {
            // Edge coordinates are resolved from IDs when possible.
            const from = list.find(o => String(o?.id) === String(v?.from));
            const to = list.find(o => String(o?.id) === String(v?.to));
            if (!from || !to) return null;

            const x1 = Number(from.x ?? 50) * 10;
            const y1 = Number(from.y ?? 50) * 6;
            const x2 = Number(to.x ?? 50) * 10;
            const y2 = Number(to.y ?? 50) * 6;

            return (
              <g key={v?.id || i} className={cls}>
                <line
                  x1={x1} y1={y1} x2={x2} y2={y2}
                  className="nv-svg-arrow"
                  stroke="#a98cff"
                  strokeWidth="3"
                  fill="none"
                  markerEnd="url(#nvArrow)"
                />
                {v?.weight != null && (
                  <text x={(x1+x2)/2} y={(y1+y2)/2-7} className="nv-svg-label" fill="#f3f8fb">
                    {esc(v.weight)}
                  </text>
                )}
              </g>
            );
          }

          if (type === "circle" || type === "point") {
            const r = type === "point" ? 8 : Math.max(8, Number(v?.radius ?? 4) * 6);
            return (
              <g key={v?.id || i} className={cls}>
                <circle
                  cx={x}
                  cy={y}
                  r={r}
                  className="nv-svg-circle"
                  fill={hot ? "#6f50c8" : "#24485a"}
                  stroke={hot ? "#c4adff" : "#8fb4c5"}
                  strokeWidth={hot ? "4" : "2"}
                />
                {v?.label != null && (
                  <text x={x} y={y+r+18} textAnchor="middle" className="nv-svg-label" fill="#f3f8fb">
                    {esc(v.label)}
                  </text>
                )}
              </g>
            );
          }

          if (type === "rect" || type === "group") {
            return (
              <g key={v?.id || i} className={cls}>
                <rect
                  x={x-w/2}
                  y={y-h/2}
                  width={w}
                  height={h}
                  rx="14"
                  className="nv-svg-rect"
                  fill={hot ? "#39275e" : "#162b37"}
                  stroke={hot ? "#b69aff" : "#7195a7"}
                  strokeWidth={hot ? "3" : "2"}
                />
                {v?.label != null && (
                  <text x={x} y={y+5} textAnchor="middle" className="nv-svg-label" fill="#f3f8fb">
                    {esc(v.label)}
                  </text>
                )}
              </g>
            );
          }

          if (type === "node") {
            return (
              <g key={v?.id || i} className={cls}>
                <circle
                  cx={x}
                  cy={y}
                  r="30"
                  className="nv-svg-node"
                  fill={hot ? "#39275e" : "#173646"}
                  stroke={hot ? "#c4adff" : "#91b4c5"}
                  strokeWidth="3"
                />
                <text x={x} y={y+5} textAnchor="middle" className="nv-svg-node-text" fill="#f3f8fb">
                  {esc(v?.label ?? v?.value ?? "")}
                </text>
              </g>
            );
          }

          if (type === "array") {
            const values = Array.isArray(v?.values) ? v.values : [];
            const cellW = Math.min(110, 820 / Math.max(values.length, 1));
            const startX = x - ((values.length - 1) * cellW) / 2;
            return (
              <g key={v?.id || i} className={cls}>
                {values.map((value, j) => (
                  <g key={j}>
                    <rect
                      x={startX + j*cellW - cellW/2}
                      y={y-32}
                      width={cellW-3}
                      height="64"
                      rx="9"
                      className="nv-svg-rect"
                      fill="#162b37"
                      stroke="#7195a7"
                    />
                    <text
                      x={startX + j*cellW}
                      y={y+5}
                      textAnchor="middle"
                      className="nv-svg-label"
                      fill="#f3f8fb"
                    >
                      {esc(typeof value === "object"
                        ? value?.value ?? value?.label ?? ""
                        : value)}
                    </text>
                    <text
                      x={startX + j*cellW}
                      y={y+24}
                      textAnchor="middle"
                      className="nv-svg-index"
                      fill="#9eb5c1"
                    >
                      {j}
                    </text>
                  </g>
                ))}
              </g>
            );
          }

          if (type === "table") {
            const headers = Array.isArray(v?.headers) ? v.headers : [];
            const rows = Array.isArray(v?.rows) ? v.rows : [];
            const all = headers.length ? [headers, ...rows] : rows;
            const cols = Math.max(...all.map(r => Array.isArray(r) ? r.length : 1), 1);
            const cellW = Math.min(180, 760 / cols);
            const rowH = 44;
            const startX = x - (cols * cellW) / 2;
            const startY = y - (all.length * rowH) / 2;

            return (
              <g key={v?.id || i} className={cls}>
                {all.map((row, r) => {
                  const cells = Array.isArray(row) ? row : [row];
                  return cells.map((cell, c) => (
                    <g key={`${r}-${c}`}>
                      <rect
                        x={startX+c*cellW}
                        y={startY+r*rowH}
                        width={cellW-2}
                        height={rowH-2}
                        className={r === 0 && headers.length ? "nv-svg-table-head" : "nv-svg-table-cell"}
                        fill={r === 0 && headers.length ? "#33265c" : "#162b37"}
                        stroke="#6f8f9f"
                      />
                      <text
                        x={startX+c*cellW+cellW/2}
                        y={startY+r*rowH+27}
                        textAnchor="middle"
                        className="nv-svg-table-text"
                        fill="#f3f8fb"
                      >
                        {esc(typeof cell === "object" ? JSON.stringify(cell) : cell)}
                      </text>
                    </g>
                  ));
                })}
              </g>
            );
          }

          if (type === "formula") {
            return (
              <g key={v?.id || i} className={cls}>
                <rect
                  x={x-180}
                  y={y-34}
                  width="360"
                  height="68"
                  rx="14"
                  className="nv-svg-formula"
                  fill="#281f42"
                  stroke="#a98cff"
                  strokeWidth="2"
                />
                <text x={x} y={y+7} textAnchor="middle" className="nv-svg-formula-text">
                  {esc(v?.text ?? v?.label ?? "")}
                </text>
              </g>
            );
          }

          return (
            <g key={v?.id || i} className={cls}>
              <text x={x} y={y} textAnchor="middle" className="nv-svg-label"
                fill="#f3f8fb">
                {esc(v?.text ?? v?.label ?? v?.value ?? v?.name ?? "")}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function NativeVisualLearn({
  topic = "Binary Search",
  difficulty = "intermediate",
  onLessonReady = null,
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
    if (typeof onLessonReady === "function") onLessonReady(null);

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
      if (typeof onLessonReady === "function") {
        onLessonReady(data.lesson);
      }
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

          <DynamicSceneRenderer
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
