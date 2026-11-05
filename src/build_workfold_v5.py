# ============================================================
# FORGE — WORKFOLD V5
# Future-Oriented Workforce Reconfiguration & Growth Engine
#
# V5 DESIGN
# ------------------------------------------------------------
# WORKTRACE
#      ↓
# Task Importance
#      ↓
# Task-level AI/Human semantic suitability
#      ↓
# Skill Shadow + Capability Risk
#      ↓
# Preservation constraint
#      ↓
# Evidence-driven AI allocation
#      ↓
# HUMAN / HYBRID / AI
#
# IMPORTANT:
# - AI suitability is a semantic index, NOT probability.
# - Skill Shadow is a FORGE-defined metric.
# - No fake salary/cost/quality assumptions.
# - AI adoption target is a scenario target.
# ============================================================

from pathlib import Path
import warnings
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

WORKTRACE_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

SKILL_SHADOW_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
)

OUTPUT_PARQUET = OUTPUT_DIR / "forge_workfold_v5.parquet"
OUTPUT_CSV = OUTPUT_DIR / "forge_workfold_v5.csv"


# ============================================================
# SCENARIO
# ============================================================

AI_ADOPTION_TARGET = 0.50

GLOBAL_MAX_AI_SHARE = 0.80
GLOBAL_MIN_AI_SHARE = 0.00


# ============================================================
# MODEL PARAMETERS
#
# These are scenario/model parameters.
# They are NOT empirical probabilities.
# ============================================================

# How strongly suitability influences allocation.
SUITABILITY_WEIGHT = 1.00

# Preservation pressure.
PRESERVATION_WEIGHT = 0.65

# Skill-shadow-specific protection.
SHADOW_WEIGHT = 0.45

# Stay close to evidence-derived preference.
PREFERENCE_WEIGHT = 0.35

# Track requested AI adoption target.
TARGET_TRACKING_WEIGHT = 2.50


# ============================================================
# SEMANTIC ANCHORS
# ============================================================

AUTOMATION_ANCHORS = [
    "routine repetitive data processing",
    "structured retrieval and document processing",
    "classification extraction transcription and standard transformation",
    "rule based administrative processing",
    "predictable monitoring reporting and record keeping",
]


HUMAN_ANCHORS = [
    "complex human judgment under uncertainty",
    "leadership negotiation persuasion and interpersonal interaction",
    "physical work dexterity and environmental interaction",
    "creative problem solving adaptation and novel situations",
    "ethical accountability ambiguous decisions and responsibility",
]


MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def weighted_mean(values, weights):

    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)

    mask = (
        np.isfinite(values)
        & np.isfinite(weights)
        & (weights > 0)
    )

    if not mask.any():
        return np.nan

    return np.average(
        values[mask],
        weights=weights[mask]
    )


def minmax(series):

    s = pd.to_numeric(
        series,
        errors="coerce"
    )

    valid = s.dropna()

    if len(valid) == 0:
        return pd.Series(
            0.5,
            index=s.index
        )

    mn = valid.min()
    mx = valid.max()

    if np.isclose(mn, mx):

        result = pd.Series(
            0.5,
            index=s.index
        )

        result[s.isna()] = np.nan

        return result

    return (
        (s - mn)
        / (mx - mn)
    )


def capability_key(df):

    return (
        df["Capability Type"]
        .fillna("Unknown")
        .astype(str)
        + "::"
        + df["Capability ID"]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("FORGE — WORKFOLD V5")
print("=" * 70)


print("\n[1/11] Loading WORKTRACE...")

worktrace = pd.read_parquet(
    WORKTRACE_PATH
)

print(
    f"WORKTRACE: {worktrace.shape}"
)


print("\n[2/11] Loading SKILL SHADOW...")

shadow = pd.read_parquet(
    SKILL_SHADOW_PATH
)

print(
    f"SKILL SHADOW: {shadow.shape}"
)


# ============================================================
# VALIDATION
# ============================================================

required_worktrace = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
]

required_shadow = [
    "O*NET-SOC Code",
    "Capability Type",
    "Capability ID",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]


missing = [
    c
    for c in required_worktrace
    if c not in worktrace.columns
]

