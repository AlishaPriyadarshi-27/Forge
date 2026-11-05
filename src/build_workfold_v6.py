# ============================================================
# FORGE — WORKFOLD V6
# Future-Oriented Workforce Reconfiguration & Growth Engine
#
# V6 = PRESERVATION-CONSTRAINED WORKFORCE OPTIMIZER
#
# Core principle:
#
#   Automate suitable work
#   +
#   Preserve human capability
#   +
#   Respect evidence
#   +
#   Never force an arbitrary AI adoption target
#
# IMPORTANT:
#   AI suitability is a semantic index, NOT probability.
#   Skill Shadow is a FORGE-defined metric.
#   Optimization parameters are scenario parameters.
# ============================================================

from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from sentence_transformers import SentenceTransformer
from scipy.optimize import minimize

warnings.filterwarnings("ignore")


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

WORKTRACE_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)

SKILL_SHADOW_PATH = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_skill_shadow.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
)

OUTPUT_PARQUET = (
    OUTPUT_DIR
    / "forge_workfold_v6.parquet"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "forge_workfold_v6.csv"
)


# ============================================================
# SCENARIO PARAMETERS
# ============================================================

# User-controlled scenario.
AI_ADOPTION_TARGET = 0.50

# Absolute maximum delegation.
GLOBAL_MAX_AI_SHARE = 0.80

# No negative allocation.
GLOBAL_MIN_AI_SHARE = 0.00


# ============================================================
# PRESERVATION PARAMETERS
#
# These define structural safeguards rather than
# empirical probabilities.
# ============================================================

# Minimum human share for a high-preservation task.
MAX_PRESERVATION_HUMAN_FLOOR = 0.80

# Human floor increases non-linearly with preservation pressure.
PRESERVATION_FLOOR_EXPONENT = 1.50


# ============================================================
# OPTIMIZATION PARAMETERS
# ============================================================

# Automation benefit.
AUTOMATION_WEIGHT = 1.00

# Distance from evidence-driven preference.
PREFERENCE_WEIGHT = 0.40

# Target tracking.
TARGET_WEIGHT = 1.25

# Penalize unnecessary AI allocation when preservation pressure
# is high.
PRESERVATION_WEIGHT = 1.20

# Additional Skill Shadow protection.
SHADOW_WEIGHT = 1.00


# ============================================================
# SEMANTIC ANCHORS
# ============================================================

AUTOMATION_ANCHORS = [
    "routine repetitive data processing",
    "structured retrieval and document processing",
    "classification extraction transcription and standard transformation",
    "rule based administrative processing",
    "predictable monitoring reporting and record keeping",
]


HUMAN_ANCHORS = [
    "complex human judgment under uncertainty",
    "leadership negotiation persuasion and interpersonal interaction",
    "physical work dexterity and environmental interaction",
    "creative problem solving adaptation and novel situations",
    "ethical accountability ambiguous decisions and responsibility",
]


MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# HELPERS
# ============================================================

def weighted_mean(values, weights):

    values = np.asarray(
        values,
        dtype=float
    )

    weights = np.asarray(
        weights,
        dtype=float
    )

    mask = (
        np.isfinite(values)
        &
        np.isfinite(weights)
        &
        (weights > 0)
    )

    if not mask.any():
        return np.nan

    return np.average(
        values[mask],
        weights=weights[mask]
    )


def minmax(series):

    s = pd.to_numeric(
        series,
        errors="coerce"
    )

    valid = s.dropna()

    if len(valid) == 0:
        return pd.Series(
            0.5,
            index=s.index
        )

    minimum = valid.min()
    maximum = valid.max()

    if np.isclose(
        minimum,
        maximum
    ):

        result = pd.Series(
            0.5,
            index=s.index
        )

        result[s.isna()] = np.nan

        return result

    return (
        (s - minimum)
        /
        (maximum - minimum)
    )


def make_capability_key(df):

    return (
        df["Capability Type"]
        .fillna("Unknown")
        .astype(str)
        + "::"
        + df["Capability ID"]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# START
# ============================================================

print("=" * 72)
print("FORGE — WORKFOLD V6")
print("=" * 72)


# ============================================================
# LOAD DATA
# ============================================================

print("\n[1/12] Loading WORKTRACE...")

worktrace = pd.read_parquet(
    WORKTRACE_PATH
)

print(
    f"WORKTRACE shape: {worktrace.shape}"
)


print("\n[2/12] Loading SKILL SHADOW...")

shadow = pd.read_parquet(
    SKILL_SHADOW_PATH
)

print(
    f"SKILL SHADOW shape: {shadow.shape}"
)


# ============================================================
# VALIDATION
# ============================================================

required_worktrace = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",
    "Capability Type",
    "Capability ID",
    "Capability Name",
    "Task Capability Weight",
]


required_shadow = [
    "O*NET-SOC Code",
    "Capability Type",
    "Capability ID",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
]


missing_worktrace = [
    c
    for c in required_worktrace
    if c not in worktrace.columns
]


missing_shadow = [
    c
    for c in required_shadow
    if c not in shadow.columns
]


if missing_worktrace:

    raise ValueError(
        "Missing WORKTRACE columns: "
        + str(missing_worktrace)
    )


