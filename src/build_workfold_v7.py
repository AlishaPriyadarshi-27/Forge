import os
import warnings
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from scipy.optimize import minimize

warnings.filterwarnings("ignore")

# ============================================================
# FORGE — WORKFOLD V7
# Adaptive Capability-Preservation Optimizer
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORKTRACE_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_worktrace.parquet"
)

SHADOW_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_skill_shadow.parquet"
)

OUT_PARQUET = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_workfold_v7.parquet"
)

OUT_CSV = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_workfold_v7.csv"
)

# ============================================================
# CONFIGURATION
# ============================================================

REQUESTED_TARGET = 0.50

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_PRIMARY_CAPABILITIES = 5

# ------------------------------------------------------------
# Skill Shadow preservation controls
# ------------------------------------------------------------

# Direct Skill Shadow penalty
SKILL_SHADOW_PENALTY = 0.55

# Capability risk penalty
CAPABILITY_RISK_PENALTY = 0.30

# Criticality penalty
CRITICALITY_PENALTY = 0.15

# ------------------------------------------------------------
# Human preservation floor
# ------------------------------------------------------------

BASE_HUMAN_FLOOR = 0.05

MAX_HUMAN_FLOOR = 0.85

PRESERVATION_FLOOR_EXPONENT = 1.25

# ------------------------------------------------------------
# AI ceiling
# ------------------------------------------------------------

MAX_AI_SHARE = 0.80

AI_CEILING_PRESERVATION_PENALTY = 0.65

# ------------------------------------------------------------
# Optimization
# ------------------------------------------------------------

SUITABILITY_REWARD = 2.0

AUTOMATION_VALUE_REWARD = 0.45

SHADOW_COST = 3.0

RISK_COST = 1.5

CRITICALITY_COST = 0.75

TARGET_GAP_COST = 0.25

SMOOTHNESS_COST = 0.15

# ------------------------------------------------------------
# Work model thresholds
# ------------------------------------------------------------

AI_LED_THRESHOLD = 0.60
AI_LED_SUITABILITY_THRESHOLD = 0.60

HUMAN_LED_THRESHOLD = 0.25

# ============================================================
# AUTOMATION / HUMAN SEMANTIC ANCHORS
# ============================================================

AUTOMATION_ANCHORS = [
    "routine repetitive data processing",
    "structured information retrieval",
    "document processing",
    "classification and extraction",
    "transcription",
    "standardized transformation",
    "rule based administrative processing",
    "predictable monitoring",
    "routine reporting",
    "record keeping",
    "data entry",
    "sorting and organizing structured information",
    "repetitive digital workflow",
]

HUMAN_ANCHORS = [
    "complex human judgment under uncertainty",
    "leadership and management",
    "negotiation and persuasion",
    "interpersonal interaction",
    "physical work requiring dexterity",
    "environment interaction",
    "creative problem solving",
    "adaptation to novel situations",
    "ethical decision making",
    "accountability",
    "ambiguous decisions",
    "empathy and human support",
    "hands on physical intervention",
]

# ============================================================
# HELPERS
# ============================================================

def minmax(series):
    series = pd.to_numeric(series, errors="coerce")
    valid = series.dropna()

    if len(valid) == 0:
        return pd.Series(
            np.zeros(len(series)),
            index=series.index
        )

    mn = valid.min()
    mx = valid.max()

    if mx <= mn:
        return pd.Series(
            np.zeros(len(series)),
            index=series.index
        )

    return ((series - mn) / (mx - mn)).fillna(0)


def safe_numeric(df, col, default=0.0):
    if col not in df.columns:
        df[col] = default

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    ).fillna(default)

    return df


def normalize_capability_key(df):
    df["Capability Key"] = (
        df["Capability Type"].astype(str)
        + "::"
        + df["Capability ID"].astype(str)
    )

    return df


# ============================================================
# START
# ============================================================

print("=" * 72)
print("FORGE — WORKFOLD V7")
print("Adaptive Capability-Preservation Optimizer")
print("=" * 72)


# ============================================================
# 1. LOAD WORKTRACE
# ============================================================

print("\n[1/13] Loading WORKTRACE...")

worktrace = pd.read_parquet(WORKTRACE_PATH)

print("WORKTRACE shape:", worktrace.shape)


required_worktrace = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
]

missing = [
    c for c in required_worktrace
    if c not in worktrace.columns
]

if missing:
    raise ValueError(
        f"WORKTRACE missing required columns: {missing}"
    )


# ============================================================
# 2. LOAD SKILL SHADOW
# ============================================================

