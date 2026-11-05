import pandas as pd
from pathlib import Path

# ============================================================
# FORGE - ESCO DATASET INSPECTION
# ============================================================

ESCO_DIR = Path(
    "datasets/esco/ESCO_EXTRACTED"
)

print("=" * 70)
print("FORGE - ESCO v1.2.1 DATA INSPECTION")
print("=" * 70)

print(f"\nESCO folder: {ESCO_DIR}")

# ------------------------------------------------------------
# CHECK FOLDER
# ------------------------------------------------------------

if not ESCO_DIR.exists():
    print("\nERROR: ESCO folder not found.")
    print("Expected:")
    print(ESCO_DIR)
    raise SystemExit(1)

# ------------------------------------------------------------
# FIND CSV FILES AUTOMATICALLY
# ------------------------------------------------------------

csv_files = sorted(ESCO_DIR.glob("*.csv"))

print(f"\nCSV files found: {len(csv_files)}")

for file in csv_files:
    print("-", file.name)

# ------------------------------------------------------------
# IMPORTANT FILES
# ------------------------------------------------------------

important_files = [
    "occupations_en.csv",
    "skills_en.csv",
    "occupationSkillRelations_en.csv",
    "skillsHierarchy_en.csv",
]

# ------------------------------------------------------------
# INSPECT IMPORTANT FILES
# ------------------------------------------------------------

for filename in important_files:

    file_path = ESCO_DIR / filename

    print("\n" + "=" * 70)
    print(f"FILE: {filename}")
    print("=" * 70)

    if not file_path.exists():
        print("WARNING: File not found.")
        continue

    try:

        # ESCO CSV files can contain semicolon-separated data.
        # We let pandas detect the delimiter automatically.
        df = pd.read_csv(
            file_path,
            sep=None,
            engine="python",
            encoding="utf-8-sig"
        )

        print(f"\nRows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        print("\nCOLUMN NAMES:")

        for i, column in enumerate(df.columns, start=1):
            print(f"{i}. {column}")

        print("\nDATA TYPES:")

        print(df.dtypes)

        print("\nMISSING VALUES:")

        missing = df.isna().sum()

        for column, count in missing.items():

            percentage = (
                count / len(df) * 100
                if len(df) > 0
                else 0
            )

            print(
                f"{column}: "
                f"{count:,} "
                f"({percentage:.2f}%)"
            )

        print("\nFIRST 3 RECORDS:")

        print(
            df.head(3).to_string(
                index=False
            )
        )

    except Exception as e:

        print("\nERROR reading file:")
        print(e)


# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("ESCO INSPECTION COMPLETE")
print("=" * 70)