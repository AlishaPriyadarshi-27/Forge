from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — LATTICE RELEVANCE VALIDATION
# ============================================================
# Purpose:
# Validate whether the Task → Capability links selected by
# LATTICE are semantically strong enough before sending them
# to the LLM for synthetic apprenticeship generation.
#
# IMPORTANT:
# This script DOES NOT delete or modify the existing data.
# It only validates and reports relevance quality.
# ============================================================


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

LATTICE_PATH = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_engine.parquet"
)

WORKTRACE_PATH = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

OUTPUT_DIR = ROOT / "datasets" / "lattice"

VALIDATED_OUTPUT = OUTPUT_DIR / "forge_lattice_relevance_validation.parquet"
VALIDATED_CSV = OUTPUT_DIR / "forge_lattice_relevance_validation.csv"

LOW_CONF_OUTPUT = OUTPUT_DIR / "forge_lattice_low_relevance_review.csv"


# ------------------------------------------------------------
# 2. CONFIGURATION
# ------------------------------------------------------------

# Existing semantic matching pipeline used 0.35 as its
# minimum semantic similarity threshold.
ORIGINAL_MATCH_THRESHOLD = 0.35

# These are REVIEW bands, not automatic deletion thresholds.
REVIEW_THRESHOLDS = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]


# ------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ------------------------------------------------------------

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def find_column(df, candidates):
    """
    Find the first available column from a list of candidates.
    """
    for col in candidates:
        if col in df.columns:
            return col
    return None


