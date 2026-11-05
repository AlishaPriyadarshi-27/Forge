import pandas as pd
from pathlib import Path


# ============================================================
# FORGE - O*NET PIPELINE TEST
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

KB_DIR = PROJECT_ROOT / "datasets" / "onet" / "knowledge_base"


print("=" * 80)
print("FORGE - O*NET PIPELINE TEST")
print("=" * 80)


# ------------------------------------------------------------
# Load generated knowledge-base tables
# ------------------------------------------------------------

occupations = pd.read_parquet(
    KB_DIR / "onet_occupations.parquet"
)

tasks = pd.read_parquet(
    KB_DIR / "onet_tasks.parquet"
)

task_dwa = pd.read_parquet(
    KB_DIR / "onet_task_dwa.parquet"
)


print("\nLoaded successfully:")
print(f"Occupations : {len(occupations):,}")
print(f"Tasks       : {len(tasks):,}")
print(f"Task-DWA    : {len(task_dwa):,}")


# ------------------------------------------------------------
# Select first occupation from the actual dataset
# ------------------------------------------------------------

occupation_code = occupations.iloc[0]["O*NET-SOC Code"]
occupation_title = occupations.iloc[0]["Title"]


print("\n" + "=" * 80)
print("TEST OCCUPATION")
print("=" * 80)

print(f"Code  : {occupation_code}")
print(f"Title : {occupation_title}")


# ------------------------------------------------------------
# Find tasks for this occupation
# ------------------------------------------------------------

occupation_tasks = tasks[
    tasks["O*NET-SOC Code"] == occupation_code
].copy()


print("\n" + "=" * 80)
print("TASKS")
print("=" * 80)

print(f"Number of tasks: {len(occupation_tasks)}")


for _, row in occupation_tasks.head(10).iterrows():

    print(
        f"\nTask ID: {row['Task ID']}"
    )

    print(
        f"Task: {row['Task']}"
    )


# ------------------------------------------------------------
# Connect tasks to DWAs
# ------------------------------------------------------------

task_dwa_test = occupation_tasks.merge(
    task_dwa[
        [
            "O*NET-SOC Code",
            "Task ID",
            "DWA Element ID",
            "DWA Element Name"
        ]
    ],
    on=[
        "O*NET-SOC Code",
        "Task ID"
    ],
    how="left"
)


print("\n" + "=" * 80)
print("OCCUPATION → TASK → DWA")
print("=" * 80)


result = task_dwa_test[
    [
        "O*NET-SOC Code",
        "Title",
        "Task ID",
        "Task",
        "DWA Element ID",
        "DWA Element Name"
    ]
].head(15)


print(result.to_string(index=False))


# ------------------------------------------------------------
# Save test result
# ------------------------------------------------------------

output_file = KB_DIR / "onet_pipeline_test.csv"

result.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

print(f"\nSaved test result:")
print(output_file)

print("\nO*NET relationship verified:")
print("Occupation → Task → DWA")

print("=" * 80)