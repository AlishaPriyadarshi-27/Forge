"""
FORGE - WORKFOLD
Future-Oriented Workforce Reconfiguration & Growth Engine

WORKFOLD:
Optimizes Human / Hybrid / AI task allocation under:
- AI adoption target
- capability preservation
- automation suitability
- capability risk
- task-level work evidence

Inputs:
    datasets/onet/knowledge_base/forge_worktrace.parquet
    datasets/onet/knowledge_base/forge_skill_shadow.parquet

Outputs:
    datasets/onet/knowledge_base/forge_workfold.parquet
    datasets/onet/knowledge_base/forge_workfold.csv

Important:
- Optimization is performed by SciPy.
- No LLM is used to make allocation decisions.
- AI suitability is a scenario signal, not a factual probability.
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

OUTPUT_PARQUET = OUTPUT_DIR / "forge_workfold.parquet"
OUTPUT_CSV = OUTPUT_DIR / "forge_workfold.csv"


# ============================================================
# SCENARIO PARAMETERS
# ============================================================

# Default scenario.
# This is a user-controlled what-if assumption, not real-world
# automation probability.

AI_ADOPTION_TARGET = 0.50

# Minimum amount of human involvement allowed for tasks that
# carry important capability exposure.
CAPABILITY_PRESERVATION_FLOOR = 0.20

# Weight given to preserving human capability.
CAPABILITY_PRESERVATION_WEIGHT = 0.45

# Weight given to automation suitability.
AUTOMATION_WEIGHT = 0.40

# Small penalty against unnecessary human involvement.
EFFICIENCY_WEIGHT = 0.15


# ============================================================
# HELPERS
# ============================================================

def minmax(series):
    """
    Robust min-max normalization.
    """
    s = pd.to_numeric(series, errors="coerce")

    if s.notna().sum() == 0:
        return pd.Series(0.0, index=series.index)

    mn = s.min()
    mx = s.max()

    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(0.5, index=series.index)

    return ((s - mn) / (mx - mn)).clip(0, 1)


def safe_numeric(df, columns):
    """
    Convert selected columns to numeric.
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FORGE - WORKFOLD BUILD")
print("=" * 70)

print("\nLoading WORKTRACE...")
worktrace = pd.read_parquet(WORKTRACE_FILE)

print("WORKTRACE shape:", worktrace.shape)

print("\nLoading SKILL SHADOW...")
shadow = pd.read_parquet(SKILL_SHADOW_FILE)

print("SKILL SHADOW shape:", shadow.shape)


# ============================================================
# VALIDATE REQUIRED COLUMNS
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
    "Avg_AI_Share",
]


missing_worktrace = [
    c for c in required_worktrace if c not in worktrace.columns
]

missing_shadow = [
    c for c in required_shadow if c not in shadow.columns
]

if missing_worktrace:
    raise ValueError(
        f"Missing WORKTRACE columns: {missing_worktrace}"
    )

if missing_shadow:
    raise ValueError(
        f"Missing SKILL SHADOW columns: {missing_shadow}"
    )


# ============================================================
# NUMERIC CLEANUP
# ============================================================

worktrace = safe_numeric(
    worktrace,
    [
        "Task Capability Weight",
        "Semantic Similarity",
    ],
)

shadow = safe_numeric(
    shadow,
    [
        "Skill_Shadow",
        "Capability_Risk",
        "Capability_Criticality",
        "Avg_Automation_Suitability",
        "Avg_AI_Share",
        "Pre_AI_Exposure",
        "Post_AI_Exposure",
    ],
)


# ============================================================
# BUILD CAPABILITY KEY
# ============================================================

worktrace["Capability Key"] = (
    worktrace["Capability Type"].astype(str)
    + "::"
    + worktrace["Capability ID"].astype(str)
)

print("\nCapability keys created.")


# ============================================================
# PREPARE CAPABILITY RISK TABLE
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
        "Avg_AI_Share",
    ]
].copy()

shadow_cap = shadow_cap.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Capability Key",
    ]
)

print(
    "Unique occupation-capability shadow records:",
    len(shadow_cap),
)


# ============================================================
# MERGE WORKTRACE + SKILL SHADOW
# ============================================================

print("\nMerging WORKTRACE with SKILL SHADOW...")

