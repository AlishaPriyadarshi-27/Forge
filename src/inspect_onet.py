import pandas as pd
from pathlib import Path

# ============================================================
# FORGE - O*NET DATASET INSPECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONET_ROOT = PROJECT_ROOT / "datasets" / "onet"

print("=" * 80)
print("FORGE - O*NET DATASET INSPECTION")
print("=" * 80)

print("\nSearching for O*NET Excel folder...")

# ------------------------------------------------------------
# Automatically find db_31_0_excel folder
# ------------------------------------------------------------

possible_folders = list(ONET_ROOT.rglob("db_31_0_excel"))

if not possible_folders:
    print("\nERROR: db_31_0_excel folder could not be found.")
    print("\nSearching for Excel files inside datasets/onet...")

    excel_files = list(ONET_ROOT.rglob("*.xlsx"))

    if excel_files:
        print(f"\nFound {len(excel_files)} Excel files:")
        for file in excel_files[:20]:
            print(file)
    else:
        print("No Excel files found inside datasets/onet.")

    raise SystemExit(1)

ONET_DIR = possible_folders[0]

print("\nO*NET folder FOUND:")
print(ONET_DIR)

# ------------------------------------------------------------
# Find all Excel files
# ------------------------------------------------------------

excel_files = sorted(ONET_DIR.glob("*.xlsx"))

print(f"\nTotal Excel files found: {len(excel_files)}")

# ------------------------------------------------------------
# List all files
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("ALL O*NET FILES")
print("=" * 80)

for i, file in enumerate(excel_files, start=1):
    print(f"{i:02d}. {file.name}")

# ------------------------------------------------------------
# Inspect each Excel file
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("O*NET FILE STRUCTURE")
print("=" * 80)

for file in excel_files:

    print("\n" + "-" * 80)
    print(f"FILE: {file.name}")
    print("-" * 80)

    try:
        df = pd.read_excel(file, nrows=5)

        print(f"Rows inspected: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        print("\nColumn names:")

        for column in df.columns:
            print(f"   - {column}")

    except Exception as e:
        print(f"ERROR reading {file.name}")
        print(f"Reason: {e}")

# ------------------------------------------------------------
# Complete
# ------------------------------------------------------------

print("\n" + "=" * 80)
print("O*NET INSPECTION COMPLETE")
print("=" * 80)