if missing_shadow:

    raise ValueError(
        "Missing SKILL SHADOW columns: "
        + str(missing_shadow)
    )


# ============================================================
# CLEAN
# ============================================================

print("\n[3/12] Cleaning task-capability evidence...")


worktrace = worktrace.copy()
shadow = shadow.copy()


worktrace["Task"] = (
    worktrace["Task"]
    .fillna("")
    .astype(str)
    .str.strip()
)


worktrace["DWA Element Name"] = (
    worktrace["DWA Element Name"]
    .fillna("")
    .astype(str)
    .str.strip()
)


worktrace[
    "Task Capability Weight"
] = pd.to_numeric(
    worktrace[
        "Task Capability Weight"
    ],
    errors="coerce"
).fillna(0)


worktrace[
    "Task Capability Weight"
] = (
    worktrace[
        "Task Capability Weight"
    ]
    .clip(lower=0)
)


# ============================================================
# KEYS
# ============================================================

worktrace[
    "Capability Key"
] = make_capability_key(
    worktrace
)


shadow[
    "Capability Key"
] = make_capability_key(
    shadow
)


worktrace["Task Key"] = (
    worktrace[
        "O*NET-SOC Code"
    ]
    .astype(str)
    + "::"
    + worktrace[
        "Task ID"
    ]
    .astype(str)
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

before = len(worktrace)


worktrace = worktrace.drop_duplicates(
    subset=[
        "O*NET-SOC Code",
        "Task ID",
        "Capability Key",
    ]
)


print(
    "Duplicate task-capability rows removed:",
    before - len(worktrace)
)


# ============================================================
# CAPABILITY WEIGHT WITHIN TASK
# ============================================================

task_weight_sum = (
    worktrace
    .groupby(
        "Task Key"
    )[
        "Task Capability Weight"
    ]
    .transform("sum")
)


task_weight_sum = (
    task_weight_sum
    .replace(
        0,
        np.nan
    )
)


worktrace[
    "Capability_Weight_Within_Task"
] = (
    worktrace[
        "Task Capability Weight"
    ]
    /
    task_weight_sum
).fillna(0)


# ============================================================
# TASK IMPORTANCE
#
# Raw capability evidence -> task importance
# within occupation.
# ============================================================

task_importance = (
    worktrace
    .groupby(
        [
            "O*NET-SOC Code",
            "Task Key",
        ]
    )[
        "Task Capability Weight"
    ]
    .sum()
    .reset_index()
    .rename(
        columns={
            "Task Capability Weight":
            "Task_Raw_Importance"
        }
    )
)


occupation_importance = (
    task_importance
    .groupby(
        "O*NET-SOC Code"
    )[
        "Task_Raw_Importance"
    ]
    .transform("sum")
)


occupation_importance = (
    occupation_importance
    .replace(
        0,
        np.nan
    )
)


task_importance[
    "Task_Importance"
] = (
    task_importance[
        "Task_Raw_Importance"
    ]
    /
    occupation_importance
).fillna(0)


worktrace = worktrace.merge(
    task_importance[
        [
            "Task Key",
            "Task_Raw_Importance",
            "Task_Importance",
        ]
    ],
    on="Task Key",
    how="left"
)


# ============================================================
# SKILL SHADOW JOIN
# ============================================================

print(
    "\n[4/12] Joining capability-preservation evidence..."
)


shadow_small = (
    shadow[
        [
            "O*NET-SOC Code",
            "Capability Key",
            "Skill_Shadow",
            "Capability_Risk",
            "Capability_Criticality",
        ]
    ]
    .drop_duplicates(
        subset=[
            "O*NET-SOC Code",
            "Capability Key",
        ]
    )
)


worktrace = worktrace.merge(
    shadow_small,
    on=[
        "O*NET-SOC Code",
        "Capability Key",
    ],
    how="left",
    indicator="_shadow_match"
)


worktrace[
    "Shadow_Matched"
] = (
    worktrace[
        "_shadow_match"
    ]
    == "both"
)


# ============================================================
# EVIDENCE COVERAGE
# ============================================================

worktrace[
    "Matched_Capability_Weight"
] = np.where(
    worktrace[
        "Shadow_Matched"
    ],
    worktrace[
        "Capability_Weight_Within_Task"
    ],
    0
)


coverage = (
    worktrace
    .groupby(
        "Task Key"
    )[
        "Matched_Capability_Weight"
    ]
    .sum()
    .rename(
        "Shadow_Evidence_Coverage"
    )
    .reset_index()
)


worktrace = worktrace.merge(
    coverage,
    on="Task Key",
    how="left"
)


worktrace[
    "Shadow_Evidence_Coverage"
] = (
    worktrace[
        "Shadow_Evidence_Coverage"
    ]
    .fillna(0)
    .clip(0, 1)
)


# ============================================================
# OCCUPATION FALLBACK EVIDENCE
# ============================================================

print(
    "\nBuilding uncertainty-aware evidence..."
)


occupation_shadow_median = (
    shadow
    .groupby(
        "O*NET-SOC Code"
    )[
        "Skill_Shadow"
    ]
    .median()
)


occupation_risk_median = (
    shadow
    .groupby(
        "O*NET-SOC Code"
    )[
        "Capability_Risk"
    ]
    .median()
)


occupation_criticality_median = (
    shadow
    .groupby(
        "O*NET-SOC Code"
    )[
        "Capability_Criticality"
    ]
    .median()
)


global_shadow_median = (
    shadow[
        "Skill_Shadow"
    ].median()
)


global_risk_median = (
    shadow[
        "Capability_Risk"
    ].median()
)


global_criticality_median = (
    shadow[
        "Capability_Criticality"
    ].median()
)


worktrace[
    "Occupation_Shadow_Median"
] = (
    worktrace[
        "O*NET-SOC Code"
    ]
    .map(
        occupation_shadow_median
    )
    .fillna(
        global_shadow_median
    )
)


worktrace[
    "Occupation_Risk_Median"
] = (
    worktrace[
        "O*NET-SOC Code"
    ]
    .map(
        occupation_risk_median
    )
    .fillna(
        global_risk_median
    )
)


worktrace[
    "Occupation_Criticality_Median"
] = (
    worktrace[
        "O*NET-SOC Code"
    ]
    .map(
        occupation_criticality_median
    )
    .fillna(
        global_criticality_median
    )
)


# ============================================================
# EFFECTIVE EVIDENCE
#
# Missing evidence is NOT treated as zero.
# ============================================================

coverage_factor = (
    worktrace[
        "Shadow_Evidence_Coverage"
    ]
)


worktrace[
    "Effective_Skill_Shadow"
] = (
    coverage_factor
    *
    worktrace[
        "Skill_Shadow"
    ].fillna(
        worktrace[
            "Occupation_Shadow_Median"
        ]
    )
    +
    (
        1
        - coverage_factor
    )
    *
    worktrace[
        "Occupation_Shadow_Median"
    ]
)


worktrace[
    "Effective_Capability_Risk"
] = (
    coverage_factor
    *
    worktrace[
        "Capability_Risk"
    ].fillna(
        worktrace[
            "Occupation_Risk_Median"
        ]
    )
    +
    (
        1
        - coverage_factor
    )
    *
    worktrace[
        "Occupation_Risk_Median"
    ]
)


worktrace[
    "Effective_Criticality"
] = (
    coverage_factor
    *
    worktrace[
        "Capability_Criticality"
    ].fillna(
        worktrace[
            "Occupation_Criticality_Median"
        ]
    )
    +
    (
        1
        - coverage_factor
    )
    *
    worktrace[
        "Occupation_Criticality_Median"
    ]
)


# ============================================================
# TASK LEVEL AGGREGATION
# ============================================================

print(
    "\n[5/12] Creating one row per task..."
)


def aggregate_task(group):

    weights = group[
        "Capability_Weight_Within_Task"
    ].to_numpy(
        dtype=float
    )


    return pd.Series({

        "Task_Skill_Shadow":
            weighted_mean(
                group[
                    "Effective_Skill_Shadow"
                ],
                weights
            ),

        "Task_Capability_Risk":
            weighted_mean(
                group[
                    "Effective_Capability_Risk"
                ],
                weights
            ),

        "Task_Capability_Criticality":
            weighted_mean(
                group[
                    "Effective_Criticality"
                ],
                weights
            ),

        "Shadow_Evidence_Coverage":
            group[
                "Matched_Capability_Weight"
            ].sum(),

    })


task_metrics = (
    worktrace
    .groupby(
        "Task Key"
    )
    .apply(
        aggregate_task,
        include_groups=False
    )
    .reset_index()
)


# ============================================================
# TASK METADATA
# ============================================================

metadata = (
    worktrace[
        [
            "Task Key",
            "O*NET-SOC Code",
            "Occupation Title",
            "Task ID",
            "Task",
            "DWA Element Name",
            "Task_Raw_Importance",
            "Task_Importance",
        ]
    ]
    .drop_duplicates(
        subset=[
            "Task Key"
        ]
    )
)


tasks = metadata.merge(
    task_metrics,
    on="Task Key",
    how="left"
)


# ============================================================
# PRIMARY CAPABILITIES
# ============================================================

print(
    "\n[6/12] Extracting primary capabilities..."
)


def get_primary_capabilities(group):

    temp = (
        group[
            [
                "Capability Name",
                "Capability_Weight_Within_Task",
            ]
        ]
        .dropna(
            subset=[
                "Capability Name"
            ]
        )
        .drop_duplicates()
        .sort_values(
            "Capability_Weight_Within_Task",
            ascending=False
        )
        .head(5)
    )

    return ", ".join(
        temp[
            "Capability Name"
        ]
        .astype(str)
        .tolist()
    )


primary_capabilities = (
    worktrace
    .groupby(
        "Task Key"
    )
    .apply(
        get_primary_capabilities,
        include_groups=False
    )
    .rename(
        "Primary_Capabilities"
    )
    .reset_index()
)


tasks = tasks.merge(
    primary_capabilities,
    on="Task Key",
    how="left"
)


# ============================================================
# TASK TEXT
# ============================================================

tasks[
    "Task_Text"
] = (
    tasks[
        "Task"
    ]
    .fillna("")
    .astype(str)
    + ". "
    +
    tasks[
        "DWA Element Name"
    ]
    .fillna("")
    .astype(str)
)


tasks[
    "Task_Text"
] = (
    tasks[
        "Task_Text"
    ]
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip()
)


# ============================================================
# SENTENCE TRANSFORMER
# ============================================================

print(
    "\n[7/12] Loading SentenceTransformer..."
)


model = SentenceTransformer(
    MODEL_NAME
)


print(
    "Encoding automation anchors..."
)


automation_embeddings = model.encode(
    AUTOMATION_ANCHORS,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False
)


print(
    "Encoding human anchors..."
)


human_embeddings = model.encode(
    HUMAN_ANCHORS,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=False
)


print(
    f"Encoding {len(tasks):,} tasks..."
)


task_embeddings = model.encode(
    tasks[
        "Task_Text"
    ].tolist(),
    batch_size=256,
    convert_to_numpy=True,
    normalize_embeddings=True,
    show_progress_bar=True
)


# ============================================================
# SEMANTIC SUITABILITY
# ============================================================

print(
    "\n[8/12] Calculating AI/Human semantic suitability..."
)


automation_scores = (
    task_embeddings
    @ automation_embeddings.T
)


human_scores = (
    task_embeddings
    @ human_embeddings.T
)


tasks[
    "Automation_Max_Similarity"
] = (
    automation_scores.max(
        axis=1
    )
)


tasks[
    "Human_Max_Similarity"
] = (
    human_scores.max(
        axis=1
    )
)


tasks[
    "Automation_Human_Balance"
] = (
    tasks[
        "Automation_Max_Similarity"
    ]
    -
    tasks[
        "Human_Max_Similarity"
    ]
)


# Semantic suitability index.
#
# [-1,+1] -> [0,1]
#
# NOT probability.

tasks[
    "Task_AI_Suitability"
] = (
    (
        tasks[
            "Automation_Human_Balance"
        ]
        + 1
    )
    / 2
).clip(
    0,
    1
)


tasks[
    "Task_Human_Suitability"
] = (
    1
    -
    tasks[
        "Task_AI_Suitability"
    ]
)


# ============================================================
# NORMALIZED PRESERVATION SIGNALS
# ============================================================

print(
    "\n[9/12] Building preservation constraints..."
)


tasks[
    "Risk_Normalized"
] = minmax(
    tasks[
        "Task_Capability_Risk"
    ]
).fillna(0.5)


tasks[
    "Shadow_Normalized"
] = minmax(
    tasks[
        "Task_Skill_Shadow"
    ]
).fillna(0.5)


tasks[
    "Criticality_Normalized"
] = minmax(
    tasks[
        "Task_Capability_Criticality"
    ]
).fillna(0.5)


# ------------------------------------------------------------
# Preservation pressure
# ------------------------------------------------------------

tasks[
    "Preservation_Pressure"
] = (
    0.45
    *
    tasks[
        "Risk_Normalized"
    ]

    +

    0.35
    *
    tasks[
        "Shadow_Normalized"
    ]

    +

    0.20
    *
    tasks[
        "Criticality_Normalized"
    ]
).clip(
    0,
    1
)


# ============================================================
# V6 HUMAN PRESERVATION FLOOR
#
# This is the major difference from V5.
#
# High preservation pressure creates an explicit human floor.
#
# Example:
#
# pressure = 0.0 -> floor ≈ 0%
# pressure = 0.5 -> meaningful human retention
# pressure = 1.0 -> up to 80% human retention
# ============================================================

tasks[
    "Human_Preservation_Floor"
] = (
    MAX_PRESERVATION_HUMAN_FLOOR
    *
    (
        tasks[
            "Preservation_Pressure"
        ]
        ** PRESERVATION_FLOOR_EXPONENT
    )
).clip(
    0,
    MAX_PRESERVATION_HUMAN_SHARE
    if False
    else MAX_PRESERVATION_HUMAN_FLOOR
)


# ============================================================
# AI CEILING
#
# AI ceiling depends primarily on suitability,
# then preservation pressure.
# ============================================================

tasks[
    "AI_Ceiling"
] = (
    GLOBAL_MAX_AI_SHARE
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
)


# Preservation protection.

tasks[
    "AI_Ceiling"
] = (
    tasks[
        "AI_Ceiling"
    ]
    *
    (
        1
        -
        0.55
        *
        tasks[
            "Preservation_Pressure"
        ]
    )
)


# Explicit human floor.

tasks[
    "AI_Ceiling"
] = np.minimum(
    tasks[
        "AI_Ceiling"
    ],
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
        GLOBAL_MIN_AI_SHARE,
        GLOBAL_MAX_AI_SHARE
    )
)