if missing:

    raise ValueError(
        f"WORKTRACE missing columns: {missing}"
    )


missing = [
    c
    for c in required_shadow
    if c not in shadow.columns
]

if missing:

    raise ValueError(
        f"SKILL SHADOW missing columns: {missing}"
    )


# ============================================================
# CLEAN
# ============================================================

print("\n[3/11] Cleaning evidence...")

worktrace = worktrace.copy()
shadow = shadow.copy()


worktrace["Task"] = (
    worktrace["Task"]
    .fillna("")
    .astype(str)
    .str.strip()
)

worktrace["DWA Element Name"] = (
    worktrace["DWA Element Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)


worktrace["Task Capability Weight"] = pd.to_numeric(
    worktrace["Task Capability Weight"],
    errors="coerce"
).fillna(0)


worktrace["Task Capability Weight"] = (
    worktrace["Task Capability Weight"]
    .clip(lower=0)
)


# ============================================================
# KEYS
# ============================================================

worktrace["Capability Key"] = capability_key(
    worktrace
)

shadow["Capability Key"] = capability_key(
    shadow
)


worktrace["Task Key"] = (
    worktrace["O*NET-SOC Code"]
    .astype(str)
    + "::"
    + worktrace["Task ID"]
    .astype(str)
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

before = len(worktrace)

worktrace = worktrace.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "Capability Key",
    ]
)

print(
    "Removed duplicates:",
    before - len(worktrace)
)


# ============================================================
# CAPABILITY IMPORTANCE WITHIN TASK
# ============================================================

task_capability_sum = (
    worktrace
    .groupby("Task Key")[
        "Task Capability Weight"
    ]
    .transform("sum")
)


task_capability_sum = (
    task_capability_sum
    .replace(0, np.nan)
)


worktrace[
    "Capability_Weight_Within_Task"
] = (
    worktrace["Task Capability Weight"]
    / task_capability_sum
).fillna(0)


# ============================================================
# TASK IMPORTANCE
#
# Raw capability evidence determines importance.
# Then normalize across tasks within occupation.
# ============================================================

task_importance = (
    worktrace
    .groupby(
        [
            "O*NET-SOC Code",
            "Task Key",
        ]
    )[
        "Task Capability Weight"
    ]
    .sum()
    .reset_index()
    .rename(
        columns={
            "Task Capability Weight":
            "Task_Raw_Importance"
        }
    )
)


occupation_sum = (
    task_importance
    .groupby("O*NET-SOC Code")[
        "Task_Raw_Importance"
    ]
    .transform("sum")
)


occupation_sum = (
    occupation_sum
    .replace(0, np.nan)
)


task_importance["Task_Importance"] = (
    task_importance["Task_Raw_Importance"]
    / occupation_sum
).fillna(0)


worktrace = worktrace.merge(
    task_importance[
        [
            "Task Key",
            "Task_Raw_Importance",
            "Task_Importance",
        ]
    ],
    on="Task Key",
    how="left",
)


# ============================================================
# SKILL SHADOW MERGE
# ============================================================

print("\n[4/11] Joining Skill Shadow...")


shadow_small = (
    shadow[
        [
            "O*NET-SOC Code",
            "Capability Key",
            "Skill_Shadow",
            "Capability_Risk",
            "Capability_Criticality",
        ]
    ]
    .drop_duplicates(
        subset=[
            "O*NET-SOC Code",
            "Capability Key",
        ]
    )
)


worktrace = worktrace.merge(
    shadow_small,
    on=[
        "O*NET-SOC Code",
        "Capability Key",
    ],
    how="left",
    indicator="_shadow_match"
)


worktrace["Shadow_Matched"] = (
    worktrace["_shadow_match"]
    == "both"
)


# ============================================================
# EVIDENCE COVERAGE
# ============================================================

worktrace["Matched_Weight"] = np.where(
    worktrace["Shadow_Matched"],
    worktrace[
        "Capability_Weight_Within_Task"
    ],
    0
)


coverage = (
    worktrace
    .groupby("Task Key")[
        "Matched_Weight"
    ]
    .sum()
    .rename(
        "Shadow_Evidence_Coverage"
    )
    .reset_index()
)


worktrace = worktrace.merge(
    coverage,
    on="Task Key",
    how="left"
)


# ============================================================
# OCCUPATION-LEVEL FALLBACK
# ============================================================

print("\nBuilding uncertainty-aware evidence...")


shadow_median = (
    shadow
    .groupby("O*NET-SOC Code")[
        "Skill_Shadow"
    ]
    .median()
)


risk_median = (
    shadow
    .groupby("O*NET-SOC Code")[
        "Capability_Risk"
    ]
    .median()
)


criticality_median = (
    shadow
    .groupby("O*NET-SOC Code")[
        "Capability_Criticality"
    ]
    .median()
)


global_shadow = shadow[
    "Skill_Shadow"
].median()


global_risk = shadow[
    "Capability_Risk"
].median()


global_criticality = shadow[
    "Capability_Criticality"
].median()


worktrace["Occupation_Shadow_Median"] = (
    worktrace["O*NET-SOC Code"]
    .map(shadow_median)
    .fillna(global_shadow)
)


worktrace["Occupation_Risk_Median"] = (
    worktrace["O*NET-SOC Code"]
    .map(risk_median)
    .fillna(global_risk)
)


worktrace[
    "Occupation_Criticality_Median"
] = (
    worktrace["O*NET-SOC Code"]
    .map(criticality_median)
    .fillna(global_criticality)
)


worktrace[
    "Effective_Skill_Shadow"
] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace["Skill_Shadow"].fillna(
        worktrace["Occupation_Shadow_Median"]
    )
    +
    (
        1
        - worktrace[
            "Shadow_Evidence_Coverage"
        ]
    )
    * worktrace[
        "Occupation_Shadow_Median"
    ]
)


