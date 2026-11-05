import React, { useEffect, useRef, useState } from "react";
import "./ella.css";


function EllaMark({ compact = false }) {
  return (
    <span
      className={`ella-mark ${compact ? "ella-mark-compact" : ""}`}
      aria-hidden="true"
    >
      <span className="ella-sigil-core" />
      <span className="ella-sigil-ring ella-sigil-ring-a" />
      <span className="ella-sigil-ring ella-sigil-ring-b" />
      <span className="ella-sigil-spark ella-sigil-spark-a" />
      <span className="ella-sigil-spark ella-sigil-spark-b" />
    </span>
  );
}


function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|__[^_]+__|`[^`]+`|~~[^~]+~~)/g);

  return parts.map((part, index) => {
    if (!part) return null;
    if (/^\*\*.*\*\*$/.test(part) || /^__.*__$/.test(part)) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (/^`.*`$/.test(part)) {
      return <code key={index} className="ella-inline-code">{part.slice(1, -1)}</code>;
    }
    if (/^~~.*~~$/.test(part)) {
      return <del key={index}>{part.slice(2, -2)}</del>;
    }
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
}

function parseMermaidFlow(source) {
  const cleaned = source
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line && !/^flowchart\s+/i.test(line) && !/^graph\s+/i.test(line));

  const nodes = [];
  const edges = [];

  const addNode = (id, label) => {
    if (!id) return;
    if (!nodes.some((node) => node.id === id)) {
      nodes.push({ id, label: label || id });
    }
  };

  cleaned.forEach((line) => {
    const parts = line.split(/\s*--+>\s*/);
    if (parts.length < 2) return;

    const ids = [];
    parts.forEach((part) => {
      const match = part.match(/^([A-Za-z0-9_-]+)(?:\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\})?$/);
      if (!match) return;
      const id = match[1];
      const label = match[2] || match[3] || match[4] || id;
      addNode(id, label);
      ids.push(id);
    });

    for (let index = 0; index < ids.length - 1; index += 1) {
      edges.push([ids[index], ids[index + 1]]);
    }
  });

  return { nodes, edges };
}

function MermaidFlow({ source }) {
  const { nodes, edges } = parseMermaidFlow(source);

  if (!nodes.length) {
    return (
      <pre className="ella-code-block">
        <code>{source}</code>
      </pre>
    );
  }

  return (
    <div className="ella-visual-card">
      <div className="ella-visual-kicker">
        <EllaMark compact />
        VISUAL EXPLANATION
      </div>
      <div className="ella-flow">
        {nodes.map((node, index) => (
          <React.Fragment key={node.id}>
            <div className="ella-flow-node">{renderInline(node.label)}</div>
            {index < nodes.length - 1 && (
              <div className="ella-flow-arrow" aria-hidden="true">→</div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function EllaRichText({ content }) {
  const lines = String(content || "").replace(/\r/g, "").split("\n");
  const blocks = [];
  let codeLines = [];
  let codeLanguage = "";
  let inCode = false;
  let listItems = [];
  let listType = null;

  const flushList = () => {
    if (!listItems.length) return;
    const Tag = listType === "ol" ? "ol" : "ul";
    blocks.push(
      <Tag key={`list-${blocks.length}`} className="ella-rich-list">
        {listItems.map((item, index) => (
          <li key={index}>{renderInline(item)}</li>
        ))}
      </Tag>
    );
    listItems = [];
    listType = null;
  };

  lines.forEach((line, index) => {
    if (line.trim().startsWith("```")) {
      if (inCode) {
        const code = codeLines.join("\n");
        blocks.push(
          codeLanguage.toLowerCase() === "mermaid" ? (
            <MermaidFlow key={`visual-${index}`} source={code} />
          ) : (
            <pre key={`code-${index}`} className="ella-code-block">
              <code>{code}</code>
            </pre>
          )
        );
        codeLines = [];
        codeLanguage = "";
        inCode = false;
      } else {
        flushList();
        inCode = true;
        codeLanguage = line.trim().slice(3).trim();
      }
      return;
    }

    if (inCode) {
      codeLines.push(line);
      return;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      return;
    }

    const unordered = trimmed.match(/^[-*]\s+(.+)$/);
    const ordered = trimmed.match(/^\d+[.)]\s+(.+)$/);

    if (unordered || ordered) {
      const nextType = ordered ? "ol" : "ul";
      if (listType && listType !== nextType) flushList();
      listType = nextType;
      listItems.push((unordered || ordered)[1]);
      return;
    }

    flushList();

    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const Tag = level === 1 ? "h3" : level === 2 ? "h4" : "h5";
      blocks.push(<Tag key={`heading-${index}`}>{renderInline(heading[2])}</Tag>);
      return;
    }

    blocks.push(
      <p key={`p-${index}`} className="ella-rich-paragraph">
        {renderInline(trimmed)}
      </p>
    );
  });

  if (inCode) {
    blocks.push(
      <pre key="unfinished-code" className="ella-code-block">
        <code>{codeLines.join("\n")}</code>
      </pre>
    );
  }
  flushList();

  return <div className="ella-rich-text">{blocks}</div>;
}

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

