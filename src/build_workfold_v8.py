import os
import warnings
import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

# ============================================================
# FORGE — WORKFOLD V8
# Safe-Budget Workforce Allocator
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

WORKTRACE_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_worktrace.parquet"
)

SHADOW_PATH = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_skill_shadow.parquet"
)

OUT_PARQUET = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_workfold_v8.parquet"
)

OUT_CSV = os.path.join(
    BASE_DIR,
    "datasets",
    "onet",
    "knowledge_base",
    "forge_workfold_v8.csv"
)

# ============================================================
# CONFIGURATION
# ============================================================

REQUESTED_TARGET = 0.50

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_PRIMARY_CAPABILITIES = 5

# ============================================================
# SAFE AI BUDGET
# ============================================================

MAX_AI_SHARE = 0.80

BASE_HUMAN_FLOOR = 0.05

MAX_HUMAN_FLOOR = 0.85

PRESERVATION_FLOOR_EXPONENT = 1.25

# ============================================================
# PRESERVATION WEIGHTS
# ============================================================

SKILL_SHADOW_WEIGHT = 0.55

CAPABILITY_RISK_WEIGHT = 0.30

CRITICALITY_WEIGHT = 0.15

# ============================================================
# ALLOCATION SCORE WEIGHTS
# ============================================================

SUITABILITY_WEIGHT = 0.50

AUTOMATION_WEIGHT = 0.20

LOW_SHADOW_WEIGHT = 0.20

LOW_RISK_WEIGHT = 0.10

# ============================================================
# WORK MODEL THRESHOLDS
# ============================================================

AI_LED_THRESHOLD = 0.60

AI_LED_SUITABILITY_THRESHOLD = 0.60

HUMAN_LED_THRESHOLD = 0.25

# ============================================================
# SEMANTIC ANCHORS
# ============================================================

AUTOMATION_ANCHORS = [
    "routine repetitive data processing",
    "structured information retrieval",
    "document processing",
    "classification and extraction",
    "transcription",
    "standardized transformation",
    "rule based administrative processing",
    "predictable monitoring",
    "routine reporting",
    "record keeping",
    "data entry",
    "sorting and organizing structured information",
    "repetitive digital workflow",
    "structured clerical processing",
]

HUMAN_ANCHORS = [
    "complex human judgment under uncertainty",
    "leadership and management",
    "negotiation and persuasion",
    "interpersonal interaction",
    "physical work requiring dexterity",
    "environment interaction",
    "creative problem solving",
    "adaptation to novel situations",
    "ethical decision making",
    "accountability",
    "ambiguous decisions",
    "empathy and human support",
    "hands on physical intervention",
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def minmax(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    result = pd.Series(
        0.0,
        index=series.index
    )

    valid = series.dropna()

    if len(valid) == 0:
        return result

    mn = valid.min()
    mx = valid.max()

    if mx <= mn:
        result.loc[valid.index] = 0.0
        return result

    result.loc[valid.index] = (
        (valid - mn)
        / (mx - mn)
    )

    return result.fillna(0.0)


def weighted_average(
    group,
    value_col
):

    values = pd.to_numeric(
        group[value_col],
        errors="coerce"
    ).fillna(0).values

    weights = pd.to_numeric(
        group["Capability_Importance"],
        errors="coerce"
    ).fillna(0).values

    if len(values) == 0:
        return 0.0

    if weights.sum() <= 0:
        return float(
            np.mean(values)
        )

    return float(
        np.average(
            values,
            weights=weights
        )
    )


# ============================================================
# START
# ============================================================

print("=" * 72)

print(
    "FORGE — WORKFOLD V8"
)

print(
    "Safe-Budget Workforce Allocator"
)

print("=" * 72)


# ============================================================
# 1. LOAD WORKTRACE
# ============================================================

print(
    "\n[1/12] Loading WORKTRACE..."
)

worktrace = pd.read_parquet(
    WORKTRACE_PATH
)

print(
    "WORKTRACE shape:",
    worktrace.shape
)

required_worktrace = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
]

missing = [
    c
    for c in required_worktrace
    if c not in worktrace.columns
]

if missing:

    raise ValueError(
        f"WORKTRACE missing columns: {missing}"
    )


# ============================================================
# 2. LOAD SKILL SHADOW
# ============================================================

print(
    "\n[2/12] Loading SKILL SHADOW..."
)

shadow = pd.read_parquet(
    SHADOW_PATH
)

print(
    "SKILL SHADOW shape:",
    shadow.shape
)

required_shadow = [
    "O*NET-SOC Code",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]

missing = [
    c
    for c in required_shadow
    if c not in shadow.columns
]

if missing:

    raise ValueError(
        f"SKILL SHADOW missing columns: {missing}"
    )


# ============================================================
# 3. CLEAN + JOIN CAPABILITY EVIDENCE
# ============================================================

print(
    "\n[3/12] Cleaning and joining capability evidence..."
)

worktrace = worktrace.copy()

shadow = shadow.copy()

# ------------------------------------------------------------
# Composite capability key
# ------------------------------------------------------------

worktrace["Capability Key"] = (
    worktrace[
        "Capability Type"
    ].astype(str)
    + "::"
    +
    worktrace[
        "Capability ID"
    ].astype(str)
)

shadow["Capability Key"] = (
    shadow[
        "Capability Type"
    ].astype(str)
    + "::"
    +
    shadow[
        "Capability ID"
    ].astype(str)
)

# ------------------------------------------------------------
# Remove duplicate task-capability records
# ------------------------------------------------------------

before = len(worktrace)

worktrace = worktrace.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "Capability Key"
    ]
).copy()