# ============================================================
# EVIDENCE-DRIVEN PREFERRED AI SHARE
# ============================================================

tasks[
    "AI_Preferred_Share"
] = (
    GLOBAL_MAX_AI_SHARE
    *
    tasks[
        "Task_AI_Suitability"
    ]
    *
    (
        1
        -
        0.30
        *
        tasks[
            "Preservation_Pressure"
        ]
    )
)


tasks[
    "AI_Preferred_Share"
] = np.minimum(
    tasks[
        "AI_Preferred_Share"
    ],
    tasks[
        "AI_Ceiling"
    ]
)


tasks[
    "AI_Preferred_Share"
] = (
    tasks[
        "AI_Preferred_Share"
    ]
    .clip(
        0,
        GLOBAL_MAX_AI_SHARE
    )
)


# ============================================================
# OCCUPATION FEASIBILITY
# ============================================================

occupation_feasibility = (
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
                "AI_Ceiling"
            ]
        ),
        include_groups=False
    )
    .rename(
        "Max_Feasible_AI_Adoption"
    )
    .reset_index()
)


tasks = tasks.merge(
    occupation_feasibility,
    on="O*NET-SOC Code",
    how="left"
)


tasks[
    "Target_Feasibility"
] = np.where(
    tasks[
        "Max_Feasible_AI_Adoption"
    ]
    >=
    AI_ADOPTION_TARGET,
    "Feasible",
    "Infeasible"
)


