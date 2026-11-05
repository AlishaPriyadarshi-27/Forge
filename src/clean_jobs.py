import pandas as pd
import ast
import re

# ============================================================
# FORGE - CLEAN GREENHOUSE JOB DATA
# ============================================================

INPUT_FILE = (
    "datasets/job_postings/greenhouse/"
    "e365621720174a7c9a735ce27e97e681-0.parquet"
)

OUTPUT_FILE = (
    "datasets/job_postings/greenhouse/"
    "forge_greenhouse_clean.csv"
)

print("Loading Greenhouse dataset...")
df = pd.read_parquet(INPUT_FILE)

print(f"Raw jobs: {len(df):,}")

# ------------------------------------------------------------
# 1. SELECT USEFUL COLUMNS
# ------------------------------------------------------------

columns_to_keep = [
    "id",
    "source_slug",
    "title",
    "apply_url",
    "description_html",
    "department",
    "locations",
    "remote",
    "posted_at",
    "updated_at"
]

df = df[columns_to_keep].copy()


# ------------------------------------------------------------
# 2. CONVERT DATES
# ------------------------------------------------------------

df["posted_at"] = pd.to_datetime(
    df["posted_at"],
    errors="coerce",
    utc=True
)

df["updated_at"] = pd.to_datetime(
    df["updated_at"],
    errors="coerce",
    utc=True
)


# ------------------------------------------------------------
# 3. REMOVE INVALID RECORDS
# ------------------------------------------------------------

df = df.dropna(
    subset=[
        "id",
        "title",
        "description_html",
        "locations",
        "posted_at"
    ]
)


# ------------------------------------------------------------
# 4. REMOVE DUPLICATE JOB IDs
# ------------------------------------------------------------

before = len(df)

df = df.drop_duplicates(
    subset=["id"],
    keep="first"
)

print(
    f"Removed duplicate IDs: "
    f"{before - len(df):,}"
)


# ------------------------------------------------------------
# 5. CLEAN HTML FROM JOB DESCRIPTIONS
# ------------------------------------------------------------

def clean_html(text):
    text = str(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


df["description"] = df["description_html"].apply(clean_html)


# ------------------------------------------------------------
# 6. CONVERT LOCATION TO TEXT
# ------------------------------------------------------------

def clean_location(value):
    try:
        if isinstance(value, list):
            return " | ".join(str(x).strip() for x in value)

        return str(value).strip()

    except Exception:
        return str(value)


df["locations"] = df["locations"].apply(clean_location)


# ------------------------------------------------------------
# 7. NORMALIZE TITLE
# ------------------------------------------------------------

df["title"] = (
    df["title"]
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------
# 8. REMOVE VERY SHORT DESCRIPTIONS
# ------------------------------------------------------------

df = df[
    df["description"].str.len() >= 100
].copy()


# ------------------------------------------------------------
# 9. SORT BY POSTING DATE
# ------------------------------------------------------------

df = df.sort_values(
    "posted_at",
    ascending=False
)


# ------------------------------------------------------------
# 10. SAVE CLEAN DATA
# ------------------------------------------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\n" + "=" * 60)
print("FORGE CLEANING COMPLETE")
print("=" * 60)

print(f"Clean jobs: {len(df):,}")
print(f"Output file: {OUTPUT_FILE}")

print("\nDate range:")
print("Latest:", df["posted_at"].max())
print("Earliest:", df["posted_at"].min())

print("\nColumns:")
for column in df.columns:
    print("-", column)