print(
    "Duplicate task-capability rows removed:",
    before - len(worktrace)
)

# ------------------------------------------------------------
# Capability evidence table
# ------------------------------------------------------------

shadow_small = shadow[
    [
        "O*NET-SOC Code",
        "Capability Key",
        "Skill_Shadow",
        "Capability_Risk",
        "Capability_Criticality",
    ]
].drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Capability Key"
    ]
)

# ------------------------------------------------------------
# RAW evidence indicator
#
# Important:
# This is created BEFORE fallback filling.
# ------------------------------------------------------------

evidence_keys = shadow_small[
    [
        "O*NET-SOC Code",
        "Capability Key"
    ]
].copy()

evidence_keys[
    "Raw_Evidence_Available"
] = True

worktrace = worktrace.merge(
    evidence_keys,
    on=[
        "O*NET-SOC Code",
        "Capability Key"
    ],
    how="left"
)

worktrace[
    "Raw_Evidence_Available"
] = (
    worktrace[
        "Raw_Evidence_Available"
    ]
    .fillna(False)
    .astype(bool)
)

# ------------------------------------------------------------
# Join actual preservation evidence
# ------------------------------------------------------------

worktrace = worktrace.merge(
    shadow_small,
    on=[
        "O*NET-SOC Code",
        "Capability Key"
    ],
    how="left"
)

# ------------------------------------------------------------
# Missing-value fallback
# ------------------------------------------------------------

for col in [
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]:

    worktrace[col] = pd.to_numeric(
        worktrace[col],
        errors="coerce"
    )

    occupation_median = (
        worktrace
        .groupby(
            "O*NET-SOC Code"
        )[col]
        .transform("median")
    )

    global_median = (
        worktrace[col]
        .median()
    )

    worktrace[col] = (
        worktrace[col]
        .fillna(
            occupation_median
        )
        .fillna(
            global_median
        )
        .fillna(0)
    )

raw_evidence_coverage = (
    worktrace[
        "Raw_Evidence_Available"
    ]
    .mean()
    * 100
)

print(
    f"Raw capability evidence coverage: "
    f"{raw_evidence_coverage:.2f}%"
)


# ============================================================
# 4. CREATE ONE ROW PER TASK
# ============================================================

print(
    "\n[4/12] Creating one row per task..."
)

worktrace[
    "Task Capability Weight"
] = pd.to_numeric(
    worktrace[
        "Task Capability Weight"
    ],
    errors="coerce"
).fillna(0).clip(
    lower=0
)

# ------------------------------------------------------------
# Capability importance within each task
# ------------------------------------------------------------

task_weight_sum = (
    worktrace
    .groupby(
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    )[
        "Task Capability Weight"
    ]
    .transform("sum")
)

task_cap_count = (
    worktrace
    .groupby(
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    )[
        "Task Capability Weight"
    ]
    .transform("count")
)

worktrace[
    "Capability_Importance"
] = np.where(

    task_weight_sum > 0,

    worktrace[
        "Task Capability Weight"
    ]
    / task_weight_sum,

    1.0 / task_cap_count
)

# ------------------------------------------------------------
# Task aggregation
# ------------------------------------------------------------

task_rows = []

