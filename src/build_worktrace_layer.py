import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# FORGE — WORKTRACE INTELLIGENCE LAYER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

TASK_CAPABILITY_FILE = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "onet_task_capability_layer.parquet"
)

ONET_OCCUPATION_FILE = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "onet_occupations.parquet"
)

JOB_CAPABILITY_FILE = (
    BASE_DIR
    / "datasets"
    / "job_postings"
    / "knowledge_base"
    / "job_capability_matches.parquet"
)

BLS_FILE = (
    BASE_DIR
    / "datasets"
    / "bls"
    / "knowledge_base"
    / "bls_occupation_projections.parquet"
)

CROSSWALK_FILE = (
    BASE_DIR
    / "datasets"
    / "crosswalk"
    / "knowledge_base"
    / "onet_esco_crosswalk.parquet"
)

OUTPUT_PARQUET = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

OUTPUT_CSV = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.csv"
)


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 75)
print("FORGE — WORKTRACE INTELLIGENCE LAYER")
print("=" * 75)


# ============================================================
# [1/7] TASK → CAPABILITY
# ============================================================

print("\n[1/7] Loading Task → Capability layer...")

task_cap = pd.read_parquet(TASK_CAPABILITY_FILE)

print(f"Task-capability records: {len(task_cap):,}")


required_task_cols = [
    "O*NET-SOC Code",
    "Task ID",
    "Task",
    "DWA Element Name",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Semantic Similarity",
    "Occupation Capability Value",
    "Task Capability Weight",
]

missing = [
    col for col in required_task_cols
    if col not in task_cap.columns
]

if missing:
    raise ValueError(
        f"Missing task-capability columns: {missing}"
    )


# ============================================================
# [2/7] O*NET OCCUPATIONS
# ============================================================

print("\n[2/7] Loading O*NET occupations...")

occupations = pd.read_parquet(ONET_OCCUPATION_FILE)

print(f"Occupation records: {len(occupations):,}")


required_occ_cols = [
    "O*NET-SOC Code",
    "Title",
    "Description",
]

missing = [
    col for col in required_occ_cols
    if col not in occupations.columns
]

if missing:
    raise ValueError(
        f"Missing occupation columns: {missing}"
    )


occupations = occupations[
    required_occ_cols
].copy()


occupations = occupations.drop_duplicates(
    subset=["O*NET-SOC Code"]
)


occupations = occupations.rename(
    columns={
        "Title": "Occupation Title",
        "Description": "Occupation Description",
    }
)


# ============================================================
# [3/7] JOB MARKET CAPABILITY EVIDENCE
# ============================================================

print("\n[3/7] Loading job-market capability evidence...")

job_cap = pd.read_parquet(JOB_CAPABILITY_FILE)

print(f"Job-capability records: {len(job_cap):,}")


required_job_cols = [
    "job_id",
    "job_title",
    "capability_type",
    "capability_id",
    "capability_name",
    "similarity_score",
    "match_quality",
]

missing = [
    col for col in required_job_cols
    if col not in job_cap.columns
]

if missing:
    raise ValueError(
        f"Missing job-capability columns: {missing}"
    )


print("\nBuilding capability-level market evidence...")


job_cap["similarity_score"] = pd.to_numeric(
    job_cap["similarity_score"],
    errors="coerce"
)


market_cap = (
    job_cap
    .groupby(
        [
            "capability_type",
            "capability_id",
            "capability_name",
        ],
        dropna=False
    )
    .agg(
        market_job_count=("job_id", "nunique"),
        market_avg_similarity=("similarity_score", "mean"),
        market_max_similarity=("similarity_score", "max"),
    )
    .reset_index()
)


print(
    f"Market capability records: {len(market_cap):,}"
)


market_cap = market_cap.rename(
    columns={
        "capability_type": "Capability Type",
        "capability_id": "Capability ID",
        "capability_name": "Capability Name",
    }
)


# ============================================================
# [4/7] BLS OCCUPATION PROJECTIONS
# ============================================================

