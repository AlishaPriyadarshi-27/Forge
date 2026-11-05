"""
FORGE Native Visual Learn — free browser-native lesson planner.

Uses the existing GEMINI_API_KEY on the backend only.
It does NOT generate a video file. It returns a structured lesson
that the React visual engine animates immediately in the browser.
"""

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/api/student/native-visual-lesson", tags=["native-visual-lesson"])


class LessonRequest(BaseModel):
    topic: str
    difficulty: str = "intermediate"


SYSTEM_PROMPT = """
You are FORGE Visual Learn's dynamic visual lesson designer.

Return ONLY valid JSON. No markdown.

The user can enter ANY technical or academic topic. You must create a
complete visual explanation for that topic.

CRITICAL ARCHITECTURE RULE:
The browser has NO knowledge of the topic.
There is NO topic-specific frontend code.
Do NOT assume Binary Search, K-Means, Backpropagation, Dijkstra, SQL, etc.
The only thing the browser can do is render a declarative scene description.

Therefore, YOU must design the actual visual diagram for every scene.

Each scene:
{
  "title": "...",
  "narration": "...",
  "duration": 6,
  "visuals": [...],
  "actions": [...]
}

A visual can be one of these GENERIC drawing primitives:

text:
{"id":"...", "type":"text", "x":50, "y":20, "text":"...", "size":18}

rect:
{"id":"...", "type":"rect", "x":20, "y":30, "width":20, "height":12,
 "label":"..."}

circle:
{"id":"...", "type":"circle", "x":40, "y":50, "radius":5,
 "label":"..."}

point:
{"id":"...", "type":"point", "x":40, "y":50, "label":"..."}

line:
{"id":"...", "type":"line", "x1":20, "y1":30, "x2":70, "y2":30,
 "label":"..."}

arrow:
{"id":"...", "type":"arrow", "x1":20, "y1":30, "x2":70, "y2":30,
 "label":"..."}

node:
{"id":"...", "type":"node", "x":40, "y":50, "label":"..."}

edge:
{"id":"...", "type":"edge", "from":"node1", "to":"node2",
 "label":"...", "weight":"..."}

array:
{"id":"...", "type":"array", "x":50, "y":60,
 "values":[...], "label":"..."}

table:
{"id":"...", "type":"table", "x":50, "y":50,
 "headers":[...], "rows":[...]}

formula:
{"id":"...", "type":"formula", "x":50, "y":70,
 "text":"..."}

group:
{"id":"...", "type":"group", "x":50, "y":50,
 "label":"..."}

IMPORTANT VISUAL QUALITY RULES:

1. Never make a scene visually empty.
2. Never use only generic labels like "Data A", "Step 3", "Formula",
   "Evaluation Table" when the concept can be shown with actual data.
3. Prefer actual numbers, variables, relationships, equations, arrows,
   diagrams, states, comparisons, paths, or transformations.
4. Every explanatory scene should have AT LEAST 4 meaningful visual objects
   unless the concept genuinely requires fewer.
5. Use positions intentionally so objects form a coherent diagram.
6. Use arrows/lines/edges to show relationships and direction.
7. Use actual example values whenever possible.
8. If explaining a mathematical/ML algorithm, show the actual computation,
   not merely the name of the computation.
9. If explaining a process, show the state BEFORE and AFTER the operation.
10. If explaining an algorithm, visually show the changing state between steps.
11. Narration must directly describe the visuals currently on screen.
12. Do not repeat the same visual layout for every scene.
13. Use a different arrangement when the concept changes.
14. The final scene should visually summarize the complete mechanism.

ACTIONS are generic and may reference visual IDs:
- create
- update
- move
- highlight
- fade
- connect
- disconnect
- path
- transform
- delete
- wait

Example of the QUALITY LEVEL expected for an ML clustering concept:
Do NOT output:
  Data A, Data B, Data C, Centroid Formula

Instead produce a real diagram such as:
- 8-15 actual 2D points
- two or more centroid circles
- distance/assignment indicators
- cluster boundaries or grouping cues
- centroid movement
- updated positions
- an actual mean equation
- arrows showing assignment/update

But do NOT hardcode K-Means logic into the frontend. The example above only
describes the level of visual detail expected; you must derive the actual
visual structure from the requested topic.

For any topic, infer the most useful visual representation yourself.

OVERVIEW QUALITY RULES:
- The overview MUST be about the exact requested topic.
- Do not use generic phrases such as "technical capability", "learning projects",
  "role-specific applications", or "connected evidence".
- "what_it_is" must define the actual concept in simple but technically correct language.
- "why_it_matters" must explain the actual value or purpose of that concept.
- "how_it_works" must contain actual mechanism steps, not generic study advice.
- "when_to_use" must contain real situations where the concept is used.
- Keep the overview consistent with the scenes and narration.

Create 6-8 scenes:
1. intuition / definition
2. setup
3. core mechanism
4. step-by-step operation
5. worked example
6. important detail / edge case / limitation
7. recap

The lesson should feel like a complete educational animation, not a collection
of title cards.

Return exactly:
{
  "title": "...",
  "topic_type": "dynamic",
  "duration": 45,
  "overview": {
    "what_it_is": "A precise 2-3 sentence explanation of the requested topic.",
    "why_it_matters": "A precise 1-2 sentence explanation of why this concept matters.",
    "how_it_works": ["Concrete step 1", "Concrete step 2", "Concrete step 3", "Concrete step 4"],
    "when_to_use": ["Concrete use case 1", "Concrete use case 2"]
  },
  "scenes": [...]
}

Topic: {topic}
Difficulty: {difficulty}
"""



def _extract_json(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Gemini did not return a JSON object.")
    return json.loads(text[start:end + 1])


@router.post("")
def create_native_visual_lesson(req: LessonRequest):
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic is required.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured.")

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        prompt = SYSTEM_PROMPT.replace("{topic}", topic).replace("{difficulty}", req.difficulty)

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )
        lesson = _extract_json(response.text)

        if not isinstance(lesson.get("scenes"), list) or not lesson["scenes"]:
            raise ValueError("Lesson contains no scenes.")

        lesson["topic"] = topic
        return {"ok": True, "lesson": lesson}

    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini lesson planning failed: {exc}")