# ============================================================
# V6 OPTIMIZATION
# ============================================================

print(
    "\n[10/12] Running preservation-constrained optimization..."
)


def optimize_occupation(group):

    group = group.copy()

    n = len(group)

    if n == 0:
        return group


    # --------------------------------------------------------
    # Arrays
    # --------------------------------------------------------

    weights = group[
        "Task_Importance"
    ].to_numpy(float)


    suitability = group[
        "Task_AI_Suitability"
    ].to_numpy(float)


    preservation = group[
        "Preservation_Pressure"
    ].to_numpy(float)


    shadow_values = group[
        "Task_Skill_Shadow"
    ].to_numpy(float)


    preferred = group[
        "AI_Preferred_Share"
    ].to_numpy(float)


    ceiling = group[
        "AI_Ceiling"
    ].to_numpy(float)


    human_floor = group[
        "Human_Preservation_Floor"
    ].to_numpy(float)


    # --------------------------------------------------------
    # Numerical cleanup
    # --------------------------------------------------------

    weights = np.nan_to_num(
        weights,
        nan=0
    )


    suitability = np.nan_to_num(
        suitability,
        nan=0.5
    )


    preservation = np.nan_to_num(
        preservation,
        nan=0.5
    )


    shadow_values = np.nan_to_num(
        shadow_values,
        nan=0.5
    )


    preferred = np.nan_to_num(
        preferred,
        nan=0
    )


    ceiling = np.nan_to_num(
        ceiling,
        nan=0
    )


    human_floor = np.nan_to_num(
        human_floor,
        nan=0
    )


    # --------------------------------------------------------
    # Normalize task weights.
    # --------------------------------------------------------

    weight_sum = weights.sum()

    if weight_sum <= 0:

        weights = (
            np.ones(n)
            / n
        )

    else:

        weights = (
            weights
            / weight_sum
        )


    # --------------------------------------------------------
    # Initial allocation
    # --------------------------------------------------------

    x0 = np.minimum(
        preferred,
        ceiling
    )


    # --------------------------------------------------------
    # IMPORTANT V6 CONSTRAINT
    #
    # Weighted occupation AI adoption cannot exceed
    # the requested scenario target.
    #
    # This prevents the optimizer from silently exceeding
    # the scenario.
    #
    # It is an inequality, NOT an equality.
    #
    # Therefore the optimizer can choose less than 50%
    # if the evidence does not justify additional automation.
    # --------------------------------------------------------

    target_constraint = {
        "type": "ineq",
        "fun": lambda x:
            AI_ADOPTION_TARGET
            -
            np.sum(
                weights
                * x
            )
    }


    # --------------------------------------------------------
    # Objective
    #
    # Minimize:
    #
    #   preference deviation
    #   + preservation loss
    #   + shadow loss
    #   + target deviation
    #   - automation benefit
    #
    # The explicit bounds enforce human preservation.
    # --------------------------------------------------------

    def objective(x):

        weighted_ai = np.sum(
            weights
            * x
        )


        # --------------------------------------------
        # Automation value
        # --------------------------------------------

        automation_value = np.sum(
            weights
            *
            suitability
            *
            x
        )


        # --------------------------------------------
        # Preservation cost
        # --------------------------------------------

        preservation_cost = np.sum(
            weights
            *
            preservation
            *
            x
        )


        # --------------------------------------------
        # Skill Shadow cost
        # --------------------------------------------

        shadow_cost = np.sum(
            weights
            *
            shadow_values
            *
            x
        )


        # --------------------------------------------
        # Evidence preference deviation
        # --------------------------------------------

        preference_cost = np.sum(
            weights
            *
            (
                x
                -
                preferred
            )
            ** 2
        )


        # --------------------------------------------
        # Target deviation
        #
        # Only penalize being below target.
        # Since exceeding target is already forbidden.
        # --------------------------------------------

        target_gap = max(
            0.0,
            AI_ADOPTION_TARGET
            -
            weighted_ai
        )


        target_cost = (
            target_gap
            ** 2
        )


        return (

            PREFERENCE_WEIGHT
            *
            preference_cost

            +

            PRESERVATION_WEIGHT
            *
            preservation_cost

            +

            SHADOW_WEIGHT
            *
            shadow_cost

            +

            TARGET_WEIGHT
            *
            target_cost

            -

            AUTOMATION_WEIGHT
            *
            automation_value

        )


    # --------------------------------------------------------
    # Bounds
    # --------------------------------------------------------

    bounds = [
        (
            max(
                GLOBAL_MIN_AI_SHARE,
                0.0
            ),
            float(
                ceiling[i]
            )
        )
        for i in range(n)
    ]


    # --------------------------------------------------------
    # Optimize
    # --------------------------------------------------------

    success = False

    try:

        result = minimize(
            objective,
            x0=x0,
            method="SLSQP",
            bounds=bounds,
            constraints=[
                target_constraint
            ],
            options={
                "maxiter": 300,
                "ftol": 1e-9,
                "disp": False,
            }
        )


        if result.success:

            allocation = result.x
            success = True

        else:

            allocation = x0


    except Exception:

        allocation = x0


    # --------------------------------------------------------
    # Safety clipping
    # --------------------------------------------------------

    allocation = np.clip(
        allocation,
        0,
        ceiling
    )


    # --------------------------------------------------------
    # Final adoption
    # --------------------------------------------------------

    actual_ai = np.sum(
        weights
        *
        allocation
    )


    actual_human = (
        1
        -
        actual_ai
    )


    max_feasible = np.sum(
        weights
        *
        ceiling
    )


    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    group[
        "AI_Share"
    ] = allocation


    group[
        "Human_Share"
    ] = (
        1
        -
        allocation
    )


    group[
        "Actual_AI_Adoption"
    ] = actual_ai


    group[
        "Actual_Human_Adoption"
    ] = actual_human


    group[
        "Target_AI_Adoption"
    ] = AI_ADOPTION_TARGET


    group[
        "Target_Gap_Percentage_Points"
    ] = (
        actual_ai
        -
        AI_ADOPTION_TARGET
    ) * 100


    group[
        "Max_Feasible_AI_Adoption"
    ] = max_feasible


    group[
        "Optimization_Success"
    ] = success


    return group


