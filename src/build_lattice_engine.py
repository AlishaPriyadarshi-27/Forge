from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — LATTICE ENGINE
# Future-Oriented Workforce Reconfiguration & Growth Engine
#
# Purpose:
# Identify capabilities that need preservation-oriented practice
# and connect them to real work tasks from WORKTRACE and WORKFOLD.
# ============================================================


BASE_DIR = Path(__file__).resolve().parents[1]


# ============================================================
# INPUT FILES
# ============================================================

SKILL_SHADOW_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)

WORKTRACE_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

WORKFOLD_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_workfold_v8.parquet"
)


# ============================================================
# OUTPUT FILES
# ============================================================

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "lattice"
)

OUTPUT_PARQUET = (
    OUTPUT_DIR
    / "forge_lattice_engine.parquet"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "forge_lattice_engine.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

# Select the highest-priority capabilities within
# each occupation.
TOP_CAPABILITIES_PER_OCCUPATION = 5

# Select the strongest real-world source tasks for
# each occupation + capability.
TOP_TASKS_PER_CAPABILITY = 3


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def require_columns(df, required, dataset_name):

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"\n{dataset_name} is missing required columns:\n"
            f"{missing}\n\n"
            f"Available columns:\n"
            f"{list(df.columns)}"
        )


def convert_numeric(df, columns):

    for column in columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def minmax(series):

    values = pd.to_numeric(
        series,
        errors="coerce"
    )

    if values.notna().sum() == 0:

        return pd.Series(
            0.0,
            index=series.index
        )

    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:

        return pd.Series(
            0.0,
            index=series.index
        )

    return (
        (values - minimum)
        / (maximum - minimum)
    ).clip(0, 1)


# ============================================================
# START
# ============================================================

print("=" * 75)
print("FORGE — LATTICE ENGINE")
print("=" * 75)


# ============================================================
# 1. LOAD SKILL SHADOW
# ============================================================

print("\n[1] Loading SKILL SHADOW...")

skill_shadow = pd.read_parquet(
    SKILL_SHADOW_PATH
)

print(
    f"Shape: {skill_shadow.shape}"
)

print(
    f"Columns: {len(skill_shadow.columns)}"
)


require_columns(
    skill_shadow,
    [
        "Occupation Title",
        "Capability Name",
        "Capability Type",
        "Capability ID",
        "Skill_Shadow",
        "Skill_Shadow_Percent",
        "Capability_Risk",
        "Capability_Risk_Percent",
        "Capability_Criticality",
        "Market_Job_Count",
    ],
    "SKILL SHADOW"
)


# ============================================================
# 2. LOAD WORKTRACE
# ============================================================

print("\n[2] Loading WORKTRACE...")

worktrace = pd.read_parquet(
    WORKTRACE_PATH
)

print(
    f"Shape: {worktrace.shape}"
)

print(
    f"Columns: {len(worktrace.columns)}"
)


require_columns(
    worktrace,
    [
        "Occupation Title",
        "Task ID",
        "Task",
        "Capability Name",
        "Capability Type",
        "Capability ID",
        "Task Capability Weight",
    ],
    "WORKTRACE"
)


# ============================================================
# 3. LOAD WORKFOLD V8
# ============================================================

print("\n[3] Loading WORKFOLD V8...")

workfold = pd.read_parquet(
    WORKFOLD_PATH
)

print(
    f"Shape: {workfold.shape}"
)

print(
    f"Columns: {len(workfold.columns)}"
)


require_columns(
    workfold,
    [
        "Occupation Title",
        "Task",
        "Task_AI_Suitability",
        "AI_Share",
        "Human_Share",
        "Preservation_Pressure",
        "Human_Preservation_Floor",
        "AI_Ceiling",
        "Work_Model",
    ],
    "WORKFOLD V8"
)


# ============================================================
# 4. PREPARE NUMERIC DATA
# ============================================================

print("\n[4] Preparing numerical evidence...")