print("\n[4/7] Loading BLS occupation projections...")

bls = pd.read_parquet(BLS_FILE)

print(f"BLS occupation records: {len(bls):,}")

print("BLS columns:")
print(bls.columns.tolist())


if "occupation_code" not in bls.columns:
    raise ValueError(
        "Processed BLS file does not contain "
        "'occupation_code'."
    )


print("\nUsing processed BLS occupation code...")


bls = bls.copy()


# ------------------------------------------------------------
# BLS uses 7-character SOC code:
# Example: 11-1011
# O*NET uses detailed code:
# Example: 11-1011.00
#
# We create a deterministic common SOC key.
# ------------------------------------------------------------

bls["SOC_7"] = (
    bls["occupation_code"]
    .astype(str)
    .str.strip()
    .str[:7]
)


bls["O*NET-SOC Code"] = (
    bls["occupation_code"]
    .astype(str)
    .str.strip()
)


bls_fields = [
    "O*NET-SOC Code",
    "SOC_7",
    "occupation_title",
    "occupation_type",
    "employment_2025_thousands",
    "employment_2035_thousands",
    "employment_distribution_2025_percent",
    "employment_distribution_2035_percent",
    "employment_change_thousands",
    "employment_change_percent",
    "percent_self_employed_2025",
    "occupational_openings_2025_35_annual_avg_thousands",
    "median_annual_wage_2025",
    "typical_education",
    "related_work_experience",
    "typical_on_the_job_training",
    "employment_change_absolute_thousands",
    "projected_growth_direction",
    "has_positive_projected_growth",
    "has_occupational_openings_data",
    "projection_period",
    "base_year",
    "projection_year",
]


bls_fields = [
    col for col in bls_fields
    if col in bls.columns
]


bls = bls[bls_fields].copy()


bls = bls.drop_duplicates(
    subset=["SOC_7"]
)


print(
    f"BLS occupation codes: {len(bls):,}"
)

print(
    f"BLS fields retained: {len(bls.columns):,}"
)


# ============================================================
# [5/7] O*NET → ESCO CROSSWALK
# ============================================================

print("\n[5/7] Loading O*NET → ESCO crosswalk...")

crosswalk = pd.read_parquet(CROSSWALK_FILE)

print(
    f"Crosswalk records: {len(crosswalk):,}"
)


required_crosswalk_cols = [
    "onet_soc_code",
    "esco_occupation_uri",
    "esco_occupation",
    "mapping_type",
]

missing = [
    col for col in required_crosswalk_cols
    if col not in crosswalk.columns
]

if missing:
    raise ValueError(
        f"Missing crosswalk columns: {missing}"
    )


crosswalk["O*NET-SOC Code"] = (
    crosswalk["onet_soc_code"]
    .astype(str)
    .str.strip()
)


crosswalk["mapping_type_clean"] = (
    crosswalk["mapping_type"]
    .astype(str)
    .str.strip()
    .str.lower()
)


crosswalk_summary = (
    crosswalk
    .groupby("O*NET-SOC Code")
    .agg(
        esco_occupation_count=(
            "esco_occupation_uri",
            "nunique"
        ),

        esco_exact_match_count=(
            "mapping_type_clean",
            lambda x: (x == "exactmatch").sum()
        ),

        esco_close_match_count=(
            "mapping_type_clean",
            lambda x: (x == "closematch").sum()
        ),

        esco_broad_match_count=(
            "mapping_type_clean",
            lambda x: (x == "broadmatch").sum()
        ),

        esco_narrow_match_count=(
            "mapping_type_clean",
            lambda x: (x == "narrowmatch").sum()
        ),
    )
    .reset_index()
)


print(
    f"Crosswalk occupation records: "
    f"{len(crosswalk_summary):,}"
)


# ============================================================
# [6/7] BUILD WORKTRACE
# ============================================================

print("\n[6/7] Building integrated WORKTRACE layer...")