worktrace[
    "Effective_Capability_Risk"
] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace["Capability_Risk"].fillna(
        worktrace["Occupation_Risk_Median"]
    )
    +
    (
        1
        - worktrace[
            "Shadow_Evidence_Coverage"
        ]
    )
    * worktrace[
        "Occupation_Risk_Median"
    ]
)


worktrace[
    "Effective_Criticality"
] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace[
        "Capability_Criticality"
    ].fillna(
        worktrace[
            "Occupation_Criticality_Median"
        ]
    )
    +
    (
        1
        - worktrace[
            "Shadow_Evidence_Coverage"
        ]
    )
    * worktrace[
        "Occupation_Criticality_Median"
    ]
)


# ============================================================
# TASK AGGREGATION
# ============================================================

print("\n[5/11] Aggregating tasks...")


def aggregate_task(group):

    weights = group[
        "Capability_Weight_Within_Task"
    ].to_numpy(float)

    return pd.Series({

        "Task_Skill_Shadow":
            weighted_mean(
                group[
                    "Effective_Skill_Shadow"
                ],
                weights
            ),

        "Task_Capability_Risk":
            weighted_mean(
                group[
                    "Effective_Capability_Risk"
                ],
                weights
            ),

        "Task_Capability_Criticality":
            weighted_mean(
                group[
                    "Effective_Criticality"
                ],
                weights
            ),

        "Shadow_Evidence_Coverage":
            group[
                "Matched_Weight"
            ].sum(),

    })


task_metrics = (
    worktrace
    .groupby("Task Key")
    .apply(
        aggregate_task,
        include_groups=False
    )
    .reset_index()
)


# ============================================================
# TASK METADATA
# ============================================================

metadata = (
    worktrace[
        [
            "Task Key",
            "O*NET-SOC Code",
            "Occupation Title",
            "Task ID",
            "Task",
            "DWA Element Name",
            "Task_Raw_Importance",
            "Task_Importance",
        ]
    ]
    .drop_duplicates(
        subset=["Task Key"]
    )
)


tasks = metadata.merge(
    task_metrics,
    on="Task Key",
    how="left"
)


# ============================================================
# PRIMARY CAPABILITIES
# ============================================================

print("\n[6/11] Extracting primary capabilities...")


