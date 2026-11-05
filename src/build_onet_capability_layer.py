import pandas as pd
from pathlib import Path


# ============================================================
# FORGE
# O*NET CAPABILITY LAYER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KB_DIR = PROJECT_ROOT / "datasets" / "onet" / "knowledge_base"

OUTPUT_DIR = KB_DIR


print("=" * 80)
print("FORGE - O*NET CAPABILITY LAYER")
print("=" * 80)


# ============================================================
# 1. CHECK KNOWLEDGE BASE
# ============================================================

if not KB_DIR.exists():
    print("\nERROR: O*NET knowledge base not found.")
    print(KB_DIR)
    raise SystemExit(1)

print("\nKnowledge base found:")
print(KB_DIR)


# ============================================================
# 2. LOAD OCCUPATIONS
# ============================================================

print("\n" + "=" * 80)
print("LOADING OCCUPATIONS")
print("=" * 80)

occupations = pd.read_parquet(
    KB_DIR / "onet_occupations.parquet"
)

occupations = occupations[
    [
        "O*NET-SOC Code",
        "Title",
        "Description"
    ]
].copy()

print(f"Occupations loaded: {len(occupations):,}")


# ============================================================
# 3. LOAD KNOWLEDGE
# ============================================================

print("\n" + "=" * 80)
print("LOADING KNOWLEDGE")
print("=" * 80)

knowledge = pd.read_parquet(
    KB_DIR / "onet_knowledge.parquet"
)

knowledge = knowledge[
    [
        "O*NET-SOC Code",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value"
    ]
].copy()

print(f"Knowledge records: {len(knowledge):,}")


# ============================================================
# 4. LOAD ABILITIES
# ============================================================

print("\n" + "=" * 80)
print("LOADING ABILITIES")
print("=" * 80)

abilities = pd.read_parquet(
    KB_DIR / "onet_abilities.parquet"
)

abilities = abilities[
    [
        "O*NET-SOC Code",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value"
    ]
].copy()

print(f"Ability records: {len(abilities):,}")


# ============================================================
# 5. LOAD TRANSFERABLE SKILLS
# ============================================================

print("\n" + "=" * 80)
print("LOADING TRANSFERABLE SKILLS")
print("=" * 80)

transferable_skills = pd.read_parquet(
    KB_DIR / "onet_transferable_skills.parquet"
)

transferable_skills = transferable_skills[
    [
        "O*NET-SOC Code",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value"
    ]
].copy()

print(
    f"Transferable skill records: "
    f"{len(transferable_skills):,}"
)


# ============================================================
# 6. LOAD WORK ACTIVITIES
# ============================================================

print("\n" + "=" * 80)
print("LOADING WORK ACTIVITIES")
print("=" * 80)

work_activities = pd.read_parquet(
    KB_DIR / "onet_work_activities.parquet"
)

work_activities = work_activities[
    [
        "O*NET-SOC Code",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value"
    ]
].copy()

print(
    f"Work activity records: "
    f"{len(work_activities):,}"
)


# ============================================================
# 7. CLEAN DATA VALUES
# ============================================================

print("\n" + "=" * 80)
print("CLEANING DATA")
print("=" * 80)

for df in [
    knowledge,
    abilities,
    transferable_skills,
    work_activities
]:

    df["Data Value"] = pd.to_numeric(
        df["Data Value"],
        errors="coerce"
    )


# Remove records where measurement is unavailable

knowledge = knowledge.dropna(
    subset=["Data Value"]
)

abilities = abilities.dropna(
    subset=["Data Value"]
)

transferable_skills = transferable_skills.dropna(
    subset=["Data Value"]
)

work_activities = work_activities.dropna(
    subset=["Data Value"]
)


# ============================================================
# 8. CREATE CAPABILITY TABLE
# ============================================================

print("\n" + "=" * 80)
print("BUILDING CAPABILITY TABLE")
print("=" * 80)


def prepare_capability_table(
    df,
    capability_type
):

    result = df.copy()

    result["Capability Type"] = capability_type

    result = result.rename(
        columns={
            "Element ID": "Capability ID",
            "Element Name": "Capability Name",
            "Scale ID": "Measurement ID",
            "Scale Name": "Measurement Name",
            "Data Value": "Capability Value"
        }
    )

    return result[
        [
            "O*NET-SOC Code",
            "Capability Type",
            "Capability ID",
            "Capability Name",
            "Measurement ID",
            "Measurement Name",
            "Capability Value"
        ]
    ]


knowledge_capabilities = prepare_capability_table(
    knowledge,
    "Knowledge"
)

ability_capabilities = prepare_capability_table(
    abilities,
    "Ability"
)

transferable_capabilities = prepare_capability_table(
    transferable_skills,
    "Transferable Skill"
)