# ============================================================
# RUN OCCUPATION OPTIMIZATION
# ============================================================

optimized = []


for occupation_code, group in tasks.groupby(
    "O*NET-SOC Code",
    sort=False
):

    optimized.append(
        optimize_occupation(
            group
        )
    )


tasks = pd.concat(
    optimized,
    ignore_index=True
)


# ============================================================
# WORK MODEL
#
# V6 uses both allocation and suitability.
#
# AI-led requires:
#   allocation >= 65%
#   AND suitability >= 60%
#
# Hybrid:
#   meaningful shared delegation
#
# Human-led:
#   predominantly human work
# ============================================================

print(
    "\n[11/12] Creating workforce decisions..."
)


def classify_work_model(row):

    ai = row[
        "AI_Share"
    ]

    suitability = row[
        "Task_AI_Suitability"
    ]


    if (
        ai >= 0.65
        and
        suitability >= 0.60
    ):

        return "AI-led"


    if ai <= 0.35:

        return "Human-led"


    return "Hybrid"


tasks[
    "Work_Model"
] = tasks.apply(
    classify_work_model,
    axis=1
)


# ============================================================
# DECISION EXPLANATION
# ============================================================

def create_explanation(row):

    ai = row[
        "AI_Share"
    ]

    suitability = row[
        "Task_AI_Suitability"
    ]

    pressure = row[
        "Preservation_Pressure"
    ]

    shadow_value = row[
        "Task_Skill_Shadow"
    ]

    model = row[
        "Work_Model"
    ]

    evidence = row[
        "Evidence_Confidence"
    ] if "Evidence_Confidence" in row else row[
        "Shadow_Evidence_Coverage"
    ]


    if model == "AI-led":

        return (
            f"AI-led allocation of {ai*100:.1f}% is supported "
            f"by high automation suitability "
            f"({suitability*100:.1f}%). Preservation pressure "
            f"is {pressure*100:.1f}%, so the remaining human "
            f"role should retain appropriate oversight."
        )


    if model == "Hybrid":

        return (
            f"Hybrid allocation of {ai*100:.1f}% AI and "
            f"{(1-ai)*100:.1f}% human balances automation "
            f"suitability ({suitability*100:.1f}%) with "
            f"capability-preservation pressure "
            f"({pressure*100:.1f}%)."
        )


    return (
        f"Human-led allocation of {(1-ai)*100:.1f}% human "
        f"is maintained because evidence-supported AI "
        f"delegation is limited to {ai*100:.1f}%. Automation "
        f"suitability is {suitability*100:.1f}% and preservation "
        f"pressure is {pressure*100:.1f}%."
    )