worktrace = task_cap.copy()


# ------------------------------------------------------------
# Create common SOC key for O*NET
# ------------------------------------------------------------

worktrace["SOC_7"] = (
    worktrace["O*NET-SOC Code"]
    .astype(str)
    .str.strip()
    .str[:7]
)


# ------------------------------------------------------------
# Merge O*NET occupation information
# ------------------------------------------------------------

worktrace = worktrace.merge(
    occupations,
    on="O*NET-SOC Code",
    how="left",
)


# ------------------------------------------------------------
# Merge BLS using normalized SOC key
# ------------------------------------------------------------

worktrace = worktrace.merge(
    bls,
    on="SOC_7",
    how="left",
    suffixes=("", "_BLS")
)


# ------------------------------------------------------------
# Merge ESCO information
# ------------------------------------------------------------

worktrace = worktrace.merge(
    crosswalk_summary,
    on="O*NET-SOC Code",
    how="left",
)


# ------------------------------------------------------------
# Merge job-market capability evidence
# ------------------------------------------------------------

worktrace = worktrace.merge(
    market_cap[
        [
            "Capability Type",
            "Capability ID",
            "Capability Name",
            "market_job_count",
            "market_avg_similarity",
            "market_max_similarity",
        ]
    ],
    on=[
        "Capability Type",
        "Capability ID",
        "Capability Name",
    ],
    how="left",
)


# ============================================================
# [7/7] INTELLIGENCE FLAGS + CLEANING
# ============================================================

print("\n[7/7] Creating WORKTRACE intelligence fields...")


# ------------------------------------------------------------
# Market evidence
# ------------------------------------------------------------

worktrace["Market Evidence Available"] = (
    worktrace["market_job_count"]
    .fillna(0)
    .gt(0)
)


# ------------------------------------------------------------
# Occupation evidence
# ------------------------------------------------------------

worktrace["Occupation Data Available"] = (
    worktrace["Occupation Title"]
    .notna()
)


# ------------------------------------------------------------
# BLS evidence
# ------------------------------------------------------------

worktrace["BLS Data Available"] = (
    worktrace["employment_2025_thousands"]
    .notna()
)


# ------------------------------------------------------------
# ESCO evidence
# ------------------------------------------------------------

worktrace["ESCO Data Available"] = (
    worktrace["esco_occupation_count"]
    .fillna(0)
    .gt(0)
)


# ============================================================
# COUNT COLUMNS
# ============================================================

count_columns = [
    "market_job_count",
    "esco_occupation_count",
    "esco_exact_match_count",
    "esco_close_match_count",
    "esco_broad_match_count",
    "esco_narrow_match_count",
]


for col in count_columns:

    if col in worktrace.columns:

        worktrace[col] = (
            pd.to_numeric(
                worktrace[col],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )


# ============================================================
# NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Semantic Similarity",
    "Occupation Capability Value",
    "Task Capability Weight",
    "market_avg_similarity",
    "market_max_similarity",
    "employment_2025_thousands",
    "employment_2035_thousands",
    "employment_change_thousands",
    "employment_change_percent",
    "occupational_openings_2025_35_annual_avg_thousands",
    "median_annual_wage_2025",
]


for col in numeric_columns:

    if col in worktrace.columns:

        worktrace[col] = pd.to_numeric(
            worktrace[col],
            errors="coerce"
        )


# ============================================================
# REMOVE EXACT DUPLICATES
# ============================================================

before = len(worktrace)

worktrace = worktrace.drop_duplicates()

after = len(worktrace)

print(
    f"\nExact duplicate records removed: "
    f"{before - after:,}"
)


# ============================================================
# COLUMN ORDER
# ============================================================

