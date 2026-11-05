"""
FORGE - WORKFOLD V3
Future-Oriented Workforce Reconfiguration & Growth Engine

V3 goals:
1. Exactly ONE decision per unique occupation-task.
2. Aggregate capability evidence before optimization.
3. Use WORKTRACE semantic evidence.
4. Use SKILL SHADOW capability risk and learning-loss signals.
5. Use SciPy SLSQP constrained optimization.
6. Treat AI adoption as an explicit occupation-level scenario target.
7. Explicitly detect when the target is infeasible.
8. Produce consistent decision explanations.
9. Produce backend-ready outputs for the Future Workforce Simulator.

Important:
    AI suitability is a scenario signal derived from semantic evidence.
    It is NOT an empirical probability that a task will be automated.
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

WORKTRACE_FILE = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

SKILL_SHADOW_FILE = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)

OUTPUT_DIR = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
)

OUTPUT_PARQUET = (
    OUTPUT_DIR
    / "forge_workfold_v3.parquet"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "forge_workfold_v3.csv"
)


# ============================================================
# SCENARIO PARAMETERS
# ============================================================

AI_ADOPTION_TARGET = 0.50

# Maximum AI share on a single task.
MAX_AI_SHARE = 0.80

# Minimum human share that remains possible on any task.
MIN_HUMAN_SHARE = 0.20

# Optimization objective weights.
AUTOMATION_WEIGHT = 0.45
CAPABILITY_PRESERVATION_WEIGHT = 0.35
LEARNING_PRESERVATION_WEIGHT = 0.20

# Small tolerance used when checking feasibility.
FEASIBILITY_TOLERANCE = 1e-6


# ============================================================
# HELPERS
# ============================================================

def minmax(series):
    """
    Robust min-max normalization.
    """

    s = pd.to_numeric(
        series,
        errors="coerce"
    )

    if s.notna().sum() == 0:
        return pd.Series(
            0.5,
            index=series.index
        )

    mn = s.min()
    mx = s.max()

    if (
        pd.isna(mn)
        or pd.isna(mx)
        or mx == mn
    ):
        return pd.Series(
            0.5,
            index=series.index
        )

    return (
        (s - mn)
        / (mx - mn)
    ).clip(0, 1)


def weighted_average(
    group,
    value_col,
    weight_col
):
    """
    Weighted average with safe fallback.
    """

    values = pd.to_numeric(
        group[value_col],
        errors="coerce"
    ).fillna(0)

    weights = pd.to_numeric(
        group[weight_col],
        errors="coerce"
    ).fillna(0)

    total_weight = weights.sum()

    if total_weight <= 0:
        return float(
            values.mean()
        )

    return float(
        np.sum(
            values * weights
        )
        / total_weight
    )


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("FORGE - WORKFOLD V3 BUILD")
print("=" * 75)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading WORKTRACE...")

worktrace = pd.read_parquet(
    WORKTRACE_FILE
)

print(
    "WORKTRACE shape:",
    worktrace.shape
)


print("\nLoading SKILL SHADOW...")

shadow = pd.read_parquet(
    SKILL_SHADOW_FILE
)

print(
    "SKILL SHADOW shape:",
    shadow.shape
)


# ============================================================
# VALIDATION
# ============================================================

required_worktrace = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
    "Semantic Similarity",
]

required_shadow = [
    "O*NET-SOC Code",
    "Capability Key",
    "Capability Name",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Avg_Automation_Suitability",
]


missing_worktrace = [
    c
    for c in required_worktrace
    if c not in worktrace.columns
]

missing_shadow = [
    c
    for c in required_shadow
    if c not in shadow.columns
]


if missing_worktrace:

    raise ValueError(
        "Missing WORKTRACE columns: "
        + str(missing_worktrace)
    )


if missing_shadow:

    raise ValueError(
        "Missing SKILL SHADOW columns: "
        + str(missing_shadow)
    )


# ============================================================
# NUMERIC CLEANUP
# ============================================================

numeric_worktrace = [
    "Task Capability Weight",
    "Semantic Similarity",
]

numeric_shadow = [
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Avg_Automation_Suitability",
]


for col in numeric_worktrace:

    worktrace[col] = pd.to_numeric(
        worktrace[col],
        errors="coerce"
    )


for col in numeric_shadow:

    shadow[col] = pd.to_numeric(
        shadow[col],
        errors="coerce"
    )


# ============================================================
# CAPABILITY KEY
# ============================================================

worktrace["Capability Key"] = (
    worktrace[
        "Capability Type"
    ]
    .astype(str)
    + "::"
    + worktrace[
        "Capability ID"
    ]
    .astype(str)
)


# ============================================================
# PREPARE SHADOW TABLE
# ============================================================

shadow_cap = shadow[
    [
        "O*NET-SOC Code",
        "Capability Key",
        "Capability Name",
        "Skill_Shadow",
        "Capability_Risk",
        "Capability_Criticality",
        "Avg_Automation_Suitability",
    ]
].copy()


shadow_cap = (
    shadow_cap
    .drop_duplicates(
        [
            "O*NET-SOC Code",
            "Capability Key",
        ]
    )
)


print(
    "\nUnique occupation-capability records:",
    len(shadow_cap)
)


# ============================================================
# MERGE WORKTRACE + SHADOW
# ============================================================

print(
    "\nMerging WORKTRACE + SKILL SHADOW..."
)

df = worktrace.merge(
    shadow_cap,
    on=[
        "O*NET-SOC Code",
        "Capability Key",
    ],
    how="left",
    suffixes=(
        "",
        "_shadow"
    )
)


print(
    "Merged shape:",
    df.shape
)


# ============================================================
# CLEAN VALUES
# ============================================================

df[
    "Task Capability Weight"
] = (
    df[
        "Task Capability Weight"
    ]
    .fillna(0)
    .clip(lower=0)
)


df[
    "Semantic Similarity"
] = (
    df[
        "Semantic Similarity"
    ]
    .fillna(0)
    .clip(0, 1)
)


for col in [
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Avg_Automation_Suitability",
]:

    df[col] = (
        df[col]
        .fillna(0)
        .clip(0, 1)
    )


# ============================================================
# NORMALIZE CAPABILITY WEIGHTS WITHIN TASK
# ============================================================

task_keys = [
    "O*NET-SOC Code",
    "Task ID",
]


weight_sum = (
    df.groupby(task_keys)[
        "Task Capability Weight"
    ]
    .transform("sum")
)


df[
    "Normalized_Capability_Weight"
] = np.where(
    weight_sum > 0,

    df[
        "Task Capability Weight"
    ]
    / weight_sum,

    0
)


# ============================================================
# AGGREGATE TO UNIQUE TASKS
# ============================================================

print(
    "\nAggregating capability evidence to task level..."
)


task_records = []


for (
    (occupation_code, task_id),
    group
) in df.groupby(
    task_keys,
    sort=False
):

    first = group.iloc[0]

    # --------------------------------------------------------
    # AI SUITABILITY
    # --------------------------------------------------------

    # Strongest semantic evidence attached to the task.
    ai_suitability_raw = float(
        group[
            "Semantic Similarity"
        ].max()
    )


    # --------------------------------------------------------
    # CAPABILITY RISK
    # --------------------------------------------------------

    capability_risk = weighted_average(
        group,
        "Capability_Risk",
        "Normalized_Capability_Weight"
    )


    # --------------------------------------------------------
    # SKILL SHADOW
    # --------------------------------------------------------

    skill_shadow = weighted_average(
        group,
        "Skill_Shadow",
        "Normalized_Capability_Weight"
    )


    # --------------------------------------------------------
    # CAPABILITY CRITICALITY
    # --------------------------------------------------------

    capability_criticality = weighted_average(
        group,
        "Capability_Criticality",
        "Normalized_Capability_Weight"
    )


    # --------------------------------------------------------
    # CAPABILITY COUNT
    # --------------------------------------------------------

    capability_count = (
        group[
            "Capability Key"
        ]
        .nunique()
    )


    # --------------------------------------------------------
    # CAPABILITY IMPORTANCE
    # --------------------------------------------------------

    # The task receives a normalized importance
    # based on its capability evidence.
    importance = float(
        group[
            "Normalized_Capability_Weight"
        ].sum()
    )


    task_records.append(
        {
            "O*NET-SOC Code":
                occupation_code,

            "Occupation Title":
                first[
                    "Occupation Title"
                ],

            "Task ID":
                task_id,

            "Task":
                first[
                    "Task"
                ],

            "Task_AI_Suitability_Raw":
                ai_suitability_raw,

            "Task_Capability_Risk":
                capability_risk,

            "Task_Skill_Shadow":
                skill_shadow,

            "Task_Capability_Criticality":
                capability_criticality,

            "Capability_Count":
                capability_count,

            "Task_Capability_Importance":
                importance,
        }
    )


tasks = pd.DataFrame(
    task_records
)


print(
    "Unique task records:",
    len(tasks)
)


expected_tasks = (
    df[
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    "Expected unique tasks:",
    expected_tasks
)


if len(tasks) != expected_tasks:

    raise RuntimeError(
        "Task aggregation validation failed."
    )


# ============================================================
# NORMALIZE AI SUITABILITY
# ============================================================

tasks[
    "Task_AI_Suitability"
] = minmax(
    tasks[
        "Task_AI_Suitability_Raw"
    ]
)


# ============================================================
# OPTIMIZATION
# ============================================================

def optimize_occupation(group):

    group = (
        group
        .drop_duplicates(
            "Task ID"
        )
        .reset_index(
            drop=True
        )
    )

    n = len(group)

    if n == 0:
        return pd.DataFrame()


    suitability = (
        group[
            "Task_AI_Suitability"
        ]
        .fillna(0)
        .to_numpy(float)
    )


    risk = (
        group[
            "Task_Capability_Risk"
        ]
        .fillna(0)
        .to_numpy(float)
    )


    shadow_value = (
        group[
            "Task_Skill_Shadow"
        ]
        .fillna(0)
        .to_numpy(float)
    )


    criticality = (
        group[
            "Task_Capability_Criticality"
        ]
        .fillna(0)
        .to_numpy(float)
    )


    # --------------------------------------------------------
    # PRESERVATION PRESSURE
    # --------------------------------------------------------

    preservation_pressure = (
        0.45 * risk
        + 0.35 * shadow_value
        + 0.20 * criticality
    )


    preservation_pressure = np.clip(
        preservation_pressure,
        0,
        1
    )


    # --------------------------------------------------------
    # HUMAN FLOOR
    # --------------------------------------------------------

    # High preservation pressure -> more human involvement.
    human_floor = (
        MIN_HUMAN_SHARE
        + (
            preservation_pressure
            * (
                1
                - MIN_HUMAN_SHARE
            )
        )
    )


    human_floor = np.clip(
        human_floor,
        MIN_HUMAN_SHARE,
        1
    )


    max_ai = np.clip(
        1 - human_floor,
        0,
        MAX_AI_SHARE
    )


    # --------------------------------------------------------
    # FEASIBILITY
    # --------------------------------------------------------

    # Equal task-weighted adoption ceiling.
    max_feasible_equal = (
        float(
            np.mean(
                max_ai
            )
        )
    )


    target_feasible = (
        max_feasible_equal
        + FEASIBILITY_TOLERANCE
        >= AI_ADOPTION_TARGET
    )


    # --------------------------------------------------------
    # EFFECTIVE TARGET
    # --------------------------------------------------------

    # If target is infeasible, optimize toward the maximum
    # feasible adoption rather than pretending the target
    # was achieved.
    effective_target = min(
        AI_ADOPTION_TARGET,
        max_feasible_equal
    )


    # --------------------------------------------------------
    # OBJECTIVE COMPONENTS
    # --------------------------------------------------------

    automation_value = (
        suitability
        * (
            0.60
            + 0.40 * (1 - risk)
        )
    )


    capability_penalty = (
        preservation_pressure
        * (
            0.60
            + 0.40 * criticality
        )
    )


    learning_penalty = (
        shadow_value
        * (
            0.60
            + 0.40 * criticality
        )
    )


    # --------------------------------------------------------
    # OBJECTIVE
    # --------------------------------------------------------

    def objective(x):

        automation_gain = np.sum(
            x
            * automation_value
        )


        capability_loss = np.sum(
            x
            * capability_penalty
        )


        learning_loss = np.sum(
            x
            * learning_penalty
        )


        score = (
            AUTOMATION_WEIGHT
            * automation_gain

            - CAPABILITY_PRESERVATION_WEIGHT
            * capability_loss

            - LEARNING_PRESERVATION_WEIGHT
            * learning_loss
        )


        return -score


    # --------------------------------------------------------
    # TARGET CONSTRAINT
    # --------------------------------------------------------

    task_weights = np.ones(n) / n


    def adoption_constraint(x):

        actual = np.sum(
            x
            * task_weights
        )

        return (
            effective_target
            - actual
        )


    constraints = [
        {
            "type": "ineq",
            "fun": adoption_constraint
        }
    ]


    # --------------------------------------------------------
    # INITIAL SOLUTION
    # --------------------------------------------------------

    # Start below the target, then let the optimizer
    # distribute additional AI allocation.
    x0 = np.minimum(
        np.full(
            n,
            effective_target
        ),
        max_ai
    )


    current = np.mean(
        x0
    )


    if current < effective_target:

        # Proportional initialization.
        if current > 0:

            scale = (
                effective_target
                / current
            )

            x0 = np.minimum(
                x0 * scale,
                max_ai
            )

        else:

            x0 = max_ai.copy()


    # --------------------------------------------------------
    # SECOND FEASIBILITY CHECK
    # --------------------------------------------------------

    if (
        np.mean(x0)
        + FEASIBILITY_TOLERANCE
        < effective_target
    ):

        x0 = max_ai.copy()


    # --------------------------------------------------------
    # OPTIMIZATION
    # --------------------------------------------------------

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=[
            (
                0,
                float(max_ai[i])
            )
            for i in range(n)
        ],
        constraints=constraints,
        options={
            "maxiter": 500,
            "ftol": 1e-9
        }
    )


    if result.success:

        ai_share = np.clip(
            result.x,
            0,
            MAX_AI_SHARE
        )

        optimization_status = (
            "Optimal"
        )

    else:

        # Safe feasible fallback.
        ai_share = np.clip(
            x0,
            0,
            MAX_AI_SHARE
        )

        optimization_status = (
            "Feasible fallback"
        )


    human_share = (
        1
        - ai_share
    )


    # ========================================================
    # ACTUAL ADOPTION
    # ========================================================

    actual_adoption = float(
        np.mean(
            ai_share
        )
    )


    target_gap = (
        AI_ADOPTION_TARGET
        - actual_adoption
    )


    # ========================================================
    # WORK MODEL
    # ========================================================

    models = []


    for ai in ai_share:

        if ai >= 0.65:

            models.append(
                "AI-led"
            )

        elif ai <= 0.35:

            models.append(
                "Human-led"
            )

        else:

            models.append(
                "Hybrid"
            )


    # ========================================================
    # BUILD RESULT
    # ========================================================

    result_df = group.copy()


    result_df[
        "AI_Share"
    ] = ai_share


    result_df[
        "Human_Share"
    ] = human_share


    result_df[
        "AI_Share_Percent"
    ] = (
        ai_share
        * 100
    )


    result_df[
        "Human_Share_Percent"
    ] = (
        human_share
        * 100
    )


    result_df[
        "Work_Model"
    ] = models


    result_df[
        "Optimization_Status"
    ] = optimization_status


    # ========================================================
    # PRESERVATION METRICS
    # ========================================================

    result_df[
        "Capability_Preservation"
    ] = (
        human_share
        * (
            1
            - preservation_pressure
        )
    ).clip(0, 1)


    result_df[
        "Residual_Capability_Risk"
    ] = (
        ai_share
        * preservation_pressure
    ).clip(0, 1)


    result_df[
        "Automation_Value"
    ] = (
        ai_share
        * suitability
    ).clip(0, 1)


    # ========================================================
    # FEASIBILITY METADATA
    # ========================================================

    result_df[
        "Requested_AI_Adoption"
    ] = AI_ADOPTION_TARGET


    result_df[
        "Requested_AI_Adoption_Percent"
    ] = (
        AI_ADOPTION_TARGET
        * 100
    )


    result_df[
        "Maximum_Feasible_AI_Adoption"
    ] = max_feasible_equal


    result_df[
        "Maximum_Feasible_AI_Adoption_Percent"
    ] = (
        max_feasible_equal
        * 100
    )


    result_df[
        "Effective_AI_Adoption_Target"
    ] = effective_target


    result_df[
        "Effective_AI_Adoption_Target_Percent"
    ] = (
        effective_target
        * 100
    )


    result_df[
        "Actual_AI_Adoption"
    ] = actual_adoption


    result_df[
        "Actual_AI_Adoption_Percent"
    ] = (
        actual_adoption
        * 100
    )


    result_df[
        "Target_Gap_Percentage_Points"
    ] = (
        target_gap
        * 100
    )


    result_df[
        "Target_Feasibility"
    ] = np.where(
        target_feasible,
        "Feasible",
        "Infeasible"
    )


    # ========================================================
    # DECISION EXPLANATION
    # ========================================================

    explanations = []


    for i in range(n):

        ai = ai_share[i]
        suitability_value = suitability[i]
        pressure = preservation_pressure[i]
        risk_value = risk[i]
        shadow_value_i = shadow_value[i]


        if (
            ai >= 0.65
            and suitability_value >= 0.50
            and pressure < 0.25
        ):

            explanation = (
                "AI-led because the task has relatively "
                "high automation suitability and lower "
                "capability-preservation pressure."
            )


        elif (
            ai <= 0.35
            and (
                suitability_value < 0.40
                or pressure >= 0.30
            )
        ):

            explanation = (
                "Human-led because automation suitability "
                "is relatively low or capability/learning "
                "preservation pressure is higher."
            )


        elif ai >= 0.65:

            explanation = (
                "AI-led allocation is supported by the "
                "optimization objective, while remaining "
                "within the task-level AI limit."
            )


        elif ai <= 0.35:

            explanation = (
                "Human-led allocation is retained to "
                "preserve human involvement under the "
                "capability-risk constraints."
            )


        else:

            explanation = (
                "Hybrid allocation balances automation "
                "suitability with capability and learning "
                "preservation."
            )


        explanations.append(
            explanation
        )


    result_df[
        "Decision_Explanation"
    ] = explanations


    # ========================================================
    # PRESERVATION PRESSURE
    # ========================================================

    result_df[
        "Preservation_Pressure"
    ] = preservation_pressure


    result_df[
        "Preservation_Pressure_Percent"
    ] = (
        preservation_pressure
        * 100
    )


    return result_df


# ============================================================
# RUN ALL OCCUPATIONS
# ============================================================

print(
    "\nRunning constrained optimization..."
)


occupation_results = []


occupation_groups = (
    tasks.groupby(
        "O*NET-SOC Code",
        sort=False
    )
)


total_occupations = (
    tasks[
        "O*NET-SOC Code"
    ]
    .nunique()
)


for counter, (
    occupation_code,
    group
) in enumerate(
    occupation_groups,
    start=1
):

    result = optimize_occupation(
        group
    )


    if result.empty:
        continue


    occupation_results.append(
        result
    )


    if (
        counter % 100 == 0
        or counter == total_occupations
    ):

        print(
            f"Processed "
            f"{counter}/"
            f"{total_occupations}"
            f" occupations"
        )


if not occupation_results:

    raise RuntimeError(
        "No WORKFOLD V3 results generated."
    )


workfold = pd.concat(
    occupation_results,
    ignore_index=True
)


# ============================================================
# OCCUPATION SUMMARY
# ============================================================

print(
    "\nBuilding occupation summaries..."
)


occupation_summary = (
    workfold.groupby(
        [
            "O*NET-SOC Code",
            "Occupation Title",
        ]
    )
    .agg(
        Task_Count=(
            "Task ID",
            "nunique"
        ),

        Average_AI_Share=(
            "AI_Share",
            "mean"
        ),

        Average_Human_Share=(
            "Human_Share",
            "mean"
        ),

        Average_Automation_Value=(
            "Automation_Value",
            "mean"
        ),

        Average_Capability_Preservation=(
            "Capability_Preservation",
            "mean"
        ),

        Average_Residual_Risk=(
            "Residual_Capability_Risk",
            "mean"
        ),

        Average_AI_Suitability=(
            "Task_AI_Suitability",
            "mean"
        ),

        Average_Capability_Risk=(
            "Task_Capability_Risk",
            "mean"
        ),

        Average_Skill_Shadow=(
            "Task_Skill_Shadow",
            "mean"
        ),

        Maximum_Feasible_AI_Adoption=(
            "Maximum_Feasible_AI_Adoption",
            "first"
        ),

        Actual_AI_Adoption=(
            "Actual_AI_Adoption",
            "first"
        ),

        Target_Gap=(
            "Target_Gap_Percentage_Points",
            "first"
        ),

        Target_Feasibility=(
            "Target_Feasibility",
            "first"
        ),
    )
    .reset_index()
)


# ============================================================
# WORK MODEL COUNTS
# ============================================================

model_counts = (
    workfold.groupby(
        [
            "O*NET-SOC Code",
            "Work_Model",
        ]
    )
    .size()
    .unstack(
        fill_value=0
    )
    .reset_index()
)


for model in [
    "AI-led",
    "Hybrid",
    "Human-led",
]:

    if model not in model_counts.columns:

        model_counts[
            model
        ] = 0


model_counts = model_counts.rename(
    columns={
        "AI-led":
            "AI_Led_Task_Count",

        "Hybrid":
            "Hybrid_Task_Count",

        "Human-led":
            "Human_Led_Task_Count",
    }
)


occupation_summary = (
    occupation_summary
    .merge(
        model_counts,
        on="O*NET-SOC Code",
        how="left"
    )
)


# ============================================================
# MERGE SUMMARY
# ============================================================

workfold = workfold.merge(
    occupation_summary,
    on=[
        "O*NET-SOC Code",
        "Occupation Title",
    ],
    how="left",
    suffixes=(
        "",
        "_Occupation"
    )
)


# ============================================================
# METADATA
# ============================================================

workfold[
    "AI_Adoption_Scenario"
] = (
    f"{AI_ADOPTION_TARGET * 100:.0f}%"
)


workfold[
    "Maximum_Task_AI_Share"
] = (
    MAX_AI_SHARE
)


workfold[
    "Minimum_Human_Share"
] = (
    MIN_HUMAN_SHARE
)


workfold[
    "Optimization_Method"
] = (
    "SciPy SLSQP constrained optimization"
)


workfold[
    "Decision_Level"
] = (
    "Unique occupation-task"
)


workfold[
    "AI_Suitability_Method"
] = (
    "WORKTRACE semantic similarity"
)


workfold[
    "Risk_Source"
] = (
    "SKILL SHADOW capability risk"
)


workfold[
    "Learning_Risk_Source"
] = (
    "SKILL SHADOW skill-shadow signal"
)


workfold[
    "Metric_Definition"
] = (
    "WORKFOLD allocates AI and human work shares "
    "at task level while balancing automation "
    "suitability against capability and learning "
    "preservation. AI adoption is treated as a "
    "scenario target. If the requested target is "
    "infeasible under preservation constraints, "
    "the maximum feasible level is reported instead."
)


# ============================================================
# FINAL VALIDATION
# ============================================================

print(
    "\n"
    + "=" * 75
)

print(
    "WORKFOLD V3 VALIDATION"
)

print(
    "=" * 75
)


print(
    "\nFinal shape:",
    workfold.shape
)


print(
    "Unique occupations:",
    workfold[
        "O*NET-SOC Code"
    ].nunique()
)


unique_task_count = (
    workfold[
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


print(
    "Unique tasks:",
    unique_task_count
)


if (
    len(workfold)
    != unique_task_count
):

    print(
        "\nWARNING: Duplicate task decisions detected."
    )

else:

    print(
        "\nTask uniqueness check: PASSED"
    )


# ============================================================
# WORK MODEL
# ============================================================

print(
    "\nWork model distribution:"
)

print(
    workfold[
        "Work_Model"
    ]
    .value_counts(
        dropna=False
    )
)


# ============================================================
# AI SHARE
# ============================================================

print(
    "\nAI share statistics:"
)

print(
    workfold[
        "AI_Share_Percent"
    ].describe()
)


print(
    "\nAverage AI share:",
    round(
        workfold[
            "AI_Share_Percent"
        ].mean(),
        2
    ),
    "%"
)


print(
    "Average human share:",
    round(
        workfold[
            "Human_Share_Percent"
        ].mean(),
        2
    ),
    "%"
)


# ============================================================
# TARGET FEASIBILITY
# ============================================================

print(
    "\nTarget feasibility:"
)

print(
    workfold[
        "Target_Feasibility"
    ]
    .value_counts(
        dropna=False
    )
)


print(
    "\nRequested AI adoption:",
    AI_ADOPTION_TARGET * 100,
    "%"
)


print(
    "Actual average AI adoption:",
    round(
        workfold[
            "Actual_AI_Adoption_Percent"
        ].mean(),
        2
    ),
    "%"
)


print(
    "Average target gap:",
    round(
        workfold[
            "Target_Gap_Percentage_Points"
        ].mean(),
        2
    ),
    "percentage points"
)


# ============================================================
# SAMPLE
# ============================================================

print(
    "\n"
    + "=" * 75
)

print(
    "WORKFOLD V3 SAMPLE"
)

print(
    "=" * 75
)


sample_columns = [
    "Occupation Title",
    "Task",
    "Task_AI_Suitability",
    "Task_Capability_Risk",
    "Task_Skill_Shadow",
    "AI_Share_Percent",
    "Human_Share_Percent",
    "Work_Model",
    "Target_Feasibility",
    "Actual_AI_Adoption_Percent",
    "Decision_Explanation",
]


print(
    workfold[
        sample_columns
    ]
    .sample(
        min(
            10,
            len(workfold)
        ),
        random_state=42
    )
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print(
    "\n"
    + "=" * 75
)

print(
    "SAVING WORKFOLD V3"
)

print(
    "=" * 75
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


workfold.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


workfold.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


print(
    "\nSaved:"
)

print(
    OUTPUT_PARQUET
)

print(
    OUTPUT_CSV
)


print(
    "\n"
    + "=" * 75
)

print(
    "WORKFOLD V3 BUILD COMPLETE"
)

print(
    "=" * 75
)