def get_primary_capabilities(group):

    x = (
        group[
            [
                "Capability Name",
                "Capability_Weight_Within_Task",
            ]
        ]
        .dropna(
            subset=["Capability Name"]
        )
        .drop_duplicates()
        .sort_values(
            "Capability_Weight_Within_Task",
            ascending=False
        )
        .head(5)
    )

    return ", ".join(
        x["Capability Name"]
        .astype(str)
        .tolist()
    )


primary = (
    worktrace
    .groupby("Task Key")
    .apply(
        get_primary_capabilities,
        include_groups=False
    )
    .rename(
        "Primary_Capabilities"
    )
    .reset_index()
)


tasks = tasks.merge(
    primary,
    on="Task Key",
    how="left"
)


# ============================================================
# TASK SEMANTIC TEXT
# ============================================================

tasks["Task_Text"] = (
    tasks["Task"]
    .fillna("")
    .astype(str)
    + ". "
    + tasks["DWA Element Name"]
    .fillna("")
    .astype(str)
)


tasks["Task_Text"] = (
    tasks["Task_Text"]
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip()
)


# ============================================================
# SENTENCE TRANSFORMER
# ============================================================

print("\n[7/11] Loading SentenceTransformer...")


model = SentenceTransformer(
    MODEL_NAME
)


print("Encoding automation anchors...")


auto_emb = model.encode(
    AUTOMATION_ANCHORS,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False,
)


print("Encoding human anchors...")


human_emb = model.encode(
    HUMAN_ANCHORS,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False,
)


print(
    f"Encoding {len(tasks):,} tasks..."
)


task_emb = model.encode(
    tasks["Task_Text"].tolist(),
    batch_size=256,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True,
)


# ============================================================
# SEMANTIC SCORES
# ============================================================

print("\n[8/11] Computing task suitability...")


auto_scores = (
    task_emb
    @ auto_emb.T
)


human_scores = (
    task_emb
    @ human_emb.T
)


tasks["Automation_Max_Similarity"] = (
    auto_scores.max(axis=1)
)


tasks["Human_Max_Similarity"] = (
    human_scores.max(axis=1)
)


tasks["Automation_Human_Balance"] = (
    tasks["Automation_Max_Similarity"]
    - tasks["Human_Max_Similarity"]
)


# Convert approximately [-1,+1] to [0,1].
tasks["Task_AI_Suitability"] = (
    (
        tasks[
            "Automation_Human_Balance"
        ]
        + 1
    )
    / 2
).clip(0, 1)


tasks["Task_Human_Suitability"] = (
    1
    - tasks["Task_AI_Suitability"]
)


# ============================================================
# NORMALIZED PRESERVATION SIGNALS
# ============================================================

print("\nBuilding preservation signal...")


tasks["Risk_N"] = minmax(
    tasks["Task_Capability_Risk"]
).fillna(0.5)


tasks["Shadow_N"] = minmax(
    tasks["Task_Skill_Shadow"]
).fillna(0.5)


tasks["Criticality_N"] = minmax(
    tasks["Task_Capability_Criticality"]
).fillna(0.5)


# ============================================================
# PRESERVATION PRESSURE
# ============================================================

tasks["Preservation_Pressure"] = (
    0.45 * tasks["Risk_N"]
    + 0.35 * tasks["Shadow_N"]
    + 0.20 * tasks["Criticality_N"]
).clip(0, 1)


# ============================================================
# EVIDENCE CONFIDENCE
# ============================================================

tasks["Evidence_Confidence"] = (
    tasks["Shadow_Evidence_Coverage"]
    .clip(0, 1)
)


# ============================================================
# V5 CORE DECISION MODEL
# ============================================================

print("\n[9/11] Building evidence-driven allocation bounds...")


# ------------------------------------------------------------
# STEP A
# Evidence-driven preference.
#
# High automation suitability -> higher preference.
#
# High preservation pressure -> lower preference.
# ------------------------------------------------------------

tasks["AI_Preferred_Share"] = (
    GLOBAL_MAX_AI_SHARE
    * tasks["Task_AI_Suitability"]
    * (
        1
        - 0.50
        * tasks["Preservation_Pressure"]
    )
)


tasks["AI_Preferred_Share"] = (
    tasks["AI_Preferred_Share"]
    .clip(
        GLOBAL_MIN_AI_SHARE,
        GLOBAL_MAX_AI_SHARE
    )
)


