"""FORGE semantic visual planner.

No topic-specific animation branches live here.
The model receives Topic Intelligence and chooses the visual grammar
that best represents the actual mechanism. A data-driven fallback is
used only when the model is unavailable.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from .animation_schema import validate_lesson_dict

DEFAULT_MODEL = os.getenv("FORGE_VISUAL_MODEL", "llama-3.3-70b-versatile")


def _context(data: Dict[str, Any]) -> str:
    # Keep the request comfortably below the provider TPM limit.
    preferred = (
        "topic", "name", "definition", "overview", "how_it_works",
        "core_concepts", "use_cases", "learning_path", "examples",
        "common_mistakes", "difficulty"
    )
    out = {}
    for key in preferred:
        value = data.get(key)
        if value not in (None, "", [], {}):
            out[key] = value
    raw = json.dumps(out, ensure_ascii=False)
    return raw[:6500]


def _narration(text: str) -> Dict[str, Any]:
    return {
        "text": str(text or ""),
        "start_after": 0,
        "duration": None,
        "voice": None,
        "language": "en",
    }


def _scene(i: int, title: str, purpose: str, elements: List[Dict[str, Any]],
           narration: str, duration: int = 6) -> Dict[str, Any]:
    return {
        "id": f"scene_{i:02d}",
        "title": title,
        "purpose": purpose,
        "elements": elements,
        "actions": [
            {
                "action": "create",
                "target": str(e.get("id", "")),
                "value": None,
                "duration": 0.6,
                "easing": "smooth",
                "metadata": {},
            }
            for e in elements if e.get("id")
        ],
        "narration": _narration(narration),
        "duration": duration,
        "camera": {},
        "metadata": {},
    }


def _fallback(topic: str, data: Dict[str, Any], language: str, difficulty: str) -> Dict[str, Any]:
    """Data-driven fallback. It never names or branches on a specific topic."""
    concepts = data.get("core_concepts") or data.get("how_it_works") or data.get("learning_path") or []
    if isinstance(concepts, str):
        concepts = [concepts]
    concepts = [str(x) for x in concepts if str(x).strip()][:8]
    if not concepts:
        concepts = [str(data.get("definition") or data.get("overview") or f"Mechanism of {topic}")]

    scenes = []
    for i, concept in enumerate(concepts[:4], 1):
        left = concepts[i - 2] if i > 1 else "Input / context"
        right = concept
        elements = [
            {"id": "source", "type": "box", "x": 23, "y": 48, "width": 25, "height": 14,
             "label": left[:28], "tone": "input"},
            {"id": "target", "type": "box", "x": 77, "y": 48, "width": 29, "height": 14,
             "label": right[:30], "tone": "output"},
            {"id": "flow", "type": "token", "x": 50, "y": 48,
             "text": "→", "motion": "travel"},
            {"id": "caption", "type": "text", "x": 50, "y": 78,
             "text": concept[:55], "emphasis": True},
            {"id": "edge", "type": "arrow", "from": "source", "to": "target",
             "label": "process"},
        ]
        scenes.append(_scene(
            i,
            f"Mechanism {i}: {concept[:45]}",
            f"How {concept} participates in {topic}.",
            elements,
            f"This step focuses on {concept}. The moving signal represents how information or state changes through the mechanism."
        ))

    while len(scenes) < 4:
        i = len(scenes) + 1
        scenes.append(_scene(
            i,
            f"Mechanism {i}",
            f"Connect the previous step to the next consequence in {topic}.",
            [
                {"id": "a", "type": "box", "x": 25, "y": 48, "width": 25, "height": 14,
                 "label": concepts[min(i-2, len(concepts)-1)][:28], "tone": "input"},
                {"id": "b", "type": "box", "x": 75, "y": 48, "width": 25, "height": 14,
                 "label": concepts[min(i-1, len(concepts)-1)][:28], "tone": "output"},
                {"id": "e", "type": "arrow", "from": "a", "to": "b", "label": "causes / transforms"},
                {"id": "p", "type": "token", "x": 50, "y": 48, "text": "data", "motion": "travel"},
            ],
            f"Follow the relationship between the two displayed concepts."
        ))

    return {
        "topic": topic,
        "title": f"{topic} · Interactive Visual Lesson",
        "learning_objective": f"Understand the mechanism of {topic} by following its evidence-backed concepts and relationships.",
        "difficulty": difficulty,
        "language": language,
        "estimated_duration": 24,
        "scenes": scenes[:4],
        "metadata": {"planner": "forge_semantic_visual_planner", "mode": "data_fallback"},
    }


def _clean_json(raw: str) -> str:
    raw = str(raw or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
        raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start >= 0 and end > start:
        return raw[start:end + 1]
    return raw


def _normalize(lesson: Dict[str, Any], topic: str, language: str, difficulty: str) -> Dict[str, Any]:
    if not isinstance(lesson, dict):
        raise ValueError("Planner did not return a JSON object.")

    lesson["topic"] = str(lesson.get("topic") or topic)
    lesson["title"] = str(lesson.get("title") or f"{topic} · Interactive Visual Lesson")
    lesson["learning_objective"] = str(
        lesson.get("learning_objective") or f"Understand how {topic} works."
    )
    lesson["difficulty"] = difficulty
    lesson["language"] = language
    lesson["estimated_duration"] = 64
    lesson.setdefault("metadata", {})

    scenes = lesson.get("scenes")
    if not isinstance(scenes, list):
        scenes = []
    normalized = []

    for i, scene in enumerate(scenes[:6], 1):
        if not isinstance(scene, dict):
            continue

        elements = scene.get("elements")
        if not isinstance(elements, list):
            elements = []

        clean_elements = []
        seen = set()
        for j, e in enumerate(elements[:10]):
            if not isinstance(e, dict):
                continue
            e = dict(e)
            eid = str(e.get("id") or f"e_{i}_{j}")
            if eid in seen:
                eid = f"{eid}_{j}"
            seen.add(eid)
            e["id"] = eid
            e["type"] = str(e.get("type") or "box").lower()
            # Accept either {x,y} or {position:{x,y}} from the model.
            if isinstance(e.get("position"), dict):
                px = e["position"].get("x", e.get("x", 50))
                py = e["position"].get("y", e.get("y", 50))
            else:
                px = e.get("x", 50)
                py = e.get("y", 50)
            try:
                px = max(8, min(92, float(px)))
            except Exception:
                px = 50.0
            try:
                py = max(10, min(82, float(py)))
            except Exception:
                py = 50.0
            e["position"] = {"x": px, "y": py}
            e["x"] = px
            e["y"] = py
            clean_elements.append(e)

        actions = []
        raw_actions = scene.get("actions")
        if isinstance(raw_actions, list):
            for a in raw_actions[:8]:
                if isinstance(a, str) and a.strip():
                    actions.append({"action": a.strip(), "target": "", "value": None,
                                    "duration": 0.6, "easing": "smooth", "metadata": {}})
                elif isinstance(a, dict):
                    name = str(a.get("action") or "").strip()
                    if name:
                        actions.append({
                            "action": name,
                            "target": str(a.get("target") or ""),
                            "value": a.get("value"),
                            "duration": float(a.get("duration") or 0.6),
                            "easing": str(a.get("easing") or "smooth"),
                            "metadata": a.get("metadata") if isinstance(a.get("metadata"), dict) else {},
                        })
        if not actions:
            actions = [
                {"action": "create", "target": e["id"], "value": None,
                 "duration": 0.6, "easing": "smooth", "metadata": {}}
                for e in clean_elements
            ]

        narration = scene.get("narration")
        if isinstance(narration, str):
            narration = _narration(narration)
        elif not isinstance(narration, dict):
            narration = _narration(str(scene.get("purpose") or scene.get("title") or ""))

        normalized.append({
            "id": str(scene.get("id") or f"scene_{i:02d}"),
            "title": str(scene.get("title") or f"Step {i}"),
            "purpose": str(scene.get("purpose") or scene.get("title") or f"Step {i}"),
            "elements": clean_elements,
            "actions": actions,
            "narration": narration,
            # Four scenes x 15.5s guarantees a >= 60s learning video.
            "duration": 15.5,
            "camera": scene.get("camera") if isinstance(scene.get("camera"), dict) else {},
            "metadata": scene.get("metadata") if isinstance(scene.get("metadata"), dict) else {},
        })

    lesson["scenes"] = normalized
    return lesson


class AnimationPlanner:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

    def create_lesson(self, topic_data: Dict[str, Any], language: str = "en",
                      difficulty: str = "intermediate") -> Dict[str, Any]:
        if not isinstance(topic_data, dict):
            raise ValueError("topic_data must be a dictionary")

        topic = str(topic_data.get("topic") or topic_data.get("name") or "Technical Topic").strip()

        # No topic-name branches. The model chooses the visual grammar from evidence.
        if self.client is None:
            return _fallback(topic, topic_data, language, difficulty)

        system = """You are FORGE's semantic visual director.

