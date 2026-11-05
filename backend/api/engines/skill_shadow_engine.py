from pathlib import Path
from typing import Optional

import pandas as pd


# ============================================================
# FORGE — SKILL SHADOW ENGINE
# ============================================================
#
# Purpose:
# Simulate how AI adoption changes human capability exposure.
#
# Core idea:
#
#       Pre-AI Human Exposure
#                ↓
#       AI Adoption Scenario
#                ↓
#       Automation Suitability
#                ↓
#       Post-AI Human Exposure
#                ↓
#       Skill Shadow
#                ↓
#       Capability Risk
#
# This engine is scenario-based.
# It does NOT claim that AI adoption is an observed probability.
# ============================================================


ROOT = Path(__file__).resolve().parents[3]

SKILL_SHADOW_PATH = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)


class SkillShadowEngine:

    def __init__(self):

        print("\n[SKILL SHADOW] Loading intelligence layer...")

        self.df = pd.read_parquet(
            SKILL_SHADOW_PATH
        )

        self._prepare_data()

        print(
            f"[SKILL SHADOW] Records: "
            f"{len(self.df):,}"
        )

        print(
            f"[SKILL SHADOW] Occupations: "
            f"{self.df['Occupation Title'].nunique():,}"
        )

        print(
            f"[SKILL SHADOW] Capabilities: "
            f"{self.df['Capability Name'].nunique():,}"
        )

        # Inject the SAME EvidenceService instance used by LATTICE.
        self.evidence_service = None


    def set_evidence_service(self, evidence_service):
        """Attach the shared LATTICE EvidenceService instance."""
        self.evidence_service = evidence_service
        print("[SKILL SHADOW] Shared EvidenceService attached")


    # ========================================================
    # DATA PREPARATION
    # ========================================================

    def _prepare_data(self):

        numeric_columns = [

            "AI_Adoption_Percent",

            "Task_Count",

            "Pre_AI_Exposure",

            "Post_AI_Exposure",

            "Exposure_Lost",

            "Avg_Automation_Suitability",

            "Avg_AI_Share",

            "Skill_Shadow",

            "Skill_Shadow_Percent",

            "Exposure_Criticality",

            "Market_Criticality",

            "Future_Demand_Signal",

            "Capability_Criticality",

            "Capability_Risk",

            "Capability_Risk_Percent",

            "Market_Job_Count",

            "Market_Avg_Similarity",

            "Employment_Change_Percent",

            "Annual_Openings_Thousands",
        ]


        for column in numeric_columns:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(
                    self.df[column],
                    errors="coerce"
                )


        # ----------------------------------------------------
        # Clean occupation/capability strings
        # ----------------------------------------------------

        self.df[
            "Occupation Title"
        ] = (
            self.df[
                "Occupation Title"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        self.df[
            "Capability Name"
        ] = (
            self.df[
                "Capability Name"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        self.df[
            "Capability Type"
        ] = (
            self.df[
                "Capability Type"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


    # ========================================================
    # OCCUPATION SEARCH
    # ========================================================

    def search_occupations(
        self,
        query: str,
        limit: int = 20
    ):

        query = str(
            query or ""
        ).strip().lower()


        if not query:

            return []


        mask = (
            self.df[
                "Occupation Title"
            ]
            .str.lower()
            .str.contains(
                query,
                regex=False
            )
        )


        occupations = (
            self.df.loc[
                mask,
                "Occupation Title"
            ]
            .drop_duplicates()
            .sort_values()
            .head(limit)
            .tolist()
        )


        return occupations


    # ========================================================
    # VALIDATE AI ADOPTION
    # ========================================================

    @staticmethod
    def validate_ai_adoption(
        ai_adoption: float
    ):

        try:

            ai_adoption = float(
                ai_adoption
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "AI adoption must be a number."
            )


        # ----------------------------------------------------
        # Accept either:
        #
        # 0.30
        # OR
        # 30
        #
        # Internally use 0–1.
        # ----------------------------------------------------

        if ai_adoption > 1:

            ai_adoption = (
                ai_adoption / 100.0
            )


        if not (
            0 <= ai_adoption <= 1
        ):

            raise ValueError(
                "AI adoption must be between 0 and 100%."
            )


        return ai_adoption


    # ========================================================
    # SINGLE CAPABILITY SIMULATION
    # ========================================================

    def simulate_capability(
        self,
        row,
        ai_adoption: float
    ):

        adoption = (
            self.validate_ai_adoption(
                ai_adoption
            )
        )


        # ----------------------------------------------------
        # Base human exposure
        # ----------------------------------------------------

        pre_exposure = float(
            row.get(
                "Pre_AI_Exposure",
                0
            )
            or 0
        )


        # ----------------------------------------------------
        # Automation suitability
        #
        # This is a semantic scenario signal
        # from FORGE's existing Skill Shadow layer.
        # ----------------------------------------------------

        automation = float(
            row.get(
                "Avg_Automation_Suitability",
                0
            )
            or 0
        )


        automation = max(
            0.0,
            min(
                1.0,
                automation
            )
        )


        # ----------------------------------------------------
        # Dynamic human exposure
        #
        # Higher AI adoption +
        # higher automation suitability
        # → lower human exposure.
        # ----------------------------------------------------

        post_exposure = (
            pre_exposure
            * (
                1.0
                - adoption
                * automation
            )
        )


        post_exposure = max(
            0.0,
            post_exposure
        )


        # ----------------------------------------------------
        # Exposure lost
        # ----------------------------------------------------

        exposure_lost = max(
            0.0,
            pre_exposure
            - post_exposure
        )


        # ----------------------------------------------------
        # Skill Shadow
        #
        # Fraction of pre-AI human exposure
        # that disappears under the scenario.
        # ----------------------------------------------------

        if pre_exposure > 0:

            skill_shadow = (
                exposure_lost
                / pre_exposure
            )

        else:

            skill_shadow = 0.0


        skill_shadow = max(
            0.0,
            min(
                1.0,
                skill_shadow
            )
        )


        # ----------------------------------------------------
        # Criticality
        # ----------------------------------------------------

        criticality = float(
            row.get(
                "Capability_Criticality",
                0
            )
            or 0
        )


        criticality = max(
            0.0,
            min(
                1.0,
                criticality
            )
        )


        # ----------------------------------------------------
        # Risk
        #
        # FORGE scenario risk:
        #
        # Skill Shadow × Capability Criticality
        # ----------------------------------------------------

        capability_risk = (
            skill_shadow
            * criticality
        )


        # ----------------------------------------------------
        # Human exposure percentage
        # ----------------------------------------------------

        if pre_exposure > 0:

            human_exposure_percent = (
                post_exposure
                / pre_exposure
                * 100
            )

        else:

            human_exposure_percent = 0.0


        # ----------------------------------------------------
        # AI transformation percentage
        # ----------------------------------------------------

        ai_transformation_percent = (
            skill_shadow
            * 100
        )


        return {

            "ai_adoption": round(
                adoption,
                4
            ),

            "ai_adoption_percent": round(
                adoption * 100,
                2
            ),

            "pre_ai_exposure": round(
                pre_exposure,
                4
            ),

            "post_ai_exposure": round(
                post_exposure,
                4
            ),

            "exposure_lost": round(
                exposure_lost,
                4
            ),

            "human_exposure_percent": round(
                human_exposure_percent,
                2
            ),

            "automation_suitability": round(
                automation,
                4
            ),

            "skill_shadow": round(
                skill_shadow,
                4
            ),

            "skill_shadow_percent": round(
                ai_transformation_percent,
                2
            ),

            "capability_criticality": round(
                criticality,
                4
            ),

            "capability_risk": round(
                capability_risk,
                4
            ),

            "capability_risk_percent": round(
                capability_risk * 100,
                2
            ),

            "risk_band": self._risk_band(
                capability_risk
            ),
        }


    # ========================================================
    # RISK BAND
    # ========================================================

    @staticmethod
    def _risk_band(
        risk: float
    ):

        if risk < 0.10:

            return "Low"

        elif risk < 0.20:

            return "Moderate"

        elif risk < 0.35:

            return "Elevated"

        elif risk < 0.50:

            return "High"

        else:

            return "Critical"


    # ========================================================
    # USER EVIDENCE / CAPABILITY STATE
    # ========================================================

    def _get_user_evidence(
        self,
        occupation: str,
        capability: str,
    ):
        """Read validated learner evidence from the shared EvidenceService."""
        default = {
            "score": None,
            "max_score": 5.0,
            "status": "NO_VALIDATED_EVIDENCE",
            "attempts": 0,
            "evidence_count": 0,
            "confidence": 0.0,
            "evidence_quality": 0.0,
            "latest_evidence_id": None,
            "latest_score": None,
            "latest_status": "NO_VALIDATED_EVIDENCE",
        }

        if self.evidence_service is None:
            return default

        try:
            state = self.evidence_service.get_capability_state(
                occupation,
                capability,
            )
            if not isinstance(state, dict):
                return default
            return {**default, **state}
        except Exception as exc:
            print(
                f"[SKILL SHADOW] Evidence lookup failed | "
                f"capability={capability} | error={exc}"
            )
            return default


    @staticmethod
    def _evidence_adjusted_state(
        risk_band: str,
        evidence: dict,
    ):
        """Combine workforce AI-risk with validated learner evidence.

        AI risk is preserved as its own signal. This creates a separate,
        evidence-aware capability state.
        """
        status = str(
            evidence.get("status")
            or "NO_VALIDATED_EVIDENCE"
        ).upper()

        if status == "NO_VALIDATED_EVIDENCE":
            return "UNVALIDATED"

        if status == "INSUFFICIENT_EVIDENCE":
            return "INSUFFICIENT_EVIDENCE"

        if status == "DEMONSTRATED":
            if risk_band in {"High", "Critical"}:
                return "DEMONSTRATED_HIGH_AI_RISK"
            return "DEMONSTRATED"

        if status == "PARTIAL":
            if risk_band in {"High", "Critical"}:
                return "HIGH_PRIORITY_GAP"
            return "DEVELOPING"

        return "UNVALIDATED"


    # ========================================================
    # OCCUPATION SIMULATION
    # ========================================================

    def simulate_occupation(
        self,
        occupation: str,
        ai_adoption: float
    ):

        occupation = str(
            occupation or ""
        ).strip()


        if not occupation:

            return None


        adoption = (
            self.validate_ai_adoption(
                ai_adoption
            )
        )


        mask = (
            self.df[
                "Occupation Title"
            ]
            .str.lower()
            == occupation.lower()
        )


        subset = self.df.loc[
            mask
        ].copy()


        if subset.empty:

            return None


        # ----------------------------------------------------
        # Simulate every capability
        # ----------------------------------------------------

        capability_results = []


        for _, row in subset.iterrows():

            simulation = (
                self.simulate_capability(
                    row,
                    adoption
                )
            )


            capability_name = str(
                row.get(
                    "Capability Name",
                    ""
                )
            ).strip()

            user_evidence = self._get_user_evidence(
                occupation,
                capability_name,
            )

            result = {

                "capability_key": str(
                    row.get(
                        "Capability Key",
                        ""
                    )
                ),

                "capability_type": str(
                    row.get(
                        "Capability Type",
                        ""
                    )
                ),

                "capability_id": str(
                    row.get(
                        "Capability ID",
                        ""
                    )
                ),

                "capability": capability_name,

                "task_count": int(
                    row.get(
                        "Task_Count",
                        0
                    )
                    or 0
                ),

                "market_job_count": int(
                    row.get(
                        "Market_Job_Count",
                        0
                    )
                    or 0
                ),

                "future_demand_signal": self._safe_float(
                    row.get(
                        "Future_Demand_Signal"
                    )
                ),

                "employment_change_percent": self._safe_float(
                    row.get(
                        "Employment_Change_Percent"
                    )
                ),

                # Workforce-side AI risk remains independent.
                "ai_risk_band": simulation["risk_band"],

                # Actual learner evidence from LATTICE.
                "user_evidence": user_evidence,
                "user_evidence_score": user_evidence.get("score"),
                "user_evidence_status": user_evidence.get(
                    "status",
                    "NO_VALIDATED_EVIDENCE",
                ),
                "user_evidence_attempts": user_evidence.get(
                    "attempts",
                    0,
                ),
                "user_evidence_confidence": user_evidence.get(
                    "confidence",
                    0.0,
                ),

                # Combined interpretation; does not overwrite AI risk.
                "evidence_adjusted_state": self._evidence_adjusted_state(
                    simulation["risk_band"],
                    user_evidence,
                ),

                **simulation
            }


            capability_results.append(
                result
            )


        # ----------------------------------------------------
        # Remove duplicate capabilities
        # ----------------------------------------------------

        unique = {}

        for result in capability_results:

            key = (
                result["capability_type"],
                result["capability_id"]
            )

            if key not in unique:

                unique[key] = result

            else:

                # Keep the more risky instance
                if (
                    result["capability_risk"]
                    >
                    unique[key]["capability_risk"]
                ):

                    unique[key] = result


        capability_results = list(
            unique.values()
        )


        # ----------------------------------------------------
        # Sort by risk
        # ----------------------------------------------------

        capability_results.sort(
            key=lambda x: (
                x["capability_risk"],
                x["skill_shadow"],
                x["capability_criticality"],
            ),
            reverse=True
        )


        # ----------------------------------------------------
        # Aggregate occupation-level indicators
        # ----------------------------------------------------

        if capability_results:

            avg_shadow = sum(
                x["skill_shadow"]
                for x in capability_results
            ) / len(
                capability_results
            )


            avg_risk = sum(
                x["capability_risk"]
                for x in capability_results
            ) / len(
                capability_results
            )


            avg_human_exposure = sum(
                x["human_exposure_percent"]
                for x in capability_results
            ) / len(
                capability_results
            )

        else:

            avg_shadow = 0.0
            avg_risk = 0.0
            avg_human_exposure = 0.0


        # ----------------------------------------------------
        # Highest-risk capabilities
        # ----------------------------------------------------

        top_risk = capability_results[:5]

        validated_evidence = [
            x for x in capability_results
            if x.get("user_evidence_status")
            in {"DEMONSTRATED", "PARTIAL", "INSUFFICIENT_EVIDENCE"}
        ]

        demonstrated_count = sum(
            1 for x in capability_results
            if x.get("user_evidence_status") == "DEMONSTRATED"
        )

        partial_count = sum(
            1 for x in capability_results
            if x.get("user_evidence_status") == "PARTIAL"
        )

        high_priority_gap_count = sum(
            1 for x in capability_results
            if x.get("evidence_adjusted_state") == "HIGH_PRIORITY_GAP"
        )


        return {

            "occupation": occupation,

            "ai_adoption": round(
                adoption,
                4
            ),

            "ai_adoption_percent": round(
                adoption * 100,
                2
            ),

            "capability_count": len(
                capability_results
            ),

            "average_skill_shadow": round(
                avg_shadow,
                4
            ),

            "average_skill_shadow_percent": round(
                avg_shadow * 100,
                2
            ),

            "average_capability_risk": round(
                avg_risk,
                4
            ),

            "average_capability_risk_percent": round(
                avg_risk * 100,
                2
            ),

            "average_human_exposure_percent": round(
                avg_human_exposure,
                2
            ),

            "top_risk_capabilities": top_risk,

            "user_evidence_summary": {
                "validated_capability_count": len(validated_evidence),
                "demonstrated_count": demonstrated_count,
                "partial_count": partial_count,
                "high_priority_gap_count": high_priority_gap_count,
            },

            "capabilities": capability_results
        }


    # ========================================================
    # COMPARE TWO AI SCENARIOS
    # ========================================================

    def compare_scenarios(
        self,
        occupation: str,
        baseline_ai: float,
        future_ai: float
    ):

        baseline = self.simulate_occupation(
            occupation,
            baseline_ai
        )


        future = self.simulate_occupation(
            occupation,
            future_ai
        )


        if baseline is None:

            return None


        if future is None:

            return None


        # ----------------------------------------------------
        # Capability comparison
        # ----------------------------------------------------

        baseline_map = {

            (
                x["capability_type"],
                x["capability_id"]
            ): x

            for x in baseline[
                "capabilities"
            ]
        }


        future_map = {

            (
                x["capability_type"],
                x["capability_id"]
            ): x

            for x in future[
                "capabilities"
            ]
        }


        changes = []


        for key in baseline_map:

            if key not in future_map:

                continue


            before = baseline_map[
                key
            ]

            after = future_map[
                key
            ]


            changes.append({

                "capability": before[
                    "capability"
                ],

                "capability_type": before[
                    "capability_type"
                ],

                "skill_shadow_before": before[
                    "skill_shadow_percent"
                ],

                "skill_shadow_after": after[
                    "skill_shadow_percent"
                ],

                "skill_shadow_change": round(
                    after[
                        "skill_shadow_percent"
                    ]
                    -
                    before[
                        "skill_shadow_percent"
                    ],
                    2
                ),

                "risk_before": before[
                    "capability_risk_percent"
                ],

                "risk_after": after[
                    "capability_risk_percent"
                ],

                "risk_change": round(
                    after[
                        "capability_risk_percent"
                    ]
                    -
                    before[
                        "capability_risk_percent"
                    ],
                    2
                ),

                "human_exposure_before": before[
                    "human_exposure_percent"
                ],

                "human_exposure_after": after[
                    "human_exposure_percent"
                ],

                "human_exposure_change": round(
                    after[
                        "human_exposure_percent"
                    ]
                    -
                    before[
                        "human_exposure_percent"
                    ],
                    2
                )
            })


        changes.sort(
            key=lambda x: x[
                "skill_shadow_change"
            ],
            reverse=True
        )


        # ----------------------------------------------------
        # Overall scenario change
        # ----------------------------------------------------

        return {

            "occupation": occupation,

            "baseline": baseline,

            "future": future,

            "scenario_change": {

                "ai_adoption_change": round(
                    future[
                        "ai_adoption_percent"
                    ]
                    -
                    baseline[
                        "ai_adoption_percent"
                    ],
                    2
                ),

                "skill_shadow_change": round(
                    future[
                        "average_skill_shadow_percent"
                    ]
                    -
                    baseline[
                        "average_skill_shadow_percent"
                    ],
                    2
                ),

                "risk_change": round(
                    future[
                        "average_capability_risk_percent"
                    ]
                    -
                    baseline[
                        "average_capability_risk_percent"
                    ],
                    2
                ),

                "human_exposure_change": round(
                    future[
                        "average_human_exposure_percent"
                    ]
                    -
                    baseline[
                        "average_human_exposure_percent"
                    ],
                    2
                )
            },

            "capability_changes": changes
        }


    # ========================================================
    # SINGLE OCCUPATION DATA
    # ========================================================

    def get_occupation(
        self,
        occupation: str
    ):

        occupation = str(
            occupation or ""
        ).strip()


        mask = (
            self.df[
                "Occupation Title"
            ]
            .str.lower()
            ==
            occupation.lower()
        )


        subset = self.df.loc[
            mask
        ].copy()


        if subset.empty:

            return None


        first = subset.iloc[0]


        return {

            "occupation": occupation,

            "occupation_code": str(
                first.get(
                    "O*NET-SOC Code",
                    ""
                )
            ),

            "soc_7": str(
                first.get(
                    "SOC_7",
                    ""
                )
            ),

            "description": str(
                first.get(
                    "Occupation Description",
                    ""
                )
            ),

            "capability_count": int(
                subset[
                    "Capability Name"
                ].nunique()
            ),

            "records": int(
                len(subset)
            )
        }


    # ========================================================
    # ENGINE SUMMARY
    # ========================================================

    def summary(self):

        return {

            "records": int(
                len(self.df)
            ),

            "occupations": int(
                self.df[
                    "Occupation Title"
                ].nunique()
            ),

            "capabilities": int(
                self.df[
                    "Capability Name"
                ].nunique()
            ),

            "default_dataset_ai_adoption": (
                self._safe_float(
                    self.df[
                        "AI_Adoption_Percent"
                    ].median()
                )
            ),

            "engine": (
                "Dynamic scenario-based "
                "Skill Shadow simulation"
            ),

            "formula": (
                "Post Exposure = "
                "Pre Exposure × "
                "(1 − AI Adoption × "
                "Automation Suitability)"
            )
        }


    # ========================================================
    # SAFE FLOAT
    # ========================================================

    @staticmethod
    def _safe_float(
        value
    ):

        try:

            if pd.isna(value):

                return None


            return round(
                float(value),
                4
            )

        except (
            TypeError,
            ValueError
        ):

            return None


# ============================================================
# SINGLE ENGINE INSTANCE
# ============================================================

skill_shadow_engine = (
    SkillShadowEngine()
)