# ------------------------------------------------------------
# STEP B
# Safety ceiling.
#
# This is deliberately LESS restrictive than V4.
#
# Preservation pressure reduces maximum delegation,
# but does not automatically collapse it toward zero.
# ------------------------------------------------------------

tasks["AI_Ceiling"] = (
    GLOBAL_MAX_AI_SHARE
    * (
        0.15
        + 0.85
        * tasks["Task_AI_Suitability"]
    )
    * (
        1
        - 0.35
        * tasks["Preservation_Pressure"]
    )
)


tasks["AI_Ceiling"] = (
    tasks["AI_Ceiling"]
    .clip(
        GLOBAL_MIN_AI_SHARE,
        GLOBAL_MAX_AI_SHARE
    )
)


# ------------------------------------------------------------
# Human floor for high-preservation tasks
# ------------------------------------------------------------

tasks["Human_Preservation_Floor"] = (
    0.15
    * tasks["Preservation_Pressure"]
)


tasks["AI_Ceiling"] = np.minimum(
    tasks["AI_Ceiling"],
    1
    - tasks["Human_Preservation_Floor"]
)


# ============================================================
# FEASIBILITY
# ============================================================

occupation_max = (
    tasks
    .groupby("O*NET-SOC Code")
    .apply(
        lambda g:
        np.sum(
            g["Task_Importance"]
            * g["AI_Ceiling"]
        ),
        include_groups=False
    )
    .rename(
        "Max_Feasible_AI_Adoption"
    )
    .reset_index()
)


tasks = tasks.merge(
    occupation_max,
    on="O*NET-SOC Code",
    how="left"
)


tasks["Target_Feasibility"] = np.where(
    tasks[
        "Max_Feasible_AI_Adoption"
    ]
    >= AI_ADOPTION_TARGET,
    "Feasible",
    "Infeasible"
)


# ============================================================
# OPTIMIZER
# ============================================================

print("\n[10/11] Optimizing occupation by occupation...")


def optimize_group(group):

    group = group.copy()

    n = len(group)

    if n == 0:
        return group


    # --------------------------------------------------------
    # Arrays
    # --------------------------------------------------------

    w = group[
        "Task_Importance"
    ].to_numpy(float)

    suitability = group[
        "Task_AI_Suitability"
    ].to_numpy(float)

    preservation = group[
        "Preservation_Pressure"
    ].to_numpy(float)

    shadow_value = group[
        "Task_Skill_Shadow"
    ].to_numpy(float)

    preferred = group[
        "AI_Preferred_Share"
    ].to_numpy(float)

    ceiling = group[
        "AI_Ceiling"
    ].to_numpy(float)


    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------

    w = np.nan_to_num(
        w,
        nan=0
    )

    suitability = np.nan_to_num(
        suitability,
        nan=0.5
    )

    preservation = np.nan_to_num(
        preservation,
        nan=0.5
    )

    shadow_value = np.nan_to_num(
        shadow_value,
        nan=0.5
    )

    preferred = np.nan_to_num(
        preferred,
        nan=0
    )

    ceiling = np.nan_to_num(
        ceiling,
        nan=0
    )


    # Normalize importance.
    total = w.sum()

    if total <= 0:

        w = np.ones(n) / n

    else:

        w = w / total


    # --------------------------------------------------------
    # Initial allocation
    # --------------------------------------------------------

    x0 = np.minimum(
        preferred,
        ceiling
    )


    # --------------------------------------------------------
    # Objective
    #
    # Three competing goals:
    #
    # 1. Automate suitable work.
    # 2. Protect capability preservation.
    # 3. Stay reasonably close to evidence preference.
    #
    # Plus target tracking.
    # --------------------------------------------------------

    def objective(x):

        weighted_adoption = np.sum(
            w * x
        )


        automation_value = np.sum(
            w
            * suitability
            * x
        )


        preservation_loss = np.sum(
            w
            * preservation
            * x
        )


        shadow_loss = np.sum(
            w
            * shadow_value
            * x
        )


        preference_loss = np.sum(
            w
            * (
                x - preferred
            ) ** 2
        )


        target_loss = (
            weighted_adoption
            - AI_ADOPTION_TARGET
        ) ** 2


        return (

            PREFERENCE_WEIGHT
            * preference_loss

            + TARGET_TRACKING_WEIGHT
            * target_loss

            - SUITABILITY_WEIGHT
            * automation_value

            + PRESERVATION_WEIGHT
            * preservation_loss

            + SHADOW_WEIGHT
            * shadow_loss

        )


    # --------------------------------------------------------
    # Bounds
    # --------------------------------------------------------

    bounds = [
        (
            GLOBAL_MIN_AI_SHARE,
            float(c)
        )
        for c in ceiling
    ]


    # --------------------------------------------------------
    # Optimize
    # --------------------------------------------------------

    success = False

    try:

        result = minimize(
            objective,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            options={
                "maxiter": 250,
                "ftol": 1e-8,
                "disp": False,
            }
        )

        if result.success:

            allocation = result.x
            success = True

        else:

            allocation = x0

    except Exception:

        allocation = x0


    allocation = np.clip(
        allocation,
        0,
        ceiling
    )


    # --------------------------------------------------------
    # Adoption
    # --------------------------------------------------------

    actual_adoption = np.sum(
        w * allocation
    )


    max_feasible = np.sum(
        w * ceiling
    )


    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    group["AI_Share"] = allocation

    group["Human_Share"] = (
        1
        - allocation
    )

    group["Actual_AI_Adoption"] = (
        actual_adoption
    )

    group["Actual_Human_Adoption"] = (
        1
        - actual_adoption
    )

    group["Target_AI_Adoption"] = (
        AI_ADOPTION_TARGET
    )

    group[
        "Target_Gap_Percentage_Points"
    ] = (
        actual_adoption
        - AI_ADOPTION_TARGET
    ) * 100

    group[
        "Max_Feasible_AI_Adoption"
    ] = max_feasible

    group[
        "Optimization_Success"
    ] = success


    return group


