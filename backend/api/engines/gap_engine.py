"""
FORGE — Capability Gap Engine

Purpose
-------
Connects:

WORKTRACE
    ↓
SKILL SHADOW
    ↓
WORKFOLD
    ↓
EVIDENCE SERVICE
    ↓
LATTICE

The engine identifies capability gaps from:
    1. capability importance
    2. validated learner evidence
    3. affected work tasks
    4. future work transformation
    5. AI relevance

Important:
-----------
NO evidence is NOT interpreted as inability.

NO_VALIDATED_EVIDENCE
    = FORGE does not yet have enough validated evidence.

The engine does not generate learner scores itself.
EvidenceService owns learner evidence state.

LATTICE owns practice-task selection.
WORKFOLD owns future task transformation.
SKILL SHADOW owns AI-impact calculations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import math


class GapEngine:
    """
    Evidence-aware capability gap analysis for FORGE.
    """

    STATUS_DEMONSTRATED = "DEMONSTRATED"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_INSUFFICIENT = "INSUFFICIENT_EVIDENCE"
    STATUS_NO_EVIDENCE = "NO_VALIDATED_EVIDENCE"

    def __init__(
        self,
        worktrace_engine,
        skill_shadow_engine,
        workfold_engine,
        lattice_engine,
        evidence_service,
    ):
        self.worktrace = worktrace_engine
        self.skill_shadow = skill_shadow_engine
        self.workfold = workfold_engine
        self.lattice = lattice_engine
        self.evidence = evidence_service

    # =========================================================
    # PUBLIC API
    # =========================================================

    def analyze_occupation(
        self,
        occupation: str,
        ai_adoption: float = 0.50,
    ) -> Dict[str, Any]:
        """
        Complete capability-gap analysis for an occupation.
        """

        if not occupation or not str(occupation).strip():
            raise ValueError("occupation is required")

        occupation = str(occupation).strip()
        ai_adoption = self._clamp(float(ai_adoption), 0.0, 1.0)

        # -----------------------------------------------------
        # 1. WORKTRACE
        # -----------------------------------------------------

        worktrace = self.worktrace.get_occupation(occupation)

        if not worktrace:
            return {
                "occupation": occupation,
                "status": "OCCUPATION_NOT_FOUND",
                "capabilities": [],
                "gaps": [],
                "highest_impact_gap": None,
                "next_practice": None,
            }

        tasks = worktrace.get("tasks") or []
        capabilities = worktrace.get("capabilities") or []

        # -----------------------------------------------------
        # 2. SKILL SHADOW
        # -----------------------------------------------------

        shadow = self._safe_skill_shadow(
            occupation=occupation,
            ai_adoption=ai_adoption,
        )

        # -----------------------------------------------------
        # 3. WORKFOLD
        # -----------------------------------------------------

        fold = self._safe_workfold(
            occupation=occupation,
            ai_adoption=ai_adoption,
        )

        fold_tasks = self._fold_tasks(fold)

        # -----------------------------------------------------
        # 4. CAPABILITY ↔ TASK MAP
        # -----------------------------------------------------

        capability_tasks = self._build_capability_task_map(
            occupation=occupation,
            worktrace=worktrace,
        )

        # -----------------------------------------------------
        # 5. CAPABILITY GAP ANALYSIS
        # -----------------------------------------------------

        gaps: List[Dict[str, Any]] = []

        for capability in self._unique_capabilities(capabilities):

            capability_name = self._capability_name(capability)

            if not capability_name:
                continue

            evidence = self._get_evidence(
                occupation,
                capability_name,
            )

            source_tasks = capability_tasks.get(
                capability_name,
                [],
            )

            shadow_row = self._shadow_row(
                shadow,
                capability_name,
            )

            affected_tasks = self._match_fold_tasks(
                source_tasks,
                fold_tasks,
            )

            # -------------------------------------------------
            # Evidence
            # -------------------------------------------------

            evidence_score = evidence.get("score")

            evidence_deficit = self._evidence_deficit(
                evidence_score
            )

            # -------------------------------------------------
            # Capability importance
            # -------------------------------------------------

            importance = self._capability_importance(
                capability
            )

            # -------------------------------------------------
            # Work impact
            # -------------------------------------------------

            task_impact = self._calculate_task_impact(
                affected_tasks
            )

            # -------------------------------------------------
            # AI relevance
            # -------------------------------------------------

            ai_relevance = self._ai_relevance(
                shadow_row,
                affected_tasks,
            )

            # -------------------------------------------------
            # Gap priority
            # -------------------------------------------------

            priority = (
                evidence_deficit
                * importance
                * task_impact
                * ai_relevance
            )

            priority = self._clamp(
                priority,
                0.0,
                1.0,
            )

            status = evidence.get(
                "status",
                self.STATUS_NO_EVIDENCE,
            )

            requires_practice = status != self.STATUS_DEMONSTRATED

            gap = {
                "occupation": occupation,
                "capability": capability_name,

                "capability_type": capability.get(
                    "type"
                ) or capability.get(
                    "Capability Type"
                ),

                "capability_id": capability.get(
                    "id"
                ) or capability.get(
                    "Capability ID"
                ),

                # -------------------------------
                # Evidence
                # -------------------------------

                "evidence": {
                    "score": evidence.get("score"),
                    "max_score": evidence.get(
                        "max_score",
                        5.0,
                    ),
                    "status": status,
                    "attempts": evidence.get(
                        "attempts",
                        0,
                    ),
                    "evidence_count": evidence.get(
                        "evidence_count",
                        0,
                    ),
                    "confidence": evidence.get(
                        "confidence",
                        0.0,
                    ),
                    "evidence_quality": evidence.get(
                        "evidence_quality",
                        0.0,
                    ),
                    "latest_evidence_id": evidence.get(
                        "latest_evidence_id"
                    ),
                },

                # -------------------------------
                # Analytical components
                # -------------------------------

                "evidence_deficit": round(
                    evidence_deficit,
                    4,
                ),

                "capability_importance": round(
                    importance,
                    4,
                ),

                "work_impact": round(
                    task_impact,
                    4,
                ),

                "ai_relevance": round(
                    ai_relevance,
                    4,
                ),

                "gap_priority": round(
                    priority,
                    4,
                ),

                "priority_band": self._priority_band(
                    priority
                ),

                "requires_practice": requires_practice,

                # -------------------------------
                # Work impact
                # -------------------------------

                "affected_task_count": len(
                    affected_tasks
                ),

                "affected_tasks": affected_tasks,

                # -------------------------------
                # Shadow
                # -------------------------------

                "skill_shadow": shadow_row,

                # -------------------------------
                # Explanation
                # -------------------------------

                "reason": self._build_reason(
                    capability_name=capability_name,
                    evidence=evidence,
                    evidence_deficit=evidence_deficit,
                    importance=importance,
                    task_impact=task_impact,
                    ai_relevance=ai_relevance,
                    affected_tasks=affected_tasks,
                    priority=priority,
                ),
            }

            gaps.append(gap)

        # -----------------------------------------------------
        # 6. SORT
        # -----------------------------------------------------

        gaps.sort(
            key=lambda item: (
                item["gap_priority"],
                item["work_impact"],
                item["ai_relevance"],
            ),
            reverse=True,
        )

        # -----------------------------------------------------
        # 7. HIGHEST IMPACT GAP
        # -----------------------------------------------------

        highest_gap = None

        for gap in gaps:
            if gap["requires_practice"]:
                highest_gap = gap
                break

        # -----------------------------------------------------
        # 8. NEXT PRACTICE
        # -----------------------------------------------------

        next_practice = None

        if highest_gap:
            next_practice = self.get_next_practice(
                occupation=occupation,
                gap=highest_gap,
            )

        return {
            "occupation": occupation,
            "ai_adoption": ai_adoption,

            "worktrace": {
                "task_count": len(tasks),
                "capability_count": len(
                    capabilities
                ),
            },

            "workfold": {
                "available": bool(fold),
                "task_count": len(fold_tasks),
            },

            "capability_count": len(gaps),
            "gap_count": sum(
                1
                for gap in gaps
                if gap["requires_practice"]
            ),

            "demonstrated_count": sum(
                1
                for gap in gaps
                if gap["evidence"]["status"]
                == self.STATUS_DEMONSTRATED
            ),

            "partial_count": sum(
                1
                for gap in gaps
                if gap["evidence"]["status"]
                == self.STATUS_PARTIAL
            ),

            "insufficient_evidence_count": sum(
                1
                for gap in gaps
                if gap["evidence"]["status"]
                in {
                    self.STATUS_INSUFFICIENT,
                    self.STATUS_NO_EVIDENCE,
                }
            ),

            "gaps": gaps,

            "highest_impact_gap": highest_gap,

            "next_practice": next_practice,
        }

    # =========================================================
    # NEXT PRACTICE
    # =========================================================

    def get_next_practice(
        self,
        occupation: str,
        gap: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve the highest-impact gap into a LATTICE practice.

        LATTICE remains the owner of practice-task selection.
        """

        capability = gap.get("capability")

        if not capability:
            return None

        try:
            result = self.lattice.get_capability(
                occupation,
                capability,
            )

            if result:
                return {
                    "source": "LATTICE",
                    "occupation": occupation,
                    "capability": capability,
                    "gap_priority": gap.get(
                        "gap_priority",
                        0.0,
                    ),
                    "practice": result,
                }

        except Exception:
            pass

        # -----------------------------------------------------
        # Fallback:
        # ask LATTICE for the occupation's practice set
        # and find the matching capability.
        # -----------------------------------------------------

        try:
            occupation_result = (
                self.lattice.get_occupation(
                    occupation
                )
            )

            if occupation_result:

                practice_tasks = (
                    occupation_result.get(
                        "practice_set"
                    )
                    or occupation_result.get(
                        "priority_practice_tasks"
                    )
                    or []
                )

                matching = []

                for task in practice_tasks:

                    task_capability = (
                        self._extract_capability(
                            task
                        )
                    )

                    if (
                        task_capability
                        and task_capability.lower()
                        == capability.lower()
                    ):
                        matching.append(task)

                if matching:
                    return {
                        "source": "LATTICE",
                        "occupation": occupation,
                        "capability": capability,
                        "gap_priority": gap.get(
                            "gap_priority",
                            0.0,
                        ),
                        "practice": matching[0],
                    }

        except Exception:
            pass

        return None

    # =========================================================
    # WORKTRACE CAPABILITY → TASK RESOLUTION
    # =========================================================

    def _build_capability_task_map(
        self,
        occupation: str,
        worktrace: Dict[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Current WorkTrace task output does not expose
        Capability Name directly.

        Therefore the engine resolves capability/task
        relationships from the WorkTrace capability records
        and source task IDs.

        If the WorkTrace engine later exposes an explicit
        task-capability mapping, this method will use it.
        """

        result: Dict[str, List[Dict[str, Any]]] = {}

        tasks = worktrace.get("tasks") or []
        capabilities = worktrace.get("capabilities") or []

        # -----------------------------------------------------
        # First try explicit relationship fields.
        # -----------------------------------------------------

        for task in tasks:

            capability_name = self._extract_capability(
                task
            )

            if capability_name:
                result.setdefault(
                    capability_name,
                    [],
                ).append(task)

        # -----------------------------------------------------
        # If task records do not contain capability names,
        # use the engine's underlying dataframe.
        # -----------------------------------------------------

        if not result:

            try:
                df = getattr(
                    self.worktrace,
                    "df",
                    None,
                )

                if df is not None:

                    occupation_mask = (
                        df["Occupation Title"]
                        .astype(str)
                        .str.strip()
                        .str.lower()
                        == occupation.strip().lower()
                    )

                    subset = df.loc[
                        occupation_mask
                    ]

                    required_columns = {
                        "Capability Name",
                        "Task ID",
                    }

                    if required_columns.issubset(
                        subset.columns
                    ):

                        grouped = (
                            subset[
                                [
                                    "Capability Name",
                                    "Task ID",
                                ]
                            ]
                            .dropna()
                            .drop_duplicates()
                        )

                        task_lookup = {
                            str(
                                task.get("Task ID")
                            ): task
                            for task in tasks
                            if task.get("Task ID")
                            is not None
                        }

                        for row in grouped.itertuples(
                            index=False
                        ):

                            capability_name = (
                                str(
                                    row[0]
                                ).strip()
                            )

                            task_id = str(
                                row[1]
                            ).strip()

                            task = task_lookup.get(
                                task_id
                            )

                            if task:
                                result.setdefault(
                                    capability_name,
                                    [],
                                ).append(task)

            except Exception:
                pass

        # -----------------------------------------------------
        # Deduplicate tasks
        # -----------------------------------------------------

        for capability_name in list(
            result.keys()
        ):

            unique = {}

            for task in result[
                capability_name
            ]:

                task_id = str(
                    task.get("Task ID")
                    or task.get("task_id")
                    or id(task)
                )

                unique[task_id] = task

            result[capability_name] = list(
                unique.values()
            )

        return result

    # =========================================================
    # EVIDENCE
    # =========================================================

    def _get_evidence(
        self,
        occupation: str,
        capability: str,
    ) -> Dict[str, Any]:

        try:
            return (
                self.evidence.get_capability_state(
                    occupation,
                    capability,
                )
                or {
                    "score": None,
                    "status": self.STATUS_NO_EVIDENCE,
                    "attempts": 0,
                    "evidence_count": 0,
                    "confidence": 0.0,
                    "evidence_quality": 0.0,
                }
            )

        except Exception:
            return {
                "score": None,
                "status": self.STATUS_NO_EVIDENCE,
                "attempts": 0,
                "evidence_count": 0,
                "confidence": 0.0,
                "evidence_quality": 0.0,
            }

    @staticmethod
    def _evidence_deficit(
        score: Optional[float],
    ) -> float:

        if score is None:
            # Absence of evidence is not proof of inability.
            # But for prioritisation, no evidence means the
            # largest unresolved evidence deficit.
            return 1.0

        try:
            score = float(score)
        except (
            TypeError,
            ValueError,
        ):
            return 1.0

        score = max(
            0.0,
            min(score, 5.0),
        )

        return 1.0 - (
            score / 5.0
        )

    # =========================================================
    # SKILL SHADOW
    # =========================================================

    def _safe_skill_shadow(
        self,
        occupation: str,
        ai_adoption: float,
    ) -> Any:

        try:

            if hasattr(
                self.skill_shadow,
                "simulate_occupation",
            ):
                return (
                    self.skill_shadow
                    .simulate_occupation(
                        occupation=occupation,
                        ai_adoption=ai_adoption,
                    )
                )

        except Exception:
            pass

        return None

    def _shadow_row(
        self,
        shadow: Any,
        capability: str,
    ) -> Dict[str, Any]:

        rows = self._extract_rows(
            shadow
        )

        for row in rows:

            name = (
                row.get("Capability Name")
                or row.get("capability")
                or row.get("Capability")
                or row.get("name")
            )

            if (
                name
                and str(name).strip().lower()
                == capability.strip().lower()
            ):
                return row

        return {}

    # =========================================================
    # WORKFOLD
    # =========================================================

    def _safe_workfold(
        self,
        occupation: str,
        ai_adoption: float,
    ) -> Any:

        try:

            if hasattr(
                self.workfold,
                "simulate_occupation",
            ):
                return (
                    self.workfold
                    .simulate_occupation(
                        occupation=occupation,
                        target_ai_adoption=ai_adoption,
                    )
                )

        except TypeError:

            try:
                return (
                    self.workfold
                    .simulate_occupation(
                        occupation,
                        ai_adoption,
                    )
                )

            except Exception:
                pass

        except Exception:
            pass

        return None

    def _fold_tasks(
        self,
        fold: Any,
    ) -> List[Dict[str, Any]]:

        if not fold:
            return []

        if isinstance(
            fold,
            dict,
        ):
            tasks = fold.get(
                "tasks"
            )

            if isinstance(
                tasks,
                list,
            ):
                return tasks

        if isinstance(
            fold,
            list,
        ):
            return [
                item
                for item in fold
                if isinstance(
                    item,
                    dict,
                )
            ]

        return []

    # =========================================================
    # TASK MATCHING
    # =========================================================

    def _match_fold_tasks(
        self,
        source_tasks: List[Dict[str, Any]],
        fold_tasks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        fold_lookup = {}

        for task in fold_tasks:

            task_id = (
                task.get("task_id")
                or task.get("Task ID")
                or task.get("id")
            )

            if task_id is not None:
                fold_lookup[
                    str(task_id)
                ] = task

        affected = []

        for source in source_tasks:

            task_id = (
                source.get("Task ID")
                or source.get("task_id")
                or source.get("id")
            )

            if task_id is None:
                continue

            fold_task = fold_lookup.get(
                str(task_id)
            )

            if fold_task:

                merged = dict(source)

                for key, value in fold_task.items():
                    merged[
                        f"workfold_{key}"
                    ] = value

                affected.append(
                    merged
                )

        return affected

    def _calculate_task_impact(
        self,
        tasks: List[Dict[str, Any]],
    ) -> float:

        if not tasks:
            return 0.0

        impacts = []

        for task in tasks:

            criticality = self._number(
                task.get(
                    "workfold_task_criticality"
                ),
                default=0.0,
            )

            preservation = self._number(
                task.get(
                    "workfold_preservation_pressure"
                ),
                default=0.0,
            )

            ai_share = self._number(
                task.get(
                    "workfold_scenario_ai_share"
                ),
                default=0.0,
            )

            human_share = self._number(
                task.get(
                    "workfold_scenario_human_share"
                ),
                default=0.0,
            )

            # WorkFold owns the future allocation.
            # We only combine its returned task signals.
            transformation = max(
                ai_share,
                human_share,
            )

            impact = (
                0.45 * criticality
                + 0.35 * preservation
                + 0.20 * transformation
            )

            impacts.append(
                self._clamp(
                    impact,
                    0.0,
                    1.0,
                )
            )

        return max(
            impacts,
            default=0.0,
        )

    # =========================================================
    # AI RELEVANCE
    # =========================================================

    def _ai_relevance(
        self,
        shadow_row: Dict[str, Any],
        affected_tasks: List[Dict[str, Any]],
    ) -> float:

        capability_risk = self._normalise(
            shadow_row.get(
                "Capability_Risk"
            ),
            default=0.0,
        )

        future_demand = self._normalise(
            shadow_row.get(
                "Future_Demand_Signal"
            ),
            default=0.0,
        )

        ai_share_values = []

        for task in affected_tasks:

            ai_share = self._number(
                task.get(
                    "workfold_scenario_ai_share"
                ),
                default=0.0,
            )

            ai_share_values.append(
                self._clamp(
                    ai_share,
                    0.0,
                    1.0,
                )
            )

        task_ai_share = max(
            ai_share_values,
            default=0.0,
        )

        # If Shadow does not provide future-demand information,
        # the task transformation signal remains usable.
        relevance = (
            0.45 * capability_risk
            + 0.25 * future_demand
            + 0.30 * task_ai_share
        )

        return self._clamp(
            relevance,
            0.0,
            1.0,
        )

    # =========================================================
    # CAPABILITY IMPORTANCE
    # =========================================================

    def _capability_importance(
        self,
        capability: Dict[str, Any],
    ) -> float:

        raw = (
            capability.get(
                "value"
            )
            if capability.get("value")
            is not None
            else capability.get(
                "Occupation Capability Value"
            )
        )

        return self._normalise(
            raw,
            default=0.0,
        )

    # =========================================================
    # CAPABILITY HELPERS
    # =========================================================

    @staticmethod
    def _unique_capabilities(
        capabilities: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        unique = {}
        order = []

        for capability in capabilities:

            name = GapEngine._capability_name(
                capability
            )

            if not name:
                continue

            key = name.strip().lower()

            if key not in unique:
                unique[key] = capability
                order.append(key)

        return [
            unique[key]
            for key in order
        ]

    @staticmethod
    def _capability_name(
        capability: Dict[str, Any],
    ) -> Optional[str]:

        value = (
            capability.get(
                "name"
            )
            or capability.get(
                "Capability Name"
            )
            or capability.get(
                "capability"
            )
        )

        if value is None:
            return None

        return str(value).strip()

    @staticmethod
    def _extract_capability(
        item: Dict[str, Any],
    ) -> Optional[str]:

        value = (
            item.get(
                "Capability Name"
            )
            or item.get(
                "capability"
            )
            or item.get(
                "Capability"
            )
            or item.get(
                "primary_capabilities"
            )
        )

        if value is None:
            return None

        # WorkFold may expose multiple capabilities
        # as a string. This method intentionally returns
        # the full string; exact matching is handled by
        # the caller where necessary.
        return str(value).strip()

    @staticmethod
    def _extract_rows(
        value: Any,
    ) -> List[Dict[str, Any]]:

        if isinstance(
            value,
            list,
        ):
            return [
                item
                for item in value
                if isinstance(
                    item,
                    dict,
                )
            ]

        if isinstance(
            value,
            dict,
        ):

            for key in (
                "capabilities",
                "results",
                "rows",
                "tasks",
                "data",
            ):

                candidate = value.get(
                    key
                )

                if isinstance(
                    candidate,
                    list,
                ):
                    return [
                        item
                        for item in candidate
                        if isinstance(
                            item,
                            dict,
                        )
                    ]

        return []

    # =========================================================
    # REASON / BAND
    # =========================================================

    @staticmethod
    def _priority_band(
        priority: float,
    ) -> str:

        if priority >= 0.70:
            return "HIGH"

        if priority >= 0.40:
            return "MEDIUM"

        return "LOW"

    def _build_reason(
        self,
        capability_name: str,
        evidence: Dict[str, Any],
        evidence_deficit: float,
        importance: float,
        task_impact: float,
        ai_relevance: float,
        affected_tasks: List[Dict[str, Any]],
        priority: float,
    ) -> str:

        status = evidence.get(
            "status",
            self.STATUS_NO_EVIDENCE,
        )

        if status == self.STATUS_NO_EVIDENCE:
            evidence_text = (
                "No validated learner evidence exists yet."
            )

        elif status == self.STATUS_INSUFFICIENT:
            evidence_text = (
                "A learner attempt exists, "
                "but the evidence is insufficient."
            )

        elif status == self.STATUS_PARTIAL:
            evidence_text = (
                "The available evidence shows "
                "partial capability."
            )

        else:
            evidence_text = (
                "Validated evidence indicates "
                "the capability is demonstrated."
            )

        task_text = (
            f"{len(affected_tasks)} affected work task(s)"
            if affected_tasks
            else "no directly mapped work tasks"
        )

        return (
            f"{capability_name}: {evidence_text} "
            f"WorkTrace/WorkFold identify {task_text}. "
            f"Evidence deficit={evidence_deficit:.2f}, "
            f"importance={importance:.2f}, "
            f"work impact={task_impact:.2f}, "
            f"AI relevance={ai_relevance:.2f}. "
            f"Computed gap priority={priority:.2f}."
        )

    # =========================================================
    # NUMERIC HELPERS
    # =========================================================

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:

            if value is None:
                return default

            value = float(value)

            if not math.isfinite(value):
                return default

            return value

        except (
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _normalise(
        value: Any,
        default: float = 0.0,
    ) -> float:

        value = GapEngine._number(
            value,
            default,
        )

        if value <= 1.0:
            return GapEngine._clamp(
                value,
                0.0,
                1.0,
            )

        if value <= 5.0:
            return GapEngine._clamp(
                value / 5.0,
                0.0,
                1.0,
            )

        if value <= 100.0:
            return GapEngine._clamp(
                value / 100.0,
                0.0,
                1.0,
            )

        return 1.0

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )


def create_gap_engine(
    worktrace_engine,
    skill_shadow_engine,
    workfold_engine,
    lattice_engine,
    evidence_service,
) -> GapEngine:

    return GapEngine(
        worktrace_engine=worktrace_engine,
        skill_shadow_engine=skill_shadow_engine,
        workfold_engine=workfold_engine,
        lattice_engine=lattice_engine,
        evidence_service=evidence_service,
    )