print("\n[2/13] Loading SKILL SHADOW...")

shadow = pd.read_parquet(SHADOW_PATH)

print("SKILL SHADOW shape:", shadow.shape)

required_shadow = [
    "O*NET-SOC Code",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]

missing = [
    c for c in required_shadow
    if c not in shadow.columns
]

if missing:
    raise ValueError(
        f"SKILL SHADOW missing required columns: {missing}"
    )


# ============================================================
# 3. CLEAN TASK-CAPABILITY EVIDENCE
# ============================================================

print("\n[3/13] Cleaning task-capability evidence...")

worktrace = worktrace.copy()
shadow = shadow.copy()

worktrace = normalize_capability_key(worktrace)
shadow = normalize_capability_key(shadow)

worktrace["Task Capability Weight"] = pd.to_numeric(
    worktrace["Task Capability Weight"],
    errors="coerce"
).fillna(0)

# Remove exact duplicate task-capability records
before = len(worktrace)

worktrace = worktrace.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "Capability Key"
    ]
).copy()

print(
    "Duplicate task-capability rows removed:",
    before - len(worktrace)
)


# ============================================================
# 4. JOIN CAPABILITY PRESERVATION EVIDENCE
# ============================================================

print("\n[4/13] Joining capability-preservation evidence...")

shadow_cols = [
    "O*NET-SOC Code",
    "Capability Key",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]

optional_shadow_cols = [
    "Skill_Shadow_Percent",
    "Risk_Band",
    "Market_Job_Count",
    "Market_Avg_Similarity",
    "Employment_Change_Percent",
    "Annual_Openings_Thousands",
]

for col in optional_shadow_cols:
    if col in shadow.columns:
        shadow_cols.append(col)

shadow_small = shadow[
    [c for c in shadow_cols if c in shadow.columns]
].copy()

# Ensure unique occupation-capability evidence
shadow_small = shadow_small.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Capability Key"
    ]
)

tasks = worktrace.merge(
    shadow_small,
    on=[
        "O*NET-SOC Code",
        "Capability Key"
    ],
    how="left",
    suffixes=("", "_shadow")
)

# ============================================================
# Missing evidence handling
# ============================================================

for col in [
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]:
    tasks[col] = pd.to_numeric(
        tasks[col],
        errors="coerce"
    )

# Occupation-level fallback
for col in [
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]:
    occ_median = tasks.groupby(
        "O*NET-SOC Code"
    )[col].transform("median")

    global_median = tasks[col].median()

    tasks[col] = (
        tasks[col]
        .fillna(occ_median)
        .fillna(global_median)
    )

# Original evidence availability flag
tasks["Evidence_Available"] = (
    tasks[
        [
            "Skill_Shadow",
            "Capability_Risk",
            "Capability_Criticality",
        ]
    ].notna().all(axis=1)
)

# Because fallback has now filled values,
# preserve the original evidence state separately.
original_shadow = worktrace.merge(
    shadow_small[
        [
            "O*NET-SOC Code",
            "Capability Key"
        ]
    ],
    on=[
        "O*NET-SOC Code",
        "Capability Key"
    ],
    how="left",
    indicator=True
)

tasks["Raw_Evidence_Available"] = (
    original_shadow["_merge"].eq("both").values
)

print(
    "Raw capability evidence coverage:",
    round(
        tasks["Raw_Evidence_Available"].mean() * 100,
        2
    ),
    "%"
)


# ============================================================
# 5. CREATE ONE ROW PER TASK
# ============================================================

print("\n[5/13] Creating one row per task...")

# Positive capability weights
tasks["Task Capability Weight"] = tasks[
    "Task Capability Weight"
].clip(lower=0)

# ------------------------------------------------------------
# Normalize capability importance within each task
# ------------------------------------------------------------

task_weight_sum = tasks.groupby(
    [
        "O*NET-SOC Code",
        "Task ID"
    ]
)["Task Capability Weight"].transform("sum")

tasks["Capability_Importance"] = np.where(
    task_weight_sum > 0,
    tasks["Task Capability Weight"] / task_weight_sum,
    1.0 / tasks.groupby(
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    )["Task Capability Weight"].transform("count")
)

# ------------------------------------------------------------
# Aggregate task-level preservation evidence
# ------------------------------------------------------------

def weighted_average(group, value_col):
    weights = group["Capability_Importance"].values
    values = pd.to_numeric(
        group[value_col],
        errors="coerce"
    ).fillna(0).values

    if weights.sum() <= 0:
        return float(np.mean(values))

    return float(
        np.average(
            values,
            weights=weights
        )
    )


