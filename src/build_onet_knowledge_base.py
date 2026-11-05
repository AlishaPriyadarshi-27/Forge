import pandas as pd
from pathlib import Path


# ============================================================
# FORGE
# O*NET 31.0 KNOWLEDGE BASE BUILDER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONET_ROOT = PROJECT_ROOT / "datasets" / "onet"


# ------------------------------------------------------------
# Find O*NET folder automatically
# ------------------------------------------------------------

onet_folders = list(ONET_ROOT.rglob("db_31_0_excel"))

if not onet_folders:
    print("ERROR: O*NET db_31_0_excel folder not found.")
    raise SystemExit(1)

ONET_DIR = onet_folders[0]

print("=" * 80)
print("FORGE - O*NET 31.0 KNOWLEDGE BASE BUILDER")
print("=" * 80)

print(f"\nO*NET directory:")
print(ONET_DIR)


# ------------------------------------------------------------
# Output directory
# ------------------------------------------------------------

OUTPUT_DIR = PROJECT_ROOT / "datasets" / "onet" / "knowledge_base"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"\nOutput directory:")
print(OUTPUT_DIR)


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def load_excel(filename):
    """
    Load an O*NET Excel file.
    """
    path = ONET_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    print(f"\nLoading: {filename}")

    df = pd.read_excel(path)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    return df


# ============================================================
# 1. OCCUPATION DATA
# ============================================================

print("\n" + "=" * 80)
print("1. OCCUPATION DATA")
print("=" * 80)

occupations = load_excel("Occupation Data.xlsx")

occupations = occupations[
    [
        "O*NET-SOC Code",
        "Title",
        "Description"
    ]
].copy()

occupations = occupations.drop_duplicates(
    subset=["O*NET-SOC Code"]
)

print(f"\nUnique occupations: {len(occupations):,}")


# ============================================================
# 2. TASK STATEMENTS
# ============================================================

print("\n" + "=" * 80)
print("2. TASK STATEMENTS")
print("=" * 80)

tasks = load_excel("Task Statements.xlsx")

tasks = tasks[
    [
        "O*NET-SOC Code",
        "Title",
        "Task ID",
        "Task",
        "Task Type",
        "Incumbents Responding",
        "Date",
        "Domain Source"
    ]
].copy()

tasks = tasks.drop_duplicates(
    subset=["O*NET-SOC Code", "Task ID"]
)

print(f"\nUnique occupation-task pairs: {len(tasks):,}")


# ============================================================
# 3. TASK RATINGS
# ============================================================

print("\n" + "=" * 80)
print("3. TASK RATINGS")
print("=" * 80)

task_ratings = load_excel("Task Ratings.xlsx")

task_ratings = task_ratings[
    [
        "O*NET-SOC Code",
        "Title",
        "Task ID",
        "Task",
        "Scale ID",
        "Scale Name",
        "Category",
        "Data Value",
        "Date",
        "Domain Source"
    ]
].copy()

print(f"\nTask rating records: {len(task_ratings):,}")


# ============================================================
# 4. TASK → DETAILED WORK ACTIVITY
# ============================================================

print("\n" + "=" * 80)
print("4. TASK → DWA")
print("=" * 80)

task_dwa = load_excel("Tasks to DWAs.xlsx")

task_dwa = task_dwa[
    [
        "O*NET-SOC Code",
        "Title",
        "Task ID",
        "Task",
        "DWA Element ID",
        "DWA Element Name",
        "Date",
        "Domain Source"
    ]
].copy()

task_dwa = task_dwa.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "DWA Element ID"
    ]
)

print(f"\nTask-DWA relationships: {len(task_dwa):,}")


# ============================================================
# 5. KNOWLEDGE
# ============================================================

print("\n" + "=" * 80)
print("5. KNOWLEDGE")
print("=" * 80)

knowledge = load_excel("Knowledge.xlsx")

knowledge = knowledge[
    [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Date",
        "Domain Source"
    ]
].copy()

print(f"\nKnowledge records: {len(knowledge):,}")


# ============================================================
# 6. ABILITIES
# ============================================================

print("\n" + "=" * 80)
print("6. ABILITIES")
print("=" * 80)

abilities = load_excel("Abilities.xlsx")

abilities = abilities[
    [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Date",
        "Domain Source"
    ]
].copy()

print(f"\nAbility records: {len(abilities):,}")


# ============================================================
# 7. TRANSFERABLE SKILLS
# ============================================================

print("\n" + "=" * 80)
print("7. TRANSFERABLE SKILLS")
print("=" * 80)

