from typing import Any, Dict, Optional, List
import json
import os
import re


class IntelligenceService:
    """
    FORGE Intelligence Service

    Connects the four core FORGE intelligence layers:

        WORKTRACE
            ↓
        SKILL SHADOW
            ↓
        WORKFOLD
            ↓
        LATTICE

    This service is an orchestration layer.
    It does not invent ML results.
    It combines outputs from the existing engines.
    """

    def __init__(
        self,
        worktrace_engine=None,
        skill_shadow_engine=None,
        workfold_engine=None,
        lattice_engine=None,
        evidence_service=None,
        topic_generator=None
    ):
        self.worktrace = worktrace_engine
        self.skill_shadow = skill_shadow_engine
        self.workfold = workfold_engine
        self.lattice = lattice_engine
        self.evidence = evidence_service

        # Optional Topic Intelligence generator.
        #
        # It can be injected from main.py, but the service also contains
        # a safe built-in Groq adapter so existing callers do not break.
        self.topic_generator = topic_generator

    # =========================================================
    # ENGINE STATUS
    # =========================================================

    def engine_status(self) -> Dict[str, bool]:

        return {
            "worktrace": self.worktrace is not None,
            "skill_shadow": self.skill_shadow is not None,
            "workfold": self.workfold is not None,
            "lattice": self.lattice is not None,
            "evidence": self.evidence is not None,
            "topic_generator": self.topic_generator is not None
        }

    # =========================================================
    # SAFE ENGINE CALL
    # =========================================================

    def _call(
        self,
        engine,
        method: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:

        if engine is None:

            return {
                "status": "unavailable",
                "error": "Engine is not loaded."
            }

        if not hasattr(engine, method):

            return {
                "status": "unavailable",
                "error": (
                    f"Method '{method}' "
                    "does not exist in this engine."
                )
            }

        try:

            result = getattr(engine, method)(
                *args,
                **kwargs
            )

            return {
                "status": "success",
                "data": result
            }

        except Exception as exc:

            return {
                "status": "error",
                "error": str(exc)
            }

    # =========================================================
    # EXTRACT DATA
    # =========================================================

    @staticmethod
    def _data(result):

        if isinstance(result, dict):

            if result.get("status") == "success":

                return result.get("data")

        return result

    # =========================================================
    # OCCUPATION INTELLIGENCE
    # =========================================================

    def get_occupation_intelligence(
        self,
        occupation: str
    ) -> Dict[str, Any]:

        occupation = occupation.strip()

        if not occupation:

            return {
                "status": "error",
                "error": "Occupation is required."
            }

        # -----------------------------------------------------
        # WORKTRACE
        # -----------------------------------------------------

        worktrace = self._call(
            self.worktrace,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # SKILL SHADOW
        # -----------------------------------------------------

        skill_shadow = self._call(
            self.skill_shadow,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # WORKFOLD
        # -----------------------------------------------------

        workfold = self._call(
            self.workfold,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # LATTICE
        # -----------------------------------------------------

        lattice = self._call(
            self.lattice,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {

            "status": "success",

            "project": "FORGE",

            "occupation": occupation,

            "pipeline": [
                "WORKTRACE",
                "SKILL SHADOW",
                "WORKFOLD",
                "LATTICE"
            ],

            "modules": {

                "worktrace": self._data(
                    worktrace
                ),

                "skill_shadow": self._data(
                    skill_shadow
                ),

                "workfold": self._data(
                    workfold
                ),

                "lattice": self._data(
                    lattice
                )
            },

            "engine_status": self.engine_status()
        }

    # =========================================================
    # FUTURE WORKFORCE SCENARIO
    # =========================================================

    def simulate_future_workforce(
        self,
        occupation: str,
        baseline_ai: float = 0.0,
        future_ai: float = 0.5
    ) -> Dict[str, Any]:

        occupation = occupation.strip()

        if not occupation:

            return {
                "status": "error",
                "error": "Occupation is required."
            }

        # -----------------------------------------------------
        # Keep values inside 0–1
        # -----------------------------------------------------

        baseline_ai = max(
            0.0,
            min(1.0, float(baseline_ai))
        )

        future_ai = max(
            0.0,
            min(1.0, float(future_ai))
        )

        # -----------------------------------------------------
        # SKILL SHADOW SCENARIO
        # -----------------------------------------------------

        skill_shadow = self._call(
            self.skill_shadow,
            "compare_scenarios",
            occupation=occupation,
            baseline_ai=baseline_ai,
            future_ai=future_ai
        )

        # -----------------------------------------------------
        # WORKFOLD SCENARIO
        # -----------------------------------------------------

        workfold = self._call(
            self.workfold,
            "compare_scenarios",
            occupation=occupation,
            baseline_ai=baseline_ai,
            future_ai=future_ai
        )

        # -----------------------------------------------------
        # LATTICE
        # -----------------------------------------------------

        lattice = self._call(
            self.lattice,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # WORKTRACE
        # -----------------------------------------------------

        worktrace = self._call(
            self.worktrace,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # AI DELTA
        # -----------------------------------------------------

        ai_delta = future_ai - baseline_ai

        if ai_delta > 0:

            direction = "increased_ai_adoption"

        elif ai_delta < 0:

            direction = "reduced_ai_adoption"

        else:

            direction = "unchanged_ai_adoption"

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {

            "status": "success",

            "project": "FORGE",

            "occupation": occupation,

            "scenario": {

                "baseline_ai": baseline_ai,

                "baseline_ai_percent": round(
                    baseline_ai * 100,
                    2
                ),

                "requested_future_ai": future_ai,

                "requested_future_ai_percent": round(
                    future_ai * 100,
                    2
                ),

                "ai_change": ai_delta,

                "ai_change_percentage_points": round(
                    ai_delta * 100,
                    2
                ),

                "direction": direction
            },

            "modules": {

                "worktrace": self._data(
                    worktrace
                ),

                "skill_shadow": self._data(
                    skill_shadow
                ),

                "workfold": self._data(
                    workfold
                ),

                "lattice": self._data(
                    lattice
                )
            },

            "pipeline": {

                "WORKTRACE": {
                    "role": "Observe",
                    "description": (
                        "Map actual work into tasks "
                        "and capabilities."
                    )
                },

                "SKILL_SHADOW": {
                    "role": "Detect",
                    "description": (
                        "Measure capability exposure "
                        "loss under automation."
                    )
                },

                "WORKFOLD": {
                    "role": "Reconfigure",
                    "description": (
                        "Allocate work between AI, "
                        "human and hybrid modes."
                    )
                },

                "LATTICE": {
                    "role": "Rebuild",
                    "description": (
                        "Preserve capabilities through "
                        "targeted practice."
                    )
                }
            },

            "engine_status": self.engine_status()
        }

    # =========================================================
    # WORKFORCE REDESIGN
    # =========================================================

    def workforce_redesign(
        self,
        occupation: str,
        requested_ai: float = 0.5
    ) -> Dict[str, Any]:

        occupation = occupation.strip()

        if not occupation:

            return {
                "status": "error",
                "error": "Occupation is required."
            }

        requested_ai = max(
            0.0,
            min(1.0, float(requested_ai))
        )

        # -----------------------------------------------------
        # WORKFOLD
        # -----------------------------------------------------

        # IMPORTANT:
        # WorkFoldEngine.simulate_occupation()
        # expects the parameter name "ai_adoption",
        # not "requested_ai".

        workfold = self._call(
            self.workfold,
            "simulate_occupation",
            occupation=occupation,
            ai_adoption=requested_ai
        )

        # -----------------------------------------------------
        # SKILL SHADOW
        # -----------------------------------------------------

        skill_shadow = self._call(
            self.skill_shadow,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # LATTICE
        # -----------------------------------------------------

        lattice = self._call(
            self.lattice,
            "get_occupation",
            occupation
        )

        # -----------------------------------------------------
        # RESPONSE
        # -----------------------------------------------------

        return {

            "status": "success",

            "project": "FORGE",

            "occupation": occupation,

            "requested_ai_adoption": requested_ai,

            "requested_ai_adoption_percent": round(
                requested_ai * 100,
                2
            ),

            "workfold": self._data(
                workfold
            ),

            "skill_shadow": self._data(
                skill_shadow
            ),

            "lattice": self._data(
                lattice
            ),

            "decision_logic": {

                "step_1": "Check AI adoption request",

                "step_2": (
                    "Apply WORKFOLD safe operating boundary"
                ),

                "step_3": (
                    "Measure capability exposure "
                    "using SKILL SHADOW"
                ),

                "step_4": (
                    "Identify capability preservation "
                    "requirements using LATTICE"
                )
            }
        }

    # =========================================================
    # CAPABILITY PRESERVATION
    # =========================================================

    def capability_preservation(
        self,
        occupation: str,
        capability: str
    ) -> Dict[str, Any]:

        occupation = occupation.strip()
        capability = capability.strip()

        if not occupation:

            return {
                "status": "error",
                "error": "Occupation is required."
            }

        if not capability:

            return {
                "status": "error",
                "error": "Capability is required."
            }

        # -----------------------------------------------------
        # LATTICE PRACTICE PLAN
        # -----------------------------------------------------

        practice_plan = self._call(
            self.lattice,
            "build_practice_plan",
            occupation=occupation,
            capability=capability
        )

        # -----------------------------------------------------
        # CAPABILITY INFORMATION
        # -----------------------------------------------------

        capability_data = self._call(
            self.lattice,
            "get_capability",
            occupation,
            capability
        )

        return {

            "status": "success",

            "project": "FORGE",

            "occupation": occupation,

            "target_capability": capability,

            "lattice": {

                "practice_plan": self._data(
                    practice_plan
                ),

                "capability_data": self._data(
                    capability_data
                )
            },

            "goal": (
                "Automate the work while preserving "
                "the human capability needed for future work."
            )
        }

    # =========================================================
    # LEARNER CAPABILITY EVIDENCE
    # =========================================================

    def capability_evidence(
        self,
        occupation: str,
        capability: str
    ) -> Dict[str, Any]:
        """Return actual learner evidence without inventing a score."""

        if self.evidence is None:
            return {
                "status": "unavailable",
                "error": "Evidence service is not loaded."
            }

        return self.evidence.get_capability_state(
            occupation=occupation.strip(),
            capability=capability.strip()
        )

    # =========================================================
    # TOPIC INTELLIGENCE
    # =========================================================
    #
    # This layer is intentionally generic.
    #
    # It must work for:
    #   RAG, React, TypeScript, Python, SQL, Kubernetes, etc.
    #
    # There are NO topic-specific branches here.
    #
    # Market facts must come from the supplied evidence context.
    # The LLM is used only to synthesize technical/learning content
    # around that evidence. It must never invent market numbers,
    # employer counts, prevalence, sample sizes, or URLs.
    # =========================================================

    @staticmethod
    def _clean_topic(topic: str) -> str:
        """Normalize whitespace without imposing topic-specific logic."""
        return re.sub(r"\s+", " ", str(topic or "")).strip()

    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Make arbitrary engine/evidence output JSON serializable."""
        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, dict):
            return {
                str(k): IntelligenceService._json_safe(v)
                for k, v in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                IntelligenceService._json_safe(v)
                for v in value
            ]

        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)

    def _collect_topic_evidence(
        self,
        topic: str,
        role: Optional[str] = None,
        horizon: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ask the existing evidence service for topic evidence.

        The method is deliberately adapter-like because FORGE has had
        different evidence-service implementations. It checks common
        method names and returns the first successful result.

        No evidence is manufactured when the evidence service cannot
        answer the request.
        """
        if self.evidence is None:
            return {
                "status": "unavailable",
                "error": "Evidence service is not loaded.",
                "sources": []
            }

        candidate_methods = (
            "get_topic_evidence",
            "get_topic_intelligence_evidence",
            "search_topic",
            "get_topic",
        )

        attempts: List[Dict[str, Any]] = []

        for method in candidate_methods:
            if not hasattr(self.evidence, method):
                continue

            fn = getattr(self.evidence, method)

            call_variants = [
                {
                    "topic": topic,
                    "role": role,
                    "horizon": horizon,
                },
                {
                    "topic": topic,
                    "role": role,
                },
                {
                    "topic": topic,
                },
            ]

            for kwargs in call_variants:
                # Remove optional None values so older implementations
                # with narrower signatures can still work.
                clean_kwargs = {
                    k: v for k, v in kwargs.items()
                    if v is not None
                }

                try:
                    result = fn(**clean_kwargs)

                    if isinstance(result, dict):
                        status = result.get("status")
                        if status in (None, "success", "available"):
                            return {
                                "status": "available",
                                "source_method": method,
                                "data": self._json_safe(
                                    result.get("data", result)
                                ),
                                "sources": self._json_safe(
                                    result.get("sources", [])
                                )
                            }

                    if result is not None:
                        return {
                            "status": "available",
                            "source_method": method,
                            "data": self._json_safe(result),
                            "sources": []
                        }

                except TypeError as exc:
                    # Signature mismatch: try the next compatible call.
                    attempts.append({
                        "method": method,
                        "error": str(exc)
                    })
                    continue

                except Exception as exc:
                    attempts.append({
                        "method": method,
                        "error": str(exc)
                    })
                    break

        return {
            "status": "insufficient_verified_evidence",
            "error": (
                "The evidence service does not expose a supported "
                "topic-evidence method, or no verified evidence was "
                "returned."
            ),
            "sources": [],
            "attempts": attempts
        }

    @staticmethod
    def _extract_verified_source_urls(evidence: Any) -> List[str]:
        """
        Extract URLs only when they are already present in evidence.

        This function NEVER constructs a URL from a topic name.
        """
        urls: List[str] = []

        def walk(value: Any):
            if isinstance(value, dict):
                for key, item in value.items():
                    key_lower = str(key).lower()
                    if (
                        "url" in key_lower
                        or key_lower in {
                            "href",
                            "link",
                            "source_url",
                            "documentation_url",
                        }
                    ):
                        if isinstance(item, str):
                            candidate = item.strip()
                            if (
                                candidate.startswith("https://")
                                or candidate.startswith("http://")
                            ):
                                urls.append(candidate)

                    walk(item)

            elif isinstance(value, (list, tuple)):
                for item in value:
                    walk(item)

        walk(evidence)

        # Stable de-duplication.
        return list(dict.fromkeys(urls))

    @staticmethod
    def _market_evidence_contract(evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preserve market evidence as evidence, not as LLM-generated claims.
        """
        if not evidence:
            return {
                "status": "insufficient_verified_evidence",
                "data": None,
                "sources": []
            }

        status = evidence.get("status")

        if status not in {"available", "success"}:
            return {
                "status": status or "insufficient_verified_evidence",
                "data": None,
                "sources": evidence.get("sources", [])
            }

        return {
            "status": "available",
            "data": evidence.get("data"),
            "sources": evidence.get("sources", [])
        }

    def _build_topic_prompt(
        self,
        topic: str,
        role: Optional[str],
        horizon: Optional[str],
        evidence: Dict[str, Any]
    ) -> str:
        """
        Build the strict synthesis prompt for the dynamic Topic Engine.
        """
        evidence_json = json.dumps(
            self._json_safe(evidence),
            ensure_ascii=False,
            indent=2
        )

        role_text = role or "not specified"
        horizon_text = horizon or "not specified"

        return f"""
You are the Topic Intelligence synthesis layer inside FORGE.

Generate a generic, evidence-aware Topic Intelligence object.

Topic: {topic}
Role context: {role_text}
Time horizon: {horizon_text}

CRITICAL RULES:
1. Do not create topic-specific code branches.
2. Do not invent market statistics, employer counts, prevalence,
   sample sizes, salary values, forecasts, or percentages.
3. Do not turn general knowledge into a FORGE market statistic.
4. Market Evidence must use ONLY the supplied evidence context.
5. If evidence is missing, mark the relevant section as
   "insufficient_verified_evidence".
6. Never fabricate a URL.
7. Technical explanations may be synthesized, but must be clearly
   separated from market evidence.
8. Keep the response useful for a student and technically concrete.
9. The same schema must work for any technical topic.
10. Return JSON only.

Required top-level JSON shape:

{{
  "topic": "<canonical topic>",
  "status": "success",
  "sections": {{
    "overview": {{
      "status": "available",
      "title": "...",
      "summary": "...",
      "why_it_matters": []
    }},
    "market_evidence": {{
      "status": "available | insufficient_verified_evidence",
      "summary": "...",
      "signals": [],
      "sources": []
    }},
    "how_it_works": {{
      "status": "available | not_applicable",
      "steps": []
    }},
    "core_concepts": {{
      "status": "available",
      "items": []
    }},
    "comparison": {{
      "status": "available | not_applicable",
      "items": []
    }},
    "architecture": {{
      "status": "available | not_applicable",
      "components": [],
      "flow": []
    }},
    "prerequisites": {{
      "status": "available",
      "items": []
    }},
    "learning_path": {{
      "status": "available",
      "stages": []
    }},
    "use_cases": {{
      "status": "available",
      "items": []
    }},
    "common_mistakes": {{
      "status": "available",
      "items": []
    }},
    "project": {{
      "status": "available",
      "title": "...",
      "objective": "...",
      "requirements": [],
      "deliverables": []
    }},
    "verified_resources": {{
      "status": "available | insufficient_verified_evidence",
      "resources": []
    }},
    "embedded_videos": {{
      "status": "available | insufficient_verified_evidence",
      "videos": []
    }},
    "quick_assessment": {{
      "status": "available",
      "questions": []
    }},
    "evidence": {{
      "status": "available | insufficient_verified_evidence",
      "source_types": []
    }}
  }}
}}

For market_evidence, copy factual values from the evidence context
rather than estimating them.

For verified_resources and embedded_videos, include a URL only if
that URL already exists in the supplied evidence context.

SUPPLIED EVIDENCE CONTEXT:
{evidence_json}
""".strip()

    def _generate_topic_with_groq(
        self,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Optional Groq adapter.

        GROQ_API_KEY/GROQ_API_TOKEN are read from environment variables.
        No API key is embedded in source code.
        """
        api_key = (
            os.getenv("GROQ_API_KEY")
            or os.getenv("GROQ_API_TOKEN")
        )

        if not api_key:
            return {
                "status": "unavailable",
                "error": (
                    "GROQ_API_KEY/GROQ_API_TOKEN is not configured."
                )
            }

        try:
            from groq import Groq
        except ImportError:
            return {
                "status": "unavailable",
                "error": (
                    "The 'groq' package is not installed."
                )
            }

        model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )

        try:
            client = Groq(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict JSON-producing Topic "
                            "Intelligence engine for FORGE."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = (
                response.choices[0]
                .message
                .content
            )

            if not content:
                return {
                    "status": "error",
                    "error": "Groq returned an empty response."
                }

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # Some model configurations may still wrap JSON in
                # markdown. Extract the first JSON object safely.
                match = re.search(
                    r"\{.*\}",
                    content,
                    flags=re.DOTALL
                )

                if not match:
                    return {
                        "status": "error",
                        "error": "Groq response was not valid JSON."
                    }

                parsed = json.loads(match.group(0))

            return {
                "status": "success",
                "model": model,
                "data": parsed
            }

        except Exception as exc:
            return {
                "status": "error",
                "error": str(exc)
            }

    @staticmethod
    def _validate_topic_payload(
        payload: Any,
        topic: str
    ) -> Dict[str, Any]:
        """
        Validate/normalize the generic topic schema without enforcing
        topic-specific content.
        """
        if not isinstance(payload, dict):
            return {
                "status": "error",
                "error": "Topic generator returned a non-object JSON value."
            }

        sections = payload.get("sections")

        if not isinstance(sections, dict):
            sections = {}

        required_sections = [
            "overview",
            "market_evidence",
            "how_it_works",
            "core_concepts",
            "comparison",
            "architecture",
            "prerequisites",
            "learning_path",
            "use_cases",
            "common_mistakes",
            "project",
            "verified_resources",
            "embedded_videos",
            "quick_assessment",
            "evidence",
        ]

        normalized_sections = {}

        for name in required_sections:
            value = sections.get(name)

            if isinstance(value, dict):
                section = dict(value)
            else:
                section = {}

            section.setdefault(
                "status",
                "available"
            )

            normalized_sections[name] = section

        return {
            "status": "success",
            "topic": payload.get("topic") or topic,
            "sections": normalized_sections
        }

    def get_topic_intelligence(
        self,
        topic: str,
        role: Optional[str] = None,
        horizon: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build the full dynamic Topic Intelligence workspace.

        Data flow:
            verified evidence
                    ↓
            Topic Intelligence synthesis
                    ↓
            generic section schema

        This method is intentionally independent of a specific topic.
        """
        topic = self._clean_topic(topic)

        if not topic:
            return {
                "status": "error",
                "error": "Topic is required."
            }

        evidence_result = self._collect_topic_evidence(
            topic=topic,
            role=role,
            horizon=horizon
        )

        market_evidence = self._market_evidence_contract(
            evidence_result
        )

        evidence_context = {
            "topic": topic,
            "role": role,
            "horizon": horizon,
            "market_evidence": market_evidence,
            "verified_source_urls": (
                self._extract_verified_source_urls(
                    evidence_result
                )
            )
        }

        prompt = self._build_topic_prompt(
            topic=topic,
            role=role,
            horizon=horizon,
            evidence=evidence_context
        )

        # Prefer an injected generator when main.py provides one.
        if self.topic_generator is not None:
            generated = self._call(
                self.topic_generator,
                "generate",
                topic=topic,
                role=role,
                horizon=horizon,
                evidence=evidence_context
            )

            if generated.get("status") == "success":
                generated_data = self._data(generated)
                validated = self._validate_topic_payload(
                    generated_data,
                    topic
                )

                if validated.get("status") == "success":
                    validated["sections"]["market_evidence"] = (
                        market_evidence
                    )

                    return {
                        "status": "success",
                        "project": "FORGE",
                        "topic": topic,
                        "role": role,
                        "horizon": horizon,
                        "source": "injected_topic_generator",
                        "intelligence": validated,
                        "evidence": evidence_context,
                    }

        # Backward-compatible built-in Groq path.
        generated = self._generate_topic_with_groq(prompt)

        if generated.get("status") != "success":
            return {
                "status": "success",
                "project": "FORGE",
                "topic": topic,
                "role": role,
                "horizon": horizon,
                "intelligence_status": "partial",
                "error": generated.get("error"),
                "sections": {
                    "market_evidence": market_evidence,
                    "overview": {
                        "status": "insufficient_verified_evidence",
                        "title": topic,
                        "summary": (
                            "Technical Topic Intelligence could not "
                            "be generated because the configured "
                            "intelligence generator is unavailable."
                        ),
                        "why_it_matters": []
                    }
                },
                "evidence": evidence_context,
            }

        validated = self._validate_topic_payload(
            generated.get("data"),
            topic
        )

        if validated.get("status") != "success":
            return {
                "status": "error",
                "project": "FORGE",
                "topic": topic,
                "error": validated.get("error"),
                "evidence": evidence_context,
            }

        # IMPORTANT: overwrite the model-generated market section with
        # the actual evidence-service output. The LLM cannot change
        # market numbers.
        validated["sections"]["market_evidence"] = market_evidence

        # Verified URLs are restricted to URLs present in evidence.
        verified_urls = set(
            evidence_context.get("verified_source_urls", [])
        )

        resources = (
            validated["sections"]
            .get("verified_resources", {})
            .get("resources", [])
        )

        if isinstance(resources, list):
            clean_resources = []

            for resource in resources:
                if not isinstance(resource, dict):
                    continue

                url = resource.get("url")

                if url and url not in verified_urls:
                    resource = dict(resource)
                    resource.pop("url", None)

                clean_resources.append(resource)

            validated["sections"]["verified_resources"][
                "resources"
            ] = clean_resources

        videos = (
            validated["sections"]
            .get("embedded_videos", {})
            .get("videos", [])
        )

        if isinstance(videos, list):
            clean_videos = []

            for video in videos:
                if not isinstance(video, dict):
                    continue

                url = video.get("url")

                if url and url not in verified_urls:
                    video = dict(video)
                    video.pop("url", None)

                clean_videos.append(video)

            validated["sections"]["embedded_videos"][
                "videos"
            ] = clean_videos

        return {
            "status": "success",
            "project": "FORGE",
            "topic": topic,
            "role": role,
            "horizon": horizon,
            "source": "groq_topic_intelligence",
            "model": generated.get("model"),
            "intelligence": validated,
            "evidence": evidence_context,
        }

    # =========================================================
    # COMPLETE FORGE ANALYSIS
    # =========================================================

    def complete_analysis(
        self,
        occupation: str,
        baseline_ai: float = 0.0,
        future_ai: float = 0.5
    ) -> Dict[str, Any]:

        occupation = occupation.strip()

        if not occupation:

            return {
                "status": "error",
                "error": "Occupation is required."
            }

        # -----------------------------------------------------
        # OCCUPATION BASELINE
        # -----------------------------------------------------

        occupation_intelligence = (
            self.get_occupation_intelligence(
                occupation
            )
        )

        # -----------------------------------------------------
        # FUTURE SCENARIO
        # -----------------------------------------------------

        future_scenario = (
            self.simulate_future_workforce(
                occupation=occupation,
                baseline_ai=baseline_ai,
                future_ai=future_ai
            )
        )

        # -----------------------------------------------------
        # COMPLETE RESPONSE
        # -----------------------------------------------------

        return {

            "status": "success",

            "project": "FORGE",

            "occupation": occupation,

            "central_question": (
                "When AI automates work, what human "
                "capability are we accidentally losing?"
            ),

            "occupation_intelligence": (
                occupation_intelligence
            ),

            "future_workforce_scenario": (
                future_scenario
            ),

            "FORGE_FLOW": [
                "CURRENT WORK",
                "WORKTRACE",
                "SKILL SHADOW",
                "WORKFOLD",
                "LATTICE",
                "CAPABILITY PRESERVED"
            ],

            "engine_status": self.engine_status()
        }