task_rows = []

group_cols = [
    "O*NET-SOC Code",
    "Task ID"
]

for (soc, task_id), group in tasks.groupby(
    group_cols,
    sort=False
):

    first = group.iloc[0]

    row = {
        "O*NET-SOC Code": soc,
        "Task ID": task_id,
        "Occupation Title": first.get(
            "Occupation Title",
            ""
        ),
        "Occupation Description": first.get(
            "Occupation Description",
            ""
        ),
        "Task": first.get(
            "Task",
            ""
        ),
        "DWA Element Name": first.get(
            "DWA Element Name",
            ""
        ),
        "Task_Capability_Count": len(group),
    }

    row["Task_Skill_Shadow"] = weighted_average(
        group,
        "Skill_Shadow"
    )

    row["Task_Capability_Risk"] = weighted_average(
        group,
        "Capability_Risk"
    )

    row["Task_Criticality"] = weighted_average(
        group,
        "Capability_Criticality"
    )

    row["Task_Evidence_Coverage"] = float(
        np.average(
            group["Raw_Evidence_Available"].astype(float),
            weights=group["Capability_Importance"]
        )
    )

    row["Capability_Importance_Total"] = float(
        group["Capability_Importance"].sum()
    )

    task_rows.append(row)


tasks = pd.DataFrame(task_rows)

print(
    "Unique task records:",
    len(tasks)
)


# ============================================================
# 6. EXTRACT PRIMARY CAPABILITIES
# ============================================================

print("\n[6/13] Extracting primary capabilities...")

capability_rows = []

for (soc, task_id), group in worktrace.groupby(
    [
        "O*NET-SOC Code",
        "Task ID"
    ],
    sort=False
):

    g = group.copy()

    g["Task Capability Weight"] = pd.to_numeric(
        g["Task Capability Weight"],
        errors="coerce"
    ).fillna(0)

    g = g.sort_values(
        "Task Capability Weight",
        ascending=False
    ).head(
        TOP_PRIMARY_CAPABILITIES
    )

    capabilities = []

    for _, r in g.iterrows():

        capabilities.append(
            f"{r['Capability Name']} "
            f"({r['Capability Type']})"
        )

    capability_rows.append(
        {
            "O*NET-SOC Code": soc,
            "Task ID": task_id,
            "Primary_Capabilities": " | ".join(
                capabilities
            )
        }
    )

primary = pd.DataFrame(capability_rows)

tasks = tasks.merge(
    primary,
    on=[
        "O*NET-SOC Code",
        "Task ID"
    ],
    how="left"
)


# ============================================================
# 7. LOAD SENTENCE TRANSFORMER
# ============================================================

print("\n[7/13] Loading SentenceTransformer...")

model = SentenceTransformer(
    MODEL_NAME
)

print("Encoding automation anchors...")

automation_embeddings = model.encode(
    AUTOMATION_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False
)

print("Encoding human anchors...")

human_embeddings = model.encode(
    HUMAN_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False
)

print(
    "Encoding",
    len(tasks),
    "tasks..."
)

task_text = (
    tasks["Occupation Title"].fillna("").astype(str)
    + ". "
    + tasks["Task"].fillna("").astype(str)
)

task_embeddings = model.encode(
    task_text.tolist(),
    normalize_embeddings=True,
    batch_size=256,
    show_progress_bar=True
)


# ============================================================
# 8. AI/HUMAN SUITABILITY
# ============================================================

print(
    "\n[8/13] Calculating AI/Human semantic suitability..."
)

automation_scores = (
    task_embeddings
    @ automation_embeddings.T
).max(axis=1)

human_scores = (
    task_embeddings
    @ human_embeddings.T
).max(axis=1)

# ------------------------------------------------------------
# Balanced suitability
# ------------------------------------------------------------

balance = (
    automation_scores
    - human_scores
)

suitability = (
    (balance + 1.0) / 2.0
)

suitability = np.clip(
    suitability,
    0,
    1
)

tasks["Automation_Semantic_Score"] = (
    automation_scores
)

tasks["Human_Semantic_Score"] = (
    human_scores
)

tasks["Task_AI_Suitability"] = suitability


# ============================================================
# 9. BUILD PRESERVATION SIGNALS
# ============================================================

print(
    "\n[9/13] Building adaptive preservation constraints..."
)

# ------------------------------------------------------------
# Normalize task-level preservation dimensions
# ------------------------------------------------------------