Create an educational animation storyboard from Topic Intelligence.
DO NOT use topic-specific templates or hardcoded topic branches.
Instead, infer the mechanism and choose the visual grammar that best
represents it.

Examples of visual grammar choices (not templates):
- ordered/search problems may use arrays, ranges and pointers
- graph/route problems may use nodes, edges and moving markers
- protocols may use client/server lanes and message packets
- trees may use hierarchical nodes and edges
- numerical/ML mechanisms may use equations, vectors, layers and flowing gradients
- database mechanisms may use tables, rows, keys and joins
- UI/state mechanisms may use component/state/effect flow
Choose what is actually appropriate for the supplied concept.

QUALITY RULES:
- Teach the mechanism, not the vocabulary.
- 4 scenes exactly.
- Every scene must show a meaningful change or relationship.
- Use 3-8 visual elements per scene.
- Use distinct coordinates; no overlapping primary objects.
- Use short labels.
- Use arrows for causal/data relationships.
- Use token motion for something that actually travels.
- Use highlight/circle/pointer for the thing being examined.
- Use arrays/tables/equations/graphs when they are semantically appropriate.
- Narration must explain the visible action.
- Do not invent facts beyond Topic Intelligence.
- Do not use filler scenes named 'core idea', 'apply', 'practice' unless the supplied concept genuinely requires those stages.