transferable_skills = load_excel("Transferable Skills.xlsx")

transferable_skills = transferable_skills[
    [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Date",
        "Domain Source"
    ]
].copy()

print(
    f"\nTransferable skill records: "
    f"{len(transferable_skills):,}"
)


# ============================================================
# 8. WORK ACTIVITIES
# ============================================================

print("\n" + "=" * 80)
print("8. WORK ACTIVITIES")
print("=" * 80)

work_activities = load_excel("Work Activities.xlsx")

work_activities = work_activities[
    [
        "O*NET-SOC Code",
        "Title",
        "Element ID",
        "Element Name",
        "Scale ID",
        "Scale Name",
        "Data Value",
        "Date",
        "Domain Source"
    ]
].copy()

print(f"\nWork activity records: {len(work_activities):,}")


# ============================================================
# 9. SOFTWARE SKILLS
# ============================================================

print("\n" + "=" * 80)
print("9. SOFTWARE SKILLS")
print("=" * 80)

software = load_excel("Software Skills.xlsx")

software = software[
    [
        "O*NET-SOC Code",
        "Title",
        "Workplace Example",
        "Element ID",
        "Element Name",
        "Hot Technology",
        "In Demand"
    ]
].copy()

print(f"\nSoftware skill records: {len(software):,}")


# ============================================================
# 10. SAVE CLEAN TABLES
# ============================================================

print("\n" + "=" * 80)
print("10. SAVING CLEAN TABLES")
print("=" * 80)


tables = {
    "occupations": occupations,
    "tasks": tasks,
    "task_ratings": task_ratings,
    "task_dwa": task_dwa,
    "knowledge": knowledge,
    "abilities": abilities,
    "transferable_skills": transferable_skills,
    "work_activities": work_activities,
    "software_skills": software
}


for name, df in tables.items():

    csv_path = OUTPUT_DIR / f"onet_{name}.csv"
    parquet_path = OUTPUT_DIR / f"onet_{name}.parquet"

    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig"
    )

    df.to_parquet(
        parquet_path,
        index=False
    )

    print(
        f"Saved {name}: "
        f"{len(df):,} rows"
    )


# ============================================================
# 11. CREATE OCCUPATION → TASK MASTER TABLE
# ============================================================

print("\n" + "=" * 80)
print("11. BUILDING OCCUPATION → TASK MASTER")
print("=" * 80)


occupation_tasks = tasks.merge(
    occupations[
        [
            "O*NET-SOC Code",
            "Description"
        ]
    ],
    on="O*NET-SOC Code",
    how="left"
)


occupation_tasks = occupation_tasks[
    [
        "O*NET-SOC Code",
        "Title",
        "Description",
        "Task ID",
        "Task",
        "Task Type",
        "Incumbents Responding",
        "Date",
        "Domain Source"
    ]
]


occupation_tasks.to_csv(
    OUTPUT_DIR / "onet_occupation_task_master.csv",
    index=False,
    encoding="utf-8-sig"
)

occupation_tasks.to_parquet(
    OUTPUT_DIR / "onet_occupation_task_master.parquet",
    index=False
)

print(
    f"\nOccupation-task master rows: "
    f"{len(occupation_tasks):,}"
)


# ============================================================
# 12. CREATE TASK → DWA MASTER
# ============================================================

print("\n" + "=" * 80)
print("12. BUILDING TASK → DWA MASTER")
print("=" * 80)


task_dwa_master = tasks.merge(
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


task_dwa_master.to_csv(
    OUTPUT_DIR / "onet_task_dwa_master.csv",
    index=False,
    encoding="utf-8-sig"
)

task_dwa_master.to_parquet(
    OUTPUT_DIR / "onet_task_dwa_master.parquet",
    index=False
)

print(
    f"\nTask-DWA master rows: "
    f"{len(task_dwa_master):,}"
)


# ============================================================
# 13. SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("O*NET KNOWLEDGE BASE COMPLETE")
print("=" * 80)

print(f"""
Occupations       : {len(occupations):,}
Tasks             : {len(tasks):,}
Task Ratings      : {len(task_ratings):,}
Task-DWA Links    : {len(task_dwa):,}
Knowledge         : {len(knowledge):,}
Abilities         : {len(abilities):,}
Transferable Skill: {len(transferable_skills):,}
Work Activities   : {len(work_activities):,}
Software Skills   : {len(software):,}

Output:
{OUTPUT_DIR}
""")

print("=" * 80)
print("FORGE O*NET DATA LAYER READY")
print("=" * 80)