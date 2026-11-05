# ============================================================
# FORGE — WORKFOLD V4
# Future-Oriented Workforce Reconfiguration & Growth Engine
#
# Purpose:
#   Task-level Human–AI work allocation using:
#   1. O*NET task/work-activity evidence
#   2. FORGE Skill Shadow
#   3. Capability Risk
#   4. SentenceTransformer semantic automation suitability
#   5. Evidence coverage
#   6. Constrained scenario optimization
#
# Important:
#   This is a scenario/decision-support model.
#   AI suitability is NOT treated as an empirical probability.
#   Skill Shadow is a FORGE-defined metric.
# ============================================================

from pathlib import Path
import warnings
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


# ============================================================
# CONFIGURATION
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

OUTPUT_PARQUET = OUTPUT_DIR / "forge_workfold_v4.parquet"
OUTPUT_CSV = OUTPUT_DIR / "forge_workfold_v4.csv"


# ------------------------------------------------------------
# Scenario parameters
# ------------------------------------------------------------

AI_ADOPTION_TARGET = 0.50

# Absolute global ceiling.
GLOBAL_MAX_AI_SHARE = 0.80

# AI cannot exceed the task-specific ceiling calculated below.
GLOBAL_MIN_AI_SHARE = 0.00


# ------------------------------------------------------------
# Preservation / decision weights
#
# These are model parameters, NOT empirical claims.
# ------------------------------------------------------------

AUTOMATION_VALUE_WEIGHT = 0.50
PRESERVATION_WEIGHT = 0.30
LEARNING_WEIGHT = 0.20

# Keeps final allocation reasonably close to evidence-driven
# preferred allocation.
PREFERENCE_WEIGHT = 1.00

# Controls how strongly the optimizer tries to follow the
# requested scenario adoption target.
TARGET_TRACKING_WEIGHT = 4.00


# ------------------------------------------------------------
# Automation semantic anchors
# ------------------------------------------------------------

AUTOMATION_ANCHORS = [
    "routine repetitive data processing",
    "structured retrieval and document processing",
    "classification extraction transcription and standard transformation",
    "rule based administrative processing",
    "predictable monitoring reporting and record keeping",
]


# ------------------------------------------------------------
# Human-centric anchors
# ------------------------------------------------------------

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

def safe_numeric(series, default=np.nan):
    """
    Convert values to numeric safely.
    """
    result = pd.to_numeric(series, errors="coerce")

    if default is not np.nan:
        result = result.fillna(default)

    return result


def minmax(series):
    """
    Robust min-max normalization.

    If all valid values are equal, returns 0.5 for valid values.
    """
    s = pd.to_numeric(series, errors="coerce")

    valid = s.dropna()

    if len(valid) == 0:
        return pd.Series(0.5, index=s.index)

    mn = valid.min()
    mx = valid.max()

    if np.isclose(mx, mn):
        result = pd.Series(0.5, index=s.index)
        result[s.isna()] = np.nan
        return result

    return (s - mn) / (mx - mn)


