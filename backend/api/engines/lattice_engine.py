from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — LATTICE INTELLIGENCE ENGINE
# ============================================================
#
# LATTICE
# Learning Architecture for Talent Transformation,
# Capability Preservation & Evidence
#
# Purpose:
#
# WORKFOLD
#    ↓
# identify transformed work
#    ↓
# LATTICE
# identify capabilities requiring practice
#    ↓
# source work context
#    ↓
# synthetic apprenticeship context
#    ↓
# capability evidence
#
# This engine is the intelligence/API layer.
# LLM generation is deliberately separated from this layer.
# ============================================================


ROOT = Path(__file__).resolve().parents[3]


LATTICE_PATH = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_ready.parquet"
)


class LatticeEngine:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print(
            "\n[LATTICE] Loading capability-preservation layer..."
        )

        if not LATTICE_PATH.exists():

            raise FileNotFoundError(
                "LATTICE dataset not found:\n"
                f"{LATTICE_PATH}"
            )

        self.df = pd.read_parquet(
            LATTICE_PATH
        )

        self._validate_schema()

        self._prepare_data()

        print(
            f"[LATTICE] Records: "
            f"{len(self.df):,}"
        )

        print(
            f"[LATTICE] Occupations: "
            f"{self.df['Occupation Title'].nunique():,}"
        )

        print(
            f"[LATTICE] Capabilities: "
            f"{self.df['Capability Name'].nunique():,}"
        )

        print(
            f"[LATTICE] Tasks: "
            f"{self.df['Task ID'].nunique():,}"
        )


    # ========================================================
    # REQUIRED SCHEMA
    # ========================================================

    def _validate_schema(self):

        required_columns = [

            "O*NET-SOC Code",

            "Task ID",

            "Occupation Title",

            "Capability Name",

            "Capability Type",

            "Capability ID",

            "Task",

            "DWA Element Name",

            "Skill_Shadow",

            "Skill_Shadow_Percent",

            "Capability_Risk",

            "Capability_Risk_Percent",

            "Capability_Criticality",

            "Market_Job_Count",

            "Capability_Preservation_Pressure",

            "Task_Preservation_Pressure",

            "LATTICE_Priority",

            "Capability_Rank",

            "Task Capability Weight",

            "Task_Evidence_Signal",

            "Task_AI_Suitability",

            "AI_Share",

            "Human_Share",

            "Human_Practice_Signal",

            "AI_Transformation_Signal",

            "Task_Practice_Relevance",

            "Task_Rank",

            "Work_Model",

            "Human_Preservation_Floor",

            "AI_Ceiling",

            "Practice_Intent",

            "LATTICE_Goal",

            "Assessment_Focus",

            "LLM_Task_Input",

            "Semantic_Similarity_Recovered",

            "Relevance_Decision",

            "Relevance_Decision_Reason"
        ]


        missing = [

            column
            for column in required_columns
            if column not in self.df.columns
        ]


        if missing:

            raise ValueError(
                "LATTICE dataset is missing required "
                f"columns:\n{missing}"
            )


    # ========================================================
    # DATA PREPARATION
    # ========================================================

    def _prepare_data(self):

        numeric_columns = [

            "Skill_Shadow",

            "Skill_Shadow_Percent",

            "Capability_Risk",

            "Capability_Risk_Percent",

            "Capability_Criticality",

            "Market_Job_Count",

            "Capability_Preservation_Pressure",

            "Task_Preservation_Pressure",

            "LATTICE_Priority",

            "Capability_Rank",

            "Task Capability Weight",

            "Task_Evidence_Signal",

            "Task_AI_Suitability",

            "AI_Share",

            "Human_Share",

            "Human_Practice_Signal",

            "AI_Transformation_Signal",

            "Task_Practice_Relevance",

            "Task_Rank",

            "Human_Preservation_Floor",

            "AI_Ceiling",

            "Semantic_Similarity_Recovered"
        ]


        for column in numeric_columns:

            self.df[column] = pd.to_numeric(
                self.df[column],
                errors="coerce"
            )


        text_columns = [

            "O*NET-SOC Code",

            "Task ID",

            "Occupation Title",

            "Capability Name",

            "Capability Type",

            "Capability ID",

            "Task",

            "DWA Element Name",

            "Work_Model",

            "Practice_Intent",

            "LATTICE_Goal",

            "Assessment_Focus",

            "LLM_Task_Input",

            "Relevance_Decision",

            "Relevance_Decision_Reason"
        ]


        for column in text_columns:

            self.df[column] = (
                self.df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )


        # ----------------------------------------------------
        # Remove rows that are not LATTICE-ready
        # ----------------------------------------------------

        self.df = self.df[
            self.df[
                "Relevance_Decision"
            ].isin(
                [
                    "KEEP_STRONG",
                    "KEEP_BORDERLINE_SUPPORTED"
                ]
            )
        ].copy()


        # ----------------------------------------------------
        # Stable ordering
        # ----------------------------------------------------

        self.df = (
            self.df
            .sort_values(
                [
                    "Occupation Title",
                    "LATTICE_Priority",
                    "Capability_Rank",
                    "Task_Practice_Relevance",
                    "Task_Rank"
                ],
                ascending=[
                    True,
                    False,
                    True,
                    False,
                    True
                ]
            )
            .reset_index(
                drop=True
            )
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
    # SEARCH CAPABILITIES
    # ========================================================

    def search_capabilities(
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
                "Capability Name"
            ]
            .str.lower()
            .str.contains(
                query,
                regex=False
            )
        )


        result = (
            self.df.loc[
                mask,
                [
                    "Capability Name",
                    "Capability Type",
                    "Capability ID"
                ]
            ]
            .drop_duplicates()
            .sort_values(
                "Capability Name"
            )
            .head(limit)
        )


        return [
            {
                "capability": str(
                    row[
                        "Capability Name"
                    ]
                ),

                "capability_type": str(
                    row[
                        "Capability Type"
                    ]
                ),

                "capability_id": str(
                    row[
                        "Capability ID"
                    ]
                )
            }

            for _, row in result.iterrows()
        ]


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
    # CAPABILITY SUBSET
    # ========================================================

    def _capability_subset(
        self,
        occupation: str,
        capability: str
    ):

        subset = self._occupation_subset(
            occupation
        )


        if subset.empty:

            return subset


        mask = (
            subset[
                "Capability Name"
            ]
            .str.lower()
            ==
            str(
                capability
            )
            .strip()
            .lower()
        )


        return subset.loc[
            mask
        ].copy()


    # ========================================================
    # CAPABILITY PRIORITY
    # ========================================================

    def _capability_priority(
        self,
        group
    ):

        first = group.iloc[0]


        priority = self.safe_float(
            first[
                "LATTICE_Priority"
            ]
        )


        shadow = self.safe_float(
            first[
                "Skill_Shadow"
            ]
        )


        risk = self.safe_float(
            first[
                "Capability_Risk"
            ]
        )


        criticality = self.safe_float(
            first[
                "Capability_Criticality"
            ]
        )


        pressure = self.safe_float(
            first[
                "Capability_Preservation_Pressure"
            ]
        )


        return {

            "capability": str(
                first[
                    "Capability Name"
                ]
            ),

            "capability_type": str(
                first[
                    "Capability Type"
                ]
            ),

            "capability_id": str(
                first[
                    "Capability ID"
                ]
            ),

            "lattice_priority": round(
                priority,
                4
            ),

            "lattice_priority_percent": round(
                priority * 100,
                2
            ),

            "skill_shadow": round(
                shadow,
                4
            ),

            "skill_shadow_percent": round(
                self.safe_float(
                    first[
                        "Skill_Shadow_Percent"
                    ]
                ),
                2
            ),

            "capability_risk": round(
                risk,
                4
            ),

            "capability_risk_percent": round(
                self.safe_float(
                    first[
                        "Capability_Risk_Percent"
                    ]
                ),
                2
            ),

            "capability_criticality": round(
                criticality,
                4
            ),

            "market_job_count": int(
                self.safe_float(
                    first[
                        "Market_Job_Count"
                    ]
                )
            ),

            "preservation_pressure": round(
                pressure,
                4
            ),

            "preservation_pressure_percent": round(
                self.safe_float(
                    first[
                        "Capability_Preservation_Pressure"
                    ]
                ) * 100,
                2
            ),

            "practice_intent": str(
                first[
                    "Practice_Intent"
                ]
            ),

            "lattice_goal": str(
                first[
                    "LATTICE_Goal"
                ]
            ),

            "assessment_focus": str(
                first[
                    "Assessment_Focus"
                ]
            )
        }


    # ========================================================
    # TOP CAPABILITIES
    # ========================================================

    def _top_capabilities(
        self,
        subset,
        limit=10
    ):

        if subset.empty:

            return []


        grouped = (
            subset
            .groupby(
                [
                    "Capability Name",
                    "Capability Type",
                    "Capability ID"
                ],
                dropna=False
            )
        )


        records = []


        for _, group in grouped:

            records.append(
                self._capability_priority(
                    group
                )
            )


        records.sort(
            key=lambda item: (
                item[
                    "lattice_priority"
                ],
                item[
                    "preservation_pressure"
                ]
            ),
            reverse=True
        )


        return records[
            :limit
        ]


    # ========================================================
    # CAPABILITY VERIFICATION RUBRIC
    # ========================================================

    def _build_rubric(
        self,
        row
    ):
        """
        Build a structured, occupation/task-specific practice rubric
        from the LATTICE source fields.

        This is deliberately deterministic: the rubric is derived from
        the actual source task, target capability, assessment focus and
        evidence signal. It does not fabricate a learner score.
        """

        task = str(
            row.get("Task", "")
        ).strip()

        capability = str(
            row.get("Capability Name", "")
        ).strip()

        assessment_focus = str(
            row.get("Assessment_Focus", "")
        ).strip()

        practice_intent = str(
            row.get("Practice_Intent", "")
        ).strip()

        evidence_signal = self.safe_float(
            row.get("Task_Evidence_Signal")
        )

        # Prefer the dataset's explicit assessment focus.
        # If it is empty, use the target capability as the anchor.
        primary_dimension = (
            assessment_focus
            if assessment_focus
            else capability
            if capability
            else "Target capability"
        )

        # Keep criteria tied to the real task rather than inventing
        # unrelated domain knowledge.
        task_reference = (
            task
            if task
            else "the source work task"
        )

        rubric = [
            {
                "dimension": primary_dimension,
                "criterion": (
                    "Performs the practice task while preserving "
                    f"the target capability: {capability or 'target capability'}."
                ),
                "good_performance": (
                    "The learner completes the required task steps "
                    "correctly and addresses the conditions described "
                    f"in the source task: {task_reference}"
                ),
                "max_score": 5,
                "evidence_type": "task_execution"
            },
            {
                "dimension": "Decision / reasoning quality",
                "criterion": (
                    "Uses the relevant information in the task to "
                    "reach a defensible result."
                ),
                "good_performance": (
                    "The response shows a clear connection between "
                    "the available task information, the reasoning "
                    "used, and the resulting action or answer."
                ),
                "max_score": 5,
                "evidence_type": "reasoning_trace"
            },
            {
                "dimension": "Constraint and error checking",
                "criterion": (
                    "Checks important task conditions before completing "
                    "the requested action."
                ),
                "good_performance": (
                    "The learner identifies relevant constraints, "
                    "detects inconsistencies when present, and avoids "
                    "an unsupported or incomplete conclusion."
                ),
                "max_score": 5,
                "evidence_type": "constraint_check"
            },
            {
                "dimension": "Observable capability evidence",
                "criterion": (
                    "Produces evidence that the target capability was "
                    "actually exercised during the attempt."
                ),
                "good_performance": (
                    "The attempt contains an observable output, action, "
                    "decision, correction, or explanation that can be "
                    "checked against the task."
                ),
                "max_score": 5,
                "evidence_type": "observable_output"
            }
        ]

        return {
            "capability": capability,
            "assessment_focus": assessment_focus,
            "practice_intent": practice_intent,
            "source_evidence_signal": round(
                evidence_signal,
                4
            ),
            "dimensions": rubric,
            "max_total_score": 20,
            "scoring_status": "NOT_SCORED_BEFORE_ATTEMPT",
            "verification_rule": (
                "Score only after a learner attempt using observable "
                "task evidence. Do not infer a score from the generated "
                "task alone."
            )
        }


    # ========================================================
    # TASK REPRESENTATION
    # ========================================================

    def _task_record(
        self,
        row
    ):

        rubric = self._build_rubric(row)

        return {

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

            "capability": str(
                row[
                    "Capability Name"
                ]
            ),

            "capability_type": str(
                row[
                    "Capability Type"
                ]
            ),

            "capability_id": str(
                row[
                    "Capability ID"
                ]
            ),

            "lattice_priority": round(
                self.safe_float(
                    row[
                        "LATTICE_Priority"
                    ]
                ),
                4
            ),

            "task_practice_relevance": round(
                self.safe_float(
                    row[
                        "Task_Practice_Relevance"
                    ]
                ),
                4
            ),

            "task_practice_relevance_percent": round(
                self.safe_float(
                    row[
                        "Task_Practice_Relevance"
                    ]
                ) * 100,
                2
            ),

            "task_ai_suitability": round(
                self.safe_float(
                    row[
                        "Task_AI_Suitability"
                    ]
                ),
                4
            ),

            "task_ai_suitability_percent": round(
                self.safe_float(
                    row[
                        "Task_AI_Suitability"
                    ]
                ) * 100,
                2
            ),

            "ai_share": round(
                self.safe_float(
                    row[
                        "AI_Share"
                    ]
                ),
                4
            ),

            "ai_share_percent": round(
                self.safe_float(
                    row[
                        "AI_Share"
                    ]
                ) * 100,
                2
            ),

            "human_share": round(
                self.safe_float(
                    row[
                        "Human_Share"
                    ]
                ),
                4
            ),

            "human_share_percent": round(
                self.safe_float(
                    row[
                        "Human_Share"
                    ]
                ) * 100,
                2
            ),

            "human_practice_signal": round(
                self.safe_float(
                    row[
                        "Human_Practice_Signal"
                    ]
                ),
                4
            ),

            "ai_transformation_signal": round(
                self.safe_float(
                    row[
                        "AI_Transformation_Signal"
                    ]
                ),
                4
            ),

            "task_preservation_pressure": round(
                self.safe_float(
                    row[
                        "Task_Preservation_Pressure"
                    ]
                ),
                4
            ),

            "task_preservation_pressure_percent": round(
                self.safe_float(
                    row[
                        "Task_Preservation_Pressure"
                    ]
                ) * 100,
                2
            ),

            "task_evidence_signal": round(
                self.safe_float(
                    row[
                        "Task_Evidence_Signal"
                    ]
                ),
                4
            ),

            "semantic_similarity": round(
                self.safe_float(
                    row[
                        "Semantic_Similarity_Recovered"
                    ]
                ),
                4
            ),

            "relevance_decision": str(
                row[
                    "Relevance_Decision"
                ]
            ),

            "work_model": str(
                row[
                    "Work_Model"
                ]
            ),

            "practice_intent": str(
                row[
                    "Practice_Intent"
                ]
            ),

            "lattice_goal": str(
                row[
                    "LATTICE_Goal"
                ]
            ),

            "assessment_focus": str(
                row[
                    "Assessment_Focus"
                ]
            ),

            "llm_task_input": str(
                row[
                    "LLM_Task_Input"
                ]
            ),

            "observable_evidence": [
                "task_execution",
                "reasoning_trace",
                "constraint_check",
                "observable_output"
            ],

            "rubric": rubric
        }


    # ========================================================
    # BEST PRACTICE TASKS
    # ========================================================

    def _practice_tasks(
        self,
        subset,
        limit=5
    ):

        if subset.empty:

            return []


        work = subset.copy()


        # Highest relevance first,
        # while preserving LATTICE priority.
        work[
            "_practice_score"
        ] = (

            work[
                "Task_Practice_Relevance"
            ].fillna(0)

            * 0.40

            +

            work[
                "Human_Practice_Signal"
            ].fillna(0)

            * 0.25

            +

            work[
                "Task_Preservation_Pressure"
            ].fillna(0)

            * 0.20

            +

            work[
                "LATTICE_Priority"
            ].fillna(0)

            * 0.15
        )


        work = (
            work
            .sort_values(
                "_practice_score",
                ascending=False
            )
            .drop_duplicates(
                subset=[
                    "Task ID"
                ]
            )
            .head(limit)
        )


        return [
            self._task_record(
                row
            )

            for _, row in work.iterrows()
        ]


    # ========================================================
    # PRACTICE SET
    # ========================================================

    def _build_practice_set(
        self,
        occupation,
        task
    ):
        """
        Convert the selected source task into a compact LATTICE
        apprenticeship/practice contract for the API/UI.
        """

        if not task:
            return None

        rubric = task.get(
            "rubric",
            {}
        )

        return {
            "title": "Capability practice",
            "occupation": occupation,
            "capability": task.get(
                "capability",
                ""
            ),
            "source_task_id": task.get(
                "task_id",
                ""
            ),
            "task_instruction": task.get(
                "task",
                ""
            ),
            "scenario": task.get(
                "dwa",
                ""
            ),
            "practice_intent": task.get(
                "practice_intent",
                ""
            ),
            "reasoning_focus": task.get(
                "assessment_focus",
                ""
            ),
            "observable_evidence": task.get(
                "observable_evidence",
                []
            ),
            "rubric": rubric,
            "scoring_status": (
                rubric.get(
                    "scoring_status",
                    "NOT_SCORED_BEFORE_ATTEMPT"
                )
                if isinstance(rubric, dict)
                else "NOT_SCORED_BEFORE_ATTEMPT"
            ),
            "source": {
                "work_context": task.get(
                    "task",
                    ""
                ),
                "dwa": task.get(
                    "dwa",
                    ""
                ),
                "llm_task_input": task.get(
                    "llm_task_input",
                    ""
                )
            }
        }


    # ========================================================
    # OCCUPATION INTELLIGENCE
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


        top_capabilities = (
            self._top_capabilities(
                subset,
                limit=10
            )
        )


        practice_tasks = (
            self._practice_tasks(
                subset,
                limit=10
            )
        )


        work_models = (
            subset[
                "Work_Model"
            ]
            .value_counts()
            .to_dict()
        )


        practice_intents = (
            subset[
                "Practice_Intent"
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
                first[
                    "O*NET-SOC Code"
                ]
            ),

            "lattice_records": int(
                len(subset)
            ),

            "capability_count": int(
                subset[
                    "Capability Name"
                ].nunique()
            ),

            "task_count": int(
                subset[
                    "Task ID"
                ].nunique()
            ),

            "mean_skill_shadow_percent": round(
                self.safe_float(
                    subset[
                        "Skill_Shadow_Percent"
                    ].mean()
                ),
                2
            ),

            "mean_capability_risk_percent": round(
                self.safe_float(
                    subset[
                        "Capability_Risk_Percent"
                    ].mean()
                ),
                2
            ),

            "mean_capability_criticality": round(
                self.safe_float(
                    subset[
                        "Capability_Criticality"
                    ].mean()
                ),
                4
            ),

            "mean_lattice_priority_percent": round(
                self.safe_float(
                    subset[
                        "LATTICE_Priority"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_practice_relevance_percent": round(
                self.safe_float(
                    subset[
                        "Task_Practice_Relevance"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_ai_transformation_percent": round(
                self.safe_float(
                    subset[
                        "AI_Transformation_Signal"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_human_practice_percent": round(
                self.safe_float(
                    subset[
                        "Human_Practice_Signal"
                    ].mean()
                ) * 100,
                2
            ),

            "work_model_distribution": (
                work_models
            ),

            "practice_intent_distribution": (
                practice_intents
            ),

            "top_capabilities": (
                top_capabilities
            ),

            "priority_practice_tasks": (
                practice_tasks
            ),

            "practice_set": (
                self._build_practice_set(
                    occupation=str(
                        first[
                            "Occupation Title"
                        ]
                    ),
                    task=(
                        practice_tasks[0]
                        if practice_tasks
                        else None
                    )
                )
            )
        }


    # ========================================================
    # CAPABILITY INTELLIGENCE
    # ========================================================

    def get_capability(
        self,
        occupation: str,
        capability: str
    ):

        subset = self._capability_subset(
            occupation,
            capability
        )


        if subset.empty:

            return None


        capability_info = (
            self._capability_priority(
                subset
            )
        )


        tasks = (
            self._practice_tasks(
                subset,
                limit=10
            )
        )


        # ----------------------------------------------------
        # Capability-level transformation state
        # ----------------------------------------------------

        mean_ai = self.safe_float(
            subset[
                "AI_Share"
            ].mean()
        )


        mean_human = self.safe_float(
            subset[
                "Human_Share"
            ].mean()
        )


        mean_human_practice = (
            self.safe_float(
                subset[
                    "Human_Practice_Signal"
                ].mean()
            )
        )


        mean_ai_transform = (
            self.safe_float(
                subset[
                    "AI_Transformation_Signal"
                ].mean()
            )
        )


        # ----------------------------------------------------
        # Practice pressure
        # ----------------------------------------------------

        practice_pressure = (
            capability_info[
                "lattice_priority"
            ]
            * 0.40

            +

            self.safe_float(
                subset[
                    "Task_Practice_Relevance"
                ].mean()
            )
            * 0.30

            +

            self.safe_float(
                subset[
                    "Task_Preservation_Pressure"
                ].mean()
            )
            * 0.30
        )


        return {

            **capability_info,

            "occupation": occupation,

            "task_count": int(
                subset[
                    "Task ID"
                ].nunique()
            ),

            "mean_ai_share_percent": round(
                mean_ai * 100,
                2
            ),

            "mean_human_share_percent": round(
                mean_human * 100,
                2
            ),

            "mean_human_practice_signal_percent": round(
                mean_human_practice * 100,
                2
            ),

            "mean_ai_transformation_signal_percent": round(
                mean_ai_transform * 100,
                2
            ),

            "practice_pressure": round(
                practice_pressure,
                4
            ),

            "practice_pressure_percent": round(
                practice_pressure * 100,
                2
            ),

            "practice_tasks": tasks
        }


    # ========================================================
    # LATTICE PRACTICE PLAN
    # ========================================================
    #
    # This is the bridge to LLM generation.
    #
    # It does NOT invent the work context.
    #
    # It passes:
    #
    # real task
    # capability
    # shadow
    # risk
    # transformation
    # practice relevance
    #
    # to the generation layer.
    # ========================================================

    def build_practice_plan(
        self,
        occupation: str,
        capability: str
    ):

        result = self.get_capability(
            occupation,
            capability
        )


        if result is None:

            return None


        practice_tasks = result[
            "practice_tasks"
        ]


        if not practice_tasks:

            return {

                "status": "NO_PRACTICE_TASK",

                "occupation": occupation,

                "capability": capability
            }


        primary = practice_tasks[0]


        return {

            "status": "READY_FOR_GENERATION",

            "occupation": occupation,

            "capability": {

                "name": capability,

                "type": result[
                    "capability_type"
                ],

                "id": result[
                    "capability_id"
                ]
            },

            "risk": {

                "skill_shadow_percent": result[
                    "skill_shadow_percent"
                ],

                "capability_risk_percent": result[
                    "capability_risk_percent"
                ],

                "criticality": result[
                    "capability_criticality"
                ],

                "lattice_priority_percent": result[
                    "lattice_priority_percent"
                ]
            },

            "transformation": {

                "mean_ai_share_percent": result[
                    "mean_ai_share_percent"
                ],

                "mean_human_share_percent": result[
                    "mean_human_share_percent"
                ],

                "ai_transformation_signal_percent": result[
                    "mean_ai_transformation_signal_percent"
                ],

                "human_practice_signal_percent": result[
                    "mean_human_practice_signal_percent"
                ]
            },

            "practice": {

                "practice_pressure_percent": result[
                    "practice_pressure_percent"
                ],

                "practice_intent": result[
                    "practice_intent"
                ],

                "goal": result[
                    "lattice_goal"
                ],

                "assessment_focus": result[
                    "assessment_focus"
                ]
            },

            "source_work_context": {

                "task_id": primary[
                    "task_id"
                ],

                "task": primary[
                    "task"
                ],

                "dwa": primary[
                    "dwa"
                ],

                "task_practice_relevance_percent": primary[
                    "task_practice_relevance_percent"
                ],

                "task_preservation_pressure_percent": primary[
                    "task_preservation_pressure_percent"
                ],

                "ai_suitability_percent": primary[
                    "task_ai_suitability_percent"
                ],

                "ai_share_percent": primary[
                    "ai_share_percent"
                ],

                "human_share_percent": primary[
                    "human_share_percent"
                ],

                "semantic_similarity": primary[
                    "semantic_similarity"
                ],

                "llm_task_input": primary[
                    "llm_task_input"
                ]
            },

            "practice_set": (
                self._build_practice_set(
                    occupation=occupation,
                    task=primary
                )
            ),

            "generation_contract": {

                "must_preserve_target_capability": True,

                "must_use_source_work_context": True,

                "must_generate_micro_task": True,

                "must_generate_observable_output": True,

                "must_generate_assessment_rubric": True,

                "must_avoid_large_project": True,

                "must_avoid_generic_course": True,

                "must_avoid_high_stakes_decision": True
            }
        }


    # ========================================================
    # GLOBAL LATTICE SUMMARY
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

            "tasks": int(
                self.df[
                    "Task ID"
                ].nunique()
            ),

            "mean_skill_shadow_percent": round(
                self.safe_float(
                    self.df[
                        "Skill_Shadow_Percent"
                    ].mean()
                ),
                2
            ),

            "mean_capability_risk_percent": round(
                self.safe_float(
                    self.df[
                        "Capability_Risk_Percent"
                    ].mean()
                ),
                2
            ),

            "mean_lattice_priority_percent": round(
                self.safe_float(
                    self.df[
                        "LATTICE_Priority"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_practice_relevance_percent": round(
                self.safe_float(
                    self.df[
                        "Task_Practice_Relevance"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_ai_transformation_percent": round(
                self.safe_float(
                    self.df[
                        "AI_Transformation_Signal"
                    ].mean()
                ) * 100,
                2
            ),

            "mean_human_practice_percent": round(
                self.safe_float(
                    self.df[
                        "Human_Practice_Signal"
                    ].mean()
                ) * 100,
                2
            ),

            "relevance_decisions": (
                self.df[
                    "Relevance_Decision"
                ]
                .value_counts()
                .to_dict()
            ),

            "practice_intents": (
                self.df[
                    "Practice_Intent"
                ]
                .value_counts()
                .to_dict()
            ),

            "engine": (
                "LATTICE capability-preservation "
                "and apprenticeship intelligence engine"
            ),

            "generation_status": (
                "SOURCE_CONTEXT_READY"
            )
        }


# ============================================================
# SINGLE ENGINE INSTANCE
# ============================================================

lattice_engine = LatticeEngine()