tasks[
    "Decision_Explanation"
] = tasks.apply(
    create_explanation,
    axis=1
)


# ============================================================
# PERCENTAGE FIELDS
# ============================================================

tasks[
    "AI_Share_Percent"
] = (
    tasks[
        "AI_Share"
    ]
    * 100
)


tasks[
    "Human_Share_Percent"
] = (
    tasks[
        "Human_Share"
    ]
    * 100
)


tasks[
    "AI_Ceiling_Percent"
] = (
    tasks[
        "AI_Ceiling"
    ]
    * 100
)


tasks[
    "AI_Preferred_Share_Percent"
] = (
    tasks[
        "AI_Preferred_Share"
    ]
    * 100
)


tasks[
    "Task_AI_Suitability_Percent"
] = (
    tasks[
        "Task_AI_Suitability"
    ]
    * 100
)


tasks[
    "Task_Human_Suitability_Percent"
] = (
    tasks[
        "Task_Human_Suitability"
    ]
    * 100
)


tasks[
    "Preservation_Pressure_Percent"
] = (
    tasks[
        "Preservation_Pressure"
    ]
    * 100
)


tasks[
    "Human_Preservation_Floor_Percent"
] = (
    tasks[
        "Human_Preservation_Floor"
    ]
    * 100
)