skill_shadow = convert_numeric(
    skill_shadow,
    [
        "Skill_Shadow",
        "Skill_Shadow_Percent",
        "Capability_Risk",
        "Capability_Risk_Percent",
        "Capability_Criticality",
        "Market_Job_Count",
    ]
)


worktrace = convert_numeric(
    worktrace,
    [
        "Task Capability Weight",
        "Semantic Similarity",
        "Occupation Capability Value",
        "market_job_count",
        "employment_change_percent",
    ]
)


workfold = convert_numeric(
    workfold,
    [
        "Task_AI_Suitability",
        "AI_Share",
        "Human_Share",
        "Preservation_Pressure",
        "Human_Preservation_Floor",
        "AI_Ceiling",
    ]
)


# ============================================================
# 5. CAPABILITY PRESERVATION PRESSURE
# ============================================================

print(
    "\n[5] Calculating capability preservation signals..."
)


shadow_signal = (
    skill_shadow["Skill_Shadow"]
    .fillna(0)
    .clip(0, 1)
)


risk_signal = (
    skill_shadow["Capability_Risk"]
    .fillna(0)
    .clip(0, 1)
)


criticality_signal = (
    skill_shadow["Capability_Criticality"]
    .fillna(0)
    .clip(0, 1)
)


market_signal = (
    minmax(
        skill_shadow["Market_Job_Count"]
    )
    .fillna(0)
)


# FORGE construct:
# Preservation pressure represents the need to
# deliberately preserve a capability after AI adoption.

skill_shadow["Preservation_Pressure"] = (
    0.45 * shadow_signal
    +
    0.30 * risk_signal
    +
    0.15 * criticality_signal
    +
    0.10 * market_signal
).clip(0, 1)


# ============================================================
# 6. LATTICE PRIORITY
# ============================================================

print(
    "\n[6] Calculating LATTICE capability priority..."
)


skill_shadow["LATTICE_Priority"] = (
    0.50
    * skill_shadow["Skill_Shadow"]
        .fillna(0)
        .clip(0, 1)

    +

    0.30
    * skill_shadow["Capability_Risk"]
        .fillna(0)
        .clip(0, 1)

    +

    0.20
    * skill_shadow["Capability_Criticality"]
        .fillna(0)
        .clip(0, 1)
).clip(0, 1)


# ============================================================
# 7. SELECT TOP CAPABILITIES PER OCCUPATION
# ============================================================

print(
    "\n[7] Selecting high-priority capabilities..."
)


capability_columns = [
    "Occupation Title",
    "Capability Name",
    "Capability Type",
    "Capability ID",
    "Skill_Shadow",
    "Skill_Shadow_Percent",
    "Capability_Risk",
    "Capability_Risk_Percent",
    "Capability_Criticality",
    "Market_Job_Count",
    "Preservation_Pressure",
    "LATTICE_Priority",
]


capabilities = (
    skill_shadow[
        capability_columns
    ]
    .drop_duplicates(
        subset=[
            "Occupation Title",
            "Capability Type",
            "Capability ID",
        ]
    )
    .copy()
)


capabilities["Capability_Rank"] = (
    capabilities
    .groupby(
        "Occupation Title"
    )["LATTICE_Priority"]
    .rank(
        ascending=False,
        method="first"
    )
)


capabilities = capabilities[
    capabilities["Capability_Rank"]
    <= TOP_CAPABILITIES_PER_OCCUPATION
].copy()


print(
    f"Selected capability records: "
    f"{len(capabilities):,}"
)

print(
    f"Unique occupations: "
    f"{capabilities['Occupation Title'].nunique():,}"
)

print(
    f"Unique capabilities: "
    f"{capabilities['Capability Name'].nunique():,}"
)


# ============================================================
# 8. PREPARE WORKTRACE
# ============================================================

print(
    "\n[8] Preparing actual Task → Capability evidence..."
)


trace_columns = [
    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",
    "Task",
    "DWA Element Name",
    "Capability Name",
    "Capability Type",
    "Capability ID",
    "Semantic Similarity",
    "Occupation Capability Value",
    "Task Capability Weight",
]


trace_columns = [
    column
    for column in trace_columns
    if column in worktrace.columns
]