for (
    soc,
    task_id
), group in worktrace.groupby(
    [
        "O*NET-SOC Code",
        "Task ID"
    ],
    sort=False
):

    first = group.iloc[0]

    row = {

        "O*NET-SOC Code":
            soc,

        "Task ID":
            task_id,

        "Occupation Title":
            first.get(
                "Occupation Title",
                ""
            ),

        "Occupation Description":
            first.get(
                "Occupation Description",
                ""
            ),

        "Task":
            first.get(
                "Task",
                ""
            ),

        "DWA Element Name":
            first.get(
                "DWA Element Name",
                ""
            ),

        "Task_Capability_Count":
            len(group),

        "Task_Skill_Shadow":
            weighted_average(
                group,
                "Skill_Shadow"
            ),

        "Task_Capability_Risk":
            weighted_average(
                group,
                "Capability_Risk"
            ),

        "Task_Criticality":
            weighted_average(
                group,
                "Capability_Criticality"
            ),

        "Task_Evidence_Coverage":
            float(
                np.average(
                    group[
                        "Raw_Evidence_Available"
                    ].astype(float),
                    weights=group[
                        "Capability_Importance"
                    ]
                )
            ),
    }

    task_rows.append(row)


tasks = pd.DataFrame(
    task_rows
)

print(
    "Unique task records:",
    len(tasks)
)


# ============================================================
# 5. PRIMARY CAPABILITIES
# ============================================================

print(
    "\n[5/12] Extracting primary capabilities..."
)

primary_rows = []

for (
    soc,
    task_id
), group in worktrace.groupby(
    [
        "O*NET-SOC Code",
        "Task ID"
    ],
    sort=False
):

    g = group.sort_values(
        "Task Capability Weight",
        ascending=False
    ).head(
        TOP_PRIMARY_CAPABILITIES
    )

    capabilities = []

    for _, r in g.iterrows():

        capabilities.append(
            f"{r['Capability Name']} "
            f"({r['Capability Type']})"
        )

    primary_rows.append(
        {
            "O*NET-SOC Code":
                soc,

            "Task ID":
                task_id,

            "Primary_Capabilities":
                " | ".join(
                    capabilities
                ),
        }
    )

primary = pd.DataFrame(
    primary_rows
)

tasks = tasks.merge(
    primary,
    on=[
        "O*NET-SOC Code",
        "Task ID"
    ],
    how="left"
)


# ============================================================
# 6. SENTENCE TRANSFORMER
# ============================================================

print(
    "\n[6/12] Loading SentenceTransformer..."
)

model = SentenceTransformer(
    MODEL_NAME
)

print(
    "Encoding automation anchors..."
)

automation_embeddings = model.encode(
    AUTOMATION_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False
)

print(
    "Encoding human anchors..."
)

human_embeddings = model.encode(
    HUMAN_ANCHORS,
    normalize_embeddings=True,
    show_progress_bar=False
)

print(
    "Encoding",
    len(tasks),
    "tasks..."
)

task_text = (
    tasks[
        "Occupation Title"
    ]
    .fillna("")
    .astype(str)

    + ". "

    +

    tasks[
        "Task"
    ]
    .fillna("")
    .astype(str)
)

task_embeddings = model.encode(
    task_text.tolist(),
    normalize_embeddings=True,
    batch_size=256,
    show_progress_bar=True
)


# ============================================================
# 7. AI / HUMAN SUITABILITY
# ============================================================

print(
    "\n[7/12] Calculating AI/Human semantic suitability..."
)

automation_scores = (
    task_embeddings
    @ automation_embeddings.T
).max(
    axis=1
)

human_scores = (
    task_embeddings
    @ human_embeddings.T
).max(
    axis=1
)

balance = (
    automation_scores
    - human_scores
)

suitability = (
    balance + 1.0
) / 2.0

suitability = np.clip(
    suitability,
    0,
    1
)

tasks[
    "Automation_Semantic_Score"
] = automation_scores

tasks[
    "Human_Semantic_Score"
] = human_scores

tasks[
    "Task_AI_Suitability"
] = suitability


# ============================================================
# 8. PRESERVATION SIGNALS
# ============================================================

print(
    "\n[8/12] Building preservation signals..."
)

tasks[
    "Skill_Shadow_Normalized"
] = minmax(
    tasks[
        "Task_Skill_Shadow"
    ]
)

tasks[
    "Capability_Risk_Normalized"
] = minmax(
    tasks[
        "Task_Capability_Risk"
    ]
)

tasks[
    "Criticality_Normalized"
] = minmax(
    tasks[
        "Task_Criticality"
    ]
)

# ------------------------------------------------------------
# Preservation pressure
# ------------------------------------------------------------

tasks[
    "Preservation_Pressure"
] = (

    SKILL_SHADOW_WEIGHT
    *
    tasks[
        "Skill_Shadow_Normalized"
    ]

    +

    CAPABILITY_RISK_WEIGHT
    *
    tasks[
        "Capability_Risk_Normalized"
    ]

    +

    CRITICALITY_WEIGHT
    *
    tasks[
        "Criticality_Normalized"
    ]
)