def normalize_text(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ------------------------------------------------------------
# 4. LOAD DATA
# ------------------------------------------------------------

print_section("1. LOADING DATA")

if not LATTICE_PATH.exists():
    raise FileNotFoundError(
        f"LATTICE file not found:\n{LATTICE_PATH}"
    )

if not WORKTRACE_PATH.exists():
    raise FileNotFoundError(
        f"WORKTRACE file not found:\n{WORKTRACE_PATH}"
    )


print(f"Loading LATTICE:")
print(LATTICE_PATH)

lattice = pd.read_parquet(LATTICE_PATH)

print(f"\nLATTICE shape: {lattice.shape}")


print("\nLoading WORKTRACE:")
print(WORKTRACE_PATH)

worktrace = pd.read_parquet(WORKTRACE_PATH)

print(f"\nWORKTRACE shape: {worktrace.shape}")


# ------------------------------------------------------------
# 5. BASIC COLUMN INSPECTION
# ------------------------------------------------------------

print_section("2. COLUMN CHECK")

print("LATTICE columns:")
for col in lattice.columns:
    print(f"  - {col}")

print("\nWORKTRACE columns:")
for col in worktrace.columns:
    print(f"  - {col}")


# ------------------------------------------------------------
# 6. IDENTIFY IMPORTANT COLUMNS
# ------------------------------------------------------------

print_section("3. IDENTIFYING RELEVANCE COLUMNS")


occupation_col_lattice = find_column(
    lattice,
    [
        "Occupation Code",
        "Occupation_Code",
        "O*NET-SOC Code",
        "ONET_SOC_Code",
        "SOC Code",
    ],
)

occupation_col_worktrace = find_column(
    worktrace,
    [
        "Occupation Code",
        "Occupation_Code",
        "O*NET-SOC Code",
        "ONET_SOC_Code",
        "SOC Code",
    ],
)


task_id_lattice = find_column(
    lattice,
    [
        "Task ID",
        "Task_ID",
        "task_id",
    ],
)

task_id_worktrace = find_column(
    worktrace,
    [
        "Task ID",
        "Task_ID",
        "task_id",
    ],
)


capability_type_lattice = find_column(
    lattice,
    [
        "Capability Type",
        "Capability_Type",
        "capability_type",
    ],
)

capability_type_worktrace = find_column(
    worktrace,
    [
        "Capability Type",
        "Capability_Type",
        "capability_type",
    ],
)


capability_id_lattice = find_column(
    lattice,
    [
        "Capability ID",
        "Capability_ID",
        "capability_id",
    ],
)

capability_id_worktrace = find_column(
    worktrace,
    [
        "Capability ID",
        "Capability_ID",
        "capability_id",
    ],
)


semantic_col_worktrace = find_column(
    worktrace,
    [
        "Semantic Similarity",
        "semantic_similarity",
        "Semantic_Similarity",
    ],
)


task_weight_worktrace = find_column(
    worktrace,
    [
        "Task Capability Weight",
        "Task_Capability_Weight",
        "task_capability_weight",
    ],
)


required = {
    "LATTICE occupation": occupation_col_lattice,
    "WORKTRACE occupation": occupation_col_worktrace,
    "LATTICE task ID": task_id_lattice,
    "WORKTRACE task ID": task_id_worktrace,
    "LATTICE capability type": capability_type_lattice,
    "WORKTRACE capability type": capability_type_worktrace,
    "LATTICE capability ID": capability_id_lattice,
    "WORKTRACE capability ID": capability_id_worktrace,
    "WORKTRACE semantic similarity": semantic_col_worktrace,
}


print("\nDetected columns:")

for name, col in required.items():
    print(f"{name:35s}: {col}")


missing = [
    name
    for name, col in required.items()
    if col is None
]

if missing:
    raise ValueError(
        "\nRequired columns missing:\n"
        + "\n".join(f"  - {x}" for x in missing)
    )


# ------------------------------------------------------------
# 7. CREATE JOIN KEYS
# ------------------------------------------------------------

print_section("4. BUILDING TASK → CAPABILITY JOIN")

lattice["_occupation_key"] = (
    lattice[occupation_col_lattice]
    .fillna("")
    .astype(str)
    .str.strip()
)

worktrace["_occupation_key"] = (
    worktrace[occupation_col_worktrace]
    .fillna("")
    .astype(str)
    .str.strip()
)


lattice["_task_key"] = (
    lattice[task_id_lattice]
    .fillna("")
    .astype(str)
    .str.strip()
)

worktrace["_task_key"] = (
    worktrace[task_id_worktrace]
    .fillna("")
    .astype(str)
    .str.strip()
)


lattice["_cap_type_key"] = (
    lattice[capability_type_lattice]
    .fillna("")
    .astype(str)
    .str.strip()
)

worktrace["_cap_type_key"] = (
    worktrace[capability_type_worktrace]
    .fillna("")
    .astype(str)
    .str.strip()
)


lattice["_cap_id_key"] = (
    lattice[capability_id_lattice]
    .fillna("")
    .astype(str)
    .str.strip()
)

worktrace["_cap_id_key"] = (
    worktrace[capability_id_worktrace]
    .fillna("")
    .astype(str)
    .str.strip()
)


join_keys = [
    "_occupation_key",
    "_task_key",
    "_cap_type_key",
    "_cap_id_key",
]


# ------------------------------------------------------------
# 8. REMOVE DUPLICATES FROM WORKTRACE JOIN SOURCE
# ------------------------------------------------------------

print("\nChecking WORKTRACE duplicate keys...")

duplicate_count = worktrace.duplicated(
    subset=join_keys,
    keep=False
).sum()

print(f"Duplicate WORKTRACE key rows: {duplicate_count}")


# Keep the strongest semantic match if duplicates exist.
worktrace_join = (
    worktrace
    .sort_values(
        semantic_col_worktrace,
        ascending=False
    )
    .drop_duplicates(
        subset=join_keys,
        keep="first"
    )
    .copy()
)


print(
    f"WORKTRACE rows after key deduplication: "
    f"{len(worktrace_join):,}"
)


# ------------------------------------------------------------
# 9. SELECT RELEVANCE INFORMATION
# ------------------------------------------------------------

relevance_cols = join_keys + [
    semantic_col_worktrace,
]

if task_weight_worktrace:
    relevance_cols.append(task_weight_worktrace)


relevance = worktrace_join[relevance_cols].copy()


rename_map = {
    semantic_col_worktrace: "Semantic_Similarity_Recovered"
}

if task_weight_worktrace:
    rename_map[task_weight_worktrace] = "Task_Capability_Weight_Recovered"


relevance = relevance.rename(columns=rename_map)


# ------------------------------------------------------------
# 10. MERGE WITH LATTICE
# ------------------------------------------------------------

print_section("5. RECOVERING SEMANTIC EVIDENCE")

validated = lattice.merge(
    relevance,
    on=join_keys,
    how="left",
    indicator="_join_status",
)


matched = (
    validated["_join_status"] == "both"
).sum()

unmatched = (
    validated["_join_status"] != "both"
).sum()

print(f"LATTICE records:       {len(validated):,}")
print(f"Semantic evidence found: {matched:,}")
print(f"Semantic evidence missing: {unmatched:,}")


# ------------------------------------------------------------
# 11. NORMALIZE SEMANTIC SIMILARITY
# ------------------------------------------------------------

validated["Semantic_Similarity_Recovered"] = pd.to_numeric(
    validated["Semantic_Similarity_Recovered"],
    errors="coerce"
)


# ------------------------------------------------------------
# 12. RELEVANCE BAND
# ------------------------------------------------------------

def relevance_band(score):

    if pd.isna(score):
        return "Missing Evidence"

    if score < 0.40:
        return "Very Low"

    elif score < 0.45:
        return "Low"

    elif score < 0.50:
        return "Moderate"

    elif score < 0.55:
        return "Good"

    elif score < 0.60:
        return "Strong"

    else:
        return "Very Strong"


validated["Relevance_Band"] = (
    validated["Semantic_Similarity_Recovered"]
    .apply(relevance_band)
)


# ------------------------------------------------------------
# 13. REVIEW FLAG
# ------------------------------------------------------------

def review_flag(score):

    if pd.isna(score):
        return "REVIEW_MISSING"

    if score < 0.40:
        return "REVIEW_HIGH_PRIORITY"

    elif score < 0.45:
        return "REVIEW"

    else:
        return "PASS"


validated["Relevance_Review_Flag"] = (
    validated["Semantic_Similarity_Recovered"]
    .apply(review_flag)
)


# ------------------------------------------------------------
# 14. DATA QUALITY CHECKS
# ------------------------------------------------------------

print_section("6. DATA QUALITY")

semantic = validated[
    "Semantic_Similarity_Recovered"
].dropna()


print(f"Semantic evidence records: {len(semantic):,}")
print(
    f"Missing semantic evidence: "
    f"{validated['Semantic_Similarity_Recovered'].isna().sum():,}"
)


if len(semantic) > 0:

    print(
        f"Minimum semantic similarity: "
        f"{semantic.min():.4f}"
    )

    print(
        f"Maximum semantic similarity: "
        f"{semantic.max():.4f}"
    )

    print(
        f"Mean semantic similarity: "
        f"{semantic.mean():.4f}"
    )

    print(
        f"Median semantic similarity: "
        f"{semantic.median():.4f}"
    )


# ------------------------------------------------------------
# 15. THRESHOLD DISTRIBUTION
# ------------------------------------------------------------

print_section("7. SEMANTIC SIMILARITY DISTRIBUTION")

if len(semantic) > 0:

    for threshold in REVIEW_THRESHOLDS:

        count = (
            semantic < threshold
        ).sum()

        percentage = (
            count / len(semantic) * 100
        )

        print(
            f"< {threshold:.2f}: "
            f"{count:>7,} records "
            f"({percentage:6.2f}%)"
        )


# ------------------------------------------------------------
# 16. RELEVANCE BAND DISTRIBUTION
# ------------------------------------------------------------

print_section("8. RELEVANCE BANDS")

band_counts = (
    validated["Relevance_Band"]
    .value_counts(dropna=False)
)

band_percentage = (
    validated["Relevance_Band"]
    .value_counts(normalize=True, dropna=False)
    * 100
)


for band, count in band_counts.items():

    pct = band_percentage[band]

    print(
        f"{str(band):18s}: "
        f"{count:>7,} "
        f"({pct:6.2f}%)"
    )


# ------------------------------------------------------------
# 17. REVIEW RECORDS
# ------------------------------------------------------------

print_section("9. LOW-RELEVANCE REVIEW SET")

review_mask = (
    validated["Relevance_Review_Flag"]
    .isin(
        [
            "REVIEW_HIGH_PRIORITY",
            "REVIEW",
            "REVIEW_MISSING",
        ]
    )
)

review = validated.loc[
    review_mask
].copy()


print(
    f"Records requiring review: "
    f"{len(review):,}"
)


# ------------------------------------------------------------
# 18. DISPLAY REPRESENTATIVE LOW-SCORE EXAMPLES
# ------------------------------------------------------------

print_section("10. LOW-SCORE EXAMPLES")

display_columns = [
    occupation_col_lattice,
    "Task",
    "Capability Name",
    "Capability Type",
    "Semantic_Similarity_Recovered",
    "Relevance_Band",
    "Relevance_Review_Flag",
]


available_display_columns = [
    col
    for col in display_columns
    if col in review.columns
]


if len(review) > 0:

    examples = (
        review
        .sort_values(
            "Semantic_Similarity_Recovered",
            ascending=True,
            na_position="first"
        )
        .head(20)
    )

    for idx, row in examples.iterrows():

        occupation = row.get(
            occupation_col_lattice,
            ""
        )

        task = row.get(
            "Task",
            ""
        )

        capability = row.get(
            "Capability Name",
            ""
        )

        similarity = row.get(
            "Semantic_Similarity_Recovered",
            np.nan
        )

        band = row.get(
            "Relevance_Band",
            ""
        )

        print("\n---")

        print(f"Occupation : {occupation}")
        print(f"Task       : {task}")
        print(f"Capability : {capability}")

        if pd.isna(similarity):
            print("Similarity : MISSING")
        else:
            print(
                f"Similarity : {similarity:.4f}"
            )

        print(f"Band       : {band}")


else:

    print("No low-relevance records found.")


# ------------------------------------------------------------
# 19. CAPABILITY-LEVEL SUMMARY
# ------------------------------------------------------------

print_section("11. CAPABILITY-LEVEL RELEVANCE SUMMARY")

capability_name_col = find_column(
    validated,
    [
        "Capability Name",
        "Capability_Name",
        "capability_name",
    ],
)

if capability_name_col:

    capability_summary = (
        validated
        .groupby(
            capability_name_col,
            dropna=False
        )
        .agg(
            Records=(
                "Semantic_Similarity_Recovered",
                "count"
            ),
            Mean_Similarity=(
                "Semantic_Similarity_Recovered",
                "mean"
            ),
            Median_Similarity=(
                "Semantic_Similarity_Recovered",
                "median"
            ),
            Min_Similarity=(
                "Semantic_Similarity_Recovered",
                "min"
            ),
        )
        .reset_index()
        .sort_values(
            "Mean_Similarity",
            ascending=True
        )
    )

    print(
        capability_summary.head(15).to_string(
            index=False
        )
    )

else:

    capability_summary = None

    print(
        "Capability Name column not found."
    )


# ------------------------------------------------------------
# 20. OCCUPATION-LEVEL SUMMARY
# ------------------------------------------------------------

print_section("12. OCCUPATION-LEVEL RELEVANCE SUMMARY")

occupation_summary = (
    validated
    .groupby(
        occupation_col_lattice,
        dropna=False
    )
    .agg(
        Records=(
            "Semantic_Similarity_Recovered",
            "count"
        ),
        Mean_Similarity=(
            "Semantic_Similarity_Recovered",
            "mean"
        ),
        Median_Similarity=(
            "Semantic_Similarity_Recovered",
            "median"
        ),
        Low_Relevance_Count=(
            "Semantic_Similarity_Recovered",
            lambda x: (x < 0.45).sum()
        ),
    )
    .reset_index()
    .sort_values(
        "Mean_Similarity",
        ascending=True
    )
)


print(
    occupation_summary.head(15).to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 21. FINAL QUALITY METRICS
# ------------------------------------------------------------

print_section("13. FINAL VALIDATION METRICS")

total_records = len(validated)

missing_similarity = (
    validated[
        "Semantic_Similarity_Recovered"
    ].isna().sum()
)

very_low = (
    validated[
        "Semantic_Similarity_Recovered"
    ] < 0.40
).sum()

low = (
    validated[
        "Semantic_Similarity_Recovered"
    ] < 0.45
).sum()

acceptable = (
    validated[
        "Semantic_Similarity_Recovered"
    ] >= 0.45
).sum()


print(f"Total LATTICE records       : {total_records:,}")
print(f"Missing semantic evidence   : {missing_similarity:,}")
print(f"< 0.40 similarity           : {very_low:,}")
print(f"< 0.45 similarity           : {low:,}")
print(f">= 0.45 similarity          : {acceptable:,}")


if total_records > 0:

    print(
        f"Missing evidence %          : "
        f"{missing_similarity / total_records * 100:.2f}%"
    )

    print(
        f"< 0.40 %                    : "
        f"{very_low / total_records * 100:.2f}%"
    )

    print(
        f"< 0.45 %                    : "
        f"{low / total_records * 100:.2f}%"
    )

    print(
        f">= 0.45 %                   : "
        f"{acceptable / total_records * 100:.2f}%"
    )


# ------------------------------------------------------------
# 22. REMOVE INTERNAL JOIN COLUMNS
# ------------------------------------------------------------

validated.drop(
    columns=[
        "_occupation_key",
        "_task_key",
        "_cap_type_key",
        "_cap_id_key",
        "_join_status",
    ],
    inplace=True,
    errors="ignore",
)


# ------------------------------------------------------------
# 23. SAVE COMPLETE VALIDATION OUTPUT
# ------------------------------------------------------------

print_section("14. SAVING VALIDATION OUTPUT")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

validated.to_parquet(
    VALIDATED_OUTPUT,
    index=False
)

validated.to_csv(
    VALIDATED_CSV,
    index=False
)


# ------------------------------------------------------------
# 24. SAVE LOW-RELEVANCE REVIEW FILE
# ------------------------------------------------------------

review_export_columns = [
    occupation_col_lattice,
    "Task",
    "Task ID",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Semantic_Similarity_Recovered",
    "Task_Capability_Weight_Recovered",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Relevance_Band",
    "Relevance_Review_Flag",
]


review_export_columns = [
    col
    for col in review_export_columns
    if col in review.columns
]


if len(review) > 0:

    review[
        review_export_columns
    ].to_csv(
        LOW_CONF_OUTPUT,
        index=False
    )

else:

    pd.DataFrame(
        columns=review_export_columns
    ).to_csv(
        LOW_CONF_OUTPUT,
        index=False
    )


# ------------------------------------------------------------
# 25. FINAL MESSAGE
# ------------------------------------------------------------

print_section("VALIDATION COMPLETE")

print(
    "LATTICE relevance validation completed successfully."
)

print(
    f"\nFull validation file:"
)

print(
    VALIDATED_OUTPUT
)

print(
    f"\nCSV version:"
)

print(
    VALIDATED_CSV
)

print(
    f"\nLow-relevance manual review file:"
)

print(
    LOW_CONF_OUTPUT
)

print(
    "\nIMPORTANT:"
)

print(
    "No LATTICE records were deleted or modified."
)

print(
    "This script only measures semantic relevance."
)

print(
    "The next step is to inspect the results and decide"
)

print(
    "the evidence-based relevance filtering strategy"
)

print(
    "BEFORE connecting the LLM."
)