results = []


for occupation, group in tasks.groupby(
    "O*NET-SOC Code",
    sort=False
):

    results.append(
        optimize_group(group)
    )


tasks = pd.concat(
    results,
    ignore_index=True
)


# ============================================================
# WORK MODEL
# ============================================================

print("\nCreating workforce model...")


def classify(ai):

    if ai >= 0.65:
        return "AI-led"

    if ai <= 0.35:
        return "Human-led"

    return "Hybrid"


tasks["Work_Model"] = (
    tasks["AI_Share"]
    .apply(classify)
)


# ============================================================
# DECISION EXPLANATION
# ============================================================

def explanation(row):

    ai = row["AI_Share"]

    suitability = (
        row["Task_AI_Suitability"]
    )

    pressure = (
        row["Preservation_Pressure"]
    )

    shadow = (
        row["Task_Skill_Shadow"]
    )

    evidence = (
        row["Evidence_Confidence"]
    )

    model = row["Work_Model"]


    if model == "AI-led":

        return (
            f"AI-led ({ai*100:.1f}%) because the task has "
            f"stronger automation suitability "
            f"({suitability*100:.1f}%) and the modeled "
            f"preservation pressure is {pressure*100:.1f}%. "
            f"Skill Shadow is {shadow*100:.1f}%."
        )


    if model == "Hybrid":

        return (
            f"Hybrid ({ai*100:.1f}% AI / "
            f"{(1-ai)*100:.1f}% human) because automation "
            f"suitability ({suitability*100:.1f}%) supports "
            f"partial delegation while preservation pressure "
            f"({pressure*100:.1f}%) argues for continued human "
            f"involvement."
        )


    return (
        f"Human-led ({(1-ai)*100:.1f}% human) because the "
        f"evidence-driven allocation limits AI delegation to "
        f"{ai*100:.1f}%. Automation suitability is "
        f"{suitability*100:.1f}% and preservation pressure is "
        f"{pressure*100:.1f}%."
    )


tasks["Decision_Explanation"] = (
    tasks.apply(
        explanation,
        axis=1
    )
)


# ============================================================
# PERCENTAGE FIELDS
# ============================================================

tasks["AI_Share_Percent"] = (
    tasks["AI_Share"]
    * 100
)