tasks["Skill_Shadow_Normalized"] = minmax(
    tasks["Task_Skill_Shadow"]
)

tasks["Capability_Risk_Normalized"] = minmax(
    tasks["Task_Capability_Risk"]
)

tasks["Criticality_Normalized"] = minmax(
    tasks["Task_Criticality"]
)

# ------------------------------------------------------------
# Direct preservation pressure
#
# Skill Shadow gets the highest weight.
# ------------------------------------------------------------

tasks["Preservation_Pressure"] = (
    SKILL_SHADOW_PENALTY
    * tasks["Skill_Shadow_Normalized"]
    +
    CAPABILITY_RISK_PENALTY
    * tasks["Capability_Risk_Normalized"]
    +
    CRITICALITY_PENALTY
    * tasks["Criticality_Normalized"]
)

tasks["Preservation_Pressure"] = np.clip(
    tasks["Preservation_Pressure"],
    0,
    1
)

# ------------------------------------------------------------
# Human preservation floor
# ------------------------------------------------------------

tasks["Human_Preservation_Floor"] = (
    BASE_HUMAN_FLOOR
    +
    (
        MAX_HUMAN_FLOOR
        - BASE_HUMAN_FLOOR
    )
    *
    (
        tasks["Preservation_Pressure"]
        ** PRESERVATION_FLOOR_EXPONENT
    )
)

tasks["Human_Preservation_Floor"] = tasks[
    "Human_Preservation_Floor"
].clip(
    0,
    MAX_HUMAN_FLOOR
)

# ------------------------------------------------------------
# AI ceiling
# ------------------------------------------------------------

raw_ceiling = (
    MAX_AI_SHARE
    *
    (
        0.15
        +
        0.85
        * tasks["Task_AI_Suitability"]
    )
    *
    (
        1
        -
        AI_CEILING_PRESERVATION_PENALTY
        * tasks["Preservation_Pressure"]
    )
)

# Never exceed complement of human floor
tasks["AI_Ceiling"] = np.minimum(
    raw_ceiling,
    1 - tasks["Human_Preservation_Floor"]
)

tasks["AI_Ceiling"] = tasks[
    "AI_Ceiling"
].clip(
    0,
    MAX_AI_SHARE
)


# ============================================================
# 10. ADAPTIVE MAXIMUM SAFE AI ADOPTION
# ============================================================

print(
    "\n[10/13] Calculating maximum safe AI adoption..."
)

# ------------------------------------------------------------
# We first calculate a task-level feasible AI share.
#
# This is NOT an AI probability.
# It is a scenario allocation bound.
# ------------------------------------------------------------

tasks["Preferred_AI_Share"] = (
    tasks["Task_AI_Suitability"]
    *
    (
        1
        -
        0.65
        * tasks["Skill_Shadow_Normalized"]
    )
    *
    (
        1
        -
        0.25
        * tasks["Capability_Risk_Normalized"]
    )
)

tasks["Preferred_AI_Share"] = np.minimum(
    tasks["Preferred_AI_Share"],
    tasks["AI_Ceiling"]
)

tasks["Preferred_AI_Share"] = tasks[
    "Preferred_AI_Share"
].clip(
    0,
    MAX_AI_SHARE
)


# ------------------------------------------------------------
# Occupation task importance
# ------------------------------------------------------------

tasks["Task_Importance_Raw"] = (
    1
    +
    tasks["Task_Capability_Risk"]
)

# Normalize within occupation
occ_sum = tasks.groupby(
    "O*NET-SOC Code"
)["Task_Importance_Raw"].transform("sum")

tasks["Task_Importance"] = np.where(
    occ_sum > 0,
    tasks["Task_Importance_Raw"] / occ_sum,
    0
)


# ------------------------------------------------------------
# Maximum safe occupation AI adoption
# ------------------------------------------------------------

tasks["Safe_AI_Bound"] = np.minimum(
    tasks["AI_Ceiling"],
    tasks["Preferred_AI_Share"]
)

max_safe = tasks.groupby(
    "O*NET-SOC Code"
).apply(
    lambda g: np.sum(
        g["Task_Importance"]
        * g["Safe_AI_Bound"]
    ),
    include_groups=False
)

max_safe = max_safe.rename(
    "Maximum_Safe_AI_Adoption"
)

tasks = tasks.merge(
    max_safe,
    left_on="O*NET-SOC Code",
    right_index=True,
    how="left"
)

tasks["Maximum_Safe_AI_Adoption"] = (
    tasks["Maximum_Safe_AI_Adoption"]
    .clip(0, MAX_AI_SHARE)
)