priority_columns = [
    "O*NET-SOC Code",
    "SOC_7",

    "Occupation Title",
    "Occupation Description",

    "Task ID",
    "Task",
    "DWA Element Name",

    "Capability Type",
    "Capability ID",
    "Capability Name",

    "Semantic Similarity",
    "Occupation Capability Value",
    "Task Capability Weight",

    "market_job_count",
    "market_avg_similarity",
    "market_max_similarity",

    "employment_2025_thousands",
    "employment_2035_thousands",
    "employment_change_thousands",
    "employment_change_percent",

    "occupational_openings_2025_35_annual_avg_thousands",

    "median_annual_wage_2025",

    "typical_education",
    "related_work_experience",
    "typical_on_the_job_training",

    "projected_growth_direction",

    "esco_occupation_count",
    "esco_exact_match_count",
    "esco_close_match_count",
    "esco_broad_match_count",
    "esco_narrow_match_count",

    "Market Evidence Available",
    "Occupation Data Available",
    "BLS Data Available",
    "ESCO Data Available",
]


existing_priority = [
    col
    for col in priority_columns
    if col in worktrace.columns
]


remaining_columns = [
    col
    for col in worktrace.columns
    if col not in existing_priority
]


worktrace = worktrace[
    existing_priority + remaining_columns
]


# ============================================================
# DATA COMPLETENESS
# ============================================================

print("\n" + "-" * 75)
print("WORKTRACE DATA COMPLETENESS")
print("-" * 75)


total = len(worktrace)


occupation_available = (
    worktrace["Occupation Title"]
    .notna()
    .sum()
)

task_available = (
    worktrace["Task"]
    .notna()
    .sum()
)

capability_available = (
    worktrace["Capability Name"]
    .notna()
    .sum()
)

weight_available = (
    worktrace["Task Capability Weight"]
    .notna()
    .sum()
)

market_available = (
    worktrace["Market Evidence Available"]
    .sum()
)

bls_available = (
    worktrace["BLS Data Available"]
    .sum()
)

esco_available = (
    worktrace["ESCO Data Available"]
    .sum()
)


completeness = pd.DataFrame({
    "Field": [
        "Occupation",
        "Task",
        "Capability",
        "Task Capability Weight",
        "Market Evidence",
        "BLS Evidence",
        "ESCO Evidence",
    ],

    "Available": [
        occupation_available,
        task_available,
        capability_available,
        weight_available,
        market_available,
        bls_available,
        esco_available,
    ],
})


completeness["Total"] = total


completeness["Coverage %"] = (
    completeness["Available"]
    / total
    * 100
)


print(
    completeness.to_string(index=False)
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("WORKTRACE SUMMARY")
print("=" * 75)


unique_occupations = (
    worktrace["O*NET-SOC Code"]
    .nunique()
)


unique_tasks = (
    worktrace["Task ID"]
    .nunique()
)


unique_capabilities = (
    worktrace[
        ["Capability Type", "Capability ID"]
    ]
    .drop_duplicates()
    .shape[0]
)


market_supported_rows = (
    worktrace["Market Evidence Available"]
    .sum()
)


bls_supported_rows = (
    worktrace["BLS Data Available"]
    .sum()
)


esco_supported_rows = (
    worktrace["ESCO Data Available"]
    .sum()
)


print(
    f"Records              : {len(worktrace):,}"
)

print(
    f"Unique occupations    : {unique_occupations:,}"
)

print(
    f"Unique tasks          : {unique_tasks:,}"
)

print(
    f"Unique capabilities   : {unique_capabilities:,}"
)

print(
    f"Market-supported rows : {market_supported_rows:,}"
)

print(
    f"BLS-supported rows    : {bls_supported_rows:,}"
)

print(
    f"ESCO-supported rows   : {esco_supported_rows:,}"
)


# ============================================================
# SAVE
# ============================================================

print("\nSaving WORKTRACE files...")


worktrace.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


worktrace.to_csv(
    OUTPUT_CSV,
    index=False
)


print("\nSaved:")
print(f"  {OUTPUT_PARQUET}")
print(f"  {OUTPUT_CSV}")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 75)
print("WORKTRACE BUILD COMPLETE")
print("=" * 75)