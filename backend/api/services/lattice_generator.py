"""
FORGE LATTICE — Groq Practice Generator

Generates a synthetic apprenticeship practice set from real LATTICE
source context. The generator does not create scores before an attempt.

Environment:
    GROQ_API_KEY=<set-in-.env>

Optional:
    GROQ_MODEL=llama-3.3-70b-versatile

The generator automatically loads .env files from:
    1. FORGE/.env
    2. FORGE/backend/.env

Environment variables already present in the system are also supported.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq


# ================================================================
# ENVIRONMENT LOADING
# ================================================================

def _load_environment() -> None:
    """
    Load FORGE environment variables from .env files.

    Priority:
        FORGE/.env
        FORGE/backend/.env
        current working directory .env

    Existing system environment variables are preserved.
    """

    # Current file:
    #
    # FORGE/
    #   backend/
    #     api/
    #       services/
    #         lattice_generator.py
    #
    # Therefore:
    # parents[0] = services
    # parents[1] = api
    # parents[2] = backend
    # parents[3] = FORGE

    current_file = Path(__file__).resolve()

    project_root = current_file.parents[3]
    backend_root = current_file.parents[2]

    env_candidates = [
        project_root / ".env",
        backend_root / ".env",
        Path.cwd() / ".env",
    ]

    loaded_files = set()

    for env_path in env_candidates:

        env_path = env_path.resolve()

        if (
            env_path.exists()
            and env_path.is_file()
            and env_path not in loaded_files
        ):
            load_dotenv(
                dotenv_path=env_path,
                override=False,
            )

            loaded_files.add(env_path)

            print(
                f"[LATTICE] Loaded environment: {env_path}"
            )


# Load environment before creating the generator.
_load_environment()


class LatticeGenerationError(RuntimeError):
    """Raised when LATTICE practice generation fails."""


class LatticeGenerator:

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):

        # ========================================================
        # GROQ API KEY
        # ========================================================

        self.api_key = (
            api_key
            or os.getenv("GROQ_API_KEY")
            or os.getenv("GROQ_API_TOKEN")
        )

        if not self.api_key:
            raise LatticeGenerationError(
                "GROQ_API_KEY is not configured. "
                "Add GROQ_API_KEY=your_key to FORGE/.env "
                "and restart the backend."
            )

        # ========================================================
        # GROQ MODEL
        # ========================================================

        self.model = (
            model
            or os.getenv("GROQ_MODEL")
            or "openai/gpt-oss-120b"
        )

        # ========================================================
        # GROQ CLIENT
        # ========================================================

        try:
            self.client = Groq(
                api_key=self.api_key
            )
        except Exception as exc:
            raise LatticeGenerationError(
                f"Unable to initialize Groq client: {exc}"
            ) from exc

        print(
            f"[LATTICE] Groq generator ready | model={self.model}"
        )

    # ============================================================
    # PUBLIC API
    # ============================================================

    def generate_practice_set(
        self,
        *,
        occupation: str,
        capability: str,
        source_task: str,
        assessment_focus: str = "",
        practice_intent: str = "",
        observable_evidence: Optional[List[str]] = None,
        source_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        """
        Generate one synthetic apprenticeship exercise.

        The returned structure is deliberately strict so the frontend
        and later assessment layer can consume it safely.
        """

        occupation = str(
            occupation or ""
        ).strip()

        capability = str(
            capability or ""
        ).strip()

        source_task = str(
            source_task or ""
        ).strip()

        if not occupation:
            raise LatticeGenerationError(
                "Occupation is required."
            )

        if not capability:
            raise LatticeGenerationError(
                "Capability is required."
            )

        if not source_task:
            raise LatticeGenerationError(
                "Source task is required."
            )

        evidence = (
            observable_evidence
            or []
        )

        prompt = self._build_prompt(
            occupation=occupation,
            capability=capability,
            source_task=source_task,
            assessment_focus=assessment_focus,
            practice_intent=practice_intent,
            observable_evidence=evidence,
            source_context=source_context or {},
        )

        # ========================================================
        # GROQ REQUEST
        # ========================================================

        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    model=self.model,
                    temperature=0.35,
                    max_tokens=2600,
                    response_format={
                        "type": "json_object"
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": self._system_prompt(),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

        except Exception as exc:

            raise LatticeGenerationError(
                f"Groq generation failed: {exc}"
            ) from exc

        # ========================================================
        # READ RESPONSE
        # ========================================================

        try:
            raw = (
                response
                .choices[0]
                .message
                .content
            )
        except Exception as exc:
            raise LatticeGenerationError(
                "Groq response did not contain message content."
            ) from exc

        if not raw:
            raise LatticeGenerationError(
                "Groq returned an empty response."
            )

        # ========================================================
        # PARSE JSON
        # ========================================================

        try:

            generated = json.loads(
                raw
            )

        except json.JSONDecodeError as exc:

            raise LatticeGenerationError(
                "Groq returned invalid JSON."
            ) from exc

        # ========================================================
        # VALIDATE
        # ========================================================

        return self._validate_and_normalize(
            generated=generated,
            occupation=occupation,
            capability=capability,
            source_task=source_task,
            assessment_focus=assessment_focus,
            practice_intent=practice_intent,
            observable_evidence=evidence,
        )

    # ============================================================
    # SYSTEM PROMPT
    # ============================================================

    @staticmethod
    def _system_prompt() -> str:

        return """
