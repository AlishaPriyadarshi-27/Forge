from pathlib import Path
import pandas as pd


# ============================================================
# FORGE — LATTICE ENGINE INSPECTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

LATTICE_PATH = (
    BASE_DIR
    / "datasets"
    / "lattice"
    / "forge_lattice_engine.parquet"
)


# ============================================================
# START
# ============================================================

print("=" * 75)
print("FORGE — LATTICE ENGINE INSPECTION")
print("=" * 75)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n[1] Loading LATTICE dataset...")

lattice = pd.read_parquet(
    LATTICE_PATH
)

print(
    f"Shape: {lattice.shape}"
)

print(
    f"Rows: {len(lattice):,}"
)

print(
    f"Columns: {len(lattice.columns)}"
)


# ============================================================
# 2. SCHEMA
# ============================================================

print("\n" + "=" * 75)
print("2. SCHEMA")
print("=" * 75)

for i, column in enumerate(
    lattice.columns,
    start=1
):

    print(
        f"{i:02d}. {column}"
    )


# ============================================================
# 3. REQUIRED COLUMN CHECK
# ============================================================

print("\n" + "=" * 75)
print("3. REQUIRED COLUMN CHECK")
print("=" * 75)


required_columns = [

    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",

    "Capability Name",
    "Capability Type",
    "Capability ID",

    "Task",

    "Skill_Shadow",
    "Skill_Shadow_Percent",

    "Capability_Risk",
    "Capability_Risk_Percent",

    "Capability_Criticality",
    "Market_Job_Count",

    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",

    "LATTICE_Priority",

    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",

    "Task_Practice_Relevance",

    "Practice_Intent",
    "LATTICE_Goal",
    "Assessment_Focus",
    "LLM_Task_Input",
]


missing = [
    column
    for column in required_columns
    if column not in lattice.columns
]


if missing:

    print("STATUS: FAIL")

    print(
        "\nMissing columns:"
    )

    for column in missing:

        print(
            f"  - {column}"
        )

else:

    print(
        "STATUS: PASS"
    )

    print(
        f"All {len(required_columns)} required columns found."
    )


# ============================================================
# 4. MISSING VALUE AUDIT
# ============================================================

print("\n" + "=" * 75)
print("4. MISSING VALUE AUDIT")
print("=" * 75)


audit_columns = [

    "Occupation Title",
    "Capability Name",
    "Capability Type",
    "Capability ID",
    "Task",

    "Skill_Shadow",
    "Capability_Risk",
    "LATTICE_Priority",

    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",

    "Task_Practice_Relevance",

    "LATTICE_Goal",
    "Assessment_Focus",
    "LLM_Task_Input",
]


for column in audit_columns:

    if column in lattice.columns:

        missing_count = (
            lattice[column]
            .isna()
            .sum()
        )

        missing_percent = (
            missing_count
            / len(lattice)
            * 100
        )

        print(
            f"{column:40s}"
            f" Missing: {missing_count:6,}"
            f" ({missing_percent:6.2f}%)"
        )


# ============================================================
# 5. BASIC COUNTS
# ============================================================

print("\n" + "=" * 75)
print("5. DATASET COUNTS")
print("=" * 75)


print(
    f"Unique occupations   : "
    f"{lattice['Occupation Title'].nunique():,}"
)


print(
    f"Unique capabilities  : "
    f"{lattice['Capability Name'].nunique():,}"
)


print(
    f"Unique capability IDs: "
    f"{lattice['Capability ID'].nunique():,}"
)


print(
    f"Unique source tasks  : "
    f"{lattice['Task'].nunique():,}"
)


print(
    f"Unique Task IDs      : "
    f"{lattice['Task ID'].nunique():,}"
)


# ============================================================
# 6. CAPABILITY TYPE DISTRIBUTION
# ============================================================

print("\n" + "=" * 75)
print("6. CAPABILITY TYPE DISTRIBUTION")
print("=" * 75)


print(
    lattice[
        "Capability Type"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 7. PRACTICE INTENT
# ============================================================

print("\n" + "=" * 75)
print("7. PRACTICE INTENT")
print("=" * 75)


print(
    lattice[
        "Practice_Intent"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 8. WORK MODEL
# ============================================================

print("\n" + "=" * 75)
print("8. SOURCE WORK MODEL")
print("=" * 75)


if "Work_Model" in lattice.columns:

    print(
        lattice[
            "Work_Model"
        ]
        .value_counts()
        .to_string()
    )


# ============================================================
# 9. NUMERICAL RANGE CHECK
# ============================================================

print("\n" + "=" * 75)
print("9. NUMERICAL RANGE CHECK")
print("=" * 75)


range_columns = [

    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",

    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",

    "LATTICE_Priority",

    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",

    "Task_Practice_Relevance",
]


for column in range_columns:

    if column not in lattice.columns:

        continue

    values = pd.to_numeric(
        lattice[column],
        errors="coerce"
    )

    minimum = values.min()
    maximum = values.max()

    violations = (
        (values < 0)
        |
        (values > 1)
    ).sum()

    status = (
        "PASS"
        if violations == 0
        else "FAIL"
    )

    print(
        f"{column:40s}"
        f" Min={minimum:.4f}"
        f" Max={maximum:.4f}"
        f" Violations={violations:,}"
        f" [{status}]"
    )


# ============================================================
# 10. AI + HUMAN CONSISTENCY
# ============================================================

print("\n" + "=" * 75)
print("10. AI + HUMAN SHARE CONSISTENCY")
print("=" * 75)


if (
    "AI_Share" in lattice.columns
    and
    "Human_Share" in lattice.columns
):

    deviation = (
        lattice["AI_Share"]
        +
        lattice["Human_Share"]
        -
        1
    ).abs()

    print(
        f"Mean deviation : "
        f"{deviation.mean():.10f}"
    )

    print(
        f"Maximum deviation : "
        f"{deviation.max():.10f}"
    )

    print(
        f"Violations > 0.000001 : "
        f"{(deviation > 0.000001).sum():,}"
    )


# ============================================================
# 11. LATTICE PRIORITY STATISTICS
# ============================================================

print("\n" + "=" * 75)
print("11. LATTICE PRIORITY STATISTICS")
print("=" * 75)


priority_columns = [

    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Capability_Preservation_Pressure",
    "LATTICE_Priority",
    "Task_Practice_Relevance",
]


available_priority_columns = [
    column
    for column in priority_columns
    if column in lattice.columns
]


print(
    lattice[
        available_priority_columns
    ]
    .describe()
    .round(4)
    .to_string()
)


# ============================================================
# 12. TOP PRIORITY CAPABILITIES
# ============================================================

print("\n" + "=" * 75)
print("12. TOP LATTICE CAPABILITIES")
print("=" * 75)


capability_summary = (
    lattice
    .groupby(
        [
            "Occupation Title",
            "Capability Name",
            "Capability Type",
        ],
        as_index=False
    )
    .agg(
        LATTICE_Priority=(
            "LATTICE_Priority",
            "max"
        ),
        Skill_Shadow=(
            "Skill_Shadow",
            "max"
        ),
        Capability_Risk=(
            "Capability_Risk",
            "max"
        ),
        Preservation_Pressure=(
            "Capability_Preservation_Pressure",
            "max"
        ),
        Task_Count=(
            "Task",
            "nunique"
        ),
    )
    .sort_values(
        [
            "LATTICE_Priority",
            "Skill_Shadow",
        ],
        ascending=False
    )
)


print(
    capability_summary
    .head(20)
    .to_string(
        index=False
    )
)


# ============================================================
# 13. TOP PRACTICE TASKS
# ============================================================

print("\n" + "=" * 75)
print("13. TOP PRACTICE TASKS")
print("=" * 75)


task_display_columns = [

    "Occupation Title",
    "Capability Name",
    "Task",

    "Skill_Shadow_Percent",
    "Capability_Risk_Percent",

    "Capability_Preservation_Pressure",
    "LATTICE_Priority",

    "Task_Practice_Relevance",

    "Work_Model",
]


task_display_columns = [
    column
    for column in task_display_columns
    if column in lattice.columns
]


print(
    lattice
    .sort_values(
        [
            "LATTICE_Priority",
            "Task_Practice_Relevance",
        ],
        ascending=False
    )
    [
        task_display_columns
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# ============================================================
# 14. LLM INPUT INSPECTION
# ============================================================

print("\n" + "=" * 75)
print("14. LLM INPUT INSPECTION")
print("=" * 75)


print(
    "\nShowing 10 representative LLM inputs..."
)


# Select records spread across the dataset
# instead of only taking the first 10.

sample_size = min(
    10,
    len(lattice)
)


sample = (
    lattice
    .sort_values(
        "LATTICE_Priority",
        ascending=False
    )
    .head(sample_size)
)


for i, (_, row) in enumerate(
    sample.iterrows(),
    start=1
):

    print(
        "\n" + "-" * 75
    )

    print(
        f"LLM INPUT #{i}"
    )

    print(
        "-" * 75
    )

    print(
        row["LLM_Task_Input"]
    )


# ============================================================
# 15. LLM INPUT QUALITY
# ============================================================

print("\n" + "=" * 75)
print("15. LLM INPUT QUALITY")
print("=" * 75)


if "LLM_Task_Input" in lattice.columns:

    input_lengths = (
        lattice["LLM_Task_Input"]
        .fillna("")
        .astype(str)
        .str.len()
    )

    print(
        f"Minimum length : "
        f"{input_lengths.min():,}"
    )

    print(
        f"Median length  : "
        f"{input_lengths.median():,.0f}"
    )

    print(
        f"Mean length    : "
        f"{input_lengths.mean():,.0f}"
    )

    print(
        f"Maximum length : "
        f"{input_lengths.max():,}"
    )

    empty_inputs = (
        input_lengths == 0
    ).sum()

    print(
        f"Empty inputs   : "
        f"{empty_inputs:,}"
    )


# ============================================================
# 16. DUPLICATE CHECK
# ============================================================

print("\n" + "=" * 75)
print("16. DUPLICATE CHECK")
print("=" * 75)


duplicate_keys = [

    "Occupation Title",
    "Capability Name",
    "Capability Type",
    "Capability ID",
    "Task",
]


duplicates = (
    lattice
    .duplicated(
        subset=duplicate_keys,
        keep=False
    )
)


print(
    f"Duplicate rows: "
    f"{duplicates.sum():,}"
)


if duplicates.sum() == 0:

    print(
        "STATUS: PASS"
    )

else:

    print(
        "STATUS: REVIEW"
    )


# ============================================================
# 17. CAPABILITY → TASK COVERAGE
# ============================================================

print("\n" + "=" * 75)
print("17. CAPABILITY → TASK COVERAGE")
print("=" * 75)


coverage = (
    lattice
    .groupby(
        [
            "Occupation Title",
            "Capability Name",
        ]
    )
    .agg(
        Task_Count=(
            "Task",
            "nunique"
        )
    )
)


print(
    f"Capability groups: "
    f"{len(coverage):,}"
)


print(
    f"Groups with >=3 tasks: "
    f"{(coverage['Task_Count'] >= 3).sum():,}"
)


print(
    f"Groups with 1 task: "
    f"{(coverage['Task_Count'] == 1).sum():,}"
)


# ============================================================
# 18. REPRESENTATIVE RECORDS
# ============================================================

print("\n" + "=" * 75)
print("18. REPRESENTATIVE LATTICE RECORDS")
print("=" * 75)


representative_columns = [

    "Occupation Title",
    "Capability Name",
    "Capability Type",
    "Task",

    "Skill_Shadow_Percent",
    "Capability_Risk_Percent",

    "Capability_Preservation_Pressure",
    "LATTICE_Priority",

    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",

    "Task_Practice_Relevance",

    "Practice_Intent",
]


representative_columns = [
    column
    for column in representative_columns
    if column in lattice.columns
]


print(
    lattice[
        representative_columns
    ]
    .sample(
        n=min(10, len(lattice)),
        random_state=42
    )
    .to_string(
        index=False
    )
)


# ============================================================
# 19. FINAL INSPECTION SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("19. FINAL LATTICE INSPECTION SUMMARY")
print("=" * 75)


print(
    f"Rows                  : "
    f"{len(lattice):,}"
)


print(
    f"Columns               : "
    f"{len(lattice.columns)}"
)


print(
    f"Occupations           : "
    f"{lattice['Occupation Title'].nunique():,}"
)


print(
    f"Capabilities          : "
    f"{lattice['Capability Name'].nunique():,}"
)


print(
    f"Source Tasks          : "
    f"{lattice['Task'].nunique():,}"
)


print(
    f"Task IDs              : "
    f"{lattice['Task ID'].nunique():,}"
)


print(
    "\nLATTICE ENGINE INSPECTION COMPLETE"
)


print(
    "=" * 75
)