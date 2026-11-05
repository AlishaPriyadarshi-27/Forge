from pathlib import Path
import pandas as pd


# ============================================================
# FORGE - BLS KNOWLEDGE BASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "bls"
    / "occupation.xlsx"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "datasets"
    / "bls"
    / "knowledge_base"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("FORGE - BLS KNOWLEDGE BASE BUILD")
print("=" * 70)

print(f"\nInput file:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"BLS file not found:\n{INPUT_FILE}"
    )

print("Input file found: YES")


# ============================================================
# 1. READ TABLE 1.2
# ============================================================

print("\nReading BLS Table 1.2...")

raw = pd.read_excel(
    INPUT_FILE,
    sheet_name="Table 1.2",
    header=None,
    dtype=str
)

print(f"Raw rows    : {len(raw):,}")
print(f"Raw columns : {len(raw.columns)}")


# ============================================================
# 2. FIND ACTUAL HEADER
# ============================================================

header_row = None

for i in range(len(raw)):
    row_text = " ".join(
        raw.iloc[i].fillna("").astype(str).tolist()
    ).lower()

    if (
        "national employment matrix title" in row_text
        and "employment, 2025" in row_text
        and "employment, 2035" in row_text
    ):
        header_row = i
        break


if header_row is None:
    raise ValueError(
        "Could not find the Table 1.2 header row."
    )

print(f"\nHeader row found at: {header_row}")


# ============================================================
# 3. CREATE CLEAN TABLE
# ============================================================

df = raw.iloc[header_row + 1:].copy()

df = df.iloc[:, :17]

df.columns = [
    "occupation_title",
    "occupation_code",
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
    "ooh_content",
    "ooh_content_link"
]


# ============================================================
# 4. CLEAN TEXT
# ============================================================

for column in [
    "occupation_title",
    "occupation_code",
    "occupation_type",
    "typical_education",
    "related_work_experience",
    "typical_on_the_job_training",
    "ooh_content",
    "ooh_content_link"
]:
    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# ============================================================
# 5. REMOVE EMPTY / NON-OCCUPATION ROWS
# ============================================================

before = len(df)

df = df[
    (df["occupation_code"] != "")
    &
    (df["occupation_title"] != "")
].copy()

removed_empty = before - len(df)

print(
    f"\nEmpty rows removed: {removed_empty:,}"
)


# ============================================================
# 6. KEEP OCCUPATION RECORDS
# ============================================================

# BLS contains both Summary and Line item records.
# FORGE primarily needs actual occupation-level records.

before = len(df)

df = df[
    df["occupation_type"].str.lower() == "line item"
].copy()

removed_non_occupation = before - len(df)

print(
    f"Non-line-item records removed: "
    f"{removed_non_occupation:,}"
)


# ============================================================
# 7. CONVERT NUMERIC FIELDS
# ============================================================

numeric_columns = [
    "employment_2025_thousands",
    "employment_2035_thousands",
    "employment_distribution_2025_percent",
    "employment_distribution_2035_percent",
    "employment_change_thousands",
    "employment_change_percent",
    "percent_self_employed_2025",
    "occupational_openings_2025_35_annual_avg_thousands",
    "median_annual_wage_2025"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 8. DERIVED FIELDS
# ============================================================

df["employment_change_absolute_thousands"] = (
    df["employment_2035_thousands"]
    - df["employment_2025_thousands"]
)

df["projected_growth_direction"] = (
    df["employment_change_thousands"]
    .apply(
        lambda x:
        "growth"
        if pd.notna(x) and x > 0
        else (
            "decline"
            if pd.notna(x) and x < 0
            else "stable"
        )
    )
)

df["has_positive_projected_growth"] = (
    df["employment_change_percent"] > 0
)

df["has_occupational_openings_data"] = (
    df[
        "occupational_openings_2025_35_annual_avg_thousands"
    ].notna()
)


# ============================================================
# 9. SOURCE METADATA
# ============================================================

df["data_source"] = "U.S. Bureau of Labor Statistics"
df["projection_period"] = "2025-2035"
df["base_year"] = 2025
df["projection_year"] = 2035


# ============================================================
# 10. REMOVE DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates(
    subset=["occupation_code"]
).reset_index(drop=True)

duplicates_removed = before - len(df)

print(
    f"Duplicate occupation codes removed: "
    f"{duplicates_removed:,}"
)


# ============================================================
# 11. VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

print(
    f"\nFinal occupation records : {len(df):,}"
)

print(
    f"Unique occupation codes  : "
    f"{df['occupation_code'].nunique():,}"
)

print(
    f"Unique occupation titles : "
    f"{df['occupation_title'].nunique():,}"
)


print("\nProjected growth direction:")

print(
    df["projected_growth_direction"]
    .value_counts()
    .to_string()
)


print("\nMissing values:")

print(
    df[
        [
            "occupation_title",
            "occupation_code",
            "employment_2025_thousands",
            "employment_2035_thousands",
            "employment_change_percent",
            "occupational_openings_2025_35_annual_avg_thousands",
            "median_annual_wage_2025"
        ]
    ]
    .isna()
    .sum()
    .to_string()
)


# ============================================================
# 12. SAVE CSV
# ============================================================

output_csv = (
    OUTPUT_DIR
    / "bls_occupation_projections.csv"
)

df.to_csv(
    output_csv,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 13. SAVE PARQUET
# ============================================================

output_parquet = (
    OUTPUT_DIR
    / "bls_occupation_projections.parquet"
)

df.to_parquet(
    output_parquet,
    index=False
)


# ============================================================
# 14. PREVIEW
# ============================================================

print("\n" + "=" * 70)
print("SAMPLE RECORDS")
print("=" * 70)

print(
    df[
        [
            "occupation_code",
            "occupation_title",
            "employment_2025_thousands",
            "employment_2035_thousands",
            "employment_change_percent",
            "occupational_openings_2025_35_annual_avg_thousands",
            "median_annual_wage_2025"
        ]
    ]
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 15. OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("OUTPUT FILES")
print("=" * 70)

print(f"\nCSV:")
print(output_csv)

print(f"\nParquet:")
print(output_parquet)

print("\n" + "=" * 70)
print("BLS KNOWLEDGE BASE BUILD COMPLETE")
print("=" * 70)