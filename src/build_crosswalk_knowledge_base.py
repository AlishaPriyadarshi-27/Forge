from pathlib import Path
import pandas as pd


# ============================================================
# FORGE - O*NET ↔ ESCO CROSSWALK KNOWLEDGE BASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "crosswalk"
    / "ONET_(Occupations)_0_updated.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "datasets"
    / "crosswalk"
    / "knowledge_base"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("FORGE - CROSSWALK KNOWLEDGE BASE BUILD")
print("=" * 70)


# ------------------------------------------------------------
# 1. Check input
# ------------------------------------------------------------

print(f"\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Crosswalk file not found:\n{INPUT_FILE}"
    )

print("Input file found: YES")


# ------------------------------------------------------------
# 2. Read raw CSV
# ------------------------------------------------------------

print("\nReading raw CSV...")

raw = pd.read_csv(
    INPUT_FILE,
    header=None,
    dtype=str,
    keep_default_na=False
)

print(f"Raw rows    : {len(raw):,}")
print(f"Raw columns : {len(raw.columns)}")


# ------------------------------------------------------------
# 3. Identify actual mapping table
# ------------------------------------------------------------

# Based on the inspected file, actual mappings start after
# the metadata section. We locate the first row containing
# an O*NET-SOC code rather than relying only on a fixed row.

onet_code_pattern = r"^\d{2}-\d{4}(?:\.\d{2})?$"

candidate_mask = raw[0].str.strip().str.match(
    onet_code_pattern,
    na=False
)

mapping_start = candidate_mask.idxmax()

if not candidate_mask.any():
    raise ValueError(
        "Could not identify the start of the O*NET-ESCO mapping table."
    )

print(f"\nMapping table starts at raw row: {mapping_start}")


# ------------------------------------------------------------
# 4. Keep mapping rows
# ------------------------------------------------------------

mapping = raw.iloc[mapping_start:].copy()

mapping = mapping.iloc[:, :7]

mapping.columns = [
    "onet_soc_code",
    "onet_occupation",
    "onet_description",
    "esco_occupation_uri",
    "esco_occupation",
    "esco_description",
    "mapping_type"
]


# ------------------------------------------------------------
# 5. Remove completely empty rows
# ------------------------------------------------------------

mapping = mapping[
    mapping["onet_soc_code"].str.strip() != ""
].copy()


# ------------------------------------------------------------
# 6. Clean whitespace
# ------------------------------------------------------------

for column in mapping.columns:
    mapping[column] = (
        mapping[column]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# ------------------------------------------------------------
# 7. Normalize mapping type
# ------------------------------------------------------------

mapping["mapping_type"] = (
    mapping["mapping_type"]
    .str.strip()
    .str.lower()
)


# ------------------------------------------------------------
# 8. Remove invalid O*NET codes
# ------------------------------------------------------------

before_invalid = len(mapping)

mapping = mapping[
    mapping["onet_soc_code"].str.match(
        onet_code_pattern,
        na=False
    )
].copy()

removed_invalid = before_invalid - len(mapping)

print(f"\nInvalid O*NET rows removed: {removed_invalid:,}")


# ------------------------------------------------------------
# 9. Remove duplicate mappings
# ------------------------------------------------------------

before_duplicates = len(mapping)

mapping = mapping.drop_duplicates(
    subset=[
        "onet_soc_code",
        "esco_occupation_uri",
        "mapping_type"
    ]
).reset_index(drop=True)

duplicates_removed = before_duplicates - len(mapping)

print(f"Duplicate mappings removed: {duplicates_removed:,}")


# ------------------------------------------------------------
# 10. Add useful derived fields
# ------------------------------------------------------------

mapping["onet_code_prefix"] = (
    mapping["onet_soc_code"]
    .str.split(".")
    .str[0]
)

mapping["has_esco_uri"] = (
    mapping["esco_occupation_uri"]
    .str.startswith("http")
)

mapping["is_exact_match"] = (
    mapping["mapping_type"] == "exactmatch"
)

mapping["is_close_match"] = (
    mapping["mapping_type"] == "closematch"
)

mapping["is_broad_match"] = (
    mapping["mapping_type"] == "broadmatch"
)


# ------------------------------------------------------------
# 11. Add source metadata
# ------------------------------------------------------------

mapping["crosswalk_source"] = "ESCO-O*NET Crosswalk"
mapping["crosswalk_version"] = "1"
mapping["crosswalk_version_date"] = "Sep-22"
mapping["onet_source_version"] = "O*NET-SOC 2019"
mapping["esco_source_version"] = "ESCO"


# ------------------------------------------------------------
# 12. Validation
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

print(f"\nFinal mapping records : {len(mapping):,}")
print(
    f"Unique O*NET occupations : "
    f"{mapping['onet_soc_code'].nunique():,}"
)
print(
    f"Unique ESCO occupations : "
    f"{mapping['esco_occupation_uri'].nunique():,}"
)

print("\nMapping types:")

print(
    mapping["mapping_type"]
    .value_counts(dropna=False)
    .to_string()
)


print("\nMissing values:")

print(
    mapping[
        [
            "onet_soc_code",
            "onet_occupation",
            "esco_occupation_uri",
            "esco_occupation",
            "mapping_type"
        ]
    ]
    .isna()
    .sum()
    .to_string()
)


# ------------------------------------------------------------
# 13. Save CSV
# ------------------------------------------------------------

output_csv = (
    OUTPUT_DIR
    / "onet_esco_crosswalk.csv"
)

mapping.to_csv(
    output_csv,
    index=False,
    encoding="utf-8-sig"
)


# ------------------------------------------------------------
# 14. Save Parquet
# ------------------------------------------------------------

output_parquet = (
    OUTPUT_DIR
    / "onet_esco_crosswalk.parquet"
)

mapping.to_parquet(
    output_parquet,
    index=False
)


# ------------------------------------------------------------
# 15. Preview
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SAMPLE RECORDS")
print("=" * 70)

print(
    mapping[
        [
            "onet_soc_code",
            "onet_occupation",
            "esco_occupation",
            "mapping_type"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ------------------------------------------------------------
# 16. Final output
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print(f"\nCSV:")
print(output_csv)

print(f"\nParquet:")
print(output_parquet)

print("\n" + "=" * 70)
print("CROSSWALK KNOWLEDGE BASE BUILD COMPLETE")
print("=" * 70)