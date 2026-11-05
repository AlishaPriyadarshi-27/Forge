import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# FORGE — SKILL SHADOW ENGINE
# ============================================================
#
# Purpose:
# Detect capabilities whose human practice/exposure decreases
# when AI adoption changes the human share of work.
#
# Core concept:
#
#   Current Human Exposure
#              ↓
#       AI Adoption Scenario
#              ↓
#   Post-AI Human Exposure
#              ↓
#        Skill Shadow
#              ↓
#      Capability Risk
#
# Skill Shadow is a FORGE-defined metric.
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

OUTPUT_FILE = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)

OUTPUT_CSV = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Default scenario.
# Frontend can later send any value from 0 to 100.
DEFAULT_AI_ADOPTION = 50.0

# Semantic model used for task automation suitability.
MODEL_NAME = "all-MiniLM-L6-v2"

# Number of task records used to derive semantic AI suitability.
# We use unique tasks rather than embedding every duplicated
# task-capability row.
MAX_UNIQUE_TASKS = 20000

# AI-work semantic anchors.
#
# These are NOT task labels and are NOT used as hard-coded
# automation percentages.
#
# They provide semantic reference points for the embedding model.
AUTOMATION_ANCHORS = [
    "routine repetitive data processing that can be performed automatically by software",
    "structured information retrieval and document processing that can be automated by AI",
    "classification extraction transcription and standard transformation of information",
    "rule based administrative processing and record keeping",
    "predictable monitoring and routine reporting that can be automated",
]

HUMAN_ANCHORS = [
    "complex human judgment under uncertainty requiring contextual reasoning",
    "leadership negotiation persuasion and interpersonal interaction",
    "physical work requiring dexterity presence and interaction with the environment",
    "creative problem solving requiring original human judgment and adaptation",
    "ethical decisions accountability and responsibility in ambiguous situations",
]


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 75)
print("FORGE — SKILL SHADOW ENGINE")
print("=" * 75)


# ============================================================
# LOAD WORKTRACE
# ============================================================

print("\n[1/8] Loading WORKTRACE...")

df = pd.read_parquet(INPUT_FILE)

print(f"WORKTRACE records: {len(df):,}")


required_columns = [
    "O*NET-SOC Code",
    "SOC_7",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
    "market_job_count",
    "market_avg_similarity",
    "employment_change_percent",
    "occupational_openings_2025_35_annual_avg_thousands",
]


