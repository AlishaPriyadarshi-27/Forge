from pathlib import Path
import pandas as pd


# ============================================================
# FORGE - BLS OCCUPATION DATASET INSPECTION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BLS_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "bls"
    / "occupation.xlsx"
)

print("=" * 70)
print("FORGE - BLS DATASET INSPECTION")
print("=" * 70)

print(f"\nFile:")
print(BLS_FILE)

print(f"Exists: {BLS_FILE.exists()}")

if not BLS_FILE.exists():
    raise FileNotFoundError(
        f"BLS file not found:\n{BLS_FILE}"
    )


# ------------------------------------------------------------
# 1. Inspect Excel sheets
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("EXCEL SHEETS")
print("=" * 70)

excel = pd.ExcelFile(BLS_FILE)

print(f"\nNumber of sheets: {len(excel.sheet_names)}")

for i, sheet in enumerate(excel.sheet_names, start=1):
    print(f"{i}. {sheet}")


# ------------------------------------------------------------
# 2. Inspect every sheet
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("SHEET DETAILS")
print("=" * 70)

for sheet in excel.sheet_names:

    print("\n" + "-" * 70)
    print(f"SHEET: {sheet}")
    print("-" * 70)

    try:
        df = pd.read_excel(
            BLS_FILE,
            sheet_name=sheet
        )

        print(f"Rows    : {len(df):,}")
        print(f"Columns : {len(df.columns)}")

        print("\nColumns:")

        for i, column in enumerate(df.columns, start=1):
            print(f"{i}. {column}")

        print("\nFirst 5 rows:")

        print(
            df.head(5).to_string(
                index=False
            )
        )

    except Exception as e:
        print(f"Could not read sheet: {e}")


print("\n" + "=" * 70)
print("BLS INSPECTION COMPLETE")
print("=" * 70)