tasks["Human_Share_Percent"] = (
    tasks["Human_Share"]
    * 100
)

tasks["AI_Ceiling_Percent"] = (
    tasks["AI_Ceiling"]
    * 100
)

tasks["AI_Preferred_Share_Percent"] = (
    tasks["AI_Preferred_Share"]
    * 100
)

tasks[
    "Task_AI_Suitability_Percent"
] = (
    tasks["Task_AI_Suitability"]
    * 100
)

tasks[
    "Preservation_Pressure_Percent"
] = (
    tasks["Preservation_Pressure"]
    * 100
)

tasks[
    "Evidence_Confidence_Percent"
] = (
    tasks["Evidence_Confidence"]
    * 100
)


# ============================================================
# SORT
# ============================================================

tasks = tasks.sort_values(
    [
        "O*NET-SOC Code",
        "Task_Importance",
    ],
    ascending=[
        True,
        False,
    ]
).reset_index(drop=True)


# ============================================================
# FINAL COLUMNS
# ============================================================

final_columns = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",

    "Primary_Capabilities",

    "Task_Raw_Importance",
    "Task_Importance",

    "Automation_Max_Similarity",
    "Human_Max_Similarity",
    "Automation_Human_Balance",

    "Task_AI_Suitability",
    "Task_AI_Suitability_Percent",
    "Task_Human_Suitability",

    "Task_Skill_Shadow",
    "Task_Capability_Risk",
    "Task_Capability_Criticality",

    "Risk_N",
    "Shadow_N",
    "Criticality_N",

    "Preservation_Pressure",
    "Preservation_Pressure_Percent",

    "Shadow_Evidence_Coverage",
    "Evidence_Confidence",
    "Evidence_Confidence_Percent",

    "AI_Preferred_Share",
    "AI_Preferred_Share_Percent",

    "AI_Ceiling",
    "AI_Ceiling_Percent",

    "Human_Preservation_Floor",

    "AI_Share",
    "AI_Share_Percent",

    "Human_Share",
    "Human_Share_Percent",

    "Work_Model",

    "Actual_AI_Adoption",
    "Actual_Human_Adoption",

    "Target_AI_Adoption",
    "Target_Gap_Percentage_Points",

    "Max_Feasible_AI_Adoption",
    "Target_Feasibility",

    "Optimization_Success",

    "Decision_Explanation",

    "Task Key",
]


final_columns = [
    c for c in final_columns
    if c in tasks.columns
]


final_df = tasks[
    final_columns
].copy()


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("WORKFOLD V5 VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# Uniqueness
# ------------------------------------------------------------

print(
    f"\nRecords: {len(final_df):,}"
)

print(
    f"Unique tasks: "
    f"{final_df['Task Key'].nunique():,}"
)

print(
    "Task uniqueness:",
    (
        "PASSED"
        if len(final_df)
        == final_df["Task Key"].nunique()
        else "FAILED"
    )
)


print(
    f"Unique occupations: "
    f"{final_df['O*NET-SOC Code'].nunique():,}"
)


# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

print("\nWork model distribution:")

print(
    final_df[
        "Work_Model"
    ].value_counts()
)


# ------------------------------------------------------------
# Adoption
# ------------------------------------------------------------

occupation_results = (
    final_df
    .groupby("O*NET-SOC Code")
    .first()
)


print("\nOccupation AI adoption:")

print(
    occupation_results[
        "Actual_AI_Adoption"
    ].describe()
)


mean_adoption = (
    occupation_results[
        "Actual_AI_Adoption"
    ].mean()
)


print(
    f"\nMean AI adoption: "
    f"{mean_adoption*100:.2f}%"
)


print(
    f"Target AI adoption: "
    f"{AI_ADOPTION_TARGET*100:.2f}%"
)


print(
    f"Mean target gap: "
    f"{(
        occupation_results[
            'Actual_AI_Adoption'
        ]
        - AI_ADOPTION_TARGET
    ).mean()*100:.2f} pp"
)


# ------------------------------------------------------------
# Feasibility
# ------------------------------------------------------------

print("\nTarget feasibility:")

print(
    occupation_results[
        "Target_Feasibility"
    ].value_counts()
)


# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

print("\nEvidence confidence:")

print(
    final_df[
        "Evidence_Confidence"
    ].describe()
)


# ------------------------------------------------------------
# Correlation audit
# ------------------------------------------------------------

print("\nBehavior audit:")


corr_suitability = (
    final_df[
        [
            "AI_Share",
            "Task_AI_Suitability",
        ]
    ]
    .corr()
    .iloc[0, 1]
)


corr_risk = (
    final_df[
        [
            "AI_Share",
            "Task_Capability_Risk",
        ]
    ]
    .corr()
    .iloc[0, 1]
)


corr_shadow = (
    final_df[
        [
            "AI_Share",
            "Task_Skill_Shadow",
        ]
    ]
    .corr()
    .iloc[0, 1]
)


corr_pressure = (
    final_df[
        [
            "AI_Share",
            "Preservation_Pressure",
        ]
    ]
    .corr()
    .iloc[0, 1]
)


print(
    f"AI share vs suitability: "
    f"{corr_suitability:.4f}"
)

print(
    f"AI share vs capability risk: "
    f"{corr_risk:.4f}"
)

print(
    f"AI share vs skill shadow: "
    f"{corr_shadow:.4f}"
)

print(
    f"AI share vs preservation pressure: "
    f"{corr_pressure:.4f}"
)


# ------------------------------------------------------------
# Ceiling check
# ------------------------------------------------------------

ceiling_violations = (
    final_df["AI_Share"]
    > final_df["AI_Ceiling"]
    + 1e-7
).sum()


print(
    f"\nAI ceiling violations: "
    f"{ceiling_violations}"
)


# ------------------------------------------------------------
# Range checks
# ------------------------------------------------------------

checks = {

    "AI_Share":
        final_df["AI_Share"]
        .between(0, 1)
        .all(),

    "Human_Share":
        final_df["Human_Share"]
        .between(0, 1)
        .all(),

    "Task_AI_Suitability":
        final_df[
            "Task_AI_Suitability"
        ]
        .between(0, 1)
        .all(),

    "Preservation_Pressure":
        final_df[
            "Preservation_Pressure"
        ]
        .between(0, 1)
        .all(),

    "Evidence_Confidence":
        final_df[
            "Evidence_Confidence"
        ]
        .between(0, 1)
        .all(),
}


print("\nRange checks:")

for key, value in checks.items():

    print(
        f"{key}:",
        "PASSED"
        if value
        else "FAILED"
    )


# ============================================================
# HIGH AI TASKS
# ============================================================

print(
    "\n"
    + "=" * 70
)

print("HIGHEST AI ALLOCATION")

print(
    "=" * 70
)


high = (
    final_df
    .sort_values(
        "AI_Share",
        ascending=False
    )
    [
        [
            "Occupation Title",
            "Task",
            "AI_Share_Percent",
            "Task_AI_Suitability_Percent",
            "Preservation_Pressure_Percent",
            "AI_Ceiling_Percent",
            "Work_Model",
        ]
    ]
    .head(15)
)


print(
    high.to_string(
        index=False
    )
)


# ============================================================
# LOW AI TASKS
# ============================================================

print(
    "\n"
    + "=" * 70
)

print("LOWEST AI ALLOCATION")

print(
    "=" * 70
)


low = (
    final_df
    .sort_values(
        "AI_Share",
        ascending=True
    )
    [
        [
            "Occupation Title",
            "Task",
            "AI_Share_Percent",
            "Task_AI_Suitability_Percent",
            "Preservation_Pressure_Percent",
            "AI_Ceiling_Percent",
            "Work_Model",
        ]
    ]
    .head(15)
)


print(
    low.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print(
    "\nSaving WORKFOLD V5..."
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


final_df.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


final_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# COMPLETE
# ============================================================

print(
    "\n"
    + "=" * 70
)

print("WORKFOLD V5 COMPLETE")

print(
    "=" * 70
)

print(
    f"Parquet: {OUTPUT_PARQUET}"
)

print(
    f"CSV:     {OUTPUT_CSV}"
)

print(
    f"Final shape: {final_df.shape}"
)

print(
    "=" * 70
)