df = worktrace.merge(
    shadow_cap,
    on=[
        "O*NET-SOC Code",
        "Capability Key",
    ],
    how="left",
    suffixes=("", "_shadow"),
)


print("Merged shape:", df.shape)


# ============================================================
# CLEAN MERGED DATA
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
# NORMALIZE TASK WEIGHTS
# ============================================================

print("\nNormalizing task-capability weights...")

group_sum = (
    df.groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    )["Task Capability Weight"]
    .transform("sum")
)

df["Normalized_Task_Capability_Weight"] = np.where(
    group_sum > 0,
    df["Task Capability Weight"] / group_sum,
    0,
)


# ============================================================
# BUILD TASK-LEVEL FEATURES
# ============================================================

print("Building task-level optimization features...")


# Capability importance for each task.
task_capability_importance = (
    df.groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    )["Normalized_Task_Capability_Weight"]
    .sum()
    .rename("Task_Capability_Importance")
    .reset_index()
)


# Average capability risk carried by the task.
task_risk = (
    df.assign(
        weighted_risk=
        df["Normalized_Task_Capability_Weight"]
        * df["Capability_Risk"]
    )
    .groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    )["weighted_risk"]
    .sum()
    .rename("Task_Capability_Risk")
    .reset_index()
)


# Average shadow associated with the task.
task_shadow = (
    df.assign(
        weighted_shadow=
        df["Normalized_Task_Capability_Weight"]
        * df["Skill_Shadow"]
    )
    .groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    )["weighted_shadow"]
    .sum()
    .rename("Task_Skill_Shadow")
    .reset_index()
)


# Semantic evidence for task-level AI suitability.
task_ai = (
    df.groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
        ]
    )["Semantic Similarity"]
    .max()
    .rename("Task_AI_Suitability")
    .reset_index()
)


task_features = (
    task_capability_importance
    .merge(
        task_risk,
        on=["O*NET-SOC Code", "Task ID"],
        how="left",
    )
    .merge(
        task_shadow,
        on=["O*NET-SOC Code", "Task ID"],
        how="left",
    )
    .merge(
        task_ai,
        on=["O*NET-SOC Code", "Task ID"],
        how="left",
    )
)


# Normalize AI suitability across all tasks.
task_features["Task_AI_Suitability"] = minmax(
    task_features["Task_AI_Suitability"]
)

task_features["Task_Capability_Risk"] = (
    task_features["Task_Capability_Risk"]
    .fillna(0)
    .clip(0, 1)
)

task_features["Task_Skill_Shadow"] = (
    task_features["Task_Skill_Shadow"]
    .fillna(0)
    .clip(0, 1)
)

task_features["Task_Capability_Importance"] = (
    task_features["Task_Capability_Importance"]
    .fillna(0)
)


# ============================================================
# JOIN TASK FEATURES BACK
# ============================================================

df = df.merge(
    task_features,
    on=[
        "O*NET-SOC Code",
        "Task ID",
    ],
    how="left",
)


# ============================================================
# OPTIMIZATION FUNCTION
# ============================================================

