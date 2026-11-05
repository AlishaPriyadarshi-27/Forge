"""
ELLA - FORGE AI Assistant Service

Handles:
- Text chat
- Image / screenshot analysis
- Speech-to-text
- Conversation history
- FORGE-aware assistant behavior
"""

from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

CHAT_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)

# Groq shut down the old Llama 4 Scout vision model.
# Keep the vision model configurable, but automatically ignore stale
# Llama-4 Scout/Maverick values that may still exist in .env.
_requested_vision_model = os.getenv("GROQ_VISION_MODEL", "").strip()

if (
    not _requested_vision_model
    or "llama-4-scout" in _requested_vision_model.lower()
    or "llama-4-maverick" in _requested_vision_model.lower()
):
    VISION_MODEL = "qwen/qwen3.8-27b"
else:
    VISION_MODEL = _requested_vision_model

STT_MODEL = os.getenv(
    "GROQ_STT_MODEL",
    "whisper-large-v3-turbo",
)

MAX_HISTORY_MESSAGES = 16
MAX_IMAGE_MB = 20
MAX_AUDIO_MB = 25


# =========================================================
# ELLA SYSTEM PROMPT
# =========================================================

ELLA_SYSTEM_PROMPT = """
You are ELLA, the intelligent AI assistant inside FORGE.

FORGE is a student-focused workforce intelligence and career development
platform.

You help students with:

- Coding
- Debugging
- DSA
- Computer Science
- AI/ML
- Projects
- Hackathons
- Career preparation
- Industry skills
- Topic Intelligence
- Skill development
- Learning plans
- Screenshots and error analysis
- FORGE platform navigation

PERSONALITY:
- Helpful
- Friendly
- Practical
- Clear
- Intelligent
- Encouraging
- Concise unless the user asks for depth

LANGUAGE:
- Match the user's language.
- If the user uses Hinglish, respond naturally in Hinglish.
- If the user uses English, respond in English.
- Keep technical terms in their normal technical form.

CODING:
- Give runnable code when appropriate.
- Clearly explain which file the code belongs in.
- For debugging, identify the likely cause and give the exact fix.
- Do not invent files, APIs, datasets, endpoints or project structure.

FORGE DATA:
- Never invent job-posting counts.
- Never invent O*NET statistics.
- Never invent ESCO statistics.
- Never invent BLS statistics.
- Never invent WEF statistics.
- If evidence is unavailable, clearly say that it is unavailable.

SCREENSHOTS:
- Analyze only what is actually visible.
- Do not claim to see information that is not visible.
- For code/error screenshots, give practical next steps.

SECURITY:
- Never reveal API keys.
- Never ask the user to paste private API keys.
- Never expose environment variables or secrets.
"""


# =========================================================
# HELPERS
# =========================================================

def clean_text(value: Any) -> str:
    """Convert a value into clean text."""
    if value is None:
        return ""

    return str(value).strip()


def get_groq_client() -> Any:
    """Create Groq client using the backend environment variable."""

    if Groq is None:
        raise RuntimeError(
            "Groq package is not installed. "
            "Run: pip install groq"
        )

    api_key = (
        os.getenv("GROQ_API_KEY")
        or os.getenv("GROQ_API_TOKEN")
    )

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured in the backend environment."
        )

    return Groq(api_key=api_key)


def normalize_history(
    history: Optional[List[Dict[str, Any]]]
) -> List[Dict[str, str]]:
    """Convert frontend history into safe chat messages."""

    if not isinstance(history, list):
        return []

    result: List[Dict[str, str]] = []

    for item in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(item, dict):
            continue

        role = clean_text(item.get("role")).lower()
        content = clean_text(item.get("content"))

        if role not in {"user", "assistant"}:
            continue

        if not content:
            continue

        result.append(
            {
                "role": role,
                "content": content[:12000],
            }
        )

    return result


def extract_response_text(response: Any) -> str:
    """Safely extract text from a Groq response."""

    try:
        text = response.choices[0].message.content
    except Exception:
        return ""

    return clean_text(text)


def detect_image_mime(
    filename: str = "",
    content_type: str = "",
) -> str:
    """Determine image MIME type."""

    content_type = clean_text(content_type).lower()

    allowed = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    if content_type in allowed:
        return content_type

    filename = clean_text(filename).lower()

    if filename.endswith(".png"):
        return "image/png"

    if filename.endswith(".webp"):
        return "image/webp"

    if filename.endswith(".gif"):
        return "image/gif"

    return "image/jpeg"


# =========================================================
# ELLA SERVICE
# =========================================================