# ============================================================
# 11. OPTIMIZATION
# ============================================================

print(
    "\n[11/13] Running adaptive preservation-constrained optimization..."
)

optimized = []

for soc, group in tasks.groupby(
    "O*NET-SOC Code",
    sort=False
):

    g = group.copy()

    n = len(g)

    weights = g[
        "Task_Importance"
    ].values

    suitability_values = g[
        "Task_AI_Suitability"
    ].values

    shadow_values = g[
        "Skill_Shadow_Normalized"
    ].values

    risk_values = g[
        "Capability_Risk_Normalized"
    ].values

    criticality_values = g[
        "Criticality_Normalized"
    ].values

    ceilings = g[
        "AI_Ceiling"
    ].values

    preferred = g[
        "Preferred_AI_Share"
    ].values

    human_floor = g[
        "Human_Preservation_Floor"
    ].values

    # --------------------------------------------------------
    # Safe target
    # --------------------------------------------------------

    max_safe_adoption = float(
        np.sum(
            weights
            * np.minimum(
                ceilings,
                preferred
            )
        )
    )

    # --------------------------------------------------------
    # Adaptive target:
    #
    # If 50% is feasible, pursue 50%.
    # Otherwise pursue the maximum safe level.
    # --------------------------------------------------------

    effective_target = min(
        REQUESTED_TARGET,
        max_safe_adoption
    )

    # --------------------------------------------------------
    # Initial point
    # --------------------------------------------------------

    x0 = np.minimum(
        preferred,
        ceilings
    )

    current_adoption = np.sum(
        weights * x0
    )

    if current_adoption > effective_target:
        scale = (
            effective_target
            / max(
                current_adoption,
                1e-9
            )
        )

        x0 = x0 * scale

    # Ensure floor constraints
    x0 = np.maximum(
        x0,
        0
    )

    x0 = np.minimum(
        x0,
        ceilings
    )

    # --------------------------------------------------------
    # Objective
    # --------------------------------------------------------

    def objective(x):

        # Suitability reward
        automation_value = np.sum(
            weights
            * suitability_values
            * x
        )

        # Direct Skill Shadow cost
        shadow_cost = np.sum(
            weights
            * shadow_values
            * x
        )

        # Risk cost
        risk_cost = np.sum(
            weights
            * risk_values
            * x
        )

        # Criticality cost
        criticality_cost = np.sum(
            weights
            * criticality_values
            * x
        )

        # Deviation from preferred allocation
        preference_deviation = np.sum(
            weights
            * (
                x
                - preferred
            ) ** 2
        )

        # Smooth allocation
        smoothness = 0

        if n > 1:
            smoothness = np.mean(
                np.diff(x) ** 2
            )

        # Target gap penalty
        adoption = np.sum(
            weights * x
        )

        target_gap = max(
            0,
            effective_target
            - adoption
        )

        return (
            SUITABILITY_REWARD
            * preference_deviation
            +
            SHADOW_COST
            * shadow_cost
            +
            RISK_COST
            * risk_cost
            +
            CRITICALITY_COST
            * criticality_cost
            +
            TARGET_GAP_COST
            * target_gap ** 2
            +
            SMOOTHNESS_COST
            * smoothness
            -
            AUTOMATION_VALUE_REWARD
            * automation_value
        )

    # --------------------------------------------------------
    # Constraint:
    # occupation AI adoption <= effective target
    # --------------------------------------------------------

    constraints = [
        {
            "type": "ineq",
            "fun": lambda x,
            w=weights,
            target=effective_target:
                target - np.sum(w * x)
        }
    ]

    try:

        result = minimize(
            objective,
            x0,
            method="SLSQP",
            bounds=[
                (0, float(c))
                for c in ceilings
            ],
            constraints=constraints,
            options={
                "maxiter": 300,
                "ftol": 1e-8,
                "disp": False
            }
        )

        if result.success:
            x_final = result.x
        else:
            x_final = x0

    except Exception:
        x_final = x0

    # --------------------------------------------------------
    # Safety clipping
    # --------------------------------------------------------

    x_final = np.clip(
        x_final,
        0,
        ceilings
    )

    # --------------------------------------------------------
    # Store
    # --------------------------------------------------------

    g["AI_Share"] = x_final

    actual_adoption = np.sum(
        weights * x_final
    )

    g["Actual_Occupation_AI_Adoption"] = (
        actual_adoption
    )

    g["Effective_AI_Target"] = (
        effective_target
    )

    g["Target_Feasibility"] = np.where(
        max_safe_adoption >= REQUESTED_TARGET,
        "Feasible",
        "Infeasible"
    )

    g["Maximum_Safe_AI_Adoption"] = (
        max_safe_adoption
    )

    g["Safe_Target_Gap"] = (
        REQUESTED_TARGET
        - max_safe_adoption
    )

    optimized.append(g)