tasks[
    "Preservation_Pressure"
] = (
    tasks[
        "Preservation_Pressure"
    ]
    .clip(0, 1)
)

# ------------------------------------------------------------
# Human preservation floor
# ------------------------------------------------------------

tasks[
    "Human_Preservation_Floor"
] = (

    BASE_HUMAN_FLOOR

    +

    (
        MAX_HUMAN_FLOOR
        -
        BASE_HUMAN_FLOOR
    )

    *

    (
        tasks[
            "Preservation_Pressure"
        ]
        **
        PRESERVATION_FLOOR_EXPONENT
    )
)

tasks[
    "Human_Preservation_Floor"
] = (
    tasks[
        "Human_Preservation_Floor"
    ]
    .clip(
        0,
        MAX_HUMAN_FLOOR
    )
)

# ------------------------------------------------------------
# AI ceiling
# ------------------------------------------------------------

raw_ceiling = (

    MAX_AI_SHARE

    *

    (
        0.10
        +
        0.90
        *
        tasks[
            "Task_AI_Suitability"
        ]
    )

    *

    (
        1
        -
        0.60
        *
        tasks[
            "Preservation_Pressure"
        ]
    )
)

tasks[
    "AI_Ceiling"
] = np.minimum(
    raw_ceiling,
    1
    -
    tasks[
        "Human_Preservation_Floor"
    ]
)

tasks[
    "AI_Ceiling"
] = (
    tasks[
        "AI_Ceiling"
    ]
    .clip(
        0,
        MAX_AI_SHARE
    )
)


# ============================================================
# 9. MAXIMUM SAFE AI ADOPTION
# ============================================================

print(
    "\n[9/12] Calculating maximum safe AI adoption..."
)

# ------------------------------------------------------------
# Equal task importance
#
# Each task gets equal occupation-level budget weight.
# ------------------------------------------------------------

occupation_task_count = (
    tasks
    .groupby(
        "O*NET-SOC Code"
    )[
        "Task ID"
    ]
    .transform("count")
)

tasks[
    "Task_Importance"
] = (
    1.0
    /
    occupation_task_count
)

# ------------------------------------------------------------
# Safe task bound
# ------------------------------------------------------------

tasks[
    "Safe_AI_Bound"
] = tasks[
    "AI_Ceiling"
]

# ------------------------------------------------------------
# Maximum safe occupation adoption
# ------------------------------------------------------------

max_safe = (
    tasks
    .groupby(
        "O*NET-SOC Code"
    )
    .apply(
        lambda g:
            np.sum(
                g[
                    "Task_Importance"
                ]
                *
                g[
                    "Safe_AI_Bound"
                ]
            ),
        include_groups=False
    )
    .rename(
        "Maximum_Safe_AI_Adoption"
    )
)

tasks = tasks.merge(
    max_safe,
    left_on="O*NET-SOC Code",
    right_index=True,
    how="left"
)

tasks[
    "Maximum_Safe_AI_Adoption"
] = (
    tasks[
        "Maximum_Safe_AI_Adoption"
    ]
    .clip(
        0,
        MAX_AI_SHARE
    )
)


# ============================================================
# 10. SAFE-BUDGET AI ALLOCATION
# ============================================================

print(
    "\n[10/12] Allocating AI budget across tasks..."
)

# ------------------------------------------------------------
# Allocation components
# ------------------------------------------------------------

tasks[
    "Suitability_Component"
] = (
    tasks[
        "Task_AI_Suitability"
    ]
)

tasks[
    "Automation_Component"
] = (
    tasks[
        "Automation_Semantic_Score"
    ]
    .clip(0, 1)
)

tasks[
    "Low_Shadow_Component"
] = (
    1
    -
    tasks[
        "Skill_Shadow_Normalized"
    ]
)

tasks[
    "Low_Risk_Component"
] = (
    1
    -
    tasks[
        "Capability_Risk_Normalized"
    ]
)

# ------------------------------------------------------------
# Composite allocation score
# ------------------------------------------------------------

tasks[
    "AI_Allocation_Score"
] = (

    SUITABILITY_WEIGHT
    *
    tasks[
        "Suitability_Component"
    ]

    +

    AUTOMATION_WEIGHT
    *
    tasks[
        "Automation_Component"
    ]

    +

    LOW_SHADOW_WEIGHT
    *
    tasks[
        "Low_Shadow_Component"
    ]

    +

    LOW_RISK_WEIGHT
    *
    tasks[
        "Low_Risk_Component"
    ]
)

tasks[
    "AI_Allocation_Score"
] = (
    tasks[
        "AI_Allocation_Score"
    ]
    .clip(
        0,
        1
    )
)


