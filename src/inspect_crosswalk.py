from pathlib import Path
import pandas as pd

# ============================================================
# FORGE - CROSSWALK DATASET INSPECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CROSSWALK_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "crosswalk"
    / "ONET_(Occupations)_0_updated.csv"
)

print("=" * 70)
print("FORGE - CROSSWALK DATASET INSPECTION")
print("=" * 70)

print(f"\nFile: {CROSSWALK_FILE}")
print(f"Exists: {CROSSWALK_FILE.exists()}")

if not CROSSWALK_FILE.exists():
    raise FileNotFoundError(
        f"Crosswalk file not found: {CROSSWALK_FILE}"
    )

# ------------------------------------------------------------
# Read raw CSV
# ------------------------------------------------------------

df = pd.read_csv(
    CROSSWALK_FILE,
    header=None,
    dtype=str
)

print("\n--- Raw Dataset Shape ---")
print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

# ------------------------------------------------------------
# Show first 30 rows
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FIRST 30 RAW ROWS")
print("=" * 70)

print(
    df.iloc[:30].to_string(
        index=True,
        header=False
    )
)

# ------------------------------------------------------------
# Show rows around the expected mapping section
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ROWS 15 TO 30")
print("=" * 70)

print(
    df.iloc[14:30].to_string(
        index=True,
        header=False
    )
)

# ------------------------------------------------------------
# Check rows for possible mapping headers
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SEARCHING FOR POSSIBLE MAPPING HEADER")
print("=" * 70)

keywords = [
    "O*NET",
    "ESCO",
    "Occupation",
    "Mapping"
]

for keyword in keywords:
    print(f"\nRows containing '{keyword}':")

    matches = df.apply(
        lambda row: row.astype(str)
        .str.contains(keyword, case=False, na=False)
        .any(),
        axis=1
    )

    matching_rows = df[matches]

    if len(matching_rows) > 0:
        print(
            matching_rows.head(20).to_string(
                index=True,
                header=False
            )
        )
    else:
        print("No matching rows found.")

# ------------------------------------------------------------
# Data types
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("RAW DATA TYPES")
print("=" * 70)

print(df.dtypes)

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)