Allowed element types:
box,node,array,pointer,token,text,equation,arrow,circle,highlight,table,layer,packet,client,server,matrix,code

For array: provide values and optional activeIndexes/highlightIndexes.
For pointer: provide label and x/y.
For arrow: provide from/to ids and optional label/reverse.
For token: provide text and motion='travel' when it should move.
For table: provide headers and rows.
For equation: provide text.
For layer: provide label and optional sublabel.

VISUAL QUALITY CONTRACT:
- Choose a visual grammar from the mechanism itself, not from a fixed page layout.
- At least 3 of the 4 scenes must visibly change state, position, membership, value, connection, or flow.
- Prefer arrays for ordered search/sorting, nodes/edges for graphs or linked structures, client/server/packet for network protocols, layers for layered systems, tables for relational data, matrix for matrix operations, code for syntax/execution, and boxes only when a component/state truly is a box.
- Use arrows to show real relationships and tokens/packets to show actual movement.
- Do not create a central generic box called Core mechanism, Interaction, Process, Input, Output, Architecture, or State change unless that exact object is part of the topic.
- Do not use decorative labels as the primary teaching content.
- The narration must describe the exact state transition visible in the current scene.
- Scene titles must name the actual mechanism/event being demonstrated.
- Use 4 scenes with 4-10 meaningful elements each.

Return ONLY a valid JSON object. No markdown.
"""

        user = f"""TOPIC INTELLIGENCE:
{_context(topic_data)}

Create the four-scene storyboard for: {topic}

The four scenes should form one causal teaching story:
1) establish the concrete state/problem,
2) show the key operation,
3) show the transformation/decision/flow,
4) show the resulting state and why it matters.

Do not copy this wording into titles; adapt the stages to the actual mechanism.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.15,
                max_completion_tokens=4500,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            raw = _clean_json(response.choices[0].message.content or "")
            lesson = _normalize(json.loads(raw), topic, language, difficulty)
            errors = validate_lesson_dict(lesson)
            if errors:
                raise ValueError("Invalid animation lesson: " + "; ".join(errors))
            lesson["metadata"].update({
                "planner": "forge_semantic_visual_planner",
                "mode": "llm",
                "visual_grammar": "model-selected",
            })
            return lesson
        except Exception as exc:
            # Do NOT manufacture a generic storyboard. A fake visual is worse than an explicit error.
            raise RuntimeError(f"Semantic visual generation failed: {exc}") from exc