def optimize_occupation(group):
    """
    Optimize AI share for all tasks in one occupation.

    Variables:
        x_t = AI share assigned to task t

    Objective:
        maximize:
            automation benefit
            + efficiency
            - capability loss

    Subject to:
        average AI allocation <= scenario target

    Additional task-level constraints:
        high capability-risk tasks retain more human involvement.
    """

    tasks = (
        group[
            [
                "Task ID",
                "Task",
                "Task_AI_Suitability",
                "Task_Capability_Risk",
                "Task_Skill_Shadow",
                "Task_Capability_Importance",
            ]
        ]
        .drop_duplicates("Task ID")
        .reset_index(drop=True)
    )

    n = len(tasks)

    if n == 0:
        return pd.DataFrame()

    ai_suitability = (
        tasks["Task_AI_Suitability"]
        .fillna(0)
        .to_numpy(dtype=float)
    )

    capability_risk = (
        tasks["Task_Capability_Risk"]
        .fillna(0)
        .to_numpy(dtype=float)
    )

    skill_shadow = (
        tasks["Task_Skill_Shadow"]
        .fillna(0)
        .to_numpy(dtype=float)
    )

    importance = (
        tasks["Task_Capability_Importance"]
        .fillna(0)
        .to_numpy(dtype=float)
    )

    # --------------------------------------------------------
    # TASK-SPECIFIC HUMAN PRESERVATION FLOOR
    # --------------------------------------------------------

    # Riskier capability-bearing tasks retain more human share.
    #
    # Example:
    # low risk -> floor near configured minimum
    # high risk -> floor approaches 1

    human_floor = (
        CAPABILITY_PRESERVATION_FLOOR
        + (
            capability_risk
            * (1 - CAPABILITY_PRESERVATION_FLOOR)
        )
    )

    human_floor = np.clip(
        human_floor,
        0,
        1,
    )

    ai_upper_bound = 1 - human_floor

    # --------------------------------------------------------
    # OBJECTIVE
    # --------------------------------------------------------

    def objective(x):

        automation_benefit = np.sum(
            x
            * ai_suitability
            * importance
        )

        efficiency_gain = np.sum(
            x
            * ai_suitability
        )

        capability_loss = np.sum(
            x
            * (
                0.60 * capability_risk
                + 0.40 * skill_shadow
            )
            * importance
        )

        value = (
            AUTOMATION_WEIGHT
            * automation_benefit
            + EFFICIENCY_WEIGHT
            * efficiency_gain
            - CAPABILITY_PRESERVATION_WEIGHT
            * capability_loss
        )

        return -value

    # --------------------------------------------------------
    # CONSTRAINT: TARGET AI ADOPTION
    # --------------------------------------------------------

    def adoption_constraint(x):

        return (
            AI_ADOPTION_TARGET
            - np.mean(x)
        )

    constraints = [
        {
            "type": "ineq",
            "fun": adoption_constraint,
        }
    ]

    # --------------------------------------------------------
    # INITIAL POINT
    # --------------------------------------------------------

    x0 = np.minimum(
        np.full(
            n,
            AI_ADOPTION_TARGET,
        ),
        ai_upper_bound,
    )

    # If the target cannot be reached because of preservation
    # constraints, use the maximum feasible allocation.
    if np.mean(x0) < AI_ADOPTION_TARGET:
        x0 = ai_upper_bound.copy()

    # --------------------------------------------------------
    # OPTIMIZE
    # --------------------------------------------------------

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=[
            (0, float(ai_upper_bound[i]))
            for i in range(n)
        ],
        constraints=constraints,
        options={
            "maxiter": 500,
            "ftol": 1e-8,
        },
    )

    if result.success:
        optimized_ai = result.x
        optimization_status = "Optimal"
    else:
        optimized_ai = x0
        optimization_status = (
            "Feasible fallback: "
            + str(result.message)
        )

    optimized_ai = np.clip(
        optimized_ai,
        0,
        1,
    )

    human_share = 1 - optimized_ai

    # --------------------------------------------------------
    # CLASSIFY WORK MODEL
    # --------------------------------------------------------

    allocation = []

    for ai, human in zip(
        optimized_ai,
        human_share,
    ):

        if ai >= 0.80:
            model = "AI-led"

        elif ai <= 0.20:
            model = "Human-led"

        else:
            model = "Hybrid"

        allocation.append(model)

    output = tasks.copy()

    output["AI_Share"] = optimized_ai
    output["Human_Share"] = human_share

    output["AI_Share_Percent"] = (
        optimized_ai * 100
    )

    output["Human_Share_Percent"] = (
        human_share * 100
    )

    output["Work_Model"] = allocation

    output["Optimization_Status"] = (
        optimization_status
    )

    return output


# ============================================================
# RUN OPTIMIZATION
# ============================================================

print("\nRunning WORKFOLD optimization...")

occupation_results = []

occupations = df[
    [
        "O*NET-SOC Code",
        "Occupation Title",
    ]
].drop_duplicates(
    "O*NET-SOC Code"
)

total_occupations = len(occupations)

print(
    "Occupations to optimize:",
    total_occupations,
)


for counter, (occupation_code, group) in enumerate(
    df.groupby("O*NET-SOC Code"),
    start=1,
):

    result = optimize_occupation(group)

    if result.empty:
        continue

    result["O*NET-SOC Code"] = occupation_code

    title = group["Occupation Title"].iloc[0]

    result["Occupation Title"] = title

    occupation_results.append(result)

    if counter % 100 == 0 or counter == total_occupations:

        print(
            f"Processed {counter}/{total_occupations} occupations"
        )


if not occupation_results:
    raise RuntimeError(
        "WORKFOLD optimization produced no results."
    )


