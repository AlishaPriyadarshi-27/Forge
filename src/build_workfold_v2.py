"""
FORGE - WORKFOLD V2
Future-Oriented Workforce Reconfiguration & Growth Engine

Purpose:
    Task-level Human / Hybrid / AI work allocation.

V2 improvements:
    1. One allocation decision per unique task.
    2. Capability evidence is aggregated before optimization.
    3. Uses Skill Shadow + WORKTRACE evidence.
    4. Uses SciPy SLSQP constrained optimization.
    5. AI adoption target is enforced at occupation level.
    6. High-risk capabilities receive stronger human-preservation pressure.
    7. Produces explainable decision fields.
    8. Supports future counterfactual AI-adoption scenarios.

Important:
    AI suitability is a scenario signal derived from semantic evidence.
    It is NOT an empirical probability of automation.
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

OUTPUT_PARQUET = OUTPUT_DIR / "forge_workfold_v2.parquet"
OUTPUT_CSV = OUTPUT_DIR / "forge_workfold_v2.csv"


# ============================================================
# SCENARIO
# ============================================================

AI_ADOPTION_TARGET = 0.50

# Maximum AI share allowed on any individual task.
MAX_AI_SHARE = 0.80

# Minimum human share for high-risk capability-bearing work.
MIN_HUMAN_SHARE = 0.20

# Relative importance of different optimization objectives.
AUTOMATION_WEIGHT = 0.40
CAPABILITY_PRESERVATION_WEIGHT = 0.45
LEARNING_PRESERVATION_WEIGHT = 0.15


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def minmax(series):
    """Robust min-max normalization."""

    s = pd.to_numeric(series, errors="coerce")

    if s.notna().sum() == 0:
        return pd.Series(
            0.5,
            index=series.index
        )

    mn = s.min()
    mx = s.max()

    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(
            0.5,
            index=series.index
        )

    return (
        (s - mn) / (mx - mn)
    ).clip(0, 1)


def safe_numeric(df, columns):

    for col in columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    return df


# ============================================================
# HEADER
# ============================================================

print("=" * 75)
print("FORGE - WORKFOLD V2 BUILD")
print("=" * 75)


# ============================================================
# LOAD WORKTRACE
# ============================================================

print("\nLoading WORKTRACE...")

worktrace = pd.read_parquet(
    WORKTRACE_FILE
)

print(
    "WORKTRACE shape:",
    worktrace.shape
)


# ============================================================
# LOAD SKILL SHADOW
# ============================================================

print("\nLoading SKILL SHADOW...")

shadow = pd.read_parquet(
    SKILL_SHADOW_FILE
)

print(
    "SKILL SHADOW shape:",
    shadow.shape
)


# ============================================================
# REQUIRED COLUMNS
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
# NUMERIC CONVERSION
# ============================================================

worktrace = safe_numeric(
    worktrace,
    [
        "Task Capability Weight",
        "Semantic Similarity",
    ]
)

shadow = safe_numeric(
    shadow,
    [
        "Skill_Shadow",
        "Capability_Risk",
        "Capability_Criticality",
        "Avg_Automation_Suitability",
    ]
)


# ============================================================
# CAPABILITY KEY
# ============================================================

worktrace["Capability Key"] = (
    worktrace["Capability Type"]
    .astype(str)
    + "::"
    + worktrace["Capability ID"]
    .astype(str)
)


# ============================================================
# PREPARE SHADOW
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
    "\nUnique occupation-capability shadow records:",
    len(shadow_cap)
)


# ============================================================
# MERGE
# ============================================================

print("\nMerging WORKTRACE + SKILL SHADOW...")

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

df["Task Capability Weight"] = (
    df["Task Capability Weight"]
    .fillna(0)
    .clip(lower=0)
)

df["Semantic Similarity"] = (
    df["Semantic Similarity"]
    .fillna(0)
    .clip(0, 1)
)

df["Skill_Shadow"] = (
    df["Skill_Shadow"]
    .fillna(0)
    .clip(0, 1)
)

df["Capability_Risk"] = (
    df["Capability_Risk"]
    .fillna(0)
    .clip(0, 1)
)

df["Capability_Criticality"] = (
    df["Capability_Criticality"]
    .fillna(0)
    .clip(0, 1)
)

df["Avg_Automation_Suitability"] = (
    df["Avg_Automation_Suitability"]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# NORMALIZE CAPABILITY WEIGHT WITHIN TASK
# ============================================================

task_group = [
    "O*NET-SOC Code",
    "Task ID",
]

task_weight_sum = (
    df.groupby(task_group)[
        "Task Capability Weight"
    ]
    .transform("sum")
)


df["Task_Capability_Weight_Normalized"] = np.where(
    task_weight_sum > 0,
    df["Task Capability Weight"]
    / task_weight_sum,
    0
)


# ============================================================
# BUILD ONE RECORD PER TASK
# ============================================================

print(
    "\nAggregating capability evidence to task level..."
)


def weighted_average(group, value_col, weight_col):

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
        return float(values.mean())

    return float(
        np.sum(values * weights)
        / total_weight
    )


task_records = []


for (
    (occupation_code, task_id),
    group
) in df.groupby(
    [
        "O*NET-SOC Code",
        "Task ID",
    ],
    sort=False
):

    first = group.iloc[0]

    capability_weight = (
        group[
            "Task_Capability_Weight_Normalized"
        ]
    )

    # --------------------------------------------------------
    # AI suitability
    # --------------------------------------------------------

    # Use the strongest semantic evidence for the task.
    ai_suitability = float(
        group[
            "Semantic Similarity"
        ].max()
    )

    # --------------------------------------------------------
    # Capability risk
    # --------------------------------------------------------

    capability_risk = weighted_average(
        group,
        "Capability_Risk",
        "Task_Capability_Weight_Normalized"
    )

    # --------------------------------------------------------
    # Skill shadow
    # --------------------------------------------------------

    skill_shadow = weighted_average(
        group,
        "Skill_Shadow",
        "Task_Capability_Weight_Normalized"
    )

    # --------------------------------------------------------
    # Capability criticality
    # --------------------------------------------------------

    criticality = weighted_average(
        group,
        "Capability_Criticality",
        "Task_Capability_Weight_Normalized"
    )

    # --------------------------------------------------------
    # Number of capabilities
    # --------------------------------------------------------

    capability_count = (
        group[
            "Capability Key"
        ]
        .nunique()
    )

    # --------------------------------------------------------
    # Capability importance
    # --------------------------------------------------------

    importance = float(
        capability_weight.sum()
    )

    task_records.append(
        {
            "O*NET-SOC Code":
                occupation_code,

            "Occupation Title":
                first["Occupation Title"],

            "Task ID":
                task_id,

            "Task":
                first["Task"],

            "Task_AI_Suitability_Raw":
                ai_suitability,

            "Task_Capability_Risk":
                capability_risk,

            "Task_Skill_Shadow":
                skill_shadow,

            "Task_Capability_Criticality":
                criticality,

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

print(
    "Expected unique tasks from WORKTRACE:",
    df[
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)


# ============================================================
# NORMALIZE TASK AI SUITABILITY
# ============================================================

tasks["Task_AI_Suitability"] = minmax(
    tasks[
        "Task_AI_Suitability_Raw"
    ]
)


# ============================================================
# NORMALIZE TASK IMPORTANCE
# ============================================================

tasks["Task_Capability_Importance"] = (
    tasks[
        "Task_Capability_Importance"
    ]
    .clip(0, 1)
)


# ============================================================
# OCCUPATION OPTIMIZER
# ============================================================

def optimize_occupation(group):

    group = (
        group
        .drop_duplicates(
            "Task ID"
        )
        .reset_index(drop=True)
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

    importance = (
        group[
            "Task_Capability_Importance"
        ]
        .fillna(0)
        .to_numpy(float)
    )

    # --------------------------------------------------------
    # COMBINED PRESERVATION PRESSURE
    # --------------------------------------------------------

    preservation_pressure = (
        0.50 * risk
        + 0.30 * shadow_value
        + 0.20 * criticality
    )

    preservation_pressure = np.clip(
        preservation_pressure,
        0,
        1
    )

    # --------------------------------------------------------
    # TASK-SPECIFIC HUMAN FLOOR
    # --------------------------------------------------------

    human_floor = (
        MIN_HUMAN_SHARE
        + (
            preservation_pressure
            * (1 - MIN_HUMAN_SHARE)
        )
    )

    human_floor = np.clip(
        human_floor,
        MIN_HUMAN_SHARE,
        1
    )

    max_ai = np.minimum(
        MAX_AI_SHARE,
        1 - human_floor
    )

    # --------------------------------------------------------
    # TASK VALUE
    # --------------------------------------------------------

    # Higher suitability = stronger automation value.
    automation_value = (
        suitability
        * (
            0.50
            + 0.50 * importance
        )
    )

    # Human-preservation penalty.
    preservation_penalty = (
        preservation_pressure
        * (
            0.50
            + 0.50 * importance
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
            * preservation_penalty
        )

        learning_loss = np.sum(
            x
            * shadow_value
            * (
                0.50
                + 0.50 * importance
            )
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
    # WEIGHTED OCCUPATION-LEVEL AI TARGET
    # --------------------------------------------------------

    weights = importance.copy()

    if weights.sum() <= 0:
        weights = np.ones(n)

    weights = (
        weights
        / weights.sum()
    )

    def adoption_constraint(x):

        weighted_ai_share = np.sum(
            x * weights
        )

        return (
            AI_ADOPTION_TARGET
            - weighted_ai_share
        )

    constraints = [
        {
            "type": "ineq",
            "fun": adoption_constraint,
        }
    ]

    # --------------------------------------------------------
    # INITIAL SOLUTION
    # --------------------------------------------------------

    x0 = np.minimum(
        np.full(
            n,
            AI_ADOPTION_TARGET
        ),
        max_ai
    )

    current_adoption = np.sum(
        x0 * weights
    )

    # If target is not feasible because of
    # preservation constraints, use maximum feasible.
    if current_adoption < AI_ADOPTION_TARGET:

        x0 = max_ai.copy()

    # --------------------------------------------------------
    # SLSQP
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
            "ftol": 1e-9,
        }
    )

    if result.success:

        ai_share = result.x

        status = "Optimal"

    else:

        ai_share = x0

        status = (
            "Feasible fallback"
        )

    ai_share = np.clip(
        ai_share,
        0,
        MAX_AI_SHARE
    )

    human_share = (
        1
        - ai_share
    )

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

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
        ai_share * 100
    )

    result_df[
        "Human_Share_Percent"
    ] = (
        human_share * 100
    )

    result_df[
        "Work_Model"
    ] = models

    result_df[
        "Optimization_Status"
    ] = status

    # --------------------------------------------------------
    # TASK-LEVEL PRESERVATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DECISION EXPLANATION
    # --------------------------------------------------------

    explanations = []

    for i in range(n):

        if (
            suitability[i] >= 0.60
            and preservation_pressure[i] < 0.25
        ):

            explanation = (
                "High automation suitability "
                "with relatively low capability "
                "preservation pressure."
            )

        elif (
            preservation_pressure[i] >= 0.45
        ):

            explanation = (
                "Human involvement is preserved "
                "because capability-loss pressure "
                "is relatively high."
            )

        elif (
            suitability[i] < 0.35
        ):

            explanation = (
                "Human involvement is retained "
                "because semantic automation "
                "suitability is relatively low."
            )

        else:

            explanation = (
                "Hybrid allocation balances "
                "automation suitability with "
                "capability preservation."
            )

        explanations.append(
            explanation
        )

    result_df[
        "Decision_Explanation"
    ] = explanations

    # --------------------------------------------------------
    # ACTUAL OCCUPATION ADOPTION
    # --------------------------------------------------------

    weighted_adoption = np.sum(
        ai_share
        * weights
    )

    result_df[
        "Occupation_AI_Adoption"
    ] = weighted_adoption

    result_df[
        "Occupation_AI_Adoption_Percent"
    ] = (
        weighted_adoption
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
        "No WORKFOLD results generated."
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

        Weighted_AI_Adoption=(
            "Occupation_AI_Adoption",
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
    )
    .reset_index()
)


occupation_summary[
    "AI_Adoption_Target_Percent"
] = (
    AI_ADOPTION_TARGET * 100
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
# MERGE SUMMARY BACK
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
# SCENARIO METADATA
# ============================================================

workfold[
    "AI_Adoption_Target"
] = AI_ADOPTION_TARGET

workfold[
    "AI_Adoption_Target_Percent"
] = (
    AI_ADOPTION_TARGET * 100
)

workfold[
    "Capability_Preservation_Floor"
] = MIN_HUMAN_SHARE

workfold[
    "Maximum_Task_AI_Share"
] = MAX_AI_SHARE

workfold[
    "Optimization_Method"
] = (
    "SciPy SLSQP constrained optimization"
)

workfold[
    "Decision_Level"
] = "Task"

workfold[
    "AI_Suitability_Method"
] = (
    "WORKTRACE semantic similarity"
)

workfold[
    "Metric_Definition"
] = (
    "Task-level AI allocation optimized under "
    "an occupation-level AI adoption target, "
    "with capability preservation and learning-loss "
    "pressure derived from SKILL SHADOW."
)


# ============================================================
# VALIDATION
# ============================================================

print(
    "\n"
    + "=" * 75
)

print(
    "WORKFOLD V2 VALIDATION"
)

print(
    "=" * 75
)


print(
    "\nFinal shape:",
    workfold.shape
)


print(
    "\nUnique occupations:",
    workfold[
        "O*NET-SOC Code"
    ].nunique()
)


print(
    "Unique tasks:",
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


print(
    "\nAI share statistics:"
)

print(
    workfold[
        "AI_Share_Percent"
    ]
    .describe()
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
    "\nAverage human share:",
    round(
        workfold[
            "Human_Share_Percent"
        ].mean(),
        2
    ),
    "%"
)


print(
    "\nOccupation weighted AI adoption:"
)

print(
    round(
        workfold[
            "Occupation_AI_Adoption_Percent"
        ].mean(),
        2
    ),
    "%"
)


# ============================================================
# TARGET DEVIATION
# ============================================================

deviation = (
    workfold[
        "Occupation_AI_Adoption_Percent"
    ]
    - (
        AI_ADOPTION_TARGET
        * 100
    )
).abs()


print(
    "\nMean occupation target deviation:",
    round(
        deviation.mean(),
        4
    ),
    "percentage points"
)


print(
    "\nMaximum occupation target deviation:",
    round(
        deviation.max(),
        4
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
    "WORKFOLD V2 SAMPLE"
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
    "SAVING WORKFOLD V2"
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
    "WORKFOLD V2 BUILD COMPLETE"
)

print(
    "=" * 75
)