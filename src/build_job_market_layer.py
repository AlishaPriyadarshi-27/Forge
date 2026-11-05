import os
import re
import html
import pandas as pd


# ============================================================
# FORGE - JOB MARKET LAYER
# ============================================================
# Input:
#   datasets/job_postings/greenhouse/forge_greenhouse_clean.csv
#
# Output:
#   datasets/job_postings/knowledge_base/
#       forge_job_market.csv
#       forge_job_market.parquet
#
# Purpose:
#   1. Load cleaned Greenhouse postings
#   2. Normalize job titles and descriptions
#   3. Parse posting dates
#   4. Define a transparent "recent market" window
#   5. Create data-quality fields
#   6. Preserve raw information for later NLP/embedding stages
#
# IMPORTANT:
# This script does NOT hard-code skill keywords or occupations.
# Skill extraction and occupation matching will be done later
# using NLP/semantic models.
# ============================================================


# ------------------------------------------------------------
# 1. PATHS
# ------------------------------------------------------------

INPUT_FILE = (
    "datasets/job_postings/greenhouse/"
    "forge_greenhouse_clean.csv"
)

OUTPUT_DIR = "datasets/job_postings/knowledge_base"

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "forge_job_market.csv"
)

OUTPUT_PARQUET = os.path.join(
    OUTPUT_DIR,
    "forge_job_market.parquet"
)


# ------------------------------------------------------------
# 2. CONFIGURATION
# ------------------------------------------------------------

# We use posted_at, NOT the partition date.
#
# The downloaded Greenhouse partition contains postings with
# different posted_at dates, including older jobs.
#
# For the first FORGE market layer, use the latest 180 days
# relative to the newest valid posting date in the dataset.

MARKET_WINDOW_DAYS = 180


# ------------------------------------------------------------
# 3. HELPER FUNCTIONS
# ------------------------------------------------------------

def clean_text(value):
    """
    Basic text normalization.

    This is intentionally NOT skill extraction.
    It only makes the text suitable for later NLP processing.
    """

    if pd.isna(value):
        return ""

    value = str(value)

    # Decode HTML entities
    value = html.unescape(value)

    # Remove HTML tags
    value = re.sub(r"<[^>]+>", " ", value)

    # Replace whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_title(value):
    """
    Normalize a job title while preserving its meaning.
    """

    if pd.isna(value):
        return ""

    value = str(value)

    value = html.unescape(value)

    # Normalize whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_locations(value):
    """
    Preserve the original locations while creating
    a normalized representation.
    """

    if pd.isna(value):
        return ""

    value = str(value)

    value = value.strip()

    return value


# ------------------------------------------------------------
# 4. LOAD DATA
# ------------------------------------------------------------

print("=" * 70)
print("FORGE - BUILDING JOB MARKET LAYER")
print("=" * 70)

print("\n[1/8] Checking input file...")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"\nInput file not found:\n{INPUT_FILE}\n"
        "Make sure forge_greenhouse_clean.csv exists."
    )

print("Input found:")
print(INPUT_FILE)


print("\n[2/8] Loading Greenhouse postings...")

df = pd.read_csv(
    INPUT_FILE,
    low_memory=False
)

print(f"Rows loaded: {len(df):,}")
print(f"Columns loaded: {len(df.columns)}")

print("\nColumns:")
for column in df.columns:
    print(f"  - {column}")


# ------------------------------------------------------------
# 5. CHECK REQUIRED COLUMNS
# ------------------------------------------------------------

print("\n[3/8] Validating required columns...")

required_columns = [
    "id",
    "title",
    "apply_url",
    "description",
    "locations",
    "remote",
    "posted_at",
    "updated_at"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(missing_columns)
    )

print("All required columns are present.")


# ------------------------------------------------------------
# 6. DATE PROCESSING
# ------------------------------------------------------------

print("\n[4/8] Processing posting dates...")

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

invalid_posted_dates = df["posted_at"].isna().sum()

print(
    f"Invalid posted_at values: "
    f"{invalid_posted_dates:,}"
)

# Remove records where posting date cannot be established
df = df[df["posted_at"].notna()].copy()

latest_posting_date = df["posted_at"].max()

market_start_date = (
    latest_posting_date -
    pd.Timedelta(days=MARKET_WINDOW_DAYS)
)

print(
    f"Latest posting date: "
    f"{latest_posting_date}"
)

print(
    f"Market window start: "
    f"{market_start_date}"
)

print(
    f"Market window: "
    f"{MARKET_WINDOW_DAYS} days"
)


# ------------------------------------------------------------
# 7. CREATE RECENT MARKET DATASET
# ------------------------------------------------------------

recent_df = df[
    (df["posted_at"] >= market_start_date)
    &
    (df["posted_at"] <= latest_posting_date)
].copy()

print(
    f"\nPostings inside market window: "
    f"{len(recent_df):,}"
)


# ------------------------------------------------------------
# 8. TEXT NORMALIZATION
# ------------------------------------------------------------

print("\n[5/8] Normalizing text fields...")

recent_df["title_normalized"] = (
    recent_df["title"]
    .apply(normalize_title)
)

recent_df["description_normalized"] = (
    recent_df["description"]
    .apply(clean_text)
)

recent_df["locations_normalized"] = (
    recent_df["locations"]
    .apply(normalize_locations)
)


# ------------------------------------------------------------
# 9. DATA QUALITY FEATURES
# ------------------------------------------------------------

print("\n[6/8] Creating data-quality features...")

recent_df["title_length"] = (
    recent_df["title_normalized"]
    .str.len()
)