# ------------------------------------------------------------
# Allocate safe occupation budget
# ------------------------------------------------------------

allocation_results = []

for soc, group in tasks.groupby(
    "O*NET-SOC Code",
    sort=False
):

    g = group.copy()

    weights = g[
        "Task_Importance"
    ].values

    scores = g[
        "AI_Allocation_Score"
    ].values

    ceilings = g[
        "AI_Ceiling"
    ].values

    safe_budget = float(
        g[
            "Maximum_Safe_AI_Adoption"
        ].iloc[0]
    )

    # --------------------------------------------------------
    # Priority score
    # --------------------------------------------------------

    priority = (
        scores
        *
        ceilings
    )

    priority = np.maximum(
        priority,
        0
    )

    # --------------------------------------------------------
    # If all scores are zero
    # --------------------------------------------------------

    if priority.sum() <= 0:

        allocation = np.zeros(
            len(g)
        )

    else:

        # ----------------------------------------------------
        # Initial proportional allocation
        # ----------------------------------------------------

        allocation = (
            priority
            /
            priority.sum()
        )

        allocation = (
            allocation
            *
            safe_budget
            /
            np.maximum(
                weights,
                1e-12
            )
        )

        allocation = np.minimum(
            allocation,
            ceilings
        )

    # --------------------------------------------------------
    # Redistribute unused safe budget
    # --------------------------------------------------------

    for _ in range(30):

        current_adoption = np.sum(
            weights
            *
            allocation
        )

        remaining_budget = (
            safe_budget
            -
            current_adoption
        )

        if remaining_budget <= 1e-9:
            break

        available_capacity = (
            ceilings
            -
            allocation
        )

        available_capacity = np.maximum(
            available_capacity,
            0
        )

        eligible = (
            available_capacity
            >
            1e-10
        )

        if not eligible.any():
            break

        redistribution_priority = (
            priority
            *
            available_capacity
        )

        redistribution_priority[
            ~eligible
        ] = 0

        weighted_priority = (
            weights
            *
            redistribution_priority
        )

        if weighted_priority.sum() <= 0:
            break

        increments = (
            remaining_budget
            *
            weighted_priority
            /
            weighted_priority.sum()
        )

        increments = np.minimum(
            increments,
            available_capacity
        )

        allocation = (
            allocation
            +
            increments
        )

        allocation = np.minimum(
            allocation,
            ceilings
        )

    # --------------------------------------------------------
    # Final clipping
    # --------------------------------------------------------

    allocation = np.clip(
        allocation,
        0,
        ceilings
    )

    g[
        "AI_Share"
    ] = allocation

    actual_adoption = np.sum(
        weights
        *
        allocation
    )

    g[
        "Actual_Occupation_AI_Adoption"
    ] = actual_adoption

    g[
        "Effective_AI_Target"
    ] = min(
        REQUESTED_TARGET,
        safe_budget
    )

    g[
        "Target_Feasibility"
    ] = np.where(
        safe_budget
        >=
        REQUESTED_TARGET,
        "Feasible",
        "Infeasible"
    )

    g[
        "Safe_Target_Gap"
    ] = (
        REQUESTED_TARGET
        -
        safe_budget
    )

    allocation_results.append(
        g
    )


tasks = pd.concat(
    allocation_results,
    ignore_index=True
)


# ============================================================
# 11. WORKFORCE DECISIONS
# ============================================================

print(
    "\n[11/12] Creating workforce decisions..."
)

tasks[
    "Human_Share"
] = (
    1
    -
    tasks[
        "AI_Share"
    ]
)

tasks[
    "AI_Share_Percent"
] = (
    tasks[
        "AI_Share"
    ]
    *
    100
)

tasks[
    "Human_Share_Percent"
] = (
    tasks[
        "Human_Share"
    ]
    *
    100
)

tasks[
    "Task_AI_Suitability_Percent"
] = (
    tasks[
        "Task_AI_Suitability"
    ]
    *
    100
)

tasks[
    "Task_Skill_Shadow_Percent"
] = (
    tasks[
        "Task_Skill_Shadow"
    ]
    *
    100
)

tasks[
    "Preservation_Pressure_Percent"
] = (
    tasks[
        "Preservation_Pressure"
    ]
    *
    100
)

tasks[
    "Human_Preservation_Floor_Percent"
] = (
    tasks[
        "Human_Preservation_Floor"
    ]
    *
    100
)

tasks[
    "Maximum_Safe_AI_Adoption_Percent"
] = (
    tasks[
        "Maximum_Safe_AI_Adoption"
    ]
    *
    100
)

tasks[
    "Requested_Target_Percent"
] = (
    REQUESTED_TARGET
    *
    100
)

