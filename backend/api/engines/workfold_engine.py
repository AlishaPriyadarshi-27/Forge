from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — WORKFOLD ENGINE
# ============================================================
#
# Human-AI Workforce Reconfiguration Engine
#
# Pipeline:
#
# AI Adoption Scenario
#        ↓
# Safe AI Boundary
#        ↓
# Task-level Allocation
#        ↓
# AI / Hybrid / Human
#        ↓
# Workforce Design
#
# Based on validated FORGE WORKFOLD V8 outputs.
# ============================================================


ROOT = Path(__file__).resolve().parents[3]

WORKFOLD_PATH = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_workfold_v8.parquet"
)


class WorkFoldEngine:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print(
            "\n[WORKFOLD] Loading V8 intelligence layer..."
        )

        if not WORKFOLD_PATH.exists():

            raise FileNotFoundError(
                f"WORKFOLD dataset not found:\n"
                f"{WORKFOLD_PATH}"
            )

        self.df = pd.read_parquet(
            WORKFOLD_PATH
        )

        self._prepare_data()

        print(
            f"[WORKFOLD] Records: "
            f"{len(self.df):,}"
        )

        print(
            f"[WORKFOLD] Occupations: "
            f"{self.df['Occupation Title'].nunique():,}"
        )

        print(
            f"[WORKFOLD] Tasks: "
            f"{self.df['Task ID'].nunique():,}"
        )


    # ========================================================
    # DATA PREPARATION
    # ========================================================

    def _prepare_data(self):

        numeric_columns = [

            "Task_Capability_Count",

            "Task_Skill_Shadow",

            "Task_Skill_Shadow_Percent",

            "Task_Capability_Risk",

            "Task_Criticality",

            "Task_Evidence_Coverage",

            "Evidence_Confidence_Percent",

            "Automation_Semantic_Score",

            "Human_Semantic_Score",

            "Task_AI_Suitability",

            "Task_AI_Suitability_Percent",

            "Skill_Shadow_Normalized",

            "Capability_Risk_Normalized",

            "Criticality_Normalized",

            "Preservation_Pressure",

            "Preservation_Pressure_Percent",

            "Human_Preservation_Floor",

            "Human_Preservation_Floor_Percent",

            "AI_Ceiling",

            "AI_Allocation_Score",

            "Safe_AI_Bound",

            "Maximum_Safe_AI_Adoption",

            "Maximum_Safe_AI_Adoption_Percent",

            "Requested_Target_Percent",

            "Effective_AI_Target",

            "Effective_AI_Target_Percent",

            "Safe_Target_Gap",

            "Safe_Target_Gap_Percent",

            "AI_Share",

            "AI_Share_Percent",

            "Human_Share",

            "Human_Share_Percent",
        ]


        for column in numeric_columns:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(
                    self.df[column],
                    errors="coerce"
                )


        text_columns = [

            "Occupation Title",

            "Occupation Description",

            "Task",

            "DWA Element Name",

            "Primary_Capabilities",

            "Target_Feasibility",

            "Work_Model",

            "Decision_Explanation",
        ]


        for column in text_columns:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )


        bounded_columns = [

            "Task_AI_Suitability",

            "Skill_Shadow_Normalized",

            "Capability_Risk_Normalized",

            "Criticality_Normalized",

            "Preservation_Pressure",

            "Human_Preservation_Floor",

            "AI_Ceiling",

            "AI_Allocation_Score",

        ]


        for column in bounded_columns:

            if column in self.df.columns:

                self.df[column] = (
                    self.df[column]
                    .fillna(0.0)
                    .clip(0.0, 1.0)
                )


    # ========================================================
    # SAFE FLOAT
    # ========================================================

    @staticmethod
    def safe_float(
        value,
        default=0.0
    ):

        try:

            if pd.isna(value):

                return default

            return float(value)

        except (
            TypeError,
            ValueError
        ):

            return default


    # ========================================================
    # VALIDATE AI ADOPTION
    # ========================================================

    @staticmethod
    def validate_ai_adoption(
        ai_adoption
    ):

        try:

            value = float(
                ai_adoption
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "AI adoption must be numeric."
            )


        # Accept both:
        #
        # 0.40
        # 40
        #

        if value > 1:

            value = value / 100.0


        if value < 0 or value > 1:

            raise ValueError(
                "AI adoption must be between 0 and 100."
            )


        return value


    # ========================================================
    # SEARCH OCCUPATIONS
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


        return (
            self.df.loc[
                mask,
                "Occupation Title"
            ]
            .drop_duplicates()
            .sort_values()
            .head(limit)
            .tolist()
        )


    # ========================================================
    # OCCUPATION SUBSET
    # ========================================================

    def _occupation_subset(
        self,
        occupation: str
    ):

        occupation = str(
            occupation or ""
        ).strip()


        if not occupation:

            return self.df.iloc[
                0:0
            ].copy()


        mask = (
            self.df[
                "Occupation Title"
            ]
            .str.lower()
            ==
            occupation.lower()
        )


        return self.df.loc[
            mask
        ].copy()


    # ========================================================
    # OCCUPATION INFORMATION
    # ========================================================

    def get_occupation(
        self,
        occupation: str
    ):

        subset = self._occupation_subset(
            occupation
        )


        if subset.empty:

            return None


        first = subset.iloc[0]


        work_models = (
            subset[
                "Work_Model"
            ]
            .value_counts()
            .to_dict()
        )


        feasibility = (
            subset[
                "Target_Feasibility"
            ]
            .value_counts()
            .to_dict()
        )


        return {

            "occupation": str(
                first[
                    "Occupation Title"
                ]
            ),

            "occupation_code": str(
                first.get(
                    "O*NET-SOC Code",
                    ""
                )
            ),

            "task_count": int(
                subset[
                    "Task ID"
                ].nunique()
            ),

            "maximum_safe_ai_adoption_percent": round(
                self.safe_float(
                    subset[
                        "Maximum_Safe_AI_Adoption"
                    ].median()
                ) * 100,
                2
            ),

            "v8_mean_ai_share_percent": round(
                self.safe_float(
                    subset[
                        "AI_Share_Percent"
                    ].mean()
                ),
                2
            ),

            "v8_mean_human_share_percent": round(
                self.safe_float(
                    subset[
                        "Human_Share_Percent"
                    ].mean()
                ),
                2
            ),

            "work_model_distribution": (
                work_models
            ),

            "target_feasibility_distribution": (
                feasibility
            )
        }


    # ========================================================
    # SAFE AI BOUNDARY
    # ========================================================

    def _get_safe_boundary(
        self,
        subset
    ):

        values = pd.to_numeric(
            subset[
                "Maximum_Safe_AI_Adoption"
            ],
            errors="coerce"
        ).dropna()


        if values.empty:

            return 1.0


        boundary = float(
            values.median()
        )


        return max(
            0.0,
            min(
                1.0,
                boundary
            )
        )


    # ========================================================
    # ALLOCATION SCORE
    # ========================================================

    def _get_allocation_scores(
        self,
        subset
    ):

        scores = pd.to_numeric(
            subset[
                "AI_Allocation_Score"
            ],
            errors="coerce"
        ).fillna(0.0)


        return scores.clip(
            0.0,
            1.0
        ).to_numpy(
            dtype=float
        )


    # ========================================================
    # CONSTRAINED TASK ALLOCATION
    # ========================================================

    def _allocate_tasks(
        self,
        subset,
        effective_target
    ):

        work = subset.copy()


        number_of_tasks = len(
            work
        )


        if number_of_tasks == 0:

            return work


        # ----------------------------------------------------
        # Task-level AI ceilings
        # ----------------------------------------------------

        ceilings = pd.to_numeric(
            work[
                "AI_Ceiling"
            ],
            errors="coerce"
        ).fillna(0.0)


        ceilings = (
            ceilings
            .clip(0.0, 1.0)
            .to_numpy(
                dtype=float
            )
        )


        # ----------------------------------------------------
        # V8 allocation intelligence
        # ----------------------------------------------------

        scores = (
            self
            ._get_allocation_scores(
                work
            )
        )


        # ----------------------------------------------------
        # Allocation weights
        # ----------------------------------------------------

        if (
            not np.isfinite(
                scores
            ).all()
            or scores.sum() <= 0
        ):

            weights = np.ones(
                number_of_tasks,
                dtype=float
            )

        else:

            weights = (
                scores
                + 0.05
            )


        # ----------------------------------------------------
        # Required total AI allocation
        #
        # Mean allocation should approach
        # the effective occupation target.
        # ----------------------------------------------------

        required_total = (
            effective_target
            * number_of_tasks
        )


        allocation = np.zeros(
            number_of_tasks,
            dtype=float
        )


        remaining = (
            required_total
        )


        active = (
            ceilings > 0
        )


        max_iterations = (
            number_of_tasks * 4
            + 20
        )


        # ----------------------------------------------------
        # Iterative weighted allocation
        # ----------------------------------------------------

        for _ in range(
            max_iterations
        ):

            if remaining <= 1e-10:

                break


            active_indices = np.where(
                active
            )[0]


            if len(
                active_indices
            ) == 0:

                break


            active_weights = (
                weights[
                    active_indices
                ]
            )


            weight_sum = (
                active_weights.sum()
            )


            if weight_sum <= 0:

                active_weights = np.ones(
                    len(
                        active_indices
                    ),
                    dtype=float
                )

                weight_sum = (
                    active_weights.sum()
                )


            proposed = (
                remaining
                *
                active_weights
                /
                weight_sum
            )


            capacity = (
                ceilings[
                    active_indices
                ]
                -
                allocation[
                    active_indices
                ]
            )


            added = np.minimum(
                proposed,
                capacity
            )


            total_added = (
                added.sum()
            )


            allocation[
                active_indices
            ] += added


            remaining -= (
                total_added
            )


            # Remove saturated tasks
            for position, index in enumerate(
                active_indices
            ):

                if (
                    ceilings[index]
                    -
                    allocation[index]
                    <= 1e-10
                ):

                    active[index] = False


            if total_added <= 1e-12:

                break


        allocation = np.clip(
            allocation,
            0.0,
            ceilings
        )


        work[
            "Scenario_AI_Share"
        ] = allocation


        work[
            "Scenario_Human_Share"
        ] = (
            1.0
            - allocation
        )


        return work


    # ========================================================
    # WORK MODEL CLASSIFIER
    # ========================================================

    @staticmethod
    def _work_model(
        ai_share,
        suitability,
        human_floor
    ):

        ai_share = max(
            0.0,
            min(
                1.0,
                ai_share
            )
        )


        suitability = max(
            0.0,
            min(
                1.0,
                suitability
            )
        )


        human_floor = max(
            0.0,
            min(
                1.0,
                human_floor
            )
        )


        # Human-led
        if ai_share <= 0.25:

            return "Human-led"


        # AI-led
        if (
            ai_share >= 0.60
            and suitability >= 0.60
            and (
                1.0 - ai_share
            ) >= (
                human_floor
                - 1e-9
            )
        ):

            return "AI-led"


        # Everything between the two
        # becomes hybrid.
        return "Hybrid"


    # ========================================================
    # DECISION EXPLANATION
    # ========================================================

    def _decision_explanation(
        self,
        row,
        ai_share,
        human_share
    ):

        suitability = self.safe_float(
            row.get(
                "Task_AI_Suitability"
            )
        )


        shadow = self.safe_float(
            row.get(
                "Skill_Shadow_Normalized"
            )
        )


        risk = self.safe_float(
            row.get(
                "Capability_Risk_Normalized"
            )
        )


        pressure = self.safe_float(
            row.get(
                "Preservation_Pressure"
            )
        )


        ceiling = self.safe_float(
            row.get(
                "AI_Ceiling"
            )
        )


        reasons = []


        if suitability >= 0.60:

            reasons.append(
                "high AI suitability"
            )

        elif suitability >= 0.40:

            reasons.append(
                "moderate AI suitability"
            )

        else:

            reasons.append(
                "lower AI suitability"
            )


        if shadow >= 0.60:

            reasons.append(
                "high skill-shadow pressure"
            )

        elif shadow >= 0.40:

            reasons.append(
                "moderate skill-shadow pressure"
            )


        if risk >= 0.60:

            reasons.append(
                "high capability risk"
            )

        elif risk >= 0.40:

            reasons.append(
                "moderate capability risk"
            )


        if pressure >= 0.60:

            reasons.append(
                "high preservation pressure"
            )


        if (
            ai_share
            >= ceiling - 1e-6
        ):

            reasons.append(
                "task AI ceiling reached"
            )


        model = self._work_model(
            ai_share,
            suitability,
            1.0 - ceiling
        )


        return (
            f"{model}: "
            f"AI allocation "
            f"{ai_share * 100:.1f}%, "
            f"human allocation "
            f"{human_share * 100:.1f}%. "
            f"Signals: "
            + ", ".join(
                reasons
            )
            + "."
        )


    # ========================================================
    # MAIN WORKFOLD SIMULATION
    # ========================================================

    def simulate_occupation(
        self,
        occupation: str,
        ai_adoption: float
    ):

        subset = self._occupation_subset(
            occupation
        )


        if subset.empty:

            return None


        requested_target = (
            self.validate_ai_adoption(
                ai_adoption
            )
        )


        safe_boundary = (
            self._get_safe_boundary(
                subset
            )
        )


        # ----------------------------------------------------
        # Safety constraint
        # ----------------------------------------------------

        effective_target = min(
            requested_target,
            safe_boundary
        )


        safe_boundary_active = (
            requested_target
            > safe_boundary
        )


        # ----------------------------------------------------
        # Allocate AI across tasks
        # ----------------------------------------------------

        allocated = (
            self._allocate_tasks(
                subset,
                effective_target
            )
        )


        tasks = []


        # ----------------------------------------------------
        # Build task-level intelligence
        # ----------------------------------------------------

        for _, row in allocated.iterrows():

            ai_share = self.safe_float(
                row[
                    "Scenario_AI_Share"
                ]
            )


            human_share = self.safe_float(
                row[
                    "Scenario_Human_Share"
                ]
            )


            suitability = self.safe_float(
                row[
                    "Task_AI_Suitability"
                ]
            )


            human_floor = self.safe_float(
                row[
                    "Human_Preservation_Floor"
                ]
            )


            work_model = (
                self._work_model(
                    ai_share,
                    suitability,
                    human_floor
                )
            )


            tasks.append({

                "task_id": str(
                    row[
                        "Task ID"
                    ]
                ),

                "task": str(
                    row[
                        "Task"
                    ]
                ),

                "dwa": str(
                    row[
                        "DWA Element Name"
                    ]
                ),

                "primary_capabilities": str(
                    row[
                        "Primary_Capabilities"
                    ]
                ),

                "task_ai_suitability": round(
                    suitability,
                    4
                ),

                "task_ai_suitability_percent": round(
                    suitability * 100,
                    2
                ),

                "task_skill_shadow": round(
                    self.safe_float(
                        row[
                            "Task_Skill_Shadow"
                        ]
                    ),
                    4
                ),

                "task_skill_shadow_percent": round(
                    self.safe_float(
                        row[
                            "Task_Skill_Shadow_Percent"
                        ]
                    ),
                    2
                ),

                "task_capability_risk": round(
                    self.safe_float(
                        row[
                            "Task_Capability_Risk"
                        ]
                    ),
                    4
                ),

                "task_criticality": round(
                    self.safe_float(
                        row[
                            "Task_Criticality"
                        ]
                    ),
                    4
                ),

                "preservation_pressure": round(
                    self.safe_float(
                        row[
                            "Preservation_Pressure"
                        ]
                    ),
                    4
                ),

                "preservation_pressure_percent": round(
                    self.safe_float(
                        row[
                            "Preservation_Pressure_Percent"
                        ]
                    ),
                    2
                ),

                "human_preservation_floor": round(
                    human_floor,
                    4
                ),

                "human_preservation_floor_percent": round(
                    human_floor * 100,
                    2
                ),

                "ai_ceiling": round(
                    self.safe_float(
                        row[
                            "AI_Ceiling"
                        ]
                    ),
                    4
                ),

                "ai_ceiling_percent": round(
                    self.safe_float(
                        row[
                            "AI_Ceiling"
                        ]
                    ) * 100,
                    2
                ),

                "ai_allocation_score": round(
                    self.safe_float(
                        row[
                            "AI_Allocation_Score"
                        ]
                    ),
                    4
                ),

                "scenario_ai_share": round(
                    ai_share,
                    4
                ),

                "scenario_ai_share_percent": round(
                    ai_share * 100,
                    2
                ),

                "scenario_human_share": round(
                    human_share,
                    4
                ),

                "scenario_human_share_percent": round(
                    human_share * 100,
                    2
                ),

                "work_model": work_model,

                "decision_explanation": (
                    self._decision_explanation(
                        row,
                        ai_share,
                        human_share
                    )
                )
            })


        # ----------------------------------------------------
        # Sort by AI allocation
        # ----------------------------------------------------

        tasks.sort(
            key=lambda item: (
                item[
                    "scenario_ai_share"
                ],
                item[
                    "ai_allocation_score"
                ]
            ),
            reverse=True
        )


        # ----------------------------------------------------
        # Aggregate metrics
        # ----------------------------------------------------

        ai_values = np.array([
            item[
                "scenario_ai_share"
            ]
            for item in tasks
        ])


        human_values = np.array([
            item[
                "scenario_human_share"
            ]
            for item in tasks
        ])


        shadow_values = np.array([
            item[
                "task_skill_shadow"
            ]
            for item in tasks
        ])


        risk_values = np.array([
            item[
                "task_capability_risk"
            ]
            for item in tasks
        ])


        pressure_values = np.array([
            item[
                "preservation_pressure"
            ]
            for item in tasks
        ])


        suitability_values = np.array([
            item[
                "task_ai_suitability"
            ]
            for item in tasks
        ])


        # ----------------------------------------------------
        # Work model distribution
        # ----------------------------------------------------

        model_counts = {}


        for item in tasks:

            model = item[
                "work_model"
            ]

            model_counts[
                model
            ] = (
                model_counts.get(
                    model,
                    0
                )
                + 1
            )


        # ----------------------------------------------------
        # Target gap
        # ----------------------------------------------------

        safe_target_gap = max(
            0.0,
            requested_target
            - safe_boundary
        )


        # ----------------------------------------------------
        # Decision status
        # ----------------------------------------------------

        if safe_boundary_active:

            decision_status = (
                "SAFE_BOUNDARY_ACTIVE"
            )

            decision_message = (
                "Requested AI adoption exceeds "
                "the V8-derived safe operating "
                "boundary. The effective scenario "
                "has been capped at the safe target."
            )

        else:

            decision_status = (
                "WITHIN_SAFE_BOUNDARY"
            )

            decision_message = (
                "Requested AI adoption is within "
                "the V8-derived safe operating "
                "boundary."
            )


        # ----------------------------------------------------
        # Return
        # ----------------------------------------------------

        return {

            "occupation": occupation,

            "scenario": {

                "requested_ai_adoption": round(
                    requested_target,
                    4
                ),

                "requested_ai_adoption_percent": round(
                    requested_target * 100,
                    2
                ),

                "maximum_safe_ai_adoption": round(
                    safe_boundary,
                    4
                ),

                "maximum_safe_ai_adoption_percent": round(
                    safe_boundary * 100,
                    2
                ),

                "effective_ai_target": round(
                    effective_target,
                    4
                ),

                "effective_ai_target_percent": round(
                    effective_target * 100,
                    2
                ),

                "safe_target_gap": round(
                    safe_target_gap,
                    4
                ),

                "safe_target_gap_percent": round(
                    safe_target_gap * 100,
                    2
                ),

                "safe_boundary_active": (
                    safe_boundary_active
                )
            },

            "workforce_summary": {

                "task_count": len(
                    tasks
                ),

                "mean_ai_share_percent": round(
                    float(
                        ai_values.mean()
                    ) * 100,
                    2
                ),

                "mean_human_share_percent": round(
                    float(
                        human_values.mean()
                    ) * 100,
                    2
                ),

                "mean_skill_shadow_percent": round(
                    float(
                        shadow_values.mean()
                    ) * 100,
                    2
                ),

                "mean_capability_risk_percent": round(
                    float(
                        risk_values.mean()
                    ) * 100,
                    2
                ),

                "mean_preservation_pressure_percent": round(
                    float(
                        pressure_values.mean()
                    ) * 100,
                    2
                ),

                "mean_task_ai_suitability_percent": round(
                    float(
                        suitability_values.mean()
                    ) * 100,
                    2
                ),

                "work_model_counts": (
                    model_counts
                )
            },

            "decision": {

                "status": decision_status,

                "message": decision_message
            },

            "top_ai_allocated_tasks": (
                sorted(
                    tasks,
                    key=lambda item:
                    item[
                        "scenario_ai_share"
                    ],
                    reverse=True
                )[:10]
            ),

            "preservation_priority_tasks": (
                sorted(
                    tasks,
                    key=lambda item: (
                        item[
                            "preservation_pressure"
                        ],
                        item[
                            "task_skill_shadow"
                        ],
                        item[
                            "task_capability_risk"
                        ]
                    ),
                    reverse=True
                )[:10]
            ),

            "tasks": tasks
        }


    # ========================================================
    # COUNTERFACTUAL SCENARIO
    # ========================================================

    def compare_scenarios(
        self,
        occupation: str,
        baseline_ai: float,
        future_ai: float
    ):

        baseline = (
            self.simulate_occupation(
                occupation,
                baseline_ai
            )
        )


        future = (
            self.simulate_occupation(
                occupation,
                future_ai
            )
        )


        if baseline is None:

            return None


        if future is None:

            return None


        # ----------------------------------------------------
        # Task maps
        # ----------------------------------------------------

        baseline_map = {

            task[
                "task_id"
            ]: task

            for task in baseline[
                "tasks"
            ]
        }


        future_map = {

            task[
                "task_id"
            ]: task

            for task in future[
                "tasks"
            ]
        }


        changes = []


        # ----------------------------------------------------
        # Task-by-task counterfactual comparison
        # ----------------------------------------------------

        for task_id in baseline_map:

            if task_id not in future_map:

                continue


            before = baseline_map[
                task_id
            ]

            after = future_map[
                task_id
            ]


            changes.append({

                "task_id": task_id,

                "task": before[
                    "task"
                ],

                "ai_share_before_percent": (
                    before[
                        "scenario_ai_share_percent"
                    ]
                ),

                "ai_share_after_percent": (
                    after[
                        "scenario_ai_share_percent"
                    ]
                ),

                "ai_share_change_percent": round(
                    after[
                        "scenario_ai_share_percent"
                    ]
                    -
                    before[
                        "scenario_ai_share_percent"
                    ],
                    2
                ),

                "human_share_before_percent": (
                    before[
                        "scenario_human_share_percent"
                    ]
                ),

                "human_share_after_percent": (
                    after[
                        "scenario_human_share_percent"
                    ]
                ),

                "human_share_change_percent": round(
                    after[
                        "scenario_human_share_percent"
                    ]
                    -
                    before[
                        "scenario_human_share_percent"
                    ],
                    2
                ),

                "work_model_before": (
                    before[
                        "work_model"
                    ]
                ),

                "work_model_after": (
                    after[
                        "work_model"
                    ]
                ),

                "preservation_pressure": (
                    before[
                        "preservation_pressure"
                    ]
                ),

                "skill_shadow_percent": (
                    before[
                        "task_skill_shadow_percent"
                    ]
                ),

                "capability_risk": (
                    before[
                        "task_capability_risk"
                    ]
                )
            })


        # ----------------------------------------------------
        # Biggest allocation changes first
        # ----------------------------------------------------

        changes.sort(
            key=lambda item: abs(
                item[
                    "ai_share_change_percent"
                ]
            ),
            reverse=True
        )


        baseline_summary = (
            baseline[
                "workforce_summary"
            ]
        )


        future_summary = (
            future[
                "workforce_summary"
            ]
        )


        return {

            "occupation": occupation,

            "baseline": baseline,

            "future": future,

            "delta": {

                "requested_ai_adoption_change_percent": round(
                    future[
                        "scenario"
                    ][
                        "requested_ai_adoption_percent"
                    ]
                    -
                    baseline[
                        "scenario"
                    ][
                        "requested_ai_adoption_percent"
                    ],
                    2
                ),

                "effective_ai_target_change_percent": round(
                    future[
                        "scenario"
                    ][
                        "effective_ai_target_percent"
                    ]
                    -
                    baseline[
                        "scenario"
                    ][
                        "effective_ai_target_percent"
                    ],
                    2
                ),

                "mean_ai_share_change_percent": round(
                    future_summary[
                        "mean_ai_share_percent"
                    ]
                    -
                    baseline_summary[
                        "mean_ai_share_percent"
                    ],
                    2
                ),

                "mean_human_share_change_percent": round(
                    future_summary[
                        "mean_human_share_percent"
                    ]
                    -
                    baseline_summary[
                        "mean_human_share_percent"
                    ],
                    2
                ),

                "mean_skill_shadow_change_percent": round(
                    future_summary[
                        "mean_skill_shadow_percent"
                    ]
                    -
                    baseline_summary[
                        "mean_skill_shadow_percent"
                    ],
                    2
                ),

                "mean_capability_risk_change_percent": round(
                    future_summary[
                        "mean_capability_risk_percent"
                    ]
                    -
                    baseline_summary[
                        "mean_capability_risk_percent"
                    ],
                    2
                )
            },

            "largest_task_allocation_changes": (
                changes[:15]
            )
        }


    # ========================================================
    # ENGINE SUMMARY
    # ========================================================

    def summary(self):

        safe_values = pd.to_numeric(
            self.df[
                "Maximum_Safe_AI_Adoption"
            ],
            errors="coerce"
        )


        mean_safe_adoption = (
            self.safe_float(
                safe_values.mean()
            )
        )


        mean_ai_share = (
            self.safe_float(
                self.df[
                    "AI_Share_Percent"
                ].mean()
            )
        )


        return {

            "records": int(
                len(self.df)
            ),

            "occupations": int(
                self.df[
                    "Occupation Title"
                ].nunique()
            ),

            "tasks": int(
                self.df[
                    "Task ID"
                ].nunique()
            ),

            "mean_v8_ai_share_percent": round(
                mean_ai_share,
                2
            ),

            "mean_maximum_safe_ai_adoption_percent": round(
                mean_safe_adoption * 100,
                2
            ),

            "engine": (
                "V8-constrained Human-AI "
                "work allocation simulator"
            ),

            "allocation_signal": (
                "AI_Allocation_Score"
            ),

            "constraint_signals": [

                "AI_Ceiling",

                "Human_Preservation_Floor",

                "Maximum_Safe_AI_Adoption"
            ]
        }


# ============================================================
# SINGLE ENGINE INSTANCE
# ============================================================

workfold_engine = WorkFoldEngine()