def weighted_mean(values, weights):
    """
    Weighted mean ignoring invalid values.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)

    mask = (
        np.isfinite(values)
        & np.isfinite(weights)
        & (weights > 0)
    )

    if not mask.any():
        return np.nan

    values = values[mask]
    weights = weights[mask]

    return np.average(values, weights=weights)


def normalize_vector(x):
    """
    L2-normalize a vector/matrix.
    """
    x = np.asarray(x, dtype=np.float32)

    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0

    return x / norms


def build_capability_key(df):
    """
    Capability identity must include type + ID.

    This prevents collisions where the same numeric ID appears
    under different capability types.
    """
    return (
        df["Capability Type"].fillna("Unknown").astype(str)
        + "::"
        + df["Capability ID"].fillna("Unknown").astype(str)
    )


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("FORGE — WORKFOLD V4")
print("=" * 70)

print("\n[1/10] Loading WORKTRACE...")

worktrace = pd.read_parquet(WORKTRACE_PATH)

print(f"WORKTRACE shape: {worktrace.shape}")


print("\n[2/10] Loading SKILL SHADOW...")

shadow = pd.read_parquet(SKILL_SHADOW_PATH)

print(f"SKILL SHADOW shape: {shadow.shape}")


# ============================================================
# VALIDATE REQUIRED COLUMNS
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
    "Capability Name",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]


missing_worktrace = [
    c for c in required_worktrace
    if c not in worktrace.columns
]

missing_shadow = [
    c for c in required_shadow
    if c not in shadow.columns
]


if missing_worktrace:
    raise ValueError(
        f"WORKTRACE missing required columns: {missing_worktrace}"
    )

if missing_shadow:
    raise ValueError(
        f"SKILL SHADOW missing required columns: {missing_shadow}"
    )


# ============================================================
# BASIC CLEANING
# ============================================================

print("\n[3/10] Preparing task-capability evidence...")

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
).fillna(0.0)


# Remove impossible negative evidence weights.
worktrace["Task Capability Weight"] = (
    worktrace["Task Capability Weight"]
    .clip(lower=0)
)


# ============================================================
# CAPABILITY KEY
# ============================================================

worktrace["Capability Key"] = build_capability_key(worktrace)
shadow["Capability Key"] = build_capability_key(shadow)


# ============================================================
# TASK KEY
# ============================================================

worktrace["Task Key"] = (
    worktrace["O*NET-SOC Code"].astype(str)
    + "::"
    + worktrace["Task ID"].astype(str)
)


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

before_duplicates = len(worktrace)

worktrace = worktrace.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "Capability Key",
    ]
)

removed_duplicates = before_duplicates - len(worktrace)

print(f"Exact task-capability duplicates removed: {removed_duplicates}")


# ============================================================
# CAPABILITY WEIGHT WITHIN TASK
# ============================================================

task_weight_sum = (
    worktrace
    .groupby("Task Key")["Task Capability Weight"]
    .transform("sum")
)

task_weight_sum = task_weight_sum.replace(0, np.nan)

worktrace["Capability_Weight_Within_Task"] = (
    worktrace["Task Capability Weight"]
    / task_weight_sum
)

worktrace["Capability_Weight_Within_Task"] = (
    worktrace["Capability_Weight_Within_Task"]
    .fillna(0)
)


# ============================================================
# TASK IMPORTANCE
#
# IMPORTANT FIX FROM V3:
#
# Do NOT sum normalized capability weights.
# That would make almost every task equal to 1.
#
# Instead use RAW task-capability evidence and normalize
# across tasks within the occupation.
# ============================================================

task_raw_importance = (
    worktrace
    .groupby(
        [
            "O*NET-SOC Code",
            "Task ID",
            "Task Key",
        ],
        as_index=False
    )["Task Capability Weight"]
    .sum()
    .rename(
        columns={
            "Task Capability Weight": "Task_Raw_Importance"
        }
    )
)


occupation_importance_sum = (
    task_raw_importance
    .groupby("O*NET-SOC Code")["Task_Raw_Importance"]
    .transform("sum")
)

occupation_importance_sum = occupation_importance_sum.replace(
    0,
    np.nan
)

task_raw_importance["Task_Importance"] = (
    task_raw_importance["Task_Raw_Importance"]
    / occupation_importance_sum
)

task_raw_importance["Task_Importance"] = (
    task_raw_importance["Task_Importance"]
    .fillna(0)
)


worktrace = worktrace.merge(
    task_raw_importance[
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
# SHADOW EVIDENCE MERGE
# ============================================================

print("\n[4/10] Merging Skill Shadow evidence...")

shadow_merge_columns = [
    "Capability Key",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]

shadow_small = (
    shadow[shadow_merge_columns]
    .drop_duplicates(subset=["Capability Key"])
    .copy()
)


worktrace = worktrace.merge(
    shadow_small,
    on="Capability Key",
    how="left",
    indicator="_shadow_match",
)


worktrace["Shadow_Evidence_Available"] = (
    worktrace["_shadow_match"] == "both"
)


# ============================================================
# EVIDENCE COVERAGE
# ============================================================

# Evidence coverage is weighted by capability importance,
# not by raw row count.

worktrace["Matched_Capability_Weight"] = np.where(
    worktrace["Shadow_Evidence_Available"],
    worktrace["Capability_Weight_Within_Task"],
    0.0
)


task_evidence_coverage = (
    worktrace
    .groupby("Task Key")["Matched_Capability_Weight"]
    .sum()
    .rename("Shadow_Evidence_Coverage")
)


worktrace = worktrace.merge(
    task_evidence_coverage,
    on="Task Key",
    how="left"
)


worktrace["Shadow_Evidence_Coverage"] = (
    worktrace["Shadow_Evidence_Coverage"]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# OCCUPATION MEDIANS FOR MISSING EVIDENCE
# ============================================================

print("\nCalculating uncertainty-aware capability evidence...")


occupation_shadow_median = (
    shadow
    .groupby("O*NET-SOC Code")["Skill_Shadow"]
    .median()
)

occupation_risk_median = (
    shadow
    .groupby("O*NET-SOC Code")["Capability_Risk"]
    .median()
)

occupation_criticality_median = (
    shadow
    .groupby("O*NET-SOC Code")["Capability_Criticality"]
    .median()
)


# Map occupation medians.
worktrace["Occupation_Shadow_Median"] = (
    worktrace["O*NET-SOC Code"]
    .map(occupation_shadow_median)
)

worktrace["Occupation_Risk_Median"] = (
    worktrace["O*NET-SOC Code"]
    .map(occupation_risk_median)
)

worktrace["Occupation_Criticality_Median"] = (
    worktrace["O*NET-SOC Code"]
    .map(occupation_criticality_median)
)


# Global fallback only if an occupation has no shadow evidence.
global_shadow_median = shadow["Skill_Shadow"].median()
global_risk_median = shadow["Capability_Risk"].median()
global_criticality_median = shadow["Capability_Criticality"].median()


worktrace["Occupation_Shadow_Median"] = (
    worktrace["Occupation_Shadow_Median"]
    .fillna(global_shadow_median)
)

worktrace["Occupation_Risk_Median"] = (
    worktrace["Occupation_Risk_Median"]
    .fillna(global_risk_median)
)

worktrace["Occupation_Criticality_Median"] = (
    worktrace["Occupation_Criticality_Median"]
    .fillna(global_criticality_median)
)


# ============================================================
# EFFECTIVE CAPABILITY EVIDENCE
#
# Missing evidence is NOT interpreted as zero risk.
#
# Instead:
#
# effective = coverage * observed
#          + (1 - coverage) * occupation median
# ============================================================

worktrace["Effective_Skill_Shadow"] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace["Skill_Shadow"].fillna(
        worktrace["Occupation_Shadow_Median"]
    )
    + (
        1
        - worktrace["Shadow_Evidence_Coverage"]
    )
    * worktrace["Occupation_Shadow_Median"]
)


worktrace["Effective_Capability_Risk"] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace["Capability_Risk"].fillna(
        worktrace["Occupation_Risk_Median"]
    )
    + (
        1
        - worktrace["Shadow_Evidence_Coverage"]
    )
    * worktrace["Occupation_Risk_Median"]
)


worktrace["Effective_Capability_Criticality"] = (
    worktrace["Shadow_Evidence_Coverage"]
    * worktrace["Capability_Criticality"].fillna(
        worktrace["Occupation_Criticality_Median"]
    )
    + (
        1
        - worktrace["Shadow_Evidence_Coverage"]
    )
    * worktrace["Occupation_Criticality_Median"]
)


# ============================================================
# TASK-LEVEL AGGREGATION
# ============================================================

print("\n[5/10] Aggregating capability evidence to task level...")


def aggregate_task(group):

    weights = group["Capability_Weight_Within_Task"].to_numpy(
        dtype=float
    )

    risk = group["Effective_Capability_Risk"].to_numpy(
        dtype=float
    )

    shadow_values = group["Effective_Skill_Shadow"].to_numpy(
        dtype=float
    )

    criticality = (
        group["Effective_Capability_Criticality"]
        .to_numpy(dtype=float)
    )

    return pd.Series(
        {
            "Task_Capability_Risk": weighted_mean(
                risk,
                weights
            ),

            "Task_Skill_Shadow": weighted_mean(
                shadow_values,
                weights
            ),

            "Task_Capability_Criticality": weighted_mean(
                criticality,
                weights
            ),

            "Shadow_Evidence_Coverage": (
                group["Matched_Capability_Weight"].sum()
            ),
        }
    )


task_capability_summary = (
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

task_metadata_columns = [
    "Task Key",
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",
    "Task_Raw_Importance",
    "Task_Importance",
]


task_metadata = (
    worktrace[
        task_metadata_columns
    ]
    .drop_duplicates(subset=["Task Key"])
)


tasks = task_metadata.merge(
    task_capability_summary,
    on="Task Key",
    how="left",
)


# ============================================================
# PRIMARY CAPABILITIES
# ============================================================

print("\nExtracting primary capabilities...")


def primary_capabilities(group):

    temp = (
        group[
            [
                "Capability Name",
                "Capability_Weight_Within_Task",
            ]
        ]
        .dropna(subset=["Capability Name"])
        .drop_duplicates()
        .sort_values(
            "Capability_Weight_Within_Task",
            ascending=False
        )
        .head(5)
    )

    return ", ".join(
        temp["Capability Name"]
        .astype(str)
        .tolist()
    )


primary_caps = (
    worktrace
    .groupby("Task Key")
    .apply(
        primary_capabilities,
        include_groups=False
    )
    .rename("Primary_Capabilities")
    .reset_index()
)


tasks = tasks.merge(
    primary_caps,
    on="Task Key",
    how="left",
)


# ============================================================
# TASK TEXT FOR SEMANTIC MODEL
# ============================================================

tasks["Task_Text"] = (
    tasks["Task"].fillna("").astype(str)
    + ". "
    + tasks["DWA Element Name"].fillna("").astype(str)
)


tasks["Task_Text"] = (
    tasks["Task_Text"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)


# ============================================================
# SENTENCE TRANSFORMER
# ============================================================

print("\n[6/10] Loading SentenceTransformer...")

model = SentenceTransformer(MODEL_NAME)


print("Encoding automation anchors...")

automation_embeddings = model.encode(
    AUTOMATION_ANCHORS,
    batch_size=32,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False,
)


print("Encoding human anchors...")

human_embeddings = model.encode(
    HUMAN_ANCHORS,
    batch_size=32,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False,
)


print(f"Encoding {len(tasks):,} task descriptions...")


task_embeddings = model.encode(
    tasks["Task_Text"].tolist(),
    batch_size=256,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True,
)


# ============================================================
# SEMANTIC SIMILARITY
# ============================================================

print("\nComputing semantic automation suitability...")


automation_similarity = (
    task_embeddings
    @ automation_embeddings.T
)

human_similarity = (
    task_embeddings
    @ human_embeddings.T
)


tasks["Automation_Max_Similarity"] = (
    automation_similarity.max(axis=1)
)

tasks["Human_Max_Similarity"] = (
    human_similarity.max(axis=1)
)


# Difference between automation-oriented and human-oriented
# semantic evidence.

tasks["Automation_Human_Balance"] = (
    tasks["Automation_Max_Similarity"]
    - tasks["Human_Max_Similarity"]
)


# Convert approximately [-1, +1] into [0, 1].
#
# This is a semantic suitability index, NOT a probability.
tasks["Task_AI_Suitability"] = (
    (
        tasks["Automation_Human_Balance"]
        + 1
    )
    / 2
).clip(0, 1)


tasks["Task_Human_Suitability"] = (
    1
    - tasks["Task_AI_Suitability"]
)


# ============================================================
# PRESERVATION PRESSURE
# ============================================================

print("\n[7/10] Computing capability preservation pressure...")


# Skill Shadow directly represents lost human exposure.
#
# Capability Risk captures the combined importance/risk signal.
#
# Criticality provides another preservation signal.
#
# These are normalized only for combining them into a task-level
# scenario pressure score.

tasks["Risk_Normalized"] = minmax(
    tasks["Task_Capability_Risk"]
)

tasks["Shadow_Normalized"] = minmax(
    tasks["Task_Skill_Shadow"]
)

tasks["Criticality_Normalized"] = minmax(
    tasks["Task_Capability_Criticality"]
)


tasks["Risk_Normalized"] = (
    tasks["Risk_Normalized"].fillna(0.5)
)

tasks["Shadow_Normalized"] = (
    tasks["Shadow_Normalized"].fillna(0.5)
)

tasks["Criticality_Normalized"] = (
    tasks["Criticality_Normalized"].fillna(0.5)
)


tasks["Preservation_Pressure"] = (
    0.45 * tasks["Risk_Normalized"]
    + 0.35 * tasks["Shadow_Normalized"]
    + 0.20 * tasks["Criticality_Normalized"]
).clip(0, 1)


# ============================================================
# EVIDENCE CONFIDENCE
# ============================================================

tasks["Evidence_Confidence"] = (
    tasks["Shadow_Evidence_Coverage"]
    .clip(0, 1)
)


# ============================================================
# AI PREFERRED SHARE
# ============================================================

print("\nBuilding evidence-driven AI preference...")


tasks["AI_Preferred_Share"] = (
    GLOBAL_MAX_AI_SHARE
    * tasks["Task_AI_Suitability"]
    * (
        1
        - tasks["Preservation_Pressure"]
    )
)


tasks["AI_Preferred_Share"] = (
    tasks["AI_Preferred_Share"]
    .clip(
        GLOBAL_MIN_AI_SHARE,
        GLOBAL_MAX_AI_SHARE
    )
)


# ============================================================
# TASK AI CEILING
#
# The ceiling is NOT a prediction.
#
# It answers:
# "Given this scenario model, how much AI delegation is
#  considered structurally allowable for this task?"
#
# Low suitability / high preservation pressure =>
# lower AI ceiling.
# ============================================================

tasks["AI_Ceiling"] = (
    GLOBAL_MIN_AI_SHARE
    + (
        GLOBAL_MAX_AI_SHARE
        - GLOBAL_MIN_AI_SHARE
    )
    * tasks["Task_AI_Suitability"]
    * (
        1
        - tasks["Preservation_Pressure"]
    )
)


tasks["AI_Ceiling"] = (
    tasks["AI_Ceiling"]
    .clip(
        GLOBAL_MIN_AI_SHARE,
        GLOBAL_MAX_AI_SHARE
    )
)


# ============================================================
# MAX FEASIBLE OCCUPATION ADOPTION
# ============================================================

occupation_max_feasible = (
    tasks
    .groupby("O*NET-SOC Code")
    .apply(
        lambda g: np.sum(
            g["Task_Importance"]
            * g["AI_Ceiling"]
        ),
        include_groups=False
    )
    .rename("Max_Feasible_AI_Adoption")
    .reset_index()
)


tasks = tasks.merge(
    occupation_max_feasible,
    on="O*NET-SOC Code",
    how="left",
)


tasks["Target_Feasibility"] = np.where(
    tasks["Max_Feasible_AI_Adoption"]
    >= AI_ADOPTION_TARGET - 1e-9,
    "Feasible",
    "Infeasible"
)


# ============================================================
# OPTIMIZATION
# ============================================================

print("\n[8/10] Running workforce allocation optimization...")


def optimize_occupation(group):

    group = group.copy()

    n = len(group)

    if n == 0:
        return group

    weights = (
        group["Task_Importance"]
        .to_numpy(dtype=float)
    )

    suitability = (
        group["Task_AI_Suitability"]
        .to_numpy(dtype=float)
    )

    preservation = (
        group["Preservation_Pressure"]
        .to_numpy(dtype=float)
    )

    shadow_values = (
        group["Task_Skill_Shadow"]
        .to_numpy(dtype=float)
    )

    preferred = (
        group["AI_Preferred_Share"]
        .to_numpy(dtype=float)
    )

    ceilings = (
        group["AI_Ceiling"]
        .to_numpy(dtype=float)
    )


    # --------------------------------------------------------
    # Numerical cleanup
    # --------------------------------------------------------

    weights = np.nan_to_num(
        weights,
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )

    suitability = np.nan_to_num(
        suitability,
        nan=0.5,
    )

    preservation = np.nan_to_num(
        preservation,
        nan=0.5,
    )

    shadow_values = np.nan_to_num(
        shadow_values,
        nan=0.5,
    )

    preferred = np.nan_to_num(
        preferred,
        nan=0.0,
    )

    ceilings = np.nan_to_num(
        ceilings,
        nan=0.0,
    )


    # Ensure weights sum to 1.
    weight_sum = weights.sum()

    if weight_sum <= 0:

        weights = np.ones(n) / n

    else:

        weights = weights / weight_sum


    # --------------------------------------------------------
    # Initial solution
    # --------------------------------------------------------

    x0 = np.minimum(
        preferred,
        ceilings
    )

    x0 = np.maximum(
        x0,
        0
    )


    # --------------------------------------------------------
    # Objective
    #
    # We minimize:
    #
    #   distance from preferred allocation
    #
    #   + target deviation
    #
    #   - automation value
    #
    #   + preservation penalty
    #
    # This avoids blindly forcing the target.
    # --------------------------------------------------------

    def objective(x):

        weighted_ai = np.sum(
            weights * x
        )

        preference_loss = np.sum(
            weights
            * (
                x - preferred
            ) ** 2
        )


        automation_value = np.sum(
            weights
            * suitability
            * x
        )


        preservation_loss = np.sum(
            weights
            * preservation
            * x
        )


        learning_loss = np.sum(
            weights
            * shadow_values
            * x
        )


        target_loss = (
            weighted_ai
            - AI_ADOPTION_TARGET
        ) ** 2


        total = (
            PREFERENCE_WEIGHT
            * preference_loss

            + TARGET_TRACKING_WEIGHT
            * target_loss

            - AUTOMATION_VALUE_WEIGHT
            * automation_value

            + PRESERVATION_WEIGHT
            * preservation_loss

            + LEARNING_WEIGHT
            * learning_loss
        )

        return total


    # --------------------------------------------------------
    # Bounds
    # --------------------------------------------------------

    bounds = [
        (
            GLOBAL_MIN_AI_SHARE,
            float(ceiling)
        )
        for ceiling in ceilings
    ]


    # --------------------------------------------------------
    # Optimize
    # --------------------------------------------------------

    try:

        result = minimize(
            objective,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            options={
                "maxiter": 200,
                "ftol": 1e-8,
                "disp": False,
            },
        )


        if result.success:

            allocation = result.x

        else:

            allocation = x0


    except Exception:

        allocation = x0


    allocation = np.clip(
        allocation,
        GLOBAL_MIN_AI_SHARE,
        ceilings
    )


    # --------------------------------------------------------
    # Final metrics
    # --------------------------------------------------------

    actual_adoption = np.sum(
        weights * allocation
    )


    max_feasible = np.sum(
        weights * ceilings
    )


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


    group["Target_Gap_Percentage_Points"] = (
        (
            actual_adoption
            - AI_ADOPTION_TARGET
        )
        * 100
    )


    group["Max_Feasible_AI_Adoption"] = (
        max_feasible
    )


    group["Optimization_Success"] = (
        result.success
        if "result" in locals()
        else False
    )


    return group


optimized_groups = []


for occupation_code, group in tasks.groupby(
    "O*NET-SOC Code",
    sort=False
):

    optimized_groups.append(
        optimize_occupation(group)
    )


tasks = pd.concat(
    optimized_groups,
    ignore_index=True
)


# ============================================================
# WORK MODEL
# ============================================================

print("\n[9/10] Creating final workforce decisions...")


def classify_work_model(ai_share):

    if ai_share >= 0.65:
        return "AI-led"

    if ai_share <= 0.35:
        return "Human-led"

    return "Hybrid"


tasks["Work_Model"] = (
    tasks["AI_Share"]
    .apply(classify_work_model)
)


# ============================================================
# DECISION EXPLANATION
# ============================================================

def generate_explanation(row):

    ai = row["AI_Share"]
    suitability = row["Task_AI_Suitability"]
    pressure = row["Preservation_Pressure"]
    coverage = row["Evidence_Confidence"]
    model = row["Work_Model"]

    ai_pct = ai * 100
    suitability_pct = suitability * 100
    pressure_pct = pressure * 100
    coverage_pct = coverage * 100


    if model == "AI-led":

        if pressure >= 0.60:

            return (
                f"AI-led allocation ({ai_pct:.1f}%) is allowed by "
                f"the scenario model despite elevated preservation "
                f"pressure ({pressure_pct:.1f}%). This task should "
                f"retain explicit human oversight."
            )

        return (
            f"AI-led allocation ({ai_pct:.1f}%) is supported by "
            f"higher automation suitability ({suitability_pct:.1f}%) "
            f"and manageable capability-preservation pressure "
            f"({pressure_pct:.1f}%)."
        )


    if model == "Human-led":

        return (
            f"Human-led allocation ({100-ai_pct:.1f}% human) is "
            f"maintained because automation suitability is "
            f"{suitability_pct:.1f}% and preservation pressure is "
            f"{pressure_pct:.1f}%. AI remains limited to the "
            f"evidence-supported portion of the task."
        )


    return (
        f"Hybrid allocation ({ai_pct:.1f}% AI / "
        f"{100-ai_pct:.1f}% human) balances automation suitability "
        f"({suitability_pct:.1f}%) with capability-preservation "
        f"pressure ({pressure_pct:.1f}%). Shadow evidence coverage "
        f"is {coverage_pct:.1f}%."
    )


tasks["Decision_Explanation"] = (
    tasks.apply(
        generate_explanation,
        axis=1
    )
)


# ============================================================
# ADDITIONAL DECISION METRICS
# ============================================================

tasks["AI_Share_Percent"] = (
    tasks["AI_Share"] * 100
)

tasks["Human_Share_Percent"] = (
    tasks["Human_Share"] * 100
)


tasks["AI_Ceiling_Percent"] = (
    tasks["AI_Ceiling"] * 100
)


tasks["AI_Preferred_Share_Percent"] = (
    tasks["AI_Preferred_Share"] * 100
)


tasks["Preservation_Pressure_Percent"] = (
    tasks["Preservation_Pressure"] * 100
)


tasks["Task_AI_Suitability_Percent"] = (
    tasks["Task_AI_Suitability"] * 100
)


tasks["Evidence_Confidence_Percent"] = (
    tasks["Evidence_Confidence"] * 100
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
    ],
).reset_index(drop=True)


# ============================================================
# FINAL COLUMN SELECTION
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

    "Shadow_Evidence_Coverage",
    "Evidence_Confidence",
    "Evidence_Confidence_Percent",

    "Risk_Normalized",
    "Shadow_Normalized",
    "Criticality_Normalized",

    "Preservation_Pressure",
    "Preservation_Pressure_Percent",

    "AI_Preferred_Share",
    "AI_Preferred_Share_Percent",

    "AI_Ceiling",
    "AI_Ceiling_Percent",

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


# Only keep columns that actually exist.
final_columns = [
    c for c in final_columns
    if c in tasks.columns
]


final_df = tasks[final_columns].copy()


# ============================================================
# VALIDATION
# ============================================================

print("\n[10/10] Running final validation...")

print("\n" + "=" * 70)
print("WORKFOLD V4 VALIDATION")
print("=" * 70)


# ------------------------------------------------------------
# Task uniqueness
# ------------------------------------------------------------

unique_task_count = (
    final_df["Task Key"]
    .nunique()
)

record_count = len(final_df)

print(
    f"\nRecords: {record_count:,}"
)

print(
    f"Unique tasks: {unique_task_count:,}"
)

print(
    "Task uniqueness:",
    "PASSED"
    if record_count == unique_task_count
    else "FAILED"
)


# ------------------------------------------------------------
# Occupations
# ------------------------------------------------------------

print(
    f"Unique occupations: "
    f"{final_df['O*NET-SOC Code'].nunique():,}"
)


# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

print("\nWork model distribution:")

print(
    final_df["Work_Model"]
    .value_counts()
)


# ------------------------------------------------------------
# Adoption statistics
# ------------------------------------------------------------

occupation_adoption = (
    final_df
    .groupby("O*NET-SOC Code")
    .first()
)

print("\nAI adoption statistics across occupations:")

print(
    occupation_adoption[
        "Actual_AI_Adoption"
    ].describe()
)


overall_weighted_adoption = (
    final_df["Task_Importance"]
    * final_df["AI_Share"]
).groupby(
    final_df["O*NET-SOC Code"]
).sum().mean()


print(
    f"\nMean occupation AI adoption: "
    f"{overall_weighted_adoption * 100:.2f}%"
)


print(
    f"Requested scenario target: "
    f"{AI_ADOPTION_TARGET * 100:.2f}%"
)


print(
    f"Mean target gap: "
    f"{(
        occupation_adoption['Actual_AI_Adoption']
        - AI_ADOPTION_TARGET
    ).mean() * 100:.2f} pp"
)


# ------------------------------------------------------------
# Feasibility
# ------------------------------------------------------------

print("\nTarget feasibility:")

print(
    occupation_adoption[
        "Target_Feasibility"
    ].value_counts()
)


# ------------------------------------------------------------
# Evidence
# ------------------------------------------------------------

print("\nEvidence coverage:")

print(
    final_df[
        "Evidence_Confidence"
    ].describe()
)


# ------------------------------------------------------------
# Correlations
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
    f"AI share vs AI suitability: "
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
# Ceiling violations
# ------------------------------------------------------------

ceiling_violations = (
    final_df["AI_Share"]
    > final_df["AI_Ceiling"] + 1e-7
).sum()


print(
    f"\nAI ceiling violations: "
    f"{ceiling_violations}"
)


# ------------------------------------------------------------
# Range checks
# ------------------------------------------------------------

range_checks = {
    "AI_Share": (
        final_df["AI_Share"].between(0, 1).all()
    ),

    "Human_Share": (
        final_df["Human_Share"].between(0, 1).all()
    ),

    "Task_AI_Suitability": (
        final_df["Task_AI_Suitability"].between(0, 1).all()
    ),

    "Preservation_Pressure": (
        final_df["Preservation_Pressure"].between(0, 1).all()
    ),

    "Evidence_Confidence": (
        final_df["Evidence_Confidence"].between(0, 1).all()
    ),
}


print("\nRange checks:")

for name, passed in range_checks.items():

    print(
        f"{name}:",
        "PASSED"
        if passed
        else "FAILED"
    )


# ============================================================
# SAMPLE EXTREMES
# ============================================================

print("\n" + "=" * 70)
print("HIGHEST AI ALLOCATION TASKS")
print("=" * 70)


highest = (
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
    .head(10)
)


print(
    highest.to_string(
        index=False
    )
)


print("\n" + "=" * 70)
print("LOWEST AI ALLOCATION TASKS")
print("=" * 70)


lowest = (
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
    .head(10)
)


print(
    lowest.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving WORKFOLD V4...")


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


print("\n" + "=" * 70)
print("WORKFOLD V4 COMPLETE")
print("=" * 70)

print(
    f"Parquet: {OUTPUT_PARQUET}"
)

print(
    f"CSV:     {OUTPUT_CSV}"
)

print(
    f"Final shape: {final_df.shape}"
)

print("=" * 70)