async function readApiResponse(response) {
  const raw = await response.text();

  let data = {};

  if (raw.trim()) {
    try {
      data = JSON.parse(raw);
    } catch {
      throw new Error(
        `ELLA server returned a non-JSON response (HTTP ${response.status}).`
      );
    }
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
        data?.message ||
        data?.error ||
        `ELLA request failed (HTTP ${response.status}).`
    );
  }

  return data;
}

export default function EllaAssistant({
  page = "FORGE",
  role = "",
  topic = "",
}) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi, I’m ELLA.\nYour FORGE AI assistant. Ask me anything — coding, DSA, AI/ML, projects, or FORGE.",
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  const [error, setError] = useState("");

  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // ------------------------------------------------------
  // Scroll to latest message
  // ------------------------------------------------------

  useEffect(() => {
    if (!open) return;

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, open]);

  // ------------------------------------------------------
  // Escape key
  // ------------------------------------------------------

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  // ------------------------------------------------------
  // Add message
  // ------------------------------------------------------

  const addMessage = (roleName, content) => {
    const newMessage = {
      id: `${Date.now()}-${Math.random()}`,
      role: roleName,
      content,
    };

    setMessages((previous) => [
      ...previous,
      newMessage,
    ]);

    return newMessage;
  };

  // ------------------------------------------------------
  // Build conversation history
  // ------------------------------------------------------

  const getHistory = () => {
    return messages
      .filter(
        (item) =>
          item.role === "user" ||
          item.role === "assistant"
      )
      .slice(-16)
      .map((item) => ({
        role: item.role,
        content: item.content,
      }));
  };

  // ------------------------------------------------------
  // Send text message
  // ------------------------------------------------------

  const sendMessage = async () => {
    const text = message.trim();

    if (!text || loading) {
      return;
    }

    setError("");
    setMessage("");
    addMessage("user", text);
    setLoading(true);

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 45000);

    try {
      const history = [
        ...messages,
        { role: "user", content: text },
      ]
        .filter((item) => item.role === "user" || item.role === "assistant")
        .slice(-16)
        .map((item) => ({ role: item.role, content: item.content }));

      const response = await fetch(
        `${API_BASE}/api/assistant/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: text,
            history,
            page,
            role,
            topic,
          }),
          signal: controller.signal,
        }
      );

      const data = await readApiResponse(response);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "ELLA could not process your request."
        );
      }

      const answer =
        data?.message ||
        data?.response ||
        data?.answer ||
        "I couldn't generate a response.";

      addMessage("assistant", answer);
    } catch (err) {
      console.error("ELLA chat error:", err);

      const errorMessage =
        err?.name === "AbortError"
          ? "ELLA took too long to respond. Please try again."
          : (err?.message || "Something went wrong while connecting to ELLA.");

      setError(errorMessage);
      addMessage("assistant", errorMessage);
    } finally {
      window.clearTimeout(timeoutId);
      setLoading(false);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }
  };

  // ------------------------------------------------------
  // Enter key
  // ------------------------------------------------------

  const handleInputKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  // ------------------------------------------------------
  // Image picker
  // ------------------------------------------------------

  const openImagePicker = () => {
    if (loading || uploadingImage) {
      return;
    }

    fileInputRef.current?.click();
  };

  // ------------------------------------------------------
  // Image upload
  // ------------------------------------------------------

  const handleImageChange = async (event) => {
    const file = event.target.files?.[0];

    event.target.value = "";

    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      setError("Please select an image file.");
      return;
    }

    setError("");
    setUploadingImage(true);

    addMessage(
      "user",
      `📷 Image uploaded: ${file.name}`
    );

    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append(
        "prompt",
        "Analyze this screenshot/image and help me understand what I am looking at. If there is an error, explain the cause and exact next step."
      );
      formData.append("page", page);
      formData.append("role", role);
      formData.append("topic", topic);

      const response = await fetch(
        `${API_BASE}/api/assistant/vision`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await readApiResponse(response);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "ELLA could not analyze this image."
        );
      }

      const answer =
        data?.message ||
        data?.response ||
        data?.answer ||
        "I couldn't analyze the image.";

      addMessage("assistant", answer);
    } catch (err) {
      console.error(
        "ELLA vision error:",
        err
      );

      const errorMessage =
        err?.message ||
        "Image analysis failed.";

      setError(errorMessage);

      addMessage(
        "assistant",
        `I couldn't analyze that image.\n\n${errorMessage}`
      );
    } finally {
      setUploadingImage(false);
    }
  };

  // ------------------------------------------------------
  // Voice recording
  // ------------------------------------------------------

  const startRecording = async () => {
    if (
      loading ||
      uploadingImage ||
      recording
    ) {
      return;
    }

    setError("");

    if (
      !navigator.mediaDevices ||
      !navigator.mediaDevices.getUserMedia
    ) {
      setError(
        "Your browser does not support microphone recording."
      );
      return;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      const recorder =
        new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(
            event.data
          );
        }
      };

      recorder.onstop = async () => {
        stream
          .getTracks()
          .forEach((track) => track.stop());

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type:
              recorder.mimeType ||
              "audio/webm",
          }
        );

        await transcribeAudio(audioBlob);
      };

      recorder.start();

      setRecording(true);
    } catch (err) {
      console.error(
        "Microphone error:",
        err
      );

      setError(
        "Microphone permission was denied or unavailable."
      );
    }
  };

  const stopRecording = () => {
    const recorder =
      mediaRecorderRef.current;

    if (
      !recorder ||
      recorder.state === "inactive"
    ) {
      return;
    }

    recorder.stop();
    setRecording(false);
  };

  // ------------------------------------------------------
  // Transcribe audio
  // ------------------------------------------------------

  const transcribeAudio = async (
    audioBlob
  ) => {
    setLoading(true);

    try {
      const extension =
        audioBlob.type.includes("mp4")
          ? "m4a"
          : "webm";

      const file = new File(
        [audioBlob],
        `ella-recording.${extension}`,
        {
          type:
            audioBlob.type ||
            "audio/webm",
        }
      );

      const formData = new FormData();

      formData.append(
        "file",
        file
      );

      const response = await fetch(
        `${API_BASE}/api/assistant/transcribe`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await readApiResponse(response);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            "Speech transcription failed."
        );
      }

      const transcript =
        data?.text ||
        data?.transcript ||
        "";

      if (!transcript.trim()) {
        throw new Error(
          "I couldn't detect any speech."
        );
      }

      setMessage(transcript);

      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    } catch (err) {
      console.error(
        "ELLA transcription error:",
        err
      );

      setError(
        err?.message ||
          "Voice transcription failed."
      );
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------------------------------
  // Voice output
  // ------------------------------------------------------

  const speakMessage = (text) => {
    if (
      !text ||
      typeof window === "undefined" ||
      !window.speechSynthesis
    ) {
      return;
    }

    window.speechSynthesis.cancel();

    const utterance =
      new SpeechSynthesisUtterance(text);

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    window.speechSynthesis.speak(
      utterance
    );
  };

  // ------------------------------------------------------
  // Empty state
  // ------------------------------------------------------

  const quickPrompts = [
    "Explain this topic simply",
    "Help me debug my code",
    "Make me a DSA study plan",
    "Visualize this concept",
  ];

  // ------------------------------------------------------
  // Render
  // ------------------------------------------------------

  return (
    <div className="ella-root">
      {/* Floating ELLA button */}

      {!open && (
        <button
          type="button"
          className="ella-floating-button"
          onClick={() => setOpen(true)}
          aria-label="Open ELLA"
          title="Ask ELLA"
        >
          <EllaMark />

          <span className="ella-floating-label">
            ELLA
          </span>
        </button>
      )}

      {/* Assistant */}

      {open && (
        <>
          <div
            className="ella-backdrop"
            onClick={() => setOpen(false)}
          />

          <section
            className="ella-panel"
            role="dialog"
            aria-modal="true"
            aria-label="ELLA AI Assistant"
          >
            {/* Header */}

            <header className="ella-header">
              <div className="ella-header-left">
                <EllaMark />

                <div>
                  <div className="ella-title">
                    ELLA
                  </div>

                  <div className="ella-status">
                    <span className="ella-status-dot" />
                    FORGE AI Assistant
                  </div>
                </div>
              </div>

              <button
                className="ella-close"
                onClick={() =>
                  setOpen(false)
                }
                aria-label="Close ELLA"
              >
                ×
              </button>
            </header>

            {/* Context */}

            {(role || topic) && (
              <div className="ella-context">
                {role && (
                  <span>
                    {role}
                  </span>
                )}

                {topic && (
                  <span>
                    {topic}
                  </span>
                )}
              </div>
            )}

            {/* Messages */}

            <div className="ella-messages">
              {messages.map((item) => (
                <div
                  key={item.id}
                  className={`ella-message-row ${
                    item.role === "user"
                      ? "ella-message-user"
                      : "ella-message-assistant"
                  }`}
                >
                  {item.role ===
                    "assistant" && (
                    <div className="ella-small-avatar">
                      <EllaMark compact />
                    </div>
                  )}

                  <div className="ella-message-content">
                    <div className="ella-message-bubble">
                      <EllaRichText content={item.content} />
                    </div>

                    {item.role ===
                      "assistant" && (
                      <button
                        className="ella-speak-button"
                        onClick={() =>
                          speakMessage(
                            item.content
                          )
                        }
                        title="Read aloud"
                      >
                        🔊
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="ella-message-row ella-message-assistant">
                  <div className="ella-small-avatar">
                    <EllaMark compact />
                  </div>

                  <div className="ella-typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}

              <div
                ref={messagesEndRef}
              />
            </div>

            {/* Error */}

            {error && (
              <div className="ella-error">
                {error}
              </div>
            )}

            {/* Quick prompts */}

            {messages.length === 1 && (
              <div className="ella-quick-prompts">
                {quickPrompts.map(
                  (prompt) => (
                    <button
                      key={prompt}
                      onClick={() =>
                        setMessage(prompt)
                      }
                    >
                      {prompt}
                    </button>
                  )
                )}
              </div>
            )}

            {/* Input */}

            <div className="ella-composer">
              <div className="ella-input-row">
                <textarea
                  ref={inputRef}
                  value={message}
                  onChange={(event) =>
                    setMessage(
                      event.target.value
                    )
                  }
                  onKeyDown={
                    handleInputKeyDown
                  }
                  placeholder={
                    recording
                      ? "Listening..."
                      : "Ask ELLA anything..."
                  }
                  rows={1}
                  disabled={
                    loading ||
                    recording
                  }
                />

                {/* Image */}

                <button
                  className="ella-tool-button"
                  onClick={
                    openImagePicker
                  }
                  disabled={
                    loading ||
                    uploadingImage ||
                    recording
                  }
                  title="Upload screenshot"
                >
                  📎
                </button>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={
                    handleImageChange
                  }
                  hidden
                />

                {/* Microphone */}

                <button
                  className={`ella-tool-button ${
                    recording
                      ? "ella-recording"
                      : ""
                  }`}
                  onClick={
                    recording
                      ? stopRecording
                      : startRecording
                  }
                  disabled={
                    loading ||
                    uploadingImage
                  }
                  title={
                    recording
                      ? "Stop recording"
                      : "Voice input"
                  }
                >
                  {recording
                    ? "■"
                    : "🎙"}
                </button>

                {/* Send */}

                <button
                  className="ella-send-button"
                  onClick={
                    sendMessage
                  }
                  disabled={
                    !message.trim() ||
                    loading ||
                    recording
                  }
                  title="Send message"
                >
                  ↑
                </button>
              </div>

              <div className="ella-composer-hint">
                Enter to send · Shift + Enter
                for a new line
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}