missing = [
    col
    for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(
        f"Missing WORKTRACE columns: {missing}"
    )


# ============================================================
# CLEAN CORE FIELDS
# ============================================================

print("\n[2/8] Cleaning task and capability data...")

df = df.copy()

df["Task"] = (
    df["Task"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["DWA Element Name"] = (
    df["DWA Element Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Capability Name"] = (
    df["Capability Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Capability Type"] = (
    df["Capability Type"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Task Capability Weight"] = pd.to_numeric(
    df["Task Capability Weight"],
    errors="coerce"
)

df["market_job_count"] = pd.to_numeric(
    df["market_job_count"],
    errors="coerce"
).fillna(0)

df["market_avg_similarity"] = pd.to_numeric(
    df["market_avg_similarity"],
    errors="coerce"
).fillna(0)

df["employment_change_percent"] = pd.to_numeric(
    df["employment_change_percent"],
    errors="coerce"
)

df[
    "occupational_openings_2025_35_annual_avg_thousands"
] = pd.to_numeric(
    df[
        "occupational_openings_2025_35_annual_avg_thousands"
    ],
    errors="coerce"
)


# ============================================================
# TASK TABLE
# ============================================================

print("\n[3/8] Building unique task layer...")


task_columns = [
    "O*NET-SOC Code",
    "SOC_7",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",
]


tasks = (
    df[task_columns]
    .drop_duplicates(
        subset=[
            "O*NET-SOC Code",
            "Task ID",
        ]
    )
    .copy()
)


tasks = tasks[
    tasks["Task"].str.len() > 0
].copy()


print(
    f"Unique occupation-task records: "
    f"{len(tasks):,}"
)


# ============================================================
# TASK AUTOMATION SUITABILITY
# ============================================================

print("\n[4/8] Calculating semantic task automation suitability...")

print(
    f"Loading SentenceTransformer: {MODEL_NAME}"
)

model = SentenceTransformer(MODEL_NAME)


# ------------------------------------------------------------
# Task text
# ------------------------------------------------------------

tasks["task_text"] = (
    tasks["Task"]
    + ". "
    + tasks["DWA Element Name"]
)


# ------------------------------------------------------------
# Limit unique task texts for computation.
#
# This does NOT randomly assign scores to capabilities.
# The same task text receives the same semantic score.
# ------------------------------------------------------------

unique_task_texts = (
    tasks["task_text"]
    .drop_duplicates()
    .tolist()
)


if len(unique_task_texts) > MAX_UNIQUE_TASKS:

    print(
        f"Unique task texts: {len(unique_task_texts):,}"
    )

    print(
        f"Using first {MAX_UNIQUE_TASKS:,} "
        "unique task texts for semantic reference..."
    )

    # Deterministic ordering
    unique_task_texts = sorted(
        unique_task_texts
    )[:MAX_UNIQUE_TASKS]


print(
    f"Semantic task texts: {len(unique_task_texts):,}"
)


# ------------------------------------------------------------
# Encode automation anchors
# ------------------------------------------------------------

print("Encoding automation reference anchors...")

automation_embeddings = model.encode(
    AUTOMATION_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False,
)


human_embeddings = model.encode(
    HUMAN_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False,
)


# ------------------------------------------------------------
# Encode tasks
# ------------------------------------------------------------

task_embeddings = model.encode(
    unique_task_texts,
    normalize_embeddings=True,
    batch_size=64,
    show_progress_bar=True,
)


# ------------------------------------------------------------
# Similarity against automation / human references
# ------------------------------------------------------------

automation_similarity = cosine_similarity(
    task_embeddings,
    automation_embeddings
).max(axis=1)


human_similarity = cosine_similarity(
    task_embeddings,
    human_embeddings
).max(axis=1)


semantic_balance = (
    automation_similarity
    - human_similarity
)


# ------------------------------------------------------------
# Convert semantic balance into [0, 1].
#
# IMPORTANT:
# This is a relative semantic suitability signal,
# not a claim that a task is objectively automatable.
# ------------------------------------------------------------

raw_score = (
    semantic_balance + 1.0
) / 2.0


# Clip extreme numerical values
raw_score = np.clip(
    raw_score,
    0.0,
    1.0
)


# ------------------------------------------------------------
# Map task text → score
# ------------------------------------------------------------

task_score_map = pd.DataFrame({
    "task_text": unique_task_texts,
    "automation_semantic_score": raw_score,
    "automation_similarity": automation_similarity,
    "human_similarity": human_similarity,
})


# ------------------------------------------------------------
# Merge scores back
# ------------------------------------------------------------

tasks = tasks.merge(
    task_score_map,
    on="task_text",
    how="left",
)


print(
    "\nAutomation semantic score:"
)

print(
    tasks["automation_semantic_score"].describe()
)


# ============================================================
# TASK AUTOMATION PROFILE
# ============================================================

print("\n[5/8] Building AI adoption scenario...")


# ------------------------------------------------------------
# Default AI adoption.
#
# This is a user-controlled scenario parameter.
# It is NOT the same as task automation probability.
# ------------------------------------------------------------

ai_adoption = DEFAULT_AI_ADOPTION / 100.0


# ------------------------------------------------------------
# Human share after AI
#
# Formula:
#
# Human Share =
# 1 - AI Adoption × Task Automation Suitability
#
# Therefore:
#
# highly automation-suitable task
#       → lower human share
#
# less automation-suitable task
#       → higher human share
# ------------------------------------------------------------

tasks["human_share_post_ai"] = (
    1.0
    - ai_adoption
    * tasks["automation_semantic_score"]
)


tasks["human_share_post_ai"] = np.clip(
    tasks["human_share_post_ai"],
    0.0,
    1.0
)


tasks["ai_share_post_adoption"] = (
    1.0
    - tasks["human_share_post_ai"]
)


# ============================================================
# TASK WEIGHTS
# ============================================================

print("\n[6/8] Calculating human capability exposure...")


# ------------------------------------------------------------
# Task weights
#
# Task Capability Weight comes from the existing
# semantic task → capability layer.
#
# Missing values are not fabricated.
# ------------------------------------------------------------

tasks_with_weight = df[
    [
        "O*NET-SOC Code",
        "Task ID",
        "Capability Type",
        "Capability ID",
        "Capability Name",
        "Task Capability Weight",
        "market_job_count",
        "market_avg_similarity",
        "employment_change_percent",
        "occupational_openings_2025_35_annual_avg_thousands",
    ]
].copy()


tasks_with_weight["Task Capability Weight"] = pd.to_numeric(
    tasks_with_weight["Task Capability Weight"],
    errors="coerce"
)


# ------------------------------------------------------------
# Merge task automation scenario
# ------------------------------------------------------------

tasks_with_weight = tasks_with_weight.merge(
    tasks[
        [
            "O*NET-SOC Code",
            "Task ID",
            "automation_semantic_score",
            "automation_similarity",
            "human_similarity",
            "human_share_post_ai",
            "ai_share_post_adoption",
        ]
    ],
    on=[
        "O*NET-SOC Code",
        "Task ID",
    ],
    how="left",
)


# ------------------------------------------------------------
# Capability identity
#
# Capability ID alone is NOT globally unique because
# different capability types can contain overlapping IDs.
# ------------------------------------------------------------

tasks_with_weight["Capability Key"] = (
    tasks_with_weight["Capability Type"]
    + "::"
    + tasks_with_weight["Capability ID"]
)


# ============================================================
# NORMALIZE TASK CAPABILITY WEIGHTS
# ============================================================

print("\nNormalizing task capability weights...")


# ------------------------------------------------------------
# Raw weight cannot directly be interpreted as exposure.
#
# Normalize within each occupation + task so the relative
# importance of linked capabilities is preserved.
# ------------------------------------------------------------

group_cols = [
    "O*NET-SOC Code",
    "Task ID",
]


def normalize_group(series):
    valid = series.notna()

    result = pd.Series(
        np.nan,
        index=series.index,
        dtype=float
    )

    if valid.sum() == 0:
        return result

    values = series[valid]

    total = values.sum()

    if total > 0:
        result.loc[valid] = values / total

    return result


tasks_with_weight[
    "Normalized Task Capability Weight"
] = (
    tasks_with_weight
    .groupby(group_cols)["Task Capability Weight"]
    .transform(normalize_group)
)


# ============================================================
# CURRENT / POST EXPOSURE
# ============================================================

# Current exposure:
#
# normalized task capability weight × human share = 1
#
# So:
# Current Exposure = normalized task-capability weight
#
# Post exposure:
#
# normalized task-capability weight × human share after AI
# ------------------------------------------------------------

tasks_with_weight[
    "Current Human Exposure"
] = (
    tasks_with_weight[
        "Normalized Task Capability Weight"
    ]
)


tasks_with_weight[
    "Post AI Human Exposure"
] = (
    tasks_with_weight[
        "Normalized Task Capability Weight"
    ]
    * tasks_with_weight[
        "human_share_post_ai"
    ]
)


# ------------------------------------------------------------
# Exposure lost
# ------------------------------------------------------------

tasks_with_weight[
    "Human Exposure Lost"
] = (
    tasks_with_weight[
        "Current Human Exposure"
    ]
    - tasks_with_weight[
        "Post AI Human Exposure"
    ]
)


tasks_with_weight[
    "Human Exposure Lost"
] = tasks_with_weight[
    "Human Exposure Lost"
].clip(lower=0)


# ============================================================
# CAPABILITY AGGREGATION
# ============================================================

print("\nAggregating capability exposure...")


capability = (
    tasks_with_weight
    .groupby(
        [
            "O*NET-SOC Code",
            "Capability Key",
            "Capability Type",
            "Capability ID",
            "Capability Name",
        ],
        dropna=False
    )
    .agg(
        Pre_AI_Exposure=(
            "Current Human Exposure",
            "sum"
        ),

        Post_AI_Exposure=(
            "Post AI Human Exposure",
            "sum"
        ),

        Exposure_Lost=(
            "Human Exposure Lost",
            "sum"
        ),

        Task_Count=(
            "Task ID",
            "nunique"
        ),

        Avg_Automation_Suitability=(
            "automation_semantic_score",
            "mean"
        ),

        Avg_AI_Share=(
            "ai_share_post_adoption",
            "mean"
        ),

        Market_Job_Count=(
            "market_job_count",
            "max"
        ),

        Market_Avg_Similarity=(
            "market_avg_similarity",
            "max"
        ),

        Employment_Change_Percent=(
            "employment_change_percent",
            "max"
        ),

        Annual_Openings_Thousands=(
            "occupational_openings_2025_35_annual_avg_thousands",
            "max"
        ),
    )
    .reset_index()
)


# ============================================================
# FORGE SKILL SHADOW
# ============================================================

print("\nCalculating FORGE Skill Shadow...")


# ------------------------------------------------------------
# Skill Shadow:
#
#   1 - Post Exposure / Pre Exposure
#
# bounded [0,1]
# ------------------------------------------------------------

capability["Skill_Shadow"] = np.where(
    capability["Pre_AI_Exposure"] > 0,
    1.0
    - (
        capability["Post_AI_Exposure"]
        / capability["Pre_AI_Exposure"]
    ),
    np.nan,
)


capability["Skill_Shadow"] = (
    capability["Skill_Shadow"]
    .clip(0.0, 1.0)
)


capability["Skill_Shadow_Percent"] = (
    capability["Skill_Shadow"]
    * 100.0
)


# ============================================================
# CAPABILITY CRITICALITY
# ============================================================

print("\nCalculating capability criticality...")


# ------------------------------------------------------------
# Criticality signals:
#
# 1. Task exposure
# 2. Market evidence
# 3. Future employment demand
#
# These are normalized within the resulting dataset.
# ------------------------------------------------------------


# ------------------------------------------------------------
# Exposure criticality
# ------------------------------------------------------------

exposure_scaler = MinMaxScaler()


capability["Exposure_Criticality"] = (
    exposure_scaler.fit_transform(
        capability[
            ["Pre_AI_Exposure"]
        ]
        .fillna(0)
    )
    .ravel()
)


# ------------------------------------------------------------
# Market criticality
# ------------------------------------------------------------

market_scaler = MinMaxScaler()


capability["Market_Criticality"] = (
    market_scaler.fit_transform(
        np.log1p(
            capability[
                ["Market_Job_Count"]
            ]
            .fillna(0)
        )
    )
    .ravel()
)


# ------------------------------------------------------------
# Future demand signal
# ------------------------------------------------------------

future_values = (
    capability[
        "Employment_Change_Percent"
    ]
    .fillna(0)
)


future_scaler = MinMaxScaler()


capability["Future_Demand_Signal"] = (
    future_scaler.fit_transform(
        future_values.to_numpy()
        .reshape(-1, 1)
    )
    .ravel()
)


# ------------------------------------------------------------
# Combined criticality
#
# Equal-weight transparent composite.
# This is a FORGE design choice, not an industry standard.
# ------------------------------------------------------------

capability["Capability_Criticality"] = (
    (
        capability["Exposure_Criticality"]
        + capability["Market_Criticality"]
        + capability["Future_Demand_Signal"]
    )
    / 3.0
)


# ============================================================
# CAPABILITY RISK
# ============================================================

print("\nCalculating capability risk...")


capability["Capability_Risk"] = (
    capability["Skill_Shadow"]
    * capability["Capability_Criticality"]
)


capability["Capability_Risk_Percent"] = (
    capability["Capability_Risk"]
    * 100.0
)


# ------------------------------------------------------------
# Risk bands
# ------------------------------------------------------------

capability["Risk_Band"] = pd.cut(
    capability["Capability_Risk"],
    bins=[
        -np.inf,
        0.20,
        0.40,
        0.60,
        0.80,
        np.inf,
    ],
    labels=[
        "Low",
        "Moderate",
        "Elevated",
        "High",
        "Critical",
    ],
)


# ============================================================
# SCENARIO METADATA
# ============================================================

capability["AI_Adoption_Percent"] = (
    DEFAULT_AI_ADOPTION
)


capability["AI_Adoption_Scenario"] = (
    f"{DEFAULT_AI_ADOPTION:.0f}%"
)


capability["Metric_Definition"] = (
    "FORGE Skill Shadow = 1 - "
    "(Post-AI Human Exposure / Pre-AI Human Exposure)"
)


# ============================================================
# OCCUPATION INFORMATION
# ============================================================

occupation_lookup = (
    df[
        [
            "O*NET-SOC Code",
            "SOC_7",
            "Occupation Title",
            "Occupation Description",
        ]
    ]
    .drop_duplicates(
        subset=["O*NET-SOC Code"]
    )
)


capability = capability.merge(
    occupation_lookup,
    on="O*NET-SOC Code",
    how="left",
)


# ============================================================
# FINAL COLUMN ORDER
# ============================================================

final_columns = [
    "O*NET-SOC Code",
    "SOC_7",
    "Occupation Title",
    "Occupation Description",

    "Capability Key",
    "Capability Type",
    "Capability ID",
    "Capability Name",

    "AI_Adoption_Percent",
    "AI_Adoption_Scenario",

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
    "Risk_Band",

    "Market_Job_Count",
    "Market_Avg_Similarity",

    "Employment_Change_Percent",
    "Annual_Openings_Thousands",

    "Metric_Definition",
]


final_columns = [
    col
    for col in final_columns
    if col in capability.columns
]


capability = capability[
    final_columns
]


# ============================================================
# REMOVE INVALID CAPABILITIES
# ============================================================

before = len(capability)

capability = capability[
    capability["Capability Name"].notna()
].copy()

capability = capability[
    capability["Capability Name"].str.len() > 0
].copy()

after = len(capability)

print(
    f"\nInvalid capability records removed: "
    f"{before - after:,}"
)


# ============================================================
# FINAL STATISTICS
# ============================================================

print("\n" + "=" * 75)
print("FORGE SKILL SHADOW SUMMARY")
print("=" * 75)


print(
    f"Capability records     : {len(capability):,}"
)

print(
    f"Unique occupations     : "
    f"{capability['O*NET-SOC Code'].nunique():,}"
)

print(
    f"Unique capabilities    : "
    f"{capability['Capability Key'].nunique():,}"
)

print(
    f"AI adoption scenario   : "
    f"{DEFAULT_AI_ADOPTION:.0f}%"
)

print(
    f"Mean Skill Shadow      : "
    f"{capability['Skill_Shadow_Percent'].mean():.2f}%"
)

print(
    f"Median Skill Shadow    : "
    f"{capability['Skill_Shadow_Percent'].median():.2f}%"
)

print(
    f"Maximum Skill Shadow   : "
    f"{capability['Skill_Shadow_Percent'].max():.2f}%"
)


print("\nRisk distribution:")

print(
    capability[
        "Risk_Band"
    ]
    .value_counts(
        dropna=False
    )
    .sort_index()
    .to_string()
)


# ============================================================
# TOP SHADOWED CAPABILITIES
# ============================================================

print("\nTop 15 capability shadows:")

top_shadow = (
    capability
    .sort_values(
        "Skill_Shadow_Percent",
        ascending=False
    )
    [
        [
            "Occupation Title",
            "Capability Name",
            "Skill_Shadow_Percent",
            "Capability_Risk_Percent",
            "Risk_Band",
        ]
    ]
    .head(15)
)


print(
    top_shadow.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving SKILL SHADOW outputs...")


capability.to_parquet(
    OUTPUT_FILE,
    index=False
)


capability.to_csv(
    OUTPUT_CSV,
    index=False
)


print("\nSaved:")

print(
    f"  {OUTPUT_FILE}"
)

print(
    f"  {OUTPUT_CSV}"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 75)
print("SKILL SHADOW BUILD COMPLETE")
print("=" * 75)