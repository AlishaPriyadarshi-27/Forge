from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — LATTICE RELEVANCE FILTERING
# ============================================================
# Purpose:
# Create a high-quality LLM-ready LATTICE dataset by filtering
# weak Task → Capability semantic links.
#
# IMPORTANT:
# - Original LATTICE is NOT modified.
# - Original WORKTRACE is NOT modified.
# - No arbitrary global deletion based only on one threshold.
# - Strong evidence is retained.
# - Weak evidence is excluded from the LLM-ready dataset.
# - All filtering decisions are recorded.
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

VALIDATION_PATH = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_relevance_validation.parquet"
)

OUTPUT_DIR = ROOT / "datasets" / "lattice"

FILTERED_PARQUET = (
    OUTPUT_DIR
    / "forge_lattice_llm_ready.parquet"
)

FILTERED_CSV = (
    OUTPUT_DIR
    / "forge_lattice_llm_ready.csv"
)

REVIEW_PARQUET = (
    OUTPUT_DIR
    / "forge_lattice_relevance_review.parquet"
)

REVIEW_CSV = (
    OUTPUT_DIR
    / "forge_lattice_relevance_review.csv"
)


# ------------------------------------------------------------
# 2. CONFIGURATION
# ------------------------------------------------------------

# Semantic similarity bands from the validation stage.
#
# >= 0.50:
# Strong enough for automated downstream use.
#
# 0.45–0.50:
# Borderline. Retained only when supporting evidence is strong.
#
# < 0.45:
# Manual review / excluded from LLM-ready dataset.
#
# This avoids blindly deleting every relationship below 0.50.

STRONG_SIMILARITY = 0.50
BORDERLINE_SIMILARITY = 0.45


# Supporting evidence thresholds.

# Task Capability Weight is already part of WORKTRACE.
# It combines semantic similarity with occupation capability value.
MIN_TASK_WEIGHT_FOR_BORDERLINE = 0.20

# Practice relevance is produced by the LATTICE engine.
MIN_PRACTICE_RELEVANCE_FOR_BORDERLINE = 0.35

# LATTICE priority helps ensure that a borderline relationship
# is still important enough to be useful for capability preservation.
MIN_LATTICE_PRIORITY_FOR_BORDERLINE = 0.15


# ------------------------------------------------------------
# 3. HELPER
# ------------------------------------------------------------

def print_section(title):
    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)


def numeric_column(df, column):
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ------------------------------------------------------------
# 4. LOAD DATA
# ------------------------------------------------------------

print_section("1. LOADING LATTICE DATA")

if not LATTICE_PATH.exists():
    raise FileNotFoundError(
        f"LATTICE file not found:\n{LATTICE_PATH}"
    )

if not VALIDATION_PATH.exists():
    raise FileNotFoundError(
        f"Validation file not found:\n{VALIDATION_PATH}"
    )


lattice = pd.read_parquet(
    LATTICE_PATH
)

validation = pd.read_parquet(
    VALIDATION_PATH
)


print(
    f"LATTICE records loaded: "
    f"{len(lattice):,}"
)

print(
    f"Validation records loaded: "
    f"{len(validation):,}"
)


# ------------------------------------------------------------
# 5. REQUIRED COLUMNS
# ------------------------------------------------------------

print_section("2. CHECKING REQUIRED COLUMNS")


required_lattice = [
    "O*NET-SOC Code",
    "Task ID",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task",
    "Task Capability Weight",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",
    "LATTICE_Priority",
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Human_Practice_Signal",
    "AI_Transformation_Signal",
    "Task_Practice_Relevance",
    "LLM_Task_Input",
]


required_validation = [
    "O*NET-SOC Code",
    "Task ID",
    "Capability Type",
    "Capability ID",
    "Semantic_Similarity_Recovered",
]


missing_lattice = [
    col
    for col in required_lattice
    if col not in lattice.columns
]

missing_validation = [
    col
    for col in required_validation
    if col not in validation.columns
]


if missing_lattice:
    raise ValueError(
        "Missing LATTICE columns:\n"
        + "\n".join(
            f"  - {x}"
            for x in missing_lattice
        )
    )