tasks = pd.concat(
    optimized,
    ignore_index=True
)


# ============================================================
# 12. WORKFORCE DECISIONS + AUDIT
# ============================================================

print(
    "\n[12/13] Creating workforce decisions..."
)

tasks["Human_Share"] = (
    1
    - tasks["AI_Share"]
)

tasks["AI_Share_Percent"] = (
    tasks["AI_Share"] * 100
)

tasks["Human_Share_Percent"] = (
    tasks["Human_Share"] * 100
)

tasks["Task_AI_Suitability_Percent"] = (
    tasks["Task_AI_Suitability"] * 100
)

tasks["Task_Skill_Shadow_Percent"] = (
    tasks["Task_Skill_Shadow"] * 100
)

tasks["Preservation_Pressure_Percent"] = (
    tasks["Preservation_Pressure"] * 100
)

tasks["Human_Preservation_Floor_Percent"] = (
    tasks["Human_Preservation_Floor"] * 100
)

tasks["Maximum_Safe_AI_Adoption_Percent"] = (
    tasks["Maximum_Safe_AI_Adoption"] * 100
)

tasks["Requested_Target_Percent"] = (
    REQUESTED_TARGET * 100
)

tasks["Effective_AI_Target_Percent"] = (
    tasks["Effective_AI_Target"] * 100
)

tasks["Evidence_Confidence_Percent"] = (
    tasks["Task_Evidence_Coverage"] * 100
)

# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

def classify_work(row):

    ai = row["AI_Share"]
    suitability = row[
        "Task_AI_Suitability"
    ]

    if (
        ai >= AI_LED_THRESHOLD
        and suitability >= AI_LED_SUITABILITY_THRESHOLD
    ):
        return "AI-led"

    if ai <= HUMAN_LED_THRESHOLD:
        return "Human-led"

    return "Hybrid"


tasks["Work_Model"] = tasks.apply(
    classify_work,
    axis=1
)

# ------------------------------------------------------------
# Explanation
# ------------------------------------------------------------

def create_explanation(row):

    ai = row["AI_Share_Percent"]
    suitability = row[
        "Task_AI_Suitability_Percent"
    ]

    shadow = row[
        "Task_Skill_Shadow_Percent"
    ]

    pressure = row[
        "Preservation_Pressure_Percent"
    ]

    safe = row[
        "Maximum_Safe_AI_Adoption_Percent"
    ]

    if row["Target_Feasibility"] == "Feasible":

        target_text = (
            f"The requested {REQUESTED_TARGET*100:.0f}% "
            f"occupation target is feasible."
        )

    else:

        target_text = (
            f"The requested {REQUESTED_TARGET*100:.0f}% "
            f"target exceeds the calculated maximum safe "
            f"occupation adoption of {safe:.1f}%."
        )

    return (
        f"AI allocation is {ai:.1f}% because task suitability "
        f"is {suitability:.1f}%, while Skill Shadow is "
        f"{shadow:.1f}% and preservation pressure is "
        f"{pressure:.1f}%. "
        f"{target_text}"
    )


tasks["Decision_Explanation"] = tasks.apply(
    create_explanation,
    axis=1
)


# ============================================================
# 13. FINAL VALIDATION
# ============================================================

print(
    "\n[13/13] Running V7 audit..."
)

print("\n" + "=" * 72)
print("WORKFOLD V7 VALIDATION")
print("=" * 72)

print(
    "\nRecords:",
    len(tasks)
)

print(
    "Unique tasks:",
    tasks[
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    ].drop_duplicates().shape[0]
)

task_unique = (
    tasks[
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    ].duplicated().sum()
    == 0
)

print(
    "Task uniqueness:",
    "PASSED" if task_unique else "FAILED"
)

print(
    "Unique occupations:",
    tasks[
        "O*NET-SOC Code"
    ].nunique()
)


# ------------------------------------------------------------
# Work model distribution
# ------------------------------------------------------------

print("\nWork model distribution:")

print(
    tasks["Work_Model"].value_counts()
)


# ------------------------------------------------------------
# Occupation adoption
# ------------------------------------------------------------

occupation_adoption = (
    tasks.groupby(
        "O*NET-SOC Code"
    )["Actual_Occupation_AI_Adoption"]
    .first()
)