class EllaService:

    def __init__(self) -> None:

        self.chat_model = CHAT_MODEL
        self.vision_model = VISION_MODEL
        self.stt_model = STT_MODEL

        # Do not use Optional[Groq] here.
        # Keeping this as Any avoids Pylance type-expression issues.
        self._client: Any = None

    # =====================================================
    # CLIENT
    # =====================================================

    @property
    def client(self) -> Any:

        if self._client is None:
            self._client = get_groq_client()

        return self._client

    # =====================================================
    # HEALTH CHECK
    # =====================================================

    def health(self) -> Dict[str, Any]:

        api_key_configured = bool(
            os.getenv("GROQ_API_KEY")
            or os.getenv("GROQ_API_TOKEN")
        )

        return {
            "service": "ELLA",
            "status": (
                "configured"
                if api_key_configured
                else "missing_api_key"
            ),
            "chat_model": self.chat_model,
            "vision_model": self.vision_model,
            "stt_model": self.stt_model,
        }

    # =====================================================
    # TEXT CHAT
    # =====================================================

    def chat(
        self,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        page: Optional[str] = None,
        role: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:

        user_message = clean_text(message)

        if not user_message:
            raise ValueError(
                "Message cannot be empty."
            )

        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": ELLA_SYSTEM_PROMPT,
            }
        ]

        # -------------------------------------------------
        # FORGE UI CONTEXT
        # -------------------------------------------------

        context: List[str] = []

        if page:
            context.append(
                f"Current FORGE page: {clean_text(page)}"
            )

        if role:
            context.append(
                f"Current student role: {clean_text(role)}"
            )

        if topic:
            context.append(
                f"Current topic: {clean_text(topic)}"
            )

        if context:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Current FORGE context:\n"
                        + "\n".join(context)
                    ),
                }
            )

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        messages.extend(
            normalize_history(history)
        )

        # -------------------------------------------------
        # CURRENT MESSAGE
        # -------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        try:

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=0.4,
                max_completion_tokens=2048,
                stream=False,
            )

            answer = extract_response_text(response)

            if not answer:
                raise RuntimeError(
                    "ELLA returned an empty response."
                )

            return {
                "success": True,
                "assistant": "ELLA",
                "message": answer,
                "model": self.chat_model,
            }

        except Exception as exc:

            raise RuntimeError(
                f"ELLA chat request failed: {exc}"
            ) from exc

    # =====================================================
    # IMAGE / VISION
    # =====================================================

    def analyze_image(
        self,
        image_bytes: bytes,
        filename: str = "image.jpg",
        content_type: str = "image/jpeg",
        prompt: str = "",
        history: Optional[List[Dict[str, Any]]] = None,
        page: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not image_bytes:
            raise ValueError(
                "Image is empty."
            )

        max_bytes = (
            MAX_IMAGE_MB * 1024 * 1024
        )

        if len(image_bytes) > max_bytes:
            raise ValueError(
                f"Image is too large. "
                f"Maximum size is {MAX_IMAGE_MB} MB."
            )

        mime = detect_image_mime(
            filename,
            content_type,
        )

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            f"data:{mime};base64,{encoded_image}"
        )

        user_prompt = clean_text(prompt)

        if not user_prompt:
            user_prompt = (
                "Analyze this image carefully. "
                "If it is a screenshot, explain what is visible, "
                "identify any relevant code or error, and provide "
                "the practical next step."
            )

        if page:
            user_prompt += (
                f"\n\nThis screenshot is from the "
                f"FORGE page: {clean_text(page)}."
            )

        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": ELLA_SYSTEM_PROMPT
                + """

You are also ELLA's visual analysis component.

When analyzing an image:
- Actually inspect the image before answering.
- Describe only what is visibly supported by the image.
- Do not invent hidden information.
- If it is a coding screenshot, read the visible code carefully and explain the code or exact error.
- If it is an error screenshot, identify the visible error, explain why it happens, and give the exact practical fix.
- If it is a diagram, explain the visible components and their relationships.
- If it is a question/exam screenshot, solve the visible question and explain the answer.
- If it is a table or chart, use the visible values and do not invent missing values.
- Prefer a clear student-friendly answer with headings, steps, and code when useful.
""",
            }
        ]

        messages.extend(
            normalize_history(history)[-6:]
        )

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        )

        try:

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                temperature=0.2,
                max_completion_tokens=2048,
                stream=False,
            )

            answer = extract_response_text(response)

            if not answer:
                raise RuntimeError(
                    "ELLA vision returned an empty response."
                )

            return {
                "success": True,
                "assistant": "ELLA",
                "message": answer,
                "model": self.vision_model,
                "filename": filename,
            }

        except Exception as exc:

            raise RuntimeError(
                f"ELLA vision request failed using model "
                f"{self.vision_model}: {exc}"
            ) from exc

    # =====================================================
    # SPEECH TO TEXT
    # =====================================================

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "recording.webm",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:

        if not audio_bytes:
            raise ValueError(
                "Audio is empty."
            )

        max_bytes = (
            MAX_AUDIO_MB * 1024 * 1024
        )

        if len(audio_bytes) > max_bytes:
            raise ValueError(
                f"Audio is too large. "
                f"Maximum size is {MAX_AUDIO_MB} MB."
            )

        request_data: Dict[str, Any] = {
            "file": (
                filename,
                audio_bytes,
            ),
            "model": self.stt_model,
            "response_format": "json",
            "temperature": 0.0,
        }

        if language:
            request_data["language"] = language

        try:

            transcription = (
                self.client.audio.transcriptions.create(
                    **request_data
                )
            )

            transcript = clean_text(
                getattr(
                    transcription,
                    "text",
                    "",
                )
            )

            return {
                "success": True,
                "assistant": "ELLA",
                "text": transcript,
                "model": self.stt_model,
            }

        except Exception as exc:

            raise RuntimeError(
                f"ELLA transcription failed: {exc}"
            ) from exc


# =========================================================
# SINGLE ELLA INSTANCE
# =========================================================

ella_service = EllaService()


__all__ = [
    "EllaService",
    "ella_service",
]