from pathlib import Path
import pandas as pd


# ============================================================
# FORGE - OCCUPATION INTELLIGENCE LAYER
# O*NET + BLS + O*NET-ESCO Crosswalk + ESCO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ONET_DIR = (
    PROJECT_ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
)

BLS_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "bls"
    / "knowledge_base"
    / "bls_occupation_projections.csv"
)

CROSSWALK_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "crosswalk"
    / "knowledge_base"
    / "onet_esco_crosswalk.csv"
)

ESCO_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "esco"
    / "knowledge_base"
    / "esco_occupation_skill_knowledge_base.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "datasets"
    / "occupation_intelligence"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


print("=" * 75)
print("FORGE - OCCUPATION INTELLIGENCE LAYER")
print("=" * 75)


# ============================================================
# 1. CHECK FILES
# ============================================================

required_files = {
    "O*NET occupations":
        ONET_DIR / "onet_occupations.csv",

    "O*NET tasks":
        ONET_DIR / "onet_tasks.csv",

    "O*NET capability layer":
        ONET_DIR / "onet_capability_master.csv",

    "BLS":
        BLS_FILE,

    "Crosswalk":
        CROSSWALK_FILE,

    "ESCO":
        ESCO_FILE,
}


print("\nChecking required files...")

for name, path in required_files.items():

    exists = path.exists()

    print(f"{name:<25} : {exists}")

    if not exists:
        raise FileNotFoundError(
            f"\nRequired file not found:\n{path}"
        )


# ============================================================
# 2. LOAD O*NET OCCUPATIONS
# ============================================================

print("\nLoading O*NET occupations...")

onet = pd.read_csv(
    ONET_DIR / "onet_occupations.csv",
    dtype=str
)

onet = onet[
    [
        "O*NET-SOC Code",
        "Title",
        "Description"
    ]
].copy()

onet.columns = [
    "onet_soc_code",
    "onet_occupation",
    "onet_description"
]

onet["onet_soc_code"] = (
    onet["onet_soc_code"]
    .astype(str)
    .str.strip()
)

print(
    f"O*NET occupations loaded: {len(onet):,}"
)


# ============================================================
# 3. LOAD BLS
# ============================================================

print("\nLoading BLS...")

bls = pd.read_csv(
    BLS_FILE
)

bls = bls.copy()

bls["occupation_code"] = (
    bls["occupation_code"]
    .astype(str)
    .str.strip()
)

# ------------------------------------------------------------
# Convert BLS code to O*NET-compatible base code
# ------------------------------------------------------------

bls["onet_base_code"] = (
    bls["occupation_code"]
    .str.strip()
)


print(
    f"BLS occupations loaded: {len(bls):,}"
)


# ============================================================
# 4. CREATE O*NET BASE CODE
# ============================================================

# Example:
#
# O*NET  : 11-1011.00
# Base   : 11-1011
#
# This allows matching against BLS:
#
# BLS    : 11-1011

onet["onet_base_code"] = (
    onet["onet_soc_code"]
    .str.split(".")
    .str[0]
)


# ============================================================
# 5. O*NET ↔ BLS MATCH
# ============================================================

print("\nMatching O*NET with BLS...")

onet_bls = onet.merge(
    bls,
    left_on="onet_base_code",
    right_on="onet_base_code",
    how="left",
    suffixes=("", "_bls")
)


onet_bls["bls_match"] = (
    onet_bls["occupation_code"].notna()
)


print(
    f"O*NET records with BLS match: "
    f"{onet_bls['bls_match'].sum():,}"
)

print(
    f"O*NET records without BLS match: "
    f"{(~onet_bls['bls_match']).sum():,}"
)


# ============================================================
# 6. LOAD CROSSWALK
# ============================================================

print("\nLoading O*NET ↔ ESCO crosswalk...")

crosswalk = pd.read_csv(
    CROSSWALK_FILE,
    dtype=str
)

crosswalk["onet_soc_code"] = (
    crosswalk["onet_soc_code"]
    .astype(str)
    .str.strip()
)

crosswalk["esco_occupation_uri"] = (
    crosswalk["esco_occupation_uri"]
    .astype(str)
    .str.strip()
)

print(
    f"Crosswalk records loaded: {len(crosswalk):,}"
)


# ============================================================
# 7. CONNECT O*NET → ESCO
# ============================================================

print("\nConnecting O*NET to ESCO...")

onet_crosswalk = onet_bls.merge(
    crosswalk[
        [
            "onet_soc_code",
            "esco_occupation_uri",
            "esco_occupation",
            "mapping_type"
        ]
    ],
    on="onet_soc_code",
    how="left"
)


onet_crosswalk["esco_match"] = (
    onet_crosswalk["esco_occupation_uri"].notna()
)


print(
    f"Records with ESCO mapping: "
    f"{onet_crosswalk['esco_match'].sum():,}"
)

print(
    f"Records without ESCO mapping: "
    f"{(~onet_crosswalk['esco_match']).sum():,}"
)


# ============================================================
# 8. LOAD ESCO SKILL KNOWLEDGE BASE
# ============================================================

print("\nLoading ESCO skill knowledge base...")

esco = pd.read_csv(
    ESCO_FILE,
    dtype=str
)

print(
    f"ESCO relationship records loaded: "
    f"{len(esco):,}"
)