tasks[
    "Effective_AI_Target_Percent"
] = (
    tasks[
        "Effective_AI_Target"
    ]
    *
    100
)

tasks[
    "Safe_Target_Gap_Percent"
] = (
    tasks[
        "Safe_Target_Gap"
    ]
    *
    100
)

tasks[
    "Evidence_Confidence_Percent"
] = (
    tasks[
        "Task_Evidence_Coverage"
    ]
    *
    100
)


# ------------------------------------------------------------
# Work model
# ------------------------------------------------------------

def classify_work(row):

    ai = row[
        "AI_Share"
    ]

    suitability = row[
        "Task_AI_Suitability"
    ]

    if (
        ai
        >=
        AI_LED_THRESHOLD
        and
        suitability
        >=
        AI_LED_SUITABILITY_THRESHOLD
    ):

        return "AI-led"

    if (
        ai
        <=
        HUMAN_LED_THRESHOLD
    ):

        return "Human-led"

    return "Hybrid"


tasks[
    "Work_Model"
] = tasks.apply(
    classify_work,
    axis=1
)


# ------------------------------------------------------------
# Decision explanation
# ------------------------------------------------------------

def explain(row):

    ai = row[
        "AI_Share_Percent"
    ]

    suitability = row[
        "Task_AI_Suitability_Percent"
    ]

    shadow_value = row[
        "Task_Skill_Shadow_Percent"
    ]

    risk = (
        row[
            "Capability_Risk_Normalized"
        ]
        *
        100
    )

    safe = row[
        "Maximum_Safe_AI_Adoption_Percent"
    ]

    if (
        row[
            "Target_Feasibility"
        ]
        ==
        "Feasible"
    ):

        target_text = (
            f"The occupation can support the "
            f"requested {REQUESTED_TARGET*100:.0f}% "
            f"AI-adoption scenario under the "
            f"current preservation constraints."
        )

    else:

        target_text = (
            f"The requested {REQUESTED_TARGET*100:.0f}% "
            f"target exceeds the calculated "
            f"maximum safe occupation adoption "
            f"of {safe:.1f}%."
        )

    return (
        f"AI allocation is {ai:.1f}% because "
        f"task AI suitability is {suitability:.1f}%, "
        f"while Skill Shadow is "
        f"{shadow_value:.1f}% and normalized "
        f"capability risk is {risk:.1f}%. "
        f"{target_text}"
    )


tasks[
    "Decision_Explanation"
] = tasks.apply(
    explain,
    axis=1
)


# ============================================================
# 12. FINAL AUDIT
# ============================================================

print(
    "\n[12/12] Running V8 audit..."
)

print(
    "\n"
    +
    "=" * 72
)

print(
    "WORKFOLD V8 VALIDATION"
)

print(
    "=" * 72
)


# ============================================================
# BASIC STRUCTURE
# ============================================================

print(
    "\nRecords:",
    len(tasks)
)

