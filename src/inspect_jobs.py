import pandas as pd

# ============================================================
# FORGE - GREENHOUSE JOB DATASET INSPECTION
# ============================================================

file_path = (
    "datasets/job_postings/greenhouse/"
    "e365621720174a7c9a735ce27e97e681-0.parquet"
)

print("Loading FORGE job dataset...")
print("Please wait...\n")

# ------------------------------------------------------------
# 1. LOAD DATASET
# ------------------------------------------------------------

df = pd.read_parquet(file_path)

print("=" * 60)
print("1. BASIC INFORMATION")
print("=" * 60)

print(f"Total jobs: {len(df):,}")
print(f"Total columns: {len(df.columns)}")


# ------------------------------------------------------------
# 2. COLUMN NAMES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("2. COLUMN NAMES")
print("=" * 60)

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# ------------------------------------------------------------
# 3. MISSING VALUES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("3. MISSING VALUES")
print("=" * 60)

missing = df.isna().sum()

for column, count in missing.items():
    percentage = (count / len(df)) * 100
    print(
        f"{column:20} "
        f"{count:8,} missing "
        f"({percentage:.2f}%)"
    )


# ------------------------------------------------------------
# 4. SAMPLE JOB TITLES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("4. SAMPLE JOB TITLES")
print("=" * 60)

for title in df["title"].dropna().head(30):
    print("-", title)


# ------------------------------------------------------------
# 5. SAMPLE LOCATIONS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("5. SAMPLE LOCATIONS")
print("=" * 60)

for location in df["locations"].dropna().head(30):
    print("-", location)


# ------------------------------------------------------------
# 6. REMOTE VALUES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("6. REMOTE VALUES")
print("=" * 60)

print(df["remote"].value_counts(dropna=False))


# ------------------------------------------------------------
# 7. EMPLOYMENT TYPES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("7. EMPLOYMENT TYPES")
print("=" * 60)

print(df["employment_type"].value_counts(dropna=False))


# ------------------------------------------------------------
# 8. POSTING DATE RANGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("8. POSTING DATE RANGE")
print("=" * 60)

# utc=True handles mixed timezones safely
dates = pd.to_datetime(
    df["posted_at"],
    errors="coerce",
    utc=True
)

print("Invalid/missing dates:", dates.isna().sum())
print("Earliest posting:", dates.min())
print("Latest posting:", dates.max())


# ------------------------------------------------------------
# 9. UPDATED DATE RANGE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("9. UPDATED DATE RANGE")
print("=" * 60)

updated_dates = pd.to_datetime(
    df["updated_at"],
    errors="coerce",
    utc=True
)

print("Invalid/missing updated dates:", updated_dates.isna().sum())
print("Earliest update:", updated_dates.min())
print("Latest update:", updated_dates.max())


# ------------------------------------------------------------
# 10. DEPARTMENTS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("10. DEPARTMENTS")
print("=" * 60)

print(
    df["department"]
    .value_counts(dropna=False)
    .head(30)
)


# ------------------------------------------------------------
# 11. SALARY INFORMATION
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("11. SALARY INFORMATION")
print("=" * 60)

salary_count = df["salary_min"].notna().sum()

print("Jobs with salary:", f"{salary_count:,}")
print(
    "Jobs without salary:",
    f"{df['salary_min'].isna().sum():,}"
)


# ------------------------------------------------------------
# 12. DESCRIPTION LENGTH
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("12. JOB DESCRIPTION INFORMATION")
print("=" * 60)

description_length = (
    df["description_html"]
    .fillna("")
    .astype(str)
    .str.len()
)

print(
    "Average description length:",
    f"{description_length.mean():,.0f} characters"
)

print(
    "Shortest description:",
    f"{description_length.min():,} characters"
)

print(
    "Longest description:",
    f"{description_length.max():,} characters"
)


# ------------------------------------------------------------
# 13. DUPLICATES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("13. DUPLICATE CHECK")
print("=" * 60)

print("Duplicate job IDs:", df["id"].duplicated().sum())
print("Duplicate apply URLs:", df["apply_url"].duplicated().sum())


# ------------------------------------------------------------
# 14. SAMPLE COMPLETE RECORD
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("14. SAMPLE COMPLETE JOB")
print("=" * 60)

sample = df.iloc[0]

print("\nJOB ID:")
print(sample["id"])

print("\nTITLE:")
print(sample["title"])

print("\nLOCATION:")
print(sample["locations"])

print("\nREMOTE:")
print(sample["remote"])

print("\nPOSTED AT:")
print(sample["posted_at"])

print("\nUPDATED AT:")
print(sample["updated_at"])

print("\nDESCRIPTION PREVIEW:")
print(str(sample["description_html"])[:1000])


# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FORGE DATASET INSPECTION COMPLETE")
print("=" * 60)