trace = worktrace[
    trace_columns
].copy()


# Remove duplicate evidence for the same
# occupation + task + capability.

trace = trace.drop_duplicates(
    subset=[
        "Occupation Title",
        "Task ID",
        "Capability Type",
        "Capability ID",
    ]
)


print(
    f"Task-capability evidence: "
    f"{len(trace):,}"
)


# ============================================================
# 9. CONNECT CAPABILITIES TO REAL TASKS
# ============================================================

print(
    "\n[9] Connecting capabilities to source tasks..."
)


lattice = trace.merge(
    capabilities,
    on=[
        "Occupation Title",
        "Capability Name",
        "Capability Type",
        "Capability ID",
    ],
    how="inner",
    suffixes=(
        "_trace",
        "_capability"
    )
)


print(
    f"Capability-task links: "
    f"{len(lattice):,}"
)


if len(lattice) == 0:

    raise RuntimeError(
        "\nLATTICE produced zero capability-task links.\n"
        "Check WORKTRACE capability identity fields."
    )


# ============================================================
# 10. CONNECT WORKFOLD V8
# ============================================================

print(
    "\n[10] Adding WORKFOLD transformation evidence..."
)


workfold_task_columns = [
    "Occupation Title",
    "Task",
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Preservation_Pressure",
    "Human_Preservation_Floor",
    "AI_Ceiling",
    "Work_Model",
]


wf = (
    workfold[
        workfold_task_columns
    ]
    .drop_duplicates(
        subset=[
            "Occupation Title",
            "Task",
        ]
    )
    .copy()
)


# IMPORTANT:
# Rename WORKFOLD's pressure before merge.
#
# Capability pressure:
#     Preservation_Pressure
#
# Task pressure from WORKFOLD:
#     Task_Preservation_Pressure
#
# Keeping these separate avoids pandas _x/_y confusion.

wf = wf.rename(
    columns={
        "Preservation_Pressure":
            "Task_Preservation_Pressure"
    }
)


lattice = lattice.merge(
    wf,
    on=[
        "Occupation Title",
        "Task",
    ],
    how="left"
)


# ============================================================
# 11. PREPARE PRESERVATION SIGNALS
# ============================================================

print(
    "\n[11] Preparing capability and task preservation signals..."
)


# Capability-level pressure from SKILL SHADOW.

lattice["Capability_Preservation_Pressure"] = (
    lattice["Preservation_Pressure"]
    .fillna(0)
    .clip(0, 1)
)


# Task-level pressure from WORKFOLD.