if missing_validation:
    raise ValueError(
        "Missing validation columns:\n"
        + "\n".join(
            f"  - {x}"
            for x in missing_validation
        )
    )


print("All required columns found.")


# ------------------------------------------------------------
# 6. CREATE UNIQUE JOIN KEY
# ------------------------------------------------------------

print_section("3. BUILDING RELEVANCE JOIN KEY")


def make_key(df):
    return (
        df["O*NET-SOC Code"]
        .fillna("")
        .astype(str)
        .str.strip()
        + "||"
        + df["Task ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        + "||"
        + df["Capability Type"]
        .fillna("")
        .astype(str)
        .str.strip()
        + "||"
        + df["Capability ID"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


lattice["_relevance_key"] = make_key(
    lattice
)

validation["_relevance_key"] = make_key(
    validation
)


# ------------------------------------------------------------
# 7. REMOVE DUPLICATE VALIDATION KEYS
# ------------------------------------------------------------

validation = (
    validation
    .sort_values(
        "Semantic_Similarity_Recovered",
        ascending=False
    )
    .drop_duplicates(
        "_relevance_key",
        keep="first"
    )
    .copy()
)


print(
    f"Unique validation keys: "
    f"{validation['_relevance_key'].nunique():,}"
)


# ------------------------------------------------------------
# 8. MERGE SEMANTIC EVIDENCE
# ------------------------------------------------------------

print_section("4. ATTACHING SEMANTIC EVIDENCE")


semantic_evidence = validation[
    [
        "_relevance_key",
        "Semantic_Similarity_Recovered",
    ]
].copy()


lattice = lattice.merge(
    semantic_evidence,
    on="_relevance_key",
    how="left",
    validate="one_to_one",
)


missing_similarity = (
    lattice[
        "Semantic_Similarity_Recovered"
    ].isna().sum()
)


print(
    f"Missing semantic similarity: "
    f"{missing_similarity:,}"
)


if missing_similarity > 0:
    raise ValueError(
        "Some LATTICE records do not have semantic evidence."
    )


# ------------------------------------------------------------
# 9. NUMERIC NORMALIZATION
# ------------------------------------------------------------

print_section("5. NORMALIZING EVIDENCE")


numeric_columns = [
    "Semantic_Similarity_Recovered",
    "Task Capability Weight",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",
    "LATTICE_Priority",
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Human_Practice_Signal",
    "AI_Transformation_Signal",
    "Task_Practice_Relevance",
]


for col in numeric_columns:
    numeric_column(
        lattice,
        col
    )


# ------------------------------------------------------------
# 10. SANITY CHECK
# ------------------------------------------------------------

similarity = lattice[
    "Semantic_Similarity_Recovered"
]


invalid_similarity = (
    (similarity < 0)
    | (similarity > 1)
).sum()


if invalid_similarity > 0:
    raise ValueError(
        f"Invalid semantic similarity values: "
        f"{invalid_similarity}"
    )


print(
    f"Semantic similarity range: "
    f"{similarity.min():.4f} → "
    f"{similarity.max():.4f}"
)

print(
    f"Mean similarity: "
    f"{similarity.mean():.4f}"
)

print(
    f"Median similarity: "
    f"{similarity.median():.4f}"
)


# ------------------------------------------------------------
# 11. SUPPORTING EVIDENCE
# ------------------------------------------------------------

print_section("6. CALCULATING SUPPORTING EVIDENCE")


# Strong semantic evidence.
lattice["Strong_Semantic_Evidence"] = (
    lattice[
        "Semantic_Similarity_Recovered"
    ]
    >= STRONG_SIMILARITY
)


# Borderline semantic evidence.
lattice["Borderline_Semantic_Evidence"] = (
    (
        lattice[
            "Semantic_Similarity_Recovered"
        ]
        >= BORDERLINE_SIMILARITY
    )
    &
    (
        lattice[
            "Semantic_Similarity_Recovered"
        ]
        < STRONG_SIMILARITY
    )
)


# Supporting evidence for borderline records.

lattice["Strong_Task_Weight_Evidence"] = (
    lattice[
        "Task Capability Weight"
    ]
    >= MIN_TASK_WEIGHT_FOR_BORDERLINE
)


lattice["Strong_Practice_Evidence"] = (
    lattice[
        "Task_Practice_Relevance"
    ]
    >= MIN_PRACTICE_RELEVANCE_FOR_BORDERLINE
)


lattice["Strong_Priority_Evidence"] = (
    lattice[
        "LATTICE_Priority"
    ]
    >= MIN_LATTICE_PRIORITY_FOR_BORDERLINE
)


# Count supporting signals.

lattice["Borderline_Support_Count"] = (
    lattice[
        [
            "Strong_Task_Weight_Evidence",
            "Strong_Practice_Evidence",
            "Strong_Priority_Evidence",
        ]
    ]
    .sum(axis=1)
)


# ------------------------------------------------------------
# 12. FILTER DECISION
# ------------------------------------------------------------

print_section("7. MAKING RELEVANCE DECISION")


def relevance_decision(row):

    similarity = row[
        "Semantic_Similarity_Recovered"
    ]

    support_count = row[
        "Borderline_Support_Count"
    ]

    # --------------------------------------------------------
    # CASE 1: Strong semantic evidence
    # --------------------------------------------------------

    if similarity >= STRONG_SIMILARITY:
        return "KEEP_STRONG"


    # --------------------------------------------------------
    # CASE 2: Borderline semantic evidence
    # --------------------------------------------------------
    # Keep only if at least 2 independent supporting signals
    # confirm that this task is useful for LATTICE.
    # --------------------------------------------------------

    if similarity >= BORDERLINE_SIMILARITY:

        if support_count >= 2:
            return "KEEP_BORDERLINE_SUPPORTED"

        return "REVIEW_BORDERLINE"


    # --------------------------------------------------------
    # CASE 3: Weak semantic evidence
    # --------------------------------------------------------

    if similarity >= 0.40:
        return "REVIEW_LOW"

    return "EXCLUDE_WEAK"


lattice["Relevance_Decision"] = (
    lattice.apply(
        relevance_decision,
        axis=1
    )
)


# ------------------------------------------------------------
# 13. WHY EACH RECORD GOT ITS DECISION
# ------------------------------------------------------------

def decision_reason(row):

    decision = row[
        "Relevance_Decision"
    ]

    similarity = row[
        "Semantic_Similarity_Recovered"
    ]

    support_count = row[
        "Borderline_Support_Count"
    ]

    if decision == "KEEP_STRONG":
        return (
            "Strong semantic task-capability evidence "
            f"(similarity={similarity:.3f})."
        )

    if decision == "KEEP_BORDERLINE_SUPPORTED":
        return (
            "Borderline semantic evidence supported by "
            f"{support_count} additional LATTICE evidence signals."
        )

    if decision == "REVIEW_BORDERLINE":
        return (
            "Borderline semantic relationship without "
            "enough supporting evidence."
        )

    if decision == "REVIEW_LOW":
        return (
            "Low semantic similarity; manual review required."
        )

    return (
        "Very weak semantic task-capability relationship; "
        "excluded from automated LLM generation."
    )


lattice["Relevance_Decision_Reason"] = (
    lattice.apply(
        decision_reason,
        axis=1
    )
)


# ------------------------------------------------------------
# 14. DISTRIBUTION
# ------------------------------------------------------------

print_section("8. FILTER RESULT")


decision_counts = (
    lattice[
        "Relevance_Decision"
    ]
    .value_counts()
)


decision_percent = (
    lattice[
        "Relevance_Decision"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)


for decision, count in decision_counts.items():

    pct = decision_percent[
        decision
    ]

    print(
        f"{decision:28s}: "
        f"{count:>7,} "
        f"({pct:6.2f}%)"
    )


# ------------------------------------------------------------
# 15. BUILD LLM-READY DATASET
# ------------------------------------------------------------

print_section("9. BUILDING LLM-READY DATASET")


keep_mask = lattice[
    "Relevance_Decision"
].isin(
    [
        "KEEP_STRONG",
        "KEEP_BORDERLINE_SUPPORTED",
    ]
)


llm_ready = (
    lattice[
        keep_mask
    ]
    .copy()
)


print(
    f"Original LATTICE records : "
    f"{len(lattice):,}"
)

print(
    f"LLM-ready records        : "
    f"{len(llm_ready):,}"
)

print(
    f"Excluded/review records  : "
    f"{len(lattice) - len(llm_ready):,}"
)


# ------------------------------------------------------------
# 16. LLM INPUT QUALITY CHECK
# ------------------------------------------------------------

print_section("10. LLM INPUT QUALITY CHECK")


llm_input_missing = (
    llm_ready[
        "LLM_Task_Input"
    ]
    .isna()
    .sum()
)


llm_input_empty = (
    llm_ready[
        "LLM_Task_Input"
    ]
    .fillna("")
    .astype(str)
    .str.strip()
    .eq("")
    .sum()
)


print(
    f"Missing LLM input: "
    f"{llm_input_missing:,}"
)

print(
    f"Empty LLM input: "
    f"{llm_input_empty:,}"
)


if llm_input_missing > 0 or llm_input_empty > 0:
    raise ValueError(
        "LLM-ready dataset contains missing/empty LLM inputs."
    )


# ------------------------------------------------------------
# 17. DUPLICATE CHECK
# ------------------------------------------------------------

print_section("11. DUPLICATE CHECK")


duplicate_keys = (
    llm_ready
    .duplicated(
        subset=[
            "O*NET-SOC Code",
            "Task ID",
            "Capability Type",
            "Capability ID",
        ],
        keep=False
    )
    .sum()
)


print(
    f"Duplicate Task → Capability records: "
    f"{duplicate_keys:,}"
)


if duplicate_keys > 0:
    raise ValueError(
        "Duplicate Task → Capability relationships found."
    )


# ------------------------------------------------------------
# 18. LOW-QUALITY REVIEW DATASET
# ------------------------------------------------------------

print_section("12. BUILDING REVIEW DATASET")


review = lattice[
    ~keep_mask
].copy()


print(
    f"Review/excluded records: "
    f"{len(review):,}"
)


# ------------------------------------------------------------
# 19. SHOW PROBLEMATIC EXAMPLES
# ------------------------------------------------------------

print_section("13. LOW-QUALITY EXAMPLES")


example_columns = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task",
    "Capability Name",
    "Capability Type",
    "Semantic_Similarity_Recovered",
    "Task Capability Weight",
    "Task_Practice_Relevance",
    "LATTICE_Priority",
    "Relevance_Decision",
]


example_columns = [
    col
    for col in example_columns
    if col in review.columns
]


if len(review) > 0:

    examples = (
        review
        .sort_values(
            [
                "Semantic_Similarity_Recovered",
                "LATTICE_Priority",
            ],
            ascending=[
                True,
                False,
            ]
        )
        .head(20)
    )


    for _, row in examples.iterrows():

        print("\n---")

        print(
            "Occupation:",
            row.get(
                "Occupation Title",
                row.get(
                    "O*NET-SOC Code",
                    ""
                )
            )
        )

        print(
            "Task:",
            row.get(
                "Task",
                ""
            )
        )

        print(
            "Capability:",
            row.get(
                "Capability Name",
                ""
            )
        )

        print(
            "Semantic Similarity:",
            f"{row['Semantic_Similarity_Recovered']:.4f}"
        )

        print(
            "Task Weight:",
            f"{row['Task Capability Weight']:.4f}"
        )

        print(
            "Practice Relevance:",
            f"{row['Task_Practice_Relevance']:.4f}"
        )

        print(
            "LATTICE Priority:",
            f"{row['LATTICE_Priority']:.4f}"
        )

        print(
            "Decision:",
            row[
                "Relevance_Decision"
            ]
        )


# ------------------------------------------------------------
# 20. CAPABILITY COVERAGE
# ------------------------------------------------------------

print_section("14. CAPABILITY COVERAGE")


original_capabilities = (
    lattice[
        "Capability Name"
    ]
    .nunique()
)


kept_capabilities = (
    llm_ready[
        "Capability Name"
    ]
    .nunique()
)


original_occupations = (
    lattice[
        "O*NET-SOC Code"
    ]
    .nunique()
)


kept_occupations = (
    llm_ready[
        "O*NET-SOC Code"
    ]
    .nunique()
)


print(
    f"Original occupations   : "
    f"{original_occupations:,}"
)

print(
    f"LLM-ready occupations  : "
    f"{kept_occupations:,}"
)

print(
    f"Original capabilities  : "
    f"{original_capabilities:,}"
)

print(
    f"LLM-ready capabilities : "
    f"{kept_capabilities:,}"
)


# ------------------------------------------------------------
# 21. PRACTICE INTENT DISTRIBUTION
# ------------------------------------------------------------

print_section("15. PRACTICE INTENT")


if "Practice_Intent" in llm_ready.columns:

    print(
        llm_ready[
            "Practice_Intent"
        ]
        .value_counts()
        .to_string()
    )


# ------------------------------------------------------------
# 22. CAPABILITY TYPE DISTRIBUTION
# ------------------------------------------------------------

print_section("16. CAPABILITY TYPES")


print(
    llm_ready[
        "Capability Type"
    ]
    .value_counts()
    .to_string()
)


# ------------------------------------------------------------
# 23. FINAL STATISTICS
# ------------------------------------------------------------

print_section("17. FINAL STATISTICS")


if len(llm_ready) > 0:

    print(
        "LLM-ready semantic similarity:"
    )

    print(
        f"  Mean   : "
        f"{llm_ready['Semantic_Similarity_Recovered'].mean():.4f}"
    )

    print(
        f"  Median : "
        f"{llm_ready['Semantic_Similarity_Recovered'].median():.4f}"
    )

    print(
        f"  Min    : "
        f"{llm_ready['Semantic_Similarity_Recovered'].min():.4f}"
    )

    print(
        f"  Max    : "
        f"{llm_ready['Semantic_Similarity_Recovered'].max():.4f}"
    )


# ------------------------------------------------------------
# 24. DROP INTERNAL COLUMN FROM FINAL OUTPUT
# ------------------------------------------------------------

internal_columns = [
    "_relevance_key",
]

llm_ready.drop(
    columns=internal_columns,
    inplace=True,
    errors="ignore"
)

review.drop(
    columns=internal_columns,
    inplace=True,
    errors="ignore"
)


# ------------------------------------------------------------
# 25. SAVE OUTPUTS
# ------------------------------------------------------------

print_section("18. SAVING OUTPUT FILES")


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


llm_ready.to_parquet(
    FILTERED_PARQUET,
    index=False
)

llm_ready.to_csv(
    FILTERED_CSV,
    index=False
)


review.to_parquet(
    REVIEW_PARQUET,
    index=False
)

review.to_csv(
    REVIEW_CSV,
    index=False
)


# ------------------------------------------------------------
# 26. FINAL MESSAGE
# ------------------------------------------------------------

print_section("FILTERING COMPLETE")


print(
    "Original LATTICE:"
)

print(
    LATTICE_PATH
)


print(
    "\nLLM-ready LATTICE:"
)

print(
    FILTERED_PARQUET
)


print(
    "\nLLM-ready CSV:"
)

print(
    FILTERED_CSV
)


print(
    "\nReview dataset:"
)

print(
    REVIEW_PARQUET
)


print(
    "\nReview CSV:"
)

print(
    REVIEW_CSV
)


print(
    "\nIMPORTANT:"
)

print(
    "Original LATTICE and WORKTRACE files were not modified."
)

print(
    "Only strong and evidence-supported borderline"
)

print(
    "Task → Capability relationships were retained"
)

print(
    "for automated LLM generation."
)

print(
    "\nNEXT STAGE:"
)

print(
    "Use forge_lattice_llm_ready.parquet as the"
)

print(
    "controlled input for the LATTICE LLM engine."
)