You are the LATTICE synthetic-apprenticeship generation engine inside
FORGE.

Your purpose is to preserve human capability when AI reduces practice
of real work.

You receive:
- a real occupation,
- a real source task,
- a target capability,
- evidence signals,
- assessment focus.

Generate ONE new, realistic workplace practice exercise.

CRITICAL RULES:

1. Do NOT simply repeat or paraphrase the source task.

2. Create a new scenario that requires the learner to perform or reason
   about the same underlying capability.

3. The exercise must be actionable by a human learner.

4. It must contain enough information to make a meaningful decision.

5. Do not require private, proprietary, dangerous, or unavailable data.

6. Do not assume the learner has access to external systems.

7. Do not pre-score the learner.

8. The rubric evaluates the quality of the eventual attempt.

9. Rubric criteria must be observable from the learner's answer,
   decisions, actions, or captured interaction evidence.

10. Keep the exercise realistic for the named occupation.

11. Do not invent a certification, legal requirement, or professional
    standard unless supplied in the source context.

12. Return ONLY valid JSON matching the requested schema.
"""

    # ============================================================
    # USER PROMPT
    # ============================================================

    @staticmethod
    def _build_prompt(
        *,
        occupation: str,
        capability: str,
        source_task: str,
        assessment_focus: str,
        practice_intent: str,
        observable_evidence: List[str],
        source_context: Dict[str, Any],
    ) -> str:

        context_json = json.dumps(
            source_context,
            ensure_ascii=False,
            default=str,
        )

        evidence_text = json.dumps(
            observable_evidence,
            ensure_ascii=False,
        )

        return f"""
Create one LATTICE synthetic apprenticeship practice set.

REAL SOURCE CONTEXT

Occupation:
{occupation}

Target capability:
{capability}

Original source task:
{source_task}

Assessment focus:
{
    assessment_focus
    or
    "Use the capability and source task to infer the most relevant observable focus."
}

Practice intent:
{
    practice_intent
    or
    "Preserve the target capability through deliberate practice."
}

Observable evidence signals:
{evidence_text}

Additional structured source context:
{context_json}

The generated exercise must be NEW.

It must preserve the underlying capability without copying the source
task wording.

Return exactly this JSON shape:

{{
  "title": "short practice title",

  "scenario": "realistic workplace situation",

  "task_instruction": "clear instruction telling the learner what to do",

  "provided_information": [
    "fact/data/input the learner can use"
  ],

  "constraints": [
    "constraint the learner must respect"
  ],

  "expected_output": "what the learner must submit or decide",

  "reasoning_focus": [
    "capability-specific reasoning behaviour"
  ],

  "observable_evidence": [
    "specific evidence that can be observed from the attempt"
  ],

  "rubric": [
    {{
      "dimension": "capability dimension",

      "criterion": "what is being evaluated",

      "good_performance": "observable description of good performance",

      "max_score": 5
    }}
  ]
}}

Requirements:

- 3 to 6 provided_information items.
- 2 to 5 constraints.
- 2 to 5 reasoning_focus items.
- 3 to 6 observable_evidence items.
- 3 to 5 rubric criteria.
- max_score must be 5 for every rubric criterion.
- Rubric criteria must be specific to this exercise.
- Do not include a final score, grade, pass/fail, or learner result.
"""

    # ============================================================
    # VALIDATION
    # ============================================================

    def _validate_and_normalize(
        self,
        *,
        generated: Dict[str, Any],
        occupation: str,
        capability: str,
        source_task: str,
        assessment_focus: str,
        practice_intent: str,
        observable_evidence: List[str],
    ) -> Dict[str, Any]:

        if not isinstance(
            generated,
            dict,
        ):
            raise LatticeGenerationError(
                "Generated practice set must be a JSON object."
            )

        title = self._required_text(
            generated.get("title"),
            "title",
        )

        scenario = self._required_text(
            generated.get("scenario"),
            "scenario",
        )

        task_instruction = self._required_text(
            generated.get(
                "task_instruction"
            ),
            "task_instruction",
        )

        expected_output = self._required_text(
            generated.get(
                "expected_output"
            ),
            "expected_output",
        )

        provided_information = self._string_list(
            generated.get(
                "provided_information"
            ),
            "provided_information",
        )

        constraints = self._string_list(
            generated.get(
                "constraints"
            ),
            "constraints",
        )

        reasoning_focus = self._string_list(
            generated.get(
                "reasoning_focus"
            ),
            "reasoning_focus",
        )

        generated_evidence = self._string_list(
            generated.get(
                "observable_evidence"
            ),
            "observable_evidence",
        )

        rubric_raw = generated.get(
            "rubric"
        )

        if (
            not isinstance(
                rubric_raw,
                list,
            )
            or not rubric_raw
        ):
            raise LatticeGenerationError(
                "Generated practice set contains no rubric."
            )

        rubric: List[
            Dict[str, Any]
        ] = []

        for index, item in enumerate(
            rubric_raw
        ):

            if not isinstance(
                item,
                dict,
            ):
                raise LatticeGenerationError(
                    f"Rubric item {index + 1} is invalid."
                )

            dimension = self._required_text(
                item.get(
                    "dimension"
                ),
                f"rubric[{index}].dimension",
            )

            criterion = self._required_text(
                item.get(
                    "criterion"
                ),
                f"rubric[{index}].criterion",
            )

            good_performance = self._required_text(
                item.get(
                    "good_performance"
                ),
                f"rubric[{index}].good_performance",
            )

            max_score = item.get(
                "max_score",
                5,
            )

            try:
                max_score = int(
                    max_score
                )

            except (
                TypeError,
                ValueError,
            ):

                raise LatticeGenerationError(
                    f"rubric[{index}].max_score must be numeric."
                )

            if max_score != 5:

                raise LatticeGenerationError(
                    f"rubric[{index}].max_score must equal 5."
                )

            rubric.append(
                {
                    "dimension": dimension,
                    "criterion": criterion,
                    "good_performance":
                        good_performance,
                    "max_score": 5,
                }
            )

        if len(rubric) < 3:

            raise LatticeGenerationError(
                "At least 3 rubric criteria are required."
            )

        # ========================================================
        # COPY PROTECTION
        # ========================================================

        if self._too_similar(
            task_instruction,
            source_task,
        ):

            raise LatticeGenerationError(
                "Generated task is too similar to the source task."
            )

        # ========================================================
        # FINAL RESULT
        # ========================================================

        return {

            "status": "generated",

            "generation_mode":
                "groq_llm",

            "scored_before_attempt":
                False,

            "occupation":
                occupation,

            "target_capability":
                capability,

            "source_context": {

                "source_task":
                    source_task,

                "assessment_focus":
                    assessment_focus,

                "practice_intent":
                    practice_intent,

                "observable_evidence":
                    observable_evidence,
            },

            "practice_set": {

                "title":
                    title,

                "scenario":
                    scenario,

                "task_instruction":
                    task_instruction,

                "provided_information":
                    provided_information,

                "constraints":
                    constraints,

                "expected_output":
                    expected_output,

                "reasoning_focus":
                    reasoning_focus,

                "observable_evidence":
                    generated_evidence,

                "rubric":
                    rubric,
            },

            "assessment": {

                "status":
                    "NOT_SCORED_BEFORE_ATTEMPT",

                "attempt_required":
                    True,

                "max_possible_score":
                    len(rubric) * 5,

                "rubric_criteria":
                    len(rubric),
            },
        }

    # ============================================================
    # REQUIRED TEXT
    # ============================================================

    @staticmethod
    def _required_text(
        value: Any,
        field: str,
    ) -> str:

        if value is None:

            raise LatticeGenerationError(
                f"Missing generated field: {field}"
            )

        text = str(
            value
        ).strip()

        if not text:

            raise LatticeGenerationError(
                f"Empty generated field: {field}"
            )

        return text

    # ============================================================
    # STRING LIST
    # ============================================================

    @staticmethod
    def _string_list(
        value: Any,
        field: str,
    ) -> List[str]:

        if not isinstance(
            value,
            list,
        ):

            raise LatticeGenerationError(
                f"Generated field '{field}' must be a list."
            )

        cleaned: List[str] = []

        for item in value:

            text = str(
                item
            ).strip()

            if text:
                cleaned.append(
                    text
                )

        if not cleaned:

            raise LatticeGenerationError(
                f"Generated field '{field}' cannot be empty."
            )

        return cleaned

    # ============================================================
    # SIMILARITY GUARD
    # ============================================================

    @staticmethod
    def _too_similar(
        generated: str,
        source: str,
    ) -> bool:

        """
        Lightweight lexical similarity guard.

        This prevents obvious copying without pretending to be a
        semantic plagiarism detector.
        """

        generated_words = {
            word.lower()
            for word in generated.split()
            if len(word) > 4
        }

        source_words = {
            word.lower()
            for word in source.split()
            if len(word) > 4
        }

        if (
            not generated_words
            or not source_words
        ):
            return False

        overlap = len(
            generated_words &
            source_words
        )

        smaller = min(
            len(generated_words),
            len(source_words),
        )

        if smaller == 0:
            return False

        return (
            overlap / smaller
        ) >= 0.85


# ================================================================
# MODULE-LEVEL FACTORY
# ================================================================

def create_lattice_generator() -> LatticeGenerator:
    return LatticeGenerator()