workfold_tasks = pd.concat(
    occupation_results,
    ignore_index=True,
)


# ============================================================
# ADD CAPABILITY EVIDENCE
# ============================================================

print("\nAdding capability evidence...")

capability_evidence = (
    df[
        [
            "O*NET-SOC Code",
            "Task ID",
            "Capability Key",
            "Capability Type",
            "Capability ID",
            "Capability Name",
            "Capability_Risk",
            "Skill_Shadow",
        ]
    ]
    .drop_duplicates(
        [
            "O*NET-SOC Code",
            "Task ID",
            "Capability Key",
        ]
    )
)


workfold = workfold_tasks.merge(
    capability_evidence,
    on=[
        "O*NET-SOC Code",
        "Task ID",
    ],
    how="left",
)


# ============================================================
# SCENARIO METRICS
# ============================================================

print("Calculating scenario metrics...")


# AI contribution weighted by task importance.
workfold["AI_Contribution"] = (
    workfold["AI_Share"]
    * workfold["Task_Capability_Importance"]
)

workfold["Human_Contribution"] = (
    workfold["Human_Share"]
    * workfold["Task_Capability_Importance"]
)


# Capability preservation score.
workfold["Capability_Preservation"] = (
    workfold["Human_Share"]
    * (1 - workfold["Task_Capability_Risk"])
)

workfold["Capability_Preservation"] = (
    workfold["Capability_Preservation"]
    .clip(0, 1)
)


# Automation value.
workfold["Automation_Value"] = (
    workfold["AI_Share"]
    * workfold["Task_AI_Suitability"]
)


# Capability risk after allocation.
workfold["Residual_Capability_Risk"] = (
    workfold["AI_Share"]
    * workfold["Task_Capability_Risk"]
)


# ============================================================
# OCCUPATION-LEVEL SUMMARY
# ============================================================

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
            "nunique",
        ),

        Average_AI_Share=(
            "AI_Share",
            "mean",
        ),

        Average_Human_Share=(
            "Human_Share",
            "mean",
        ),

        Automation_Value=(
            "Automation_Value",
            "mean",
        ),

        Capability_Preservation=(
            "Capability_Preservation",
            "mean",
        ),

        Residual_Capability_Risk=(
            "Residual_Capability_Risk",
            "mean",
        ),

        Average_Task_AI_Suitability=(
            "Task_AI_Suitability",
            "mean",
        ),

        Average_Task_Capability_Risk=(
            "Task_Capability_Risk",
            "mean",
        ),
    )
    .reset_index()
)


occupation_summary["AI_Adoption_Target"] = (
    AI_ADOPTION_TARGET
)

occupation_summary["AI_Adoption_Target_Percent"] = (
    AI_ADOPTION_TARGET * 100
)


# ============================================================
# JOIN OCCUPATION SUMMARY
# ============================================================

workfold = workfold.merge(
    occupation_summary,
    on=[
        "O*NET-SOC Code",
        "Occupation Title",
    ],
    how="left",
    suffixes=("", "_Occupation"),
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
    .unstack(fill_value=0)
    .reset_index()
)


for model in [
    "AI-led",
    "Hybrid",
    "Human-led",
]:

    if model not in model_counts.columns:
        model_counts[model] = 0


model_counts = model_counts.rename(
    columns={
        "AI-led": "AI_Led_Task_Count",
        "Hybrid": "Hybrid_Task_Count",
        "Human-led": "Human_Led_Task_Count",
    }
)


workfold = workfold.merge(
    model_counts,
    on="O*NET-SOC Code",
    how="left",
)


# ============================================================
# COUNTERFACTUAL METRICS
# ============================================================

workfold["Estimated_Work_Reconfiguration"] = (
    np.abs(
        workfold["AI_Share"]
        - AI_ADOPTION_TARGET
    )
)


workfold["Capability_Preservation_Percent"] = (
    workfold["Capability_Preservation"]
    * 100
)

workfold["Residual_Capability_Risk_Percent"] = (
    workfold["Residual_Capability_Risk"]
    * 100
)

workfold["Automation_Value_Percent"] = (
    workfold["Automation_Value"]
    * 100
)


# ============================================================
# METADATA
# ============================================================

workfold["AI_Adoption_Scenario"] = (
    f"{AI_ADOPTION_TARGET * 100:.0f}%"
)