recent_df["description_length"] = (
    recent_df["description_normalized"]
    .str.len()
)

recent_df["description_word_count"] = (
    recent_df["description_normalized"]
    .str.split()
    .str.len()
)

recent_df["has_description"] = (
    recent_df["description_length"] > 0
)

recent_df["has_location"] = (
    recent_df["locations_normalized"]
    .str.len() > 0
)

recent_df["has_apply_url"] = (
    recent_df["apply_url"]
    .notna()
    &
    (recent_df["apply_url"].astype(str).str.len() > 0)
)


# ------------------------------------------------------------
# 10. MARKET TIME FEATURES
# ------------------------------------------------------------

recent_df["posting_date"] = (
    recent_df["posted_at"]
    .dt.date
)

recent_df["posting_year"] = (
    recent_df["posted_at"]
    .dt.year
)

recent_df["posting_month"] = (
    recent_df["posted_at"]
    .dt.to_period("M")
    .astype(str)
)

recent_df["posting_week"] = (
    recent_df["posted_at"]
    .dt.isocalendar()
    .week
    .astype(int)
)


# ------------------------------------------------------------
# 11. REMOTE NORMALIZATION
# ------------------------------------------------------------

print("\n[7/8] Normalizing remote-work information...")

def normalize_remote(value):

    if pd.isna(value):
        return "unknown"

    if isinstance(value, bool):
        return "remote" if value else "non_remote"

    value = str(value).lower().strip()

    if value in ["true", "1", "yes"]:
        return "remote"

    if value in ["false", "0", "no"]:
        return "non_remote"

    return "unknown"


recent_df["remote_type"] = (
    recent_df["remote"]
    .apply(normalize_remote)
)


# ------------------------------------------------------------
# 12. SOURCE METADATA
# ------------------------------------------------------------

recent_df["market_source"] = "Greenhouse"

recent_df["market_window_days"] = (
    MARKET_WINDOW_DAYS
)

recent_df["market_window_start"] = (
    market_start_date
)

recent_df["market_window_end"] = (
    latest_posting_date
)


# ------------------------------------------------------------
# 13. SELECT OUTPUT COLUMNS
# ------------------------------------------------------------

output_columns = [
    "id",
    "source_slug",

    # Job identity
    "title",
    "title_normalized",

    # Description
    "description",
    "description_normalized",

    # Application
    "apply_url",

    # Organization metadata
    "department",
    "employment_type",

    # Location
    "locations",
    "locations_normalized",
    "remote",
    "remote_type",

    # Dates
    "posted_at",
    "updated_at",
    "posting_date",
    "posting_year",
    "posting_month",
    "posting_week",

    # Text quality
    "title_length",
    "description_length",
    "description_word_count",
    "has_description",
    "has_location",
    "has_apply_url",

    # Market metadata
    "market_source",
    "market_window_days",
    "market_window_start",
    "market_window_end"
]

# Keep only columns that actually exist
output_columns = [
    column
    for column in output_columns
    if column in recent_df.columns
]

market_df = recent_df[output_columns].copy()


# ------------------------------------------------------------
# 14. REMOVE EXACT DUPLICATE POSTINGS
# ------------------------------------------------------------

before_duplicates = len(market_df)

market_df = market_df.drop_duplicates(
    subset=["id"],
    keep="first"
)

duplicates_removed = (
    before_duplicates - len(market_df)
)

print(
    f"\nDuplicate posting IDs removed: "
    f"{duplicates_removed:,}"
)


# ------------------------------------------------------------
# 15. SORT
# ------------------------------------------------------------

market_df = market_df.sort_values(
    by="posted_at",
    ascending=False
).reset_index(drop=True)


# ------------------------------------------------------------
# 16. CREATE OUTPUT DIRECTORY
# ------------------------------------------------------------

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ------------------------------------------------------------
# 17. SAVE CSV
# ------------------------------------------------------------

print("\nSaving CSV...")

market_df.to_csv(
    OUTPUT_CSV,
    index=False
)


# ------------------------------------------------------------
# 18. SAVE PARQUET
# ------------------------------------------------------------

print("Saving Parquet...")

market_df.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


# ------------------------------------------------------------
# 19. VALIDATION
# ------------------------------------------------------------

print("\n[8/8] Validation")
print("=" * 70)

print(
    f"Final postings: "
    f"{len(market_df):,}"
)

print(
    f"Unique posting IDs: "
    f"{market_df['id'].nunique():,}"
)

print(
    f"Unique job titles: "
    f"{market_df['title_normalized'].nunique():,}"
)

print(
    f"Descriptions available: "
    f"{market_df['has_description'].sum():,}"
)

print(
    f"Locations available: "
    f"{market_df['has_location'].sum():,}"
)

print(
    f"Remote postings: "
    f"{(market_df['remote_type'] == 'remote').sum():,}"
)

print(
    f"Non-remote postings: "
    f"{(market_df['remote_type'] == 'non_remote').sum():,}"
)

print(
    f"Unknown remote status: "
    f"{(market_df['remote_type'] == 'unknown').sum():,}"
)

print("\nTop 20 job titles:")

print(
    market_df["title_normalized"]
    .value_counts()
    .head(20)
    .to_string()
)

print("\nPosting counts by month:")

print(
    market_df["posting_month"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nOutput files:")

print(f"CSV:")
print(OUTPUT_CSV)

print(f"\nParquet:")
print(OUTPUT_PARQUET)

print("\n" + "=" * 70)
print("JOB MARKET LAYER COMPLETED SUCCESSFULLY")
print("=" * 70)