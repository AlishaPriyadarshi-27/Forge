from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from groq import Groq


class TopicIntelligenceGenerationError(RuntimeError):
    pass


def _load_environment() -> None:
    current = Path(__file__).resolve()
    project_root = current.parents[3]
    backend_root = current.parents[2]
    for path in (project_root / ".env", backend_root / ".env", Path.cwd() / ".env"):
        if path.exists() and path.is_file():
            load_dotenv(path, override=False)


_load_environment()


class TopicIntelligenceGenerator:
    """Generate topic-learning content; never generate market facts or URLs."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_TOKEN")
        if not self.api_key:
            raise TopicIntelligenceGenerationError("GROQ_API_KEY is not configured.")
        self.model = model or os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"
        self.client = Groq(api_key=self.api_key)

    def generate(self, *, topic: str, role: str, market_evidence: Dict[str, Any],
                 onet_evidence: Dict[str, Any], future_evidence: Dict[str, Any],
                 related_topics: list[str]) -> Dict[str, Any]:
        prompt = self._prompt(topic, role, market_evidence, onet_evidence, future_evidence, related_topics)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.25,
                max_tokens=6500,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self._system()},
                    {"role": "user", "content": prompt},
                ],
            )
        except Exception as exc:
            raise TopicIntelligenceGenerationError(f"Topic generation failed: {exc}") from exc
        raw = response.choices[0].message.content
        if not raw:
            raise TopicIntelligenceGenerationError("Topic generator returned an empty response.")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TopicIntelligenceGenerationError("Topic generator returned invalid JSON.") from exc
        return self._normalize(data, topic)

    @staticmethod
    def _system() -> str:
        return """You are FORGE Topic Intelligence, a technical learning-content generator.

Your job is to create deep, accurate, topic-specific educational content for any technology, skill,
method, framework, platform, or capability. The frontend has a fixed schema, but the content must be
specific to the supplied topic. Never write topic-specific application code or assume a hard-coded topic list.

CRITICAL EVIDENCE RULES:
1. Market numbers, prevalence, posting counts, dates, O*NET records and future-source facts are supplied by FORGE.
2. Never invent, modify, round, reinterpret, or forecast those evidence values.
3. Do not claim WEF/BLS/O*NET says something unless it appears in the supplied evidence.
4. Technical explanations may use your general technical knowledge, but do not invent citations or URLs.
5. Do not output resource URLs. Verified resources are supplied separately by FORGE.
6. If a comparison is not genuinely meaningful, return an empty comparisons array.
7. If a section is not applicable, return an empty array/object and explain why in section_status.
8. Keep the content useful to a 3rd-year CSE/AI-ML student: concrete, technical, implementation-aware, and not marketing copy.

Return ONLY valid JSON."""

    @staticmethod
    def _prompt(topic: str, role: str, market: Dict[str, Any], onet: Dict[str, Any],
                future: Dict[str, Any], related: list[str]) -> str:
        schema = {
            "topic_category": "string",
            "difficulty": "Beginner|Intermediate|Advanced",
            "overview": {
                "definition": "string",
                "why_it_exists": "string",
                "when_to_use": ["string"],
                "when_not_to_use": ["string"],
                "why_it_matters": "string"
            },
            "related_capabilities": ["string"],
            "how_it_works": {
                "summary": "string",
                "steps": [{"title": "string", "description": "string"}],
                "architecture": {"nodes": [{"id": "string", "label": "string", "layer": "string"}], "edges": [{"from": "string", "to": "string", "label": "string"}]}
            },
            "key_concepts": [{"title": "string", "description": "string", "importance": "string"}],
            "comparison": {"available": True, "title": "string", "columns": ["string"], "rows": [{"dimension": "string", "values": ["string"]}]},
            "prerequisites": {"required": ["string"], "recommended": ["string"]},
            "learning_path": [{"stage": "string", "focus": "string", "outcome": "string", "prerequisites": ["string"]}],
            "use_cases": [{"title": "string", "description": "string"}],
            "common_mistakes": [{"mistake": "string", "why": "string", "fix": "string"}],
            "project": {"title": "string", "brief": "string", "dataset": "string", "stages": ["string"], "evaluation": ["string"], "expected_output": "string"},
            "assessment": {"questions": [{"type": "conceptual|implementation|debugging|scenario", "question": "string", "options": ["string"], "answer_index": 0, "explanation": "string"}]},
            "section_status": {"comparison": "available|not_applicable", "architecture": "available|not_applicable"}
        }
        return f"""Generate Topic Intelligence for:

TOPIC: {topic}
TARGET ROLE: {role}
RELATED TOPICS FROM FORGE: {json.dumps(related, ensure_ascii=False)}

MARKET EVIDENCE (DO NOT CHANGE):
{json.dumps(market, ensure_ascii=False, indent=2)}

O*NET EVIDENCE (DO NOT CHANGE):
{json.dumps(onet, ensure_ascii=False, indent=2)}

FUTURE CONTEXT (DO NOT CHANGE):
{json.dumps(future, ensure_ascii=False, indent=2)}

Required JSON shape:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Content requirements:
- Overview must answer what it is, why it exists, when to use and when not to use.
- How it works must describe a real end-to-end flow and provide renderable architecture nodes/edges.
- Core concepts should be 6–12 concepts appropriate to this exact topic.
- Comparison should be technical and meaningful; do not force one.
- Learning path should progress from foundation to production where appropriate.
- Project must be concrete enough to implement and evaluate.
- Assessment must contain 5 questions spanning conceptual, implementation, debugging and scenario reasoning. Use exactly 4 options per question.
- Keep answer_index zero-based and correct.
"""

    @staticmethod
    def _normalize(data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        def arr(v): return v if isinstance(v, list) else []
        data["topic"] = topic
        data["related_capabilities"] = arr(data.get("related_capabilities"))
        data["key_concepts"] = arr(data.get("key_concepts"))
        data["learning_path"] = arr(data.get("learning_path"))
        data["use_cases"] = arr(data.get("use_cases"))
        data["common_mistakes"] = arr(data.get("common_mistakes"))
        overview = data.get("overview") if isinstance(data.get("overview"), dict) else {}
        overview["when_to_use"] = arr(overview.get("when_to_use"))
        overview["when_not_to_use"] = arr(overview.get("when_not_to_use"))
        data["overview"] = overview
        how = data.get("how_it_works") if isinstance(data.get("how_it_works"), dict) else {}
        how["steps"] = arr(how.get("steps"))
        arch = how.get("architecture") if isinstance(how.get("architecture"), dict) else {}
        arch["nodes"] = arr(arch.get("nodes")); arch["edges"] = arr(arch.get("edges"))
        how["architecture"] = arch; data["how_it_works"] = how
        pre = data.get("prerequisites") if isinstance(data.get("prerequisites"), dict) else {}
        pre["required"] = arr(pre.get("required")); pre["recommended"] = arr(pre.get("recommended")); data["prerequisites"] = pre
        comp = data.get("comparison") if isinstance(data.get("comparison"), dict) else {"available": False}
        comp["columns"] = arr(comp.get("columns")); comp["rows"] = arr(comp.get("rows")); data["comparison"] = comp
        proj = data.get("project") if isinstance(data.get("project"), dict) else {}
        proj["stages"] = arr(proj.get("stages")); proj["evaluation"] = arr(proj.get("evaluation")); data["project"] = proj
        assessment = data.get("assessment") if isinstance(data.get("assessment"), dict) else {}
        qs = arr(assessment.get("questions"))[:5]
        normalized_qs = []
        for q in qs:
            if not isinstance(q, dict): continue
            q["options"] = arr(q.get("options"))[:4]
            try: q["answer_index"] = int(q.get("answer_index", 0))
            except Exception: q["answer_index"] = 0
            if q["answer_index"] < 0 or q["answer_index"] >= len(q["options"]): q["answer_index"] = 0
            normalized_qs.append(q)
        assessment["questions"] = normalized_qs; data["assessment"] = assessment
        status = data.get("section_status") if isinstance(data.get("section_status"), dict) else {}
        status.setdefault("comparison", "available" if comp.get("available") else "not_applicable")
        status.setdefault("architecture", "available" if arch["nodes"] else "not_applicable")
        data["section_status"] = status
        return data
