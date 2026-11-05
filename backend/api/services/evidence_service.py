"""
FORGE — Evidence Service

Stores and aggregates validated learner evidence produced by LATTICE.
Core scoring is deliberately NOT an LLM responsibility.

The service distinguishes:
    NO_VALIDATED_EVIDENCE  -> no completed/validated attempt yet
    INSUFFICIENT_EVIDENCE  -> an attempt exists, but evidence is insufficient
    PARTIAL                -> partial capability demonstrated
    DEMONSTRATED            -> capability demonstrated

Task-specific validators can be plugged into evaluate_submission().
Until a validator supplies rubric scores, the service will not invent a
learner score from the fact that a task was generated or submitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


STATUS_DEMONSTRATED = "DEMONSTRATED"
STATUS_PARTIAL = "PARTIAL"
STATUS_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
STATUS_NO_EVIDENCE = "NO_VALIDATED_EVIDENCE"


@dataclass
class EvidenceSubmission:
    practice_id: str
    occupation: str
    capability: str
    task_id: str
    submission: Any
    observable_evidence: List[str] = field(default_factory=list)
    # rubric_scores are intentionally NOT part of the learner submission.
    # They must be produced by the server-side TaskEvaluationService.
    time_seconds: Optional[float] = None
    attempts: int = 1
    accuracy: Optional[float] = None
    mode: str = "DIGITAL"
    submitted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class EvidenceRecord:
    evidence_id: str
    practice_id: str
    occupation: str
    capability: str
    task_id: str
    mode: str
    score: Optional[float]
    max_score: float
    status: str
    rubric: List[Dict[str, Any]]
    observable_evidence: List[str]
    evidence_quality: float
    confidence: float
    attempts: int
    time_seconds: Optional[float]
    accuracy: Optional[float]
    submitted_at: str
    evaluated_at: str
    valid: bool = True


class EvidenceService:
    """Evidence persistence + capability-state aggregation."""

    def __init__(self):
        # First implementation is in-memory. Replace this store with a DB
        # later without changing the API contract.
        self._evidence: Dict[str, EvidenceRecord] = {}
        self._capability_index: Dict[str, List[str]] = {}

    # ---------------------------------------------------------
    # SUBMISSION
    # ---------------------------------------------------------

    def submit_evaluated_evidence(
        self,
        submission: EvidenceSubmission,
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Persist an evaluation produced by a trusted server-side evaluator.

        Learner/client input cannot provide rubric scores.
        """
        self._validate_submission(submission)
        self._validate_evaluation(evaluation)

        evidence_id = str(uuid4())

        record = EvidenceRecord(
            evidence_id=evidence_id,
            practice_id=submission.practice_id,
            occupation=submission.occupation,
            capability=submission.capability,
            task_id=submission.task_id,
            mode=submission.mode,
            score=evaluation.get("score"),
            max_score=5.0,
            status=evaluation.get(
                "status",
                STATUS_INSUFFICIENT,
            ),
            rubric=evaluation.get("rubric", []),
            observable_evidence=evaluation.get(
                "observable_evidence",
                submission.observable_evidence,
            ),
            evidence_quality=evaluation.get(
                "evidence_quality",
                0.0,
            ),
            confidence=evaluation.get(
                "confidence",
                0.0,
            ),
            attempts=submission.attempts,
            time_seconds=submission.time_seconds,
            accuracy=submission.accuracy,
            submitted_at=submission.submitted_at,
            evaluated_at=datetime.now(timezone.utc).isoformat(),
        )

        self._evidence[evidence_id] = record

        key = self._capability_key(
            submission.occupation,
            submission.capability,
        )

        self._capability_index.setdefault(
            key,
            [],
        ).append(evidence_id)

        return {
            "evidence": asdict(record),
            "capability_state": self.get_capability_state(
                submission.occupation,
                submission.capability,
            ),
        }

    # Backward-compatible internal method.
    # It deliberately refuses unevaluated submissions rather than
    # inventing a learner score.
    def submit_evidence(
        self,
        submission: EvidenceSubmission,
    ) -> Dict[str, Any]:
        raise ValueError(
            "Evidence must be evaluated by TaskEvaluationService "
            "before it can be persisted. Use submit_evaluated_evidence()."
        )

    # ---------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------

    def evaluate_submission(
        self,
        submission: EvidenceSubmission,
    ) -> Dict[str, Any]:
        """
        Deprecated compatibility boundary.

        EvidenceService no longer scores learner work. Evaluation belongs
        to TaskEvaluationService.
        """
        raise ValueError(
            "EvidenceService does not score learner work. "
            "Use TaskEvaluationService first."
        )

    # ---------------------------------------------------------
    # CAPABILITY STATE
    # ---------------------------------------------------------

    def get_capability_state(
        self,
        occupation: str,
        capability: str,
    ) -> Dict[str, Any]:
        key = self._capability_key(occupation, capability)
        ids = self._capability_index.get(key, [])
        records = [self._evidence[eid] for eid in ids if self._evidence[eid].valid]

        if not records:
            return {
                "occupation": occupation,
                "capability": capability,
                "score": None,
                "max_score": 5.0,
                "status": STATUS_NO_EVIDENCE,
                "attempts": 0,
                "evidence_count": 0,
                "confidence": 0.0,
                "evidence_quality": 0.0,
                "latest_evidence_id": None,
            }

        scored = [r for r in records if r.score is not None]
        if not scored:
            return {
                "occupation": occupation,
                "capability": capability,
                "score": None,
                "max_score": 5.0,
                "status": STATUS_INSUFFICIENT,
                "attempts": len(records),
                "evidence_count": len(records),
                "confidence": round(sum(r.confidence for r in records) / len(records), 2),
                "evidence_quality": round(sum(r.evidence_quality for r in records) / len(records), 2),
                "latest_evidence_id": records[-1].evidence_id,
            }

        score = self._aggregate_scores(scored)
        confidence = sum(r.confidence for r in scored) / len(scored)
        quality = sum(r.evidence_quality for r in scored) / len(scored)
        latest = records[-1]

        return {
            "occupation": occupation,
            "capability": capability,
            "score": round(score, 2),
            "max_score": 5.0,
            "status": self._status_from_score(score),
            "attempts": len(records),
            "evidence_count": len(scored),
            "confidence": round(confidence, 2),
            "evidence_quality": round(quality, 2),
            "latest_evidence_id": latest.evidence_id,
            "latest_score": latest.score,
            "latest_status": latest.status,
        }

    def get_occupation_evidence(self, occupation: str) -> List[Dict[str, Any]]:
        capabilities = []
        prefix = f"{occupation}::"
        for key in self._capability_index:
            if key.startswith(prefix):
                capabilities.append(key.split("::", 1)[1])

        return [
            self.get_capability_state(occupation, capability)
            for capability in sorted(set(capabilities))
        ]

    # ---------------------------------------------------------
    # HISTORY / LOOKUP
    # ---------------------------------------------------------

    def get_evidence_history(
        self,
        occupation: str,
        capability: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        records = []
        for record in self._evidence.values():
            if not record.valid or record.occupation != occupation:
                continue
            if capability is not None and record.capability != capability:
                continue
            records.append(asdict(record))

        return sorted(records, key=lambda item: item["evaluated_at"])

    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        record = self._evidence.get(evidence_id)
        return asdict(record) if record else None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _capability_key(occupation: str, capability: str) -> str:
        return f"{occupation.strip()}::{capability.strip()}"

    @staticmethod
    def _status_from_score(score: Optional[float]) -> str:
        if score is None:
            return STATUS_INSUFFICIENT
        if score >= 4.0:
            return STATUS_DEMONSTRATED
        if score >= 2.5:
            return STATUS_PARTIAL
        return STATUS_INSUFFICIENT

    @staticmethod
    def _aggregate_scores(records: List[EvidenceRecord]) -> float:
        # Later validated attempts have slightly greater weight, while
        # earlier evidence remains part of the capability history.
        weighted = 0.0
        total_weight = 0.0
        for index, record in enumerate(records):
            weight = 1.0 + (0.10 * index)
            weighted += float(record.score) * weight
            total_weight += weight
        return weighted / total_weight if total_weight else 0.0

    @staticmethod
    def _validate_evaluation(
        evaluation: Dict[str, Any],
    ) -> None:
        if not isinstance(evaluation, dict):
            raise ValueError(
                "evaluation must be a server-generated dictionary."
            )

        required = {
            "score": evaluation.get("score"),
            "status": evaluation.get("status"),
            "rubric": evaluation.get("rubric"),
        }

        if required["status"] not in {
            STATUS_DEMONSTRATED,
            STATUS_PARTIAL,
            STATUS_INSUFFICIENT,
        }:
            raise ValueError(
                "Invalid evaluator status."
            )

        score = required["score"]

        if score is not None:
            try:
                score = float(score)
            except (TypeError, ValueError):
                raise ValueError(
                    "Evaluator score must be numeric or None."
                )

            if not 0.0 <= score <= 5.0:
                raise ValueError(
                    "Evaluator score must be between 0 and 5."
                )

        if not isinstance(
            required["rubric"],
            list,
        ):
            raise ValueError(
                "Evaluator rubric must be a list."
            )

    @staticmethod
    def _evidence_quality(submission: EvidenceSubmission) -> float:
        quality = 0.0
        if submission.observable_evidence:
            quality += 0.35
        if submission.submission not in (None, "", [], {}):
            quality += 0.25
        if submission.accuracy is not None:
            quality += 0.15
        if submission.time_seconds is not None:
            quality += 0.10
        if submission.attempts >= 1:
            quality += 0.15
        return min(1.0, quality)

    @staticmethod
    def _validate_submission(submission: EvidenceSubmission) -> None:
        required = {
            "practice_id": submission.practice_id,
            "occupation": submission.occupation,
            "capability": submission.capability,
            "task_id": submission.task_id,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError("Missing required evidence fields: " + ", ".join(missing))
        if submission.mode != "DIGITAL":
            raise ValueError("Only DIGITAL evidence mode is currently supported.")
        if submission.attempts < 1:
            raise ValueError("attempts must be at least 1")
        if submission.time_seconds is not None and submission.time_seconds < 0:
            raise ValueError("time_seconds cannot be negative")



def create_evidence_service() -> EvidenceService:
    return EvidenceService()