tasks[
    "Evidence_Confidence_Percent"
] = (
    tasks[
        "Shadow_Evidence_Coverage"
    ]
    * 100
)


# ============================================================
# SORT
# ============================================================

tasks = tasks.sort_values(
    [
        "O*NET-SOC Code",
        "Task_Importance",
    ],
    ascending=[
        True,
        False,
    ]
).reset_index(
    drop=True
)


# ============================================================
# FINAL COLUMNS
# ============================================================

final_columns = [
    "O*NET-SOC Code",
    "Occupation Title",
    "Task ID",
    "Task",
    "DWA Element Name",

    "Primary_Capabilities",

    "Task_Raw_Importance",
    "Task_Importance",

    "Automation_Max_Similarity",
    "Human_Max_Similarity",
    "Automation_Human_Balance",

    "Task_AI_Suitability",
    "Task_AI_Suitability_Percent",

    "Task_Human_Suitability",
    "Task_Human_Suitability_Percent",

    "Task_Skill_Shadow",
    "Task_Capability_Risk",
    "Task_Capability_Criticality",

    "Risk_Normalized",
    "Shadow_Normalized",
    "Criticality_Normalized",

    "Preservation_Pressure",
    "Preservation_Pressure_Percent",

    "Human_Preservation_Floor",
    "Human_Preservation_Floor_Percent",

    "Shadow_Evidence_Coverage",
    "Evidence_Confidence_Percent",

    "AI_Preferred_Share",
    "AI_Preferred_Share_Percent",

    "AI_Ceiling",
    "AI_Ceiling_Percent",

    "AI_Share",
    "AI_Share_Percent",

    "Human_Share",
    "Human_Share_Percent",

    "Work_Model",

    "Actual_AI_Adoption",
    "Actual_Human_Adoption",

    "Target_AI_Adoption",
    "Target_Gap_Percentage_Points",

    "Max_Feasible_AI_Adoption",
    "Target_Feasibility",

    "Optimization_Success",

    "Decision_Explanation",

    "Task Key",
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
# FINAL VALIDATION
# ============================================================

print(
    "\n[12/12] Running V6 audit..."
)


print(
    "\n"
    + "=" * 72
)

print(
    "WORKFOLD V6 VALIDATION"
)

print(
    "=" * 72
)


# ------------------------------------------------------------
# SIZE
# ------------------------------------------------------------

print(
    f"\nRecords: {len(final_df):,}"
)


print(
    f"Unique tasks: "
    f"{final_df['Task Key'].nunique():,}"
)


print(
    "Task uniqueness:",
    (
        "PASSED"
        if len(final_df)
        ==
        final_df[
            "Task Key"
        ].nunique()
        else
        "FAILED"
    )
)


print(
    f"Unique occupations: "
    f"{final_df['O*NET-SOC Code'].nunique():,}"
)


# ------------------------------------------------------------
# WORK MODEL
# ------------------------------------------------------------

print(
    "\nWork model distribution:"
)


print(
    final_df[
        "Work_Model"
    ].value_counts()
)


# ------------------------------------------------------------
# AI ADOPTION
# ------------------------------------------------------------

occupation_results = (
    final_df
    .groupby(
        "O*NET-SOC Code"
    )
    .first()
)


print(
    "\nOccupation AI adoption:"
)


print(
    occupation_results[
        "Actual_AI_Adoption"
    ].describe()
)


mean_ai = (
    occupation_results[
        "Actual_AI_Adoption"
    ].mean()
)


print(
    f"\nMean AI adoption: "
    f"{mean_ai*100:.2f}%"
)


print(
    f"Requested target: "
    f"{AI_ADOPTION_TARGET*100:.2f}%"
)


print(
    f"Mean target gap: "
    f"{(
        occupation_results[
            'Actual_AI_Adoption'
        ]
        -
        AI_ADOPTION_TARGET
    ).mean()*100:.2f} pp"
)


# ------------------------------------------------------------
# FEASIBILITY
# ------------------------------------------------------------

print(
    "\nTarget feasibility:"
)


print(
    occupation_results[
        "Target_Feasibility"
    ].value_counts()
)


# ------------------------------------------------------------
# EVIDENCE
# ------------------------------------------------------------

print(
    "\nEvidence coverage:"
)


print(
    final_df[
        "Evidence_Confidence_Percent"
    ].describe()
)


# ------------------------------------------------------------
# CORRELATIONS
# ------------------------------------------------------------

print(
    "\n"
    + "-" * 72
)

print(
    "BEHAVIOR AUDIT"
)

print(
    "-" * 72
)


corr_suitability = (
    final_df[
        [
            "AI_Share",
            "Task_AI_Suitability",
        ]
    ]
    .corr()
    .iloc[
        0,
        1
    ]
)