print("\nESCO columns:")

for column in esco.columns:
    print(f" - {column}")


# ============================================================
# 9. DETECT ESCO OCCUPATION URI COLUMN
# ============================================================

possible_uri_columns = [
    "occupation_uri",
    "occupationUri",
    "Occupation URI",
    "esco_occupation_uri"
]

esco_uri_column = None

for column in possible_uri_columns:

    if column in esco.columns:
        esco_uri_column = column
        break


if esco_uri_column is None:

    raise ValueError(
        "\nCould not identify ESCO occupation URI column.\n"
        "Check the printed ESCO columns above."
    )


print(
    f"\nESCO occupation URI column: "
    f"{esco_uri_column}"
)


# ============================================================
# 10. NORMALIZE ESCO URI
# ============================================================

esco[esco_uri_column] = (
    esco[esco_uri_column]
    .astype(str)
    .str.strip()
)


# ============================================================
# 11. COUNT ESCO SKILLS PER OCCUPATION
# ============================================================

esco_skill_counts = (
    esco
    .groupby(esco_uri_column)
    .size()
    .reset_index(
        name="esco_skill_relationship_count"
    )
)


# ============================================================
# 12. ADD ESCO SKILL COUNT
# ============================================================

onet_crosswalk = onet_crosswalk.merge(
    esco_skill_counts,
    left_on="esco_occupation_uri",
    right_on=esco_uri_column,
    how="left"
)


onet_crosswalk[
    "esco_skill_relationship_count"
] = (
    onet_crosswalk[
        "esco_skill_relationship_count"
    ]
    .fillna(0)
    .astype(int)
)


# ============================================================
# 13. FINAL MATCH STATUS
# ============================================================

onet_crosswalk["intelligence_status"] = "unmatched"

onet_crosswalk.loc[
    (
        onet_crosswalk["bls_match"]
        &
        onet_crosswalk["esco_match"]
    ),
    "intelligence_status"
] = "onet_bls_esco"

onet_crosswalk.loc[
    (
        onet_crosswalk["bls_match"]
        &
        ~onet_crosswalk["esco_match"]
    ),
    "intelligence_status"
] = "onet_bls_only"

onet_crosswalk.loc[
    (
        ~onet_crosswalk["bls_match"]
        &
        onet_crosswalk["esco_match"]
    ),
    "intelligence_status"
] = "onet_esco_only"


# ============================================================
# 14. VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("INTELLIGENCE LAYER VALIDATION")
print("=" * 75)

print("\nStatus distribution:")

print(
    onet_crosswalk[
        "intelligence_status"
    ]
    .value_counts()
    .to_string()
)


print("\nUnique O*NET occupations:")

print(
    onet_crosswalk[
        "onet_soc_code"
    ]
    .nunique()
)


print("\nUnique BLS occupations matched:")

print(
    onet_crosswalk[
        "occupation_code"
    ]
    .dropna()
    .nunique()
)


print("\nUnique ESCO occupations matched:")

print(
    onet_crosswalk[
        "esco_occupation_uri"
    ]
    .dropna()
    .nunique()
)


# ============================================================
# 15. SAVE MAIN OCCUPATION INTELLIGENCE TABLE
# ============================================================

output_file = (
    OUTPUT_DIR
    / "occupation_intelligence_master.csv"
)

onet_crosswalk.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 16. SAVE PARQUET
# ============================================================

output_parquet = (
    OUTPUT_DIR
    / "occupation_intelligence_master.parquet"
)

onet_crosswalk.to_parquet(
    output_parquet,
    index=False
)


# ============================================================
# 17. SAVE UNMATCHED O*NET OCCUPATIONS
# ============================================================

unmatched_bls = onet_crosswalk[
    ~onet_crosswalk["bls_match"]
].copy()

unmatched_bls.to_csv(
    OUTPUT_DIR / "unmatched_onet_bls.csv",
    index=False,
    encoding="utf-8-sig"
)


unmatched_esco = onet_crosswalk[
    ~onet_crosswalk["esco_match"]
].copy()

unmatched_esco.to_csv(
    OUTPUT_DIR / "unmatched_onet_esco.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 18. PREVIEW
# ============================================================

print("\n" + "=" * 75)
print("SAMPLE CONNECTED RECORDS")
print("=" * 75)

preview_columns = [
    "onet_soc_code",
    "onet_occupation",
    "occupation_code",
    "occupation_title",
    "employment_change_percent",
    "occupational_openings_2025_35_annual_avg_thousands",
    "esco_occupation",
    "mapping_type",
    "esco_skill_relationship_count",
    "intelligence_status"
]

print(
    onet_crosswalk[
        preview_columns
    ]
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 19. OUTPUT SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("OUTPUT FILES")
print("=" * 75)

print(
    f"\nMaster CSV:\n{output_file}"
)

print(
    f"\nMaster Parquet:\n{output_parquet}"
)

print(
    f"\nUnmatched O*NET-BLS:\n"
    f"{OUTPUT_DIR / 'unmatched_onet_bls.csv'}"
)

print(
    f"\nUnmatched O*NET-ESCO:\n"
    f"{OUTPUT_DIR / 'unmatched_onet_esco.csv'}"
)

print("\n" + "=" * 75)
print("OCCUPATION INTELLIGENCE LAYER BUILD COMPLETE")
print("=" * 75)