print(
    "\nOccupation AI adoption:"
)

print(
    occupation_adoption.describe()
)

print(
    f"\nMean AI adoption: "
    f"{occupation_adoption.mean()*100:.2f}%"
)

print(
    f"Requested target: "
    f"{REQUESTED_TARGET*100:.2f}%"
)

print(
    f"Mean target gap: "
    f"{(occupation_adoption.mean()-REQUESTED_TARGET)*100:.2f} pp"
)


# ------------------------------------------------------------
# Maximum safe adoption
# ------------------------------------------------------------

max_safe_occ = (
    tasks.groupby(
        "O*NET-SOC Code"
    )["Maximum_Safe_AI_Adoption"]
    .first()
)

print(
    "\nMaximum safe AI adoption:"
)

print(
    max_safe_occ.describe()
)

print(
    f"\nMean maximum safe adoption: "
    f"{max_safe_occ.mean()*100:.2f}%"
)

print(
    f"Occupations able to support "
    f"{REQUESTED_TARGET*100:.0f}% target:",
    (
        max_safe_occ >= REQUESTED_TARGET
    ).sum()
)

print(
    f"Occupations below "
    f"{REQUESTED_TARGET*100:.0f}% target:",
    (
        max_safe_occ < REQUESTED_TARGET
    ).sum()
)


# ------------------------------------------------------------
# Target feasibility
# ------------------------------------------------------------

print(
    "\nTarget feasibility:"
)

print(
    tasks[
        [
            "O*NET-SOC Code",
            "Target_Feasibility"
        ]
    ]
    .drop_duplicates()["Target_Feasibility"]
    .value_counts()
)


# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

print(
    "\nEvidence coverage:"
)

print(
    tasks[
        "Evidence_Confidence_Percent"
    ].describe()
)

raw_evidence = tasks[
    "Raw_Evidence_Available"
].mean() * 100

print(
    f"\nRaw capability evidence coverage: "
    f"{raw_evidence:.2f}%"
)


# ------------------------------------------------------------
# Behavior audit
# ------------------------------------------------------------

print(
    "\n" + "-" * 72
)

print("BEHAVIOR AUDIT")

print("-" * 72)

print(
    "AI share vs suitability:",
    round(
        tasks[
            [
                "AI_Share",
                "Task_AI_Suitability"
            ]
        ].corr().iloc[0, 1],
        4
    )
)

print(
    "AI share vs capability risk:",
    round(
        tasks[
            [
                "AI_Share",
                "Task_Capability_Risk"
            ]
        ].corr().iloc[0, 1],
        4
    )
)

print(
    "AI share vs Skill Shadow:",
    round(
        tasks[
            [
                "AI_Share",
                "Task_Skill_Shadow"
            ]
        ].corr().iloc[0, 1],
        4
    )
)

print(
    "AI share vs preservation pressure:",
    round(
        tasks[
            [
                "AI_Share",
                "Preservation_Pressure"
            ]
        ].corr().iloc[0, 1],
        4
    )
)


# ------------------------------------------------------------
# Spearman monotonicity audit
# ------------------------------------------------------------

print(
    "\nSPEARMAN MONOTONICITY AUDIT"
)

print(
    "AI share vs suitability:",
    round(
        tasks[
            [
                "AI_Share",
                "Task_AI_Suitability"
            ]
        ].corr(
            method="spearman"
        ).iloc[0, 1],
        4
    )
)

print(
    "AI share vs Skill Shadow:",
    round(
        tasks[
            [
                "AI_Share",
                "Task_Skill_Shadow"
            ]
        ].corr(
            method="spearman"
        ).iloc[0, 1],
        4
    )
)

print(
    "AI share vs preservation pressure:",
    round(
        tasks[
            [
                "AI_Share",
                "Preservation_Pressure"
            ]
        ].corr(
            method="spearman"
        ).iloc[0, 1],
        4
    )
)


# ------------------------------------------------------------
# Constraint violations
# ------------------------------------------------------------

ceiling_violation = (
    tasks["AI_Share"]
    >
    tasks["AI_Ceiling"] + 1e-8
).sum()

floor_violation = (
    (
        1 - tasks["AI_Share"]
    )
    <
    tasks["Human_Preservation_Floor"] - 1e-8
).sum()

occupation_target_violation = 0

for soc, group in tasks.groupby(
    "O*NET-SOC Code"
):

    adoption = group[
        "Actual_Occupation_AI_Adoption"
    ].iloc[0]

    target = group[
        "Effective_AI_Target"
    ].iloc[0]

    if adoption > target + 1e-7:
        occupation_target_violation += 1