unique_tasks = (
    tasks[
        [
            "O*NET-SOC Code",
            "Task ID"
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    "Unique tasks:",
    unique_tasks
)

print(
    "Task uniqueness:",
    (
        "PASSED"
        if unique_tasks == len(tasks)
        else "FAILED"
    )
)

print(
    "Unique occupations:",
    tasks[
        "O*NET-SOC Code"
    ].nunique()
)


# ============================================================
# WORK MODEL DISTRIBUTION
# ============================================================

print(
    "\nWork model distribution:"
)

print(
    tasks[
        "Work_Model"
    ].value_counts()
)


# ============================================================
# OCCUPATION AI ADOPTION
# ============================================================

occupation_adoption = (
    tasks
    .groupby(
        "O*NET-SOC Code"
    )[
        "Actual_Occupation_AI_Adoption"
    ]
    .first()
)

print(
    "\nOccupation AI adoption:"
)

print(
    occupation_adoption.describe()
)

print(
    f"\nMean AI adoption: "
    f"{occupation_adoption.mean()*100:.2f}%"
)

print(
    f"Requested target: "
    f"{REQUESTED_TARGET*100:.2f}%"
)

print(
    f"Mean target gap: "
    f"{(occupation_adoption.mean()-REQUESTED_TARGET)*100:.2f} pp"
)


# ============================================================
# MAXIMUM SAFE ADOPTION
# ============================================================

maximum_safe = (
    tasks
    .groupby(
        "O*NET-SOC Code"
    )[
        "Maximum_Safe_AI_Adoption"
    ]
    .first()
)

print(
    "\nMaximum safe AI adoption:"
)

print(
    maximum_safe.describe()
)

print(
    f"\nMean maximum safe adoption: "
    f"{maximum_safe.mean()*100:.2f}%"
)

print(
    "Occupations able to support 50% target:",
    (
        maximum_safe
        >=
        REQUESTED_TARGET
    ).sum()
)

print(
    "Occupations below 50% target:",
    (
        maximum_safe
        <
        REQUESTED_TARGET
    ).sum()
)


# ============================================================
# TARGET FEASIBILITY
# ============================================================

print(
    "\nTarget feasibility:"
)

print(
    tasks[
        [
            "O*NET-SOC Code",
            "Target_Feasibility"
        ]
    ]
    .drop_duplicates()[
        "Target_Feasibility"
    ]
    .value_counts()
)


# ============================================================
# EVIDENCE
# ============================================================

print(
    "\nEvidence coverage:"
)

print(
    tasks[
        "Evidence_Confidence_Percent"
    ].describe()
)

print(
    f"\nRaw evidence coverage: "
    f"{raw_evidence_coverage:.2f}%"
)


# ============================================================
# BEHAVIOR AUDIT
# ============================================================

print(
    "\n"
    +
    "-" * 72
)

print(
    "BEHAVIOR AUDIT"
)

print(
    "-" * 72
)

pearson_suitability = (
    tasks[
        [
            "AI_Share",
            "Task_AI_Suitability"
        ]
    ]
    .corr()
    .iloc[0, 1]
)

pearson_shadow = (
    tasks[
        [
            "AI_Share",
            "Task_Skill_Shadow"
        ]
    ]
    .corr()
    .iloc[0, 1]
)

pearson_risk = (
    tasks[
        [
            "AI_Share",
            "Task_Capability_Risk"
        ]
    ]
    .corr()
    .iloc[0, 1]
)

pearson_pressure = (
    tasks[
        [
            "AI_Share",
            "Preservation_Pressure"
        ]
    ]
    .corr()
    .iloc[0, 1]
)

print(
    "AI share vs suitability:",
    round(
        pearson_suitability,
        4
    )
)

print(
    "AI share vs Skill Shadow:",
    round(
        pearson_shadow,
        4
    )
)

print(
    "AI share vs capability risk:",
    round(
        pearson_risk,
        4
    )
)

print(
    "AI share vs preservation pressure:",
    round(
        pearson_pressure,
        4
    )
)


# ============================================================
# SPEARMAN MONOTONICITY
# ============================================================

print(
    "\nSPEARMAN MONOTONICITY AUDIT"
)

spearman_suitability = (
    tasks[
        [
            "AI_Share",
            "Task_AI_Suitability"
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)

spearman_shadow = (
    tasks[
        [
            "AI_Share",
            "Task_Skill_Shadow"
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)

spearman_pressure = (
    tasks[
        [
            "AI_Share",
            "Preservation_Pressure"
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)

print(
    "AI share vs suitability:",
    round(
        spearman_suitability,
        4
    )
)

print(
    "AI share vs Skill Shadow:",
    round(
        spearman_shadow,
        4
    )
)

print(
    "AI share vs preservation pressure:",
    round(
        spearman_pressure,
        4
    )
)


# ============================================================
# CONSTRAINT CHECKS
# ============================================================

ceiling_violations = (
    tasks[
        "AI_Share"
    ]
    >
    tasks[
        "AI_Ceiling"
    ]
    +
    1e-8
).sum()

floor_violations = (
    (
        1
        -
        tasks[
            "AI_Share"
        ]
    )
    <
    tasks[
        "Human_Preservation_Floor"
    ]
    -
    1e-8
).sum()

occupation_target_violations = 0

for soc, group in tasks.groupby(
    "O*NET-SOC Code"
):

    actual = group[
        "Actual_Occupation_AI_Adoption"
    ].iloc[0]

    target = group[
        "Effective_AI_Target"
    ].iloc[0]

    if actual > target + 1e-8:

        occupation_target_violations += 1


print(
    "\nAI ceiling violations:",
    ceiling_violations
)

print(
    "Human preservation floor violations:",
    floor_violations
)

print(
    "Occupation target violations:",
    occupation_target_violations
)


# ============================================================
# RANGE CHECKS
# ============================================================

print(
    "\nRange checks:"
)

range_checks = {

    "AI_Share":
        tasks[
            "AI_Share"
        ].between(
            0,
            1
        ).all(),

    "Human_Share":
        tasks[
            "Human_Share"
        ].between(
            0,
            1
        ).all(),

    "AI_Suitability":
        tasks[
            "Task_AI_Suitability"
        ].between(
            0,
            1
        ).all(),

    "Preservation_Pressure":
        tasks[
            "Preservation_Pressure"
        ].between(
            0,
            1
        ).all(),

    "Human_Preservation_Floor":
        tasks[
            "Human_Preservation_Floor"
        ].between(
            0,
            1
        ).all(),

    "Evidence":
        tasks[
            "Evidence_Confidence_Percent"
        ].between(
            0,
            100
        ).all(),
}

for name, passed in range_checks.items():

    print(
        f"{name}:",
        (
            "PASSED"
            if passed
            else "FAILED"
        )
    )


# ============================================================
# DISPLAY COLUMNS
# ============================================================

display_cols = [

    "Occupation Title",

    "Task",

    "AI_Share_Percent",

    "Task_AI_Suitability_Percent",

    "Task_Skill_Shadow_Percent",

    "Preservation_Pressure_Percent",

    "Human_Preservation_Floor_Percent",

    "Maximum_Safe_AI_Adoption_Percent",

    "Work_Model",
]


# ============================================================
# HIGHEST AI
# ============================================================

print(
    "\n"
    +
    "-" * 72
)

print(
    "HIGHEST AI ALLOCATION"
)

print(
    "-" * 72
)

print(
    tasks
    .sort_values(
        "AI_Share_Percent",
        ascending=False
    )[
        display_cols
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# ============================================================
# LOWEST AI
# ============================================================

print(
    "\n"
    +
    "-" * 72
)

print(
    "LOWEST AI ALLOCATION"
)

print(
    "-" * 72
)

print(
    tasks
    .sort_values(
        "AI_Share_Percent",
        ascending=True
    )[
        display_cols
    ]
    .head(15)
    .to_string(
        index=False
    )
)


# ============================================================
# HIGHEST SKILL SHADOW
# ============================================================

print(
    "\n"
    +
    "-" * 72
)

print(
    "HIGHEST SKILL SHADOW"
)

print(
    "-" * 72
)

print(
    tasks
    .sort_values(
        "Task_Skill_Shadow_Percent",
        ascending=False
    )[
        display_cols
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# HIGHEST PRESERVATION PRESSURE
# ============================================================

print(
    "\n"
    +
    "-" * 72
)

print(
    "HIGHEST PRESERVATION PRESSURE"
)

print(
    "-" * 72
)

print(
    tasks
    .sort_values(
        "Preservation_Pressure_Percent",
        ascending=False
    )[
        display_cols
    ]
    .head(10)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print(
    "\nSaving WORKFOLD V8..."
)

final_columns = [

    "O*NET-SOC Code",

    "Task ID",

    "Occupation Title",

    "Occupation Description",

    "Task",

    "DWA Element Name",

    "Primary_Capabilities",

    "Task_Capability_Count",

    "Task_Skill_Shadow",

    "Task_Skill_Shadow_Percent",

    "Task_Capability_Risk",

    "Task_Criticality",

    "Task_Evidence_Coverage",

    "Evidence_Confidence_Percent",

    "Raw_Evidence_Available",

    "Automation_Semantic_Score",

    "Human_Semantic_Score",

    "Task_AI_Suitability",

    "Task_AI_Suitability_Percent",

    "Skill_Shadow_Normalized",

    "Capability_Risk_Normalized",

    "Criticality_Normalized",

    "Preservation_Pressure",

    "Preservation_Pressure_Percent",

    "Human_Preservation_Floor",

    "Human_Preservation_Floor_Percent",

    "AI_Ceiling",

    "AI_Allocation_Score",

    "Safe_AI_Bound",

    "Maximum_Safe_AI_Adoption",

    "Maximum_Safe_AI_Adoption_Percent",

    "Requested_Target_Percent",

    "Effective_AI_Target",

    "Effective_AI_Target_Percent",

    "Safe_Target_Gap",

    "Safe_Target_Gap_Percent",

    "AI_Share",

    "AI_Share_Percent",

    "Human_Share",

    "Human_Share_Percent",

    "Target_Feasibility",

    "Work_Model",

    "Decision_Explanation",
]

final_columns = [
    c
    for c in final_columns
    if c in tasks.columns
]

final_df = tasks[
    final_columns
].copy()


# ============================================================
# SAVE PARQUET + CSV
# ============================================================

final_df.to_parquet(
    OUT_PARQUET,
    index=False
)

final_df.to_csv(
    OUT_CSV,
    index=False
)


# ============================================================
# COMPLETE
# ============================================================

print(
    "\n"
    +
    "=" * 72
)

print(
    "WORKFOLD V8 COMPLETE"
)

print(
    "=" * 72
)

print(
    "Parquet:",
    OUT_PARQUET
)

print(
    "CSV:    ",
    OUT_CSV
)

print(
    "Final shape:",
    final_df.shape
)

print(
    "=" * 72
)