workfold["Capability_Preservation_Floor"] = (
    CAPABILITY_PRESERVATION_FLOOR
)

workfold["Optimization_Method"] = (
    "SciPy SLSQP constrained optimization"
)

workfold["AI_Suitability_Method"] = (
    "Semantic similarity signal from WORKTRACE"
)

workfold["Decision_Level"] = (
    "Task"
)

workfold["Metric_Definition"] = (
    "WORKFOLD optimizes task-level AI share under "
    "an AI-adoption target and capability-preservation "
    "constraints. AI suitability is a scenario signal "
    "derived from semantic evidence, not an empirical "
    "automation probability."
)


# ============================================================
# SORT
# ============================================================

workfold = workfold.sort_values(
    [
        "Occupation Title",
        "Task_ID"
        if "Task_ID" in workfold.columns
        else "Task ID",
    ]
).reset_index(drop=True)


# ============================================================
# SELECT IMPORTANT COLUMNS FIRST
# ============================================================

priority_columns = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "Task_AI_Suitability",
    "Task_Capability_Risk",
    "Task_Skill_Shadow",
    "Task_Capability_Importance",
    "AI_Share",
    "Human_Share",
    "AI_Share_Percent",
    "Human_Share_Percent",
    "Work_Model",
    "Automation_Value",
    "Capability_Preservation",
    "Residual_Capability_Risk",
    "AI_Led_Task_Count",
    "Hybrid_Task_Count",
    "Human_Led_Task_Count",
    "Average_AI_Share",
    "Average_Human_Share",
    "Capability_Preservation_Percent",
    "Residual_Capability_Risk_Percent",
    "Automation_Value_Percent",
    "AI_Adoption_Target",
    "AI_Adoption_Target_Percent",
    "Optimization_Status",
    "Optimization_Method",
    "AI_Suitability_Method",
    "Decision_Level",
    "Metric_Definition",
]


priority_columns = [
    c for c in priority_columns
    if c in workfold.columns
]


remaining_columns = [
    c for c in workfold.columns
    if c not in priority_columns
]

workfold = workfold[
    priority_columns + remaining_columns
]


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("WORKFOLD VALIDATION")
print("=" * 70)

print("\nFinal shape:", workfold.shape)

print(
    "\nUnique occupations:",
    workfold["O*NET-SOC Code"].nunique(),
)

print(
    "Unique tasks:",
    workfold[
        ["O*NET-SOC Code", "Task ID"]
    ].drop_duplicates().shape[0],
)

print(
    "AI-led tasks:",
    (workfold["Work_Model"] == "AI-led").sum(),
)

print(
    "Hybrid tasks:",
    (workfold["Work_Model"] == "Hybrid").sum(),
)

print(
    "Human-led tasks:",
    (workfold["Work_Model"] == "Human-led").sum(),
)


print("\nWork model distribution:")

print(
    workfold["Work_Model"]
    .value_counts(dropna=False)
)


print("\nAverage AI share:")

print(
    round(
        workfold["AI_Share"].mean() * 100,
        2,
    ),
    "%",
)


print("\nAverage human share:")

print(
    round(
        workfold["Human_Share"].mean() * 100,
        2,
    ),
    "%",
)


print("\nAverage capability preservation:")

print(
    round(
        workfold["Capability_Preservation"].mean()
        * 100,
        2,
    ),
    "%",
)


# ============================================================
# SAMPLE
# ============================================================

print("\n" + "=" * 70)
print("WORKFOLD SAMPLE")
print("=" * 70)

sample_columns = [
    "Occupation Title",
    "Task",
    "Task_AI_Suitability",
    "Task_Capability_Risk",
    "AI_Share_Percent",
    "Human_Share_Percent",
    "Work_Model",
]

print(
    workfold[
        sample_columns
    ]
    .sample(
        min(10, len(workfold)),
        random_state=42,
    )
    .to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

print("\n" + "=" * 70)
print("SAVING WORKFOLD OUTPUTS")
print("=" * 70)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

workfold.to_parquet(
    OUTPUT_PARQUET,
    index=False,
)

workfold.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


print("\nSaved:")
print(OUTPUT_PARQUET)
print(OUTPUT_CSV)

print("\n" + "=" * 70)
print("WORKFOLD BUILD COMPLETE")
print("=" * 70)