corr_risk = (
    final_df[
        [
            "AI_Share",
            "Task_Capability_Risk",
        ]
    ]
    .corr()
    .iloc[
        0,
        1
    ]
)


corr_shadow = (
    final_df[
        [
            "AI_Share",
            "Task_Skill_Shadow",
        ]
    ]
    .corr()
    .iloc[
        0,
        1
    ]
)


corr_pressure = (
    final_df[
        [
            "AI_Share",
            "Preservation_Pressure",
        ]
    ]
    .corr()
    .iloc[
        0,
        1
    ]
)


print(
    f"AI share vs suitability: "
    f"{corr_suitability:.4f}"
)


print(
    f"AI share vs capability risk: "
    f"{corr_risk:.4f}"
)


print(
    f"AI share vs Skill Shadow: "
    f"{corr_shadow:.4f}"
)


print(
    f"AI share vs preservation pressure: "
    f"{corr_pressure:.4f}"
)


# ------------------------------------------------------------
# CEILING VIOLATIONS
# ------------------------------------------------------------

ceiling_violations = (
    final_df[
        "AI_Share"
    ]
    >
    final_df[
        "AI_Ceiling"
    ]
    + 1e-7
).sum()


print(
    f"\nAI ceiling violations: "
    f"{ceiling_violations}"
)


# ------------------------------------------------------------
# HUMAN FLOOR VIOLATIONS
# ------------------------------------------------------------

human_floor_violations = (
    final_df[
        "Human_Share"
    ]
    <
    final_df[
        "Human_Preservation_Floor"
    ]
    - 1e-7
).sum()


print(
    f"Human preservation floor violations: "
    f"{human_floor_violations}"
)


# ------------------------------------------------------------
# TARGET VIOLATIONS
# ------------------------------------------------------------

target_violations = (
    occupation_results[
        "Actual_AI_Adoption"
    ]
    >
    AI_ADOPTION_TARGET
    + 1e-7
).sum()


print(
    f"Occupation target violations: "
    f"{target_violations}"
)


# ------------------------------------------------------------
# RANGE CHECKS
# ------------------------------------------------------------

print(
    "\nRange checks:"
)


checks = {

    "AI_Share":
        final_df[
            "AI_Share"
        ]
        .between(
            0,
            1
        )
        .all(),

    "Human_Share":
        final_df[
            "Human_Share"
        ]
        .between(
            0,
            1
        )
        .all(),

    "AI_Suitability":
        final_df[
            "Task_AI_Suitability"
        ]
        .between(
            0,
            1
        )
        .all(),

    "Preservation_Pressure":
        final_df[
            "Preservation_Pressure"
        ]
        .between(
            0,
            1
        )
        .all(),

    "Human_Preservation_Floor":
        final_df[
            "Human_Preservation_Floor"
        ]
        .between(
            0,
            1
        )
        .all(),

    "Evidence":
        final_df[
            "Shadow_Evidence_Coverage"
        ]
        .between(
            0,
            1
        )
        .all(),
}


for name, passed in checks.items():

    print(
        f"{name}:",
        (
            "PASSED"
            if passed
            else
            "FAILED"
        )
    )


# ============================================================
# HIGH AI ALLOCATION
# ============================================================

print(
    "\n"
    + "=" * 72
)

print(
    "HIGHEST AI ALLOCATION"
)

print(
    "=" * 72
)


highest = (
    final_df
    .sort_values(
        "AI_Share",
        ascending=False
    )
    [
        [
            "Occupation Title",
            "Task",
            "AI_Share_Percent",
            "Task_AI_Suitability_Percent",
            "Task_Skill_Shadow",
            "Preservation_Pressure_Percent",
            "Human_Preservation_Floor_Percent",
            "Work_Model",
        ]
    ]
    .head(15)
)


print(
    highest.to_string(
        index=False
    )
)


# ============================================================
# LOW AI ALLOCATION
# ============================================================

print(
    "\n"
    + "=" * 72
)

print(
    "LOWEST AI ALLOCATION"
)

print(
    "=" * 72
)


lowest = (
    final_df
    .sort_values(
        "AI_Share",
        ascending=True
    )
    [
        [
            "Occupation Title",
            "Task",
            "AI_Share_Percent",
            "Task_AI_Suitability_Percent",
            "Task_Skill_Shadow",
            "Preservation_Pressure_Percent",
            "Human_Preservation_Floor_Percent",
            "Work_Model",
        ]
    ]
    .head(15)
)


print(
    lowest.to_string(
        index=False
    )
)


# ============================================================
# SAVE
# ============================================================

print(
    "\nSaving WORKFOLD V6..."
)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


final_df.to_parquet(
    OUTPUT_PARQUET,
    index=False
)


final_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# COMPLETE
# ============================================================

print(
    "\n"
    + "=" * 72
)

print(
    "WORKFOLD V6 COMPLETE"
)

print(
    "=" * 72
)

print(
    f"Parquet: {OUTPUT_PARQUET}"
)

print(
    f"CSV:     {OUTPUT_CSV}"
)

print(
    f"Final shape: {final_df.shape}"
)

print(
    "=" * 72
)