lattice["Task_Preservation_Pressure"] = (
    lattice["Task_Preservation_Pressure"]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# 12. TASK PRACTICE SIGNAL
# ============================================================

print(
    "\n[12] Calculating practice-task relevance..."
)


lattice["Task_AI_Suitability"] = (
    lattice["Task_AI_Suitability"]
    .fillna(0)
    .clip(0, 1)
)


lattice["AI_Share"] = (
    lattice["AI_Share"]
    .fillna(0)
    .clip(0, 1)
)


lattice["Human_Share"] = (
    lattice["Human_Share"]
    .fillna(0)
    .clip(0, 1)
)


# Human involvement matters because LATTICE
# is designed to preserve human capability.

lattice["Human_Practice_Signal"] = (
    lattice["Human_Share"]
    .clip(0, 1)
)


# AI transformation gives the practice task
# a realistic post-automation context.

lattice["AI_Transformation_Signal"] = (
    lattice["AI_Share"]
    .clip(0, 1)
)


# ============================================================
# 13. TASK EVIDENCE SIGNAL
# ============================================================

print(
    "\n[13] Calculating task evidence strength..."
)


task_weight = (
    lattice["Task Capability Weight"]
    .fillna(0)
)


task_weight_normalized = (
    minmax(
        task_weight
    )
    .fillna(0)
)


lattice["Task_Evidence_Signal"] = (
    task_weight_normalized
)


# ============================================================
# 14. PRACTICE RELEVANCE
# ============================================================

print(
    "\n[14] Calculating final practice relevance..."
)


lattice["Task_Practice_Relevance"] = (
    0.35
    * lattice["LATTICE_Priority"]

    +

    0.25
    * lattice["Human_Practice_Signal"]

    +

    0.20
    * lattice["AI_Transformation_Signal"]

    +

    0.20
    * lattice["Task_Evidence_Signal"]

).clip(0, 1)


# ============================================================
# 15. RANK TASKS
# ============================================================

print(
    "\n[15] Ranking source tasks..."
)


lattice["Task_Rank"] = (
    lattice
    .groupby(
        [
            "Occupation Title",
            "Capability Name",
            "Capability Type",
            "Capability ID",
        ]
    )[
        "Task_Practice_Relevance"
    ]
    .rank(
        ascending=False,
        method="first"
    )
)


lattice = lattice[
    lattice["Task_Rank"]
    <= TOP_TASKS_PER_CAPABILITY
].copy()


# ============================================================
# 16. PRACTICE INTENT
# ============================================================

def determine_practice_intent(row):

    shadow = (
        float(row["Skill_Shadow"])
        if pd.notna(row["Skill_Shadow"])
        else 0.0
    )

    risk = (
        float(row["Capability_Risk"])
        if pd.notna(row["Capability_Risk"])
        else 0.0
    )

    if shadow >= 0.40 or risk >= 0.40:

        return "Priority capability preservation"

    elif shadow >= 0.25 or risk >= 0.25:

        return "Capability preservation"

    else:

        return "Capability maintenance"


lattice["Practice_Intent"] = lattice.apply(
    determine_practice_intent,
    axis=1
)


# ============================================================
# 17. LATTICE GOAL
# ============================================================

print(
    "\n[16] Creating LATTICE goals..."
)


lattice["LATTICE_Goal"] = lattice.apply(
    lambda row:
        (
            "Create a realistic synthetic apprenticeship "
            "experience that exercises the capability "
            f"'{row['Capability Name']}' "
            "using the real work context represented by "
            f"the source task: '{row['Task']}'."
        ),
    axis=1
)


# ============================================================
# 18. ASSESSMENT FOCUS
# ============================================================

lattice["Assessment_Focus"] = lattice.apply(
    lambda row:
        (
            "Assess whether the participant can demonstrate "
            f"'{row['Capability Name']}' "
            "while solving the underlying work problem, "
            "making appropriate decisions, explaining "
            "reasoning where relevant, and producing "
            "an observable work outcome."
        ),
    axis=1
)


# ============================================================
# 19. LLM INPUT CONTRACT
# ============================================================

print(
    "\n[17] Building LLM-ready task specifications..."
)


def create_llm_input(row):

    return (

        "FORGE LATTICE SYNTHETIC APPRENTICESHIP\n\n"

        f"Occupation: "
        f"{row['Occupation Title']}\n"

        f"Target Capability: "
        f"{row['Capability Name']}\n"

        f"Capability Type: "
        f"{row['Capability Type']}\n"

        f"Original Work Task: "
        f"{row['Task']}\n"

        f"Work Context / DWA: "
        f"{row.get('DWA Element Name', '')}\n"

        f"Skill Shadow: "
        f"{row['Skill_Shadow']:.4f}\n"

        f"Capability Risk: "
        f"{row['Capability_Risk']:.4f}\n"

        f"Capability Criticality: "
        f"{row['Capability_Criticality']:.4f}\n"

        f"Capability Preservation Pressure: "
        f"{row['Capability_Preservation_Pressure']:.4f}\n"

        f"Task Preservation Pressure: "
        f"{row['Task_Preservation_Pressure']:.4f}\n"

        f"AI Share: "
        f"{row['AI_Share']:.4f}\n"

        f"Human Share: "
        f"{row['Human_Share']:.4f}\n"

        f"AI Suitability: "
        f"{row['Task_AI_Suitability']:.4f}\n\n"

        "Generate a realistic synthetic apprenticeship "
        "task that requires the human participant to "
        "actively demonstrate the target capability.\n\n"

        "Do NOT simply ask the participant to define "
        "or describe the capability.\n\n"

        "The task should simulate a realistic work "
        "situation and produce an observable outcome "
        "that can later be assessed using a fixed "
        "rubric and, where available, objective "
        "interaction evidence."
    )


lattice["LLM_Task_Input"] = lattice.apply(
    create_llm_input,
    axis=1
)


# ============================================================
# 20. FINAL COLUMN ORDER
# ============================================================

print(
    "\n[18] Organizing final LATTICE dataset..."
)


final_columns = [

    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",

    "Capability Name",
    "Capability Type",
    "Capability ID",

    "Task",
    "DWA Element Name",

    "Skill_Shadow",
    "Skill_Shadow_Percent",

    "Capability_Risk",
    "Capability_Risk_Percent",

    "Capability_Criticality",
    "Market_Job_Count",

    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",

    "LATTICE_Priority",
    "Capability_Rank",

    "Task Capability Weight",
    "Task_Evidence_Signal",

    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",

    "Human_Practice_Signal",
    "AI_Transformation_Signal",

    "Task_Practice_Relevance",
    "Task_Rank",

    "Work_Model",
    "Human_Preservation_Floor",
    "AI_Ceiling",

    "Practice_Intent",

    "LATTICE_Goal",
    "Assessment_Focus",
    "LLM_Task_Input",
]


final_columns = [
    column
    for column in final_columns
    if column in lattice.columns
]


lattice = lattice[
    final_columns
].copy()


# ============================================================
# 21. REMOVE DUPLICATES
# ============================================================

lattice = lattice.drop_duplicates(
    subset=[
        "Occupation Title",
        "Capability Name",
        "Capability Type",
        "Capability ID",
        "Task",
    ]
)


lattice = lattice.reset_index(
    drop=True
)


# ============================================================
# 22. SAVE
# ============================================================

print(
    "\n[19] Saving LATTICE knowledge base..."
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


lattice.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


lattice.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 23. FINAL DIAGNOSTICS
# ============================================================

print(
    "\n" + "=" * 75
)

print(
    "LATTICE ENGINE COMPLETE"
)

print(
    "=" * 75
)


print(
    f"\nFinal records        : "
    f"{len(lattice):,}"
)


print(
    f"Unique occupations   : "
    f"{lattice['Occupation Title'].nunique():,}"
)


print(
    f"Unique capabilities  : "
    f"{lattice['Capability Name'].nunique():,}"
)


print(
    f"Unique source tasks  : "
    f"{lattice['Task'].nunique():,}"
)


print(
    f"Unique task IDs      : "
    f"{lattice['Task ID'].nunique():,}"
)


print(
    "\nPractice Intent:"
)


print(
    lattice[
        "Practice_Intent"
    ]
    .value_counts()
    .to_string()
)


print(
    "\nCapability Types:"
)


print(
    lattice[
        "Capability Type"
    ]
    .value_counts()
    .to_string()
)


# ============================================================
# 24. TOP LATTICE CANDIDATES
# ============================================================

print(
    "\nTop LATTICE candidates:"
)


display_columns = [

    "Occupation Title",
    "Capability Name",
    "Task",
    "Skill_Shadow_Percent",
    "Capability_Risk_Percent",
    "Capability_Preservation_Pressure",
    "LATTICE_Priority",
    "Task_Practice_Relevance",
    "Work_Model",
]


display_columns = [
    column
    for column in display_columns
    if column in lattice.columns
]


print(
    lattice
    .sort_values(
        [
            "LATTICE_Priority",
            "Task_Practice_Relevance",
        ],
        ascending=False
    )[
        display_columns
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# ============================================================
# 25. OUTPUT PATHS
# ============================================================

print(
    "\nOutput files:"
)


print(
    f"Parquet : "
    f"{OUTPUT_PARQUET}"
)


print(
    f"CSV     : "
    f"{OUTPUT_CSV}"
)


print(
    "\n" + "=" * 75
)

print(
    "NEXT STAGE: LATTICE LLM GENERATION"
)

print(
    "=" * 75
)