print(
    "\nAI ceiling violations:",
    ceiling_violation
)

print(
    "Human preservation floor violations:",
    floor_violation
)

print(
    "Occupation target violations:",
    occupation_target_violation
)


# ------------------------------------------------------------
# Range checks
# ------------------------------------------------------------

range_checks = {

    "AI_Share": tasks[
        "AI_Share"
    ].between(0, 1).all(),

    "Human_Share": tasks[
        "Human_Share"
    ].between(0, 1).all(),

    "AI_Suitability": tasks[
        "Task_AI_Suitability"
    ].between(0, 1).all(),

    "Preservation_Pressure": tasks[
        "Preservation_Pressure"
    ].between(0, 1).all(),

    "Human_Preservation_Floor": tasks[
        "Human_Preservation_Floor"
    ].between(0, 1).all(),

    "Evidence": tasks[
        "Evidence_Confidence_Percent"
    ].between(0, 100).all(),
}

print("\nRange checks:")

for name, passed in range_checks.items():

    print(
        f"{name}:",
        "PASSED" if passed else "FAILED"
    )


# ------------------------------------------------------------
# Highest AI allocation
# ------------------------------------------------------------

display_cols = [
    "Occupation Title",
    "Task",
    "AI_Share_Percent",
    "Task_AI_Suitability_Percent",
    "Task_Skill_Shadow_Percent",
    "Preservation_Pressure_Percent",
    "Human_Preservation_Floor_Percent",
    "Maximum_Safe_AI_Adoption_Percent",
    "Work_Model",
]

print(
    "\n" + "-" * 72
)

print("HIGHEST AI ALLOCATION")

print("-" * 72)

print(
    tasks.sort_values(
        "AI_Share_Percent",
        ascending=False
    )[
        display_cols
    ].head(15).to_string(
        index=False
    )
)


# ------------------------------------------------------------
# Lowest AI allocation
# ------------------------------------------------------------

print(
    "\n" + "-" * 72
)

print("LOWEST AI ALLOCATION")

print("-" * 72)

print(
    tasks.sort_values(
        "AI_Share_Percent",
        ascending=True
    )[
        display_cols
    ].head(15).to_string(
        index=False
    )
)


# ------------------------------------------------------------
# Highest Skill Shadow
# ------------------------------------------------------------

print(
    "\n" + "-" * 72
)

print("HIGHEST SKILL SHADOW")

print("-" * 72)

print(
    tasks.sort_values(
        "Task_Skill_Shadow_Percent",
        ascending=False
    )[
        display_cols
    ].head(10).to_string(
        index=False
    )
)


# ------------------------------------------------------------
# Highest preservation pressure
# ------------------------------------------------------------

print(
    "\n" + "-" * 72
)

print("HIGHEST PRESERVATION PRESSURE")

print("-" * 72)

print(
    tasks.sort_values(
        "Preservation_Pressure_Percent",
        ascending=False
    )[
        display_cols
    ].head(10).to_string(
        index=False
    )
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print(
    "\nSaving WORKFOLD V7..."
)

# ------------------------------------------------------------
# Final column ordering
# ------------------------------------------------------------

final_columns = [
    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",
    "Occupation Description",
    "Task",
    "DWA Element Name",

    "Primary_Capabilities",
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

    "Preferred_AI_Share",
    "Safe_AI_Bound",

    "Maximum_Safe_AI_Adoption",
    "Maximum_Safe_AI_Adoption_Percent",

    "Requested_Target_Percent",
    "Effective_AI_Target",
    "Effective_AI_Target_Percent",

    "AI_Share",
    "AI_Share_Percent",

    "Human_Share",
    "Human_Share_Percent",

    "Target_Feasibility",
    "Safe_Target_Gap",

    "Work_Model",
    "Decision_Explanation",

    "Raw_Evidence_Available",
]


final_columns = [
    c for c in final_columns
    if c in tasks.columns
]

final_df = tasks[
    final_columns
].copy()

# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

final_df.to_parquet(
    OUT_PARQUET,
    index=False
)

final_df.to_csv(
    OUT_CSV,
    index=False
)

print(
    "\n" + "=" * 72
)

print(
    "WORKFOLD V7 COMPLETE"
)

print("=" * 72)

print(
    "Parquet:",
    OUT_PARQUET
)

print(
    "CSV:    ",
    OUT_CSV
)

print(
    "Final shape:",
    final_df.shape
)

print("=" * 72)