work_activity_capabilities = prepare_capability_table(
    work_activities,
    "Work Activity"
)


# Combine all capability types

capabilities = pd.concat(
    [
        knowledge_capabilities,
        ability_capabilities,
        transferable_capabilities,
        work_activity_capabilities
    ],
    ignore_index=True
)


print(
    f"Total capability records: "
    f"{len(capabilities):,}"
)


# ============================================================
# 9. ADD OCCUPATION INFORMATION
# ============================================================

print("\n" + "=" * 80)
print("LINKING CAPABILITIES TO OCCUPATIONS")
print("=" * 80)


capabilities = capabilities.merge(
    occupations[
        [
            "O*NET-SOC Code",
            "Title"
        ]
    ],
    on="O*NET-SOC Code",
    how="left"
)


# Rename occupation title

capabilities = capabilities.rename(
    columns={
        "Title": "Occupation Title"
    }
)


# ============================================================
# 10. REORDER COLUMNS
# ============================================================

capabilities = capabilities[
    [
        "O*NET-SOC Code",
        "Occupation Title",
        "Capability Type",
        "Capability ID",
        "Capability Name",
        "Measurement ID",
        "Measurement Name",
        "Capability Value"
    ]
]


# ============================================================
# 11. REMOVE DUPLICATES
# ============================================================

capabilities = capabilities.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Capability Type",
        "Capability ID",
        "Measurement ID"
    ]
)


# ============================================================
# 12. SAVE MASTER CAPABILITY TABLE
# ============================================================

print("\n" + "=" * 80)
print("SAVING CAPABILITY MASTER")
print("=" * 80)


master_csv = OUTPUT_DIR / "onet_capability_master.csv"
master_parquet = OUTPUT_DIR / "onet_capability_master.parquet"


capabilities.to_csv(
    master_csv,
    index=False,
    encoding="utf-8-sig"
)

capabilities.to_parquet(
    master_parquet,
    index=False
)


print(f"\nSaved:")
print(master_csv)
print(master_parquet)


# ============================================================
# 13. CREATE CAPABILITY SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("CREATING CAPABILITY SUMMARY")
print("=" * 80)


capability_summary = (
    capabilities
    .groupby(
        [
            "O*NET-SOC Code",
            "Occupation Title",
            "Capability Type"
        ],
        as_index=False
    )
    .agg(
        Capability_Count=(
            "Capability ID",
            "nunique"
        ),
        Average_Value=(
            "Capability Value",
            "mean"
        ),
        Maximum_Value=(
            "Capability Value",
            "max"
        )
    )
)


# ============================================================
# 14. SAVE CAPABILITY SUMMARY
# ============================================================

summary_csv = (
    OUTPUT_DIR /
    "onet_occupation_capability_summary.csv"
)

summary_parquet = (
    OUTPUT_DIR /
    "onet_occupation_capability_summary.parquet"
)


capability_summary.to_csv(
    summary_csv,
    index=False,
    encoding="utf-8-sig"
)

capability_summary.to_parquet(
    summary_parquet,
    index=False
)


print(f"\nSaved:")
print(summary_csv)
print(summary_parquet)


# ============================================================
# 15. CREATE CAPABILITY TYPE COUNTS
# ============================================================

print("\n" + "=" * 80)
print("CAPABILITY TYPE COUNTS")
print("=" * 80)


type_counts = (
    capabilities["Capability Type"]
    .value_counts()
)


for capability_type, count in type_counts.items():

    print(
        f"{capability_type:20s}: {count:,}"
    )


# ============================================================
# 16. BASIC VALIDATION
# ============================================================

print("\n" + "=" * 80)
print("VALIDATION")
print("=" * 80)


missing_occupation = capabilities[
    "Occupation Title"
].isna().sum()


missing_capability_name = capabilities[
    "Capability Name"
].isna().sum()


print(
    f"Missing occupation titles : "
    f"{missing_occupation:,}"
)

print(
    f"Missing capability names : "
    f"{missing_capability_name:,}"
)

print(
    f"Unique occupations       : "
    f"{capabilities['O*NET-SOC Code'].nunique():,}"
)

print(
    f"Unique capabilities      : "
    f"{capabilities['Capability ID'].nunique():,}"
)


# ============================================================
# 17. FINAL
# ============================================================

print("\n" + "=" * 80)
print("FORGE O*NET CAPABILITY LAYER READY")
print("=" * 80)

print("""
The capability layer now contains:

Occupation
    ↓
Capability Type
    ↓
Capability
    ↓
Measurement
    ↓
Capability Value

Capability types:
    • Knowledge
    • Ability
    • Transferable Skill
    • Work Activity
""")

print("=" * 80)