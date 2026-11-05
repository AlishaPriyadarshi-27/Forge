from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# FORGE — WORKFOLD V8 VALIDATION / AUDIT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_workfold_v8.parquet"
)


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def correlation(df, x, y, method="pearson"):
    temp = df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()

    if len(temp) < 3:
        return np.nan

    if temp[x].nunique() < 2 or temp[y].nunique() < 2:
        return np.nan

    return temp[x].corr(temp[y], method=method)


def check_range(df, column, low=0.0, high=1.0):

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    below = int((values < low).sum())
    above = int((values > high).sum())
    missing = int(values.isna().sum())

    passed = (
        below == 0
        and above == 0
    )

    print(
        f"{column:35s} "
        f"below={below:,} "
        f"above={above:,} "
        f"missing={missing:,} "
        f"→ {'PASS' if passed else 'FAIL'}"
    )

    return passed


def show_table(data, columns, n=10):

    columns = [
        c for c in columns
        if c in data.columns
    ]

    if len(columns) == 0:
        print("No requested columns available.")
        return

    print(
        data[columns]
        .head(n)
        .to_string(index=False)
    )


# ============================================================
# 1. LOAD V8
# ============================================================

section("1. LOADING WORKFOLD V8")

print("Input:")
print(INPUT_FILE)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nFile not found:\n{INPUT_FILE}"
    )

df = pd.read_parquet(INPUT_FILE)

print("\nLoaded successfully.")
print(f"Shape   : {df.shape}")
print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns):,}")


# ============================================================
# 2. SCHEMA
# ============================================================

section("2. SCHEMA CHECK")

for i, col in enumerate(df.columns, start=1):
    print(f"{i:02d}. {col}")


# ============================================================
# 3. REQUIRED COLUMNS
# ============================================================

section("3. REQUIRED COLUMN CHECK")

required_columns = [
    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",
    "Task",

    "Task_Skill_Shadow",
    "Task_Skill_Shadow_Percent",

    "Task_Capability_Risk",
    "Task_Criticality",
    "Task_Evidence_Coverage",
    "Evidence_Confidence_Percent",

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

missing_required = [
    col
    for col in required_columns
    if col not in df.columns
]

if not missing_required:

    print(
        f"All {len(required_columns)} required columns found."
    )
    print("Schema: PASS")

else:

    print("Missing columns:")

    for col in missing_required:
        print(" -", col)

    print("Schema: FAIL")


# ============================================================
# 4. TASK UNIQUENESS
# ============================================================

section("4. TASK UNIQUENESS")

if "Task ID" in df.columns:

    unique_ids = df["Task ID"].nunique()
    duplicate_ids = df["Task ID"].duplicated().sum()

    print(f"Total Task IDs   : {len(df):,}")
    print(f"Unique Task IDs  : {unique_ids:,}")
    print(f"Duplicate IDs    : {duplicate_ids:,}")

    if duplicate_ids == 0:
        print("Task ID uniqueness: PASS")
    else:
        print("Task ID uniqueness: FAIL")


# ============================================================
# 5. OCCUPATION CHECK
# ============================================================

section("5. OCCUPATION CHECK")

if "Occupation Title" in df.columns:
    print(
        "Unique occupations:",
        df["Occupation Title"].nunique()
    )

if "O*NET-SOC Code" in df.columns:
    print(
        "Unique O*NET occupations:",
        df["O*NET-SOC Code"].nunique()
    )


# ============================================================
# 6. MISSING VALUES
# ============================================================

section("6. IMPORTANT MISSING VALUES")

important_columns = [
    "Occupation Title",
    "Task",
    "Task_Skill_Shadow",
    "Task_Capability_Risk",
    "Task_Criticality",
    "Task_Evidence_Coverage",
    "Task_AI_Suitability",
    "Skill_Shadow_Normalized",
    "Capability_Risk_Normalized",
    "Preservation_Pressure",
    "Human_Preservation_Floor",
    "AI_Ceiling",
    "AI_Allocation_Score",
    "Safe_AI_Bound",
    "Maximum_Safe_AI_Adoption",
    "AI_Share",
    "Human_Share",
    "Work_Model",
]

for col in important_columns:

    if col not in df.columns:

        print(
            f"{col:35s} NOT FOUND"
        )

        continue

    missing = df[col].isna().sum()
    percentage = (
        missing / len(df) * 100
    )

    print(
        f"{col:35s} "
        f"missing={missing:8,} "
        f"({percentage:.3f}%)"
    )


# ============================================================
# 7. RANGE CHECK
# ============================================================

section("7. RANGE CHECKS")

range_columns = [
    "Task_Evidence_Coverage",
    "Task_AI_Suitability",
    "Skill_Shadow_Normalized",
    "Capability_Risk_Normalized",
    "Criticality_Normalized",
    "Preservation_Pressure",
    "Human_Preservation_Floor",
    "AI_Ceiling",
    "AI_Allocation_Score",
    "Safe_AI_Bound",
    "Maximum_Safe_AI_Adoption",
    "Effective_AI_Target",
    "AI_Share",
    "Human_Share",
]

for col in range_columns:

    if col in df.columns:
        check_range(df, col)


# ============================================================
# 8. PERCENTAGE COLUMNS
# ============================================================

section("8. PERCENTAGE COLUMN RANGE CHECK")

percentage_columns = [
    "Task_Skill_Shadow_Percent",
    "Evidence_Confidence_Percent",
    "Task_AI_Suitability_Percent",
    "Preservation_Pressure_Percent",
    "Human_Preservation_Floor_Percent",
    "Maximum_Safe_AI_Adoption_Percent",
    "Requested_Target_Percent",
    "Effective_AI_Target_Percent",
    "Safe_Target_Gap_Percent",
    "AI_Share_Percent",
    "Human_Share_Percent",
]

for col in percentage_columns:

    if col in df.columns:
        check_range(df, col, 0, 100)


# ============================================================
# 9. AI + HUMAN CONSISTENCY
# ============================================================

section("9. AI + HUMAN SHARE CONSISTENCY")

if (
    "AI_Share" in df.columns
    and "Human_Share" in df.columns
):

    temp = df[
        ["AI_Share", "Human_Share"]
    ].apply(
        pd.to_numeric,
        errors="coerce"
    ).dropna()

    total_share = (
        temp["AI_Share"]
        + temp["Human_Share"]
    )

    deviation = (
        total_share - 1
    ).abs()

    print(
        f"Mean deviation : {deviation.mean():.10f}"
    )

    print(
        f"Max deviation  : {deviation.max():.10f}"
    )

    violations = (
        deviation > 1e-6
    ).sum()

    print(
        f"Violations     : {violations:,}"
    )

    if violations == 0:
        print("AI + Human = 100%: PASS")
    else:
        print("AI + Human = 100%: FAIL")


# ============================================================
# 10. AI ALLOCATION STATISTICS
# ============================================================

section("10. AI ALLOCATION STATISTICS")

for col in [
    "AI_Share",
    "Human_Share",
    "Task_AI_Suitability",
    "Skill_Shadow_Normalized",
    "Capability_Risk_Normalized",
    "Preservation_Pressure",
    "AI_Ceiling",
    "Maximum_Safe_AI_Adoption",
]:

    if col not in df.columns:
        continue

    print(f"\n{col}")

    print(
        pd.to_numeric(
            df[col],
            errors="coerce"
        )
        .describe(
            percentiles=[
                0.10,
                0.25,
                0.50,
                0.75,
                0.90,
            ]
        )
        .to_string()
    )


# ============================================================
# 11. WORK MODEL DISTRIBUTION
# ============================================================

section("11. WORK MODEL DISTRIBUTION")

if "Work_Model" in df.columns:

    counts = (
        df["Work_Model"]
        .value_counts(dropna=False)
    )

    print(counts.to_string())

    print("\nPercentages:")

    percentages = (
        df["Work_Model"]
        .value_counts(
            normalize=True,
            dropna=False
        )
        * 100
    )

    print(
        percentages.round(2)
        .to_string()
    )


# ============================================================
# 12. CORRELATION AUDIT
# ============================================================

section("12. CORRELATION AUDIT")

features = [
    "Task_AI_Suitability",
    "Skill_Shadow_Normalized",
    "Capability_Risk_Normalized",
    "Preservation_Pressure",
    "Human_Preservation_Floor",
    "AI_Ceiling",
    "Maximum_Safe_AI_Adoption",
]

if "AI_Share" in df.columns:

    for feature in features:

        if feature not in df.columns:
            continue

        pearson = correlation(
            df,
            "AI_Share",
            feature,
            "pearson"
        )

        spearman = correlation(
            df,
            "AI_Share",
            feature,
            "spearman"
        )

        print(
            f"\nAI_Share vs {feature}"
        )

        print(
            f"  Pearson : {pearson:.4f}"
        )

        print(
            f"  Spearman: {spearman:.4f}"
        )


# ============================================================
# 13. DECILE ANALYSIS
# ============================================================

section("13. DECILE MONOTONICITY AUDIT")


def decile_analysis(
    df,
    feature,
    target="AI_Share"
):

    print(
        f"\n--- {feature} ---"
    )

    if feature not in df.columns:
        print("Feature not found.")
        return

    if target not in df.columns:
        print("Target not found.")
        return

    temp = df[
        [feature, target]
    ].apply(
        pd.to_numeric,
        errors="coerce"
    ).dropna()

    if len(temp) < 20:
        print("Insufficient data.")
        return

    try:

        temp["Decile"] = pd.qcut(
            temp[feature],
            q=10,
            labels=False,
            duplicates="drop"
        )

    except Exception as e:

        print("Could not create deciles:")
        print(e)
        return

    result = (
        temp.groupby(
            "Decile",
            observed=True
        )
        .agg(
            Feature_Mean=(
                feature,
                "mean"
            ),
            AI_Share_Mean=(
                target,
                "mean"
            ),
            Count=(
                target,
                "size"
            )
        )
        .reset_index()
    )

    print(
        result.to_string(
            index=False,
            formatters={
                "Feature_Mean":
                    "{:.4f}".format,
                "AI_Share_Mean":
                    "{:.4f}".format,
            }
        )
    )

    ai_values = (
        result["AI_Share_Mean"]
        .values
    )

    differences = np.diff(
        ai_values
    )

    increasing = np.all(
        differences >= -1e-6
    )

    decreasing = np.all(
        differences <= 1e-6
    )

    if increasing:
        print(
            "Trend: MONOTONIC INCREASING"
        )

    elif decreasing:
        print(
            "Trend: MONOTONIC DECREASING"
        )

    else:
        print(
            "Trend: NON-MONOTONIC"
        )


decile_analysis(
    df,
    "Task_AI_Suitability"
)

decile_analysis(
    df,
    "Skill_Shadow_Normalized"
)

decile_analysis(
    df,
    "Capability_Risk_Normalized"
)

decile_analysis(
    df,
    "Preservation_Pressure"
)


# ============================================================
# 14. AI CEILING CHECK
# ============================================================

section("14. AI CEILING CHECK")

if (
    "AI_Share" in df.columns
    and "AI_Ceiling" in df.columns
):

    ai = pd.to_numeric(
        df["AI_Share"],
        errors="coerce"
    )

    ceiling = pd.to_numeric(
        df["AI_Ceiling"],
        errors="coerce"
    )

    violations = (
        ai > ceiling + 1e-8
    )

    print(
        f"Ceiling violations: "
        f"{violations.sum():,}"
    )

    if violations.sum() == 0:
        print("AI ceiling constraint: PASS")
    else:
        print("AI ceiling constraint: FAIL")

        print(
            df.loc[
                violations,
                [
                    "Occupation Title",
                    "Task",
                    "AI_Share",
                    "AI_Ceiling",
                ]
            ]
            .head(10)
            .to_string(index=False)
        )


# ============================================================
# 15. HUMAN PRESERVATION FLOOR CHECK
# ============================================================

section("15. HUMAN PRESERVATION FLOOR CHECK")

if (
    "AI_Share" in df.columns
    and "Human_Preservation_Floor" in df.columns
):

    ai = pd.to_numeric(
        df["AI_Share"],
        errors="coerce"
    )

    human_floor = pd.to_numeric(
        df["Human_Preservation_Floor"],
        errors="coerce"
    )

    human_share = 1 - ai

    violations = (
        human_share
        < human_floor - 1e-8
    )

    print(
        f"Human floor violations: "
        f"{violations.sum():,}"
    )

    if violations.sum() == 0:
        print("Human preservation floor: PASS")
    else:
        print("Human preservation floor: FAIL")


# ============================================================
# 16. SAFE BUDGET UTILIZATION
# ============================================================

section("16. SAFE-BUDGET UTILIZATION")

if (
    "AI_Share" in df.columns
    and "Maximum_Safe_AI_Adoption" in df.columns
    and "Occupation Title" in df.columns
):

    occupation_stats = (
        df.groupby(
            "Occupation Title"
        )
        .agg(
            Mean_AI_Share=(
                "AI_Share",
                "mean"
            ),
            Maximum_Safe_AI_Adoption=(
                "Maximum_Safe_AI_Adoption",
                "mean"
            ),
            Task_Count=(
                "AI_Share",
                "size"
            )
        )
        .reset_index()
    )

    occupation_stats[
        "Budget_Utilization"
    ] = (
        occupation_stats["Mean_AI_Share"]
        /
        occupation_stats[
            "Maximum_Safe_AI_Adoption"
        ]
    )

    occupation_stats[
        "Budget_Utilization"
    ] = (
        occupation_stats[
            "Budget_Utilization"
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

    print(
        "\nOccupation-level statistics:"
    )

    print(
        occupation_stats[
            [
                "Mean_AI_Share",
                "Maximum_Safe_AI_Adoption",
                "Budget_Utilization",
                "Task_Count",
            ]
        ]
        .describe()
        .to_string()
    )

    print(
        "\nHighest budget utilization:"
    )

    print(
        occupation_stats
        .sort_values(
            "Budget_Utilization",
            ascending=False
        )
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nLowest budget utilization:"
    )

    print(
        occupation_stats
        .sort_values(
            "Budget_Utilization",
            ascending=True
        )
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# 17. MAXIMUM SAFE ADOPTION
# ============================================================

section("17. MAXIMUM SAFE AI ADOPTION")

if "Maximum_Safe_AI_Adoption" in df.columns:

    safe = pd.to_numeric(
        df["Maximum_Safe_AI_Adoption"],
        errors="coerce"
    )

    print(
        f"Mean:   {safe.mean() * 100:.2f}%"
    )

    print(
        f"Median: {safe.median() * 100:.2f}%"
    )

    print(
        f"Min:    {safe.min() * 100:.2f}%"
    )

    print(
        f"Max:    {safe.max() * 100:.2f}%"
    )

    if "Occupation Title" in df.columns:

        occupation_safe = (
            df.groupby(
                "Occupation Title"
            )["Maximum_Safe_AI_Adoption"]
            .mean()
        )

        print(
            "\nOccupations supporting >= 50%:"
        )

        count_50 = (
            occupation_safe >= 0.50
        ).sum()

        print(
            f"{count_50:,}"
        )

        print(
            "\nOccupations below 50%:"
        )

        count_below = (
            occupation_safe < 0.50
        ).sum()

        print(
            f"{count_below:,}"
        )


# ============================================================
# 18. AI-LED THRESHOLD AUDIT
# ============================================================

section("18. AI-LED THRESHOLD AUDIT")

if "AI_Share" in df.columns:

    ai_share = pd.to_numeric(
        df["AI_Share"],
        errors="coerce"
    )

    print(
        f"Maximum AI Share: "
        f"{ai_share.max() * 100:.2f}%"
    )

    print(
        f"Tasks AI Share >= 60%: "
        f"{(ai_share >= 0.60).sum():,}"
    )

if "Task_AI_Suitability" in df.columns:

    suitability = pd.to_numeric(
        df["Task_AI_Suitability"],
        errors="coerce"
    )

    print(
        f"Tasks Suitability >= 60%: "
        f"{(suitability >= 0.60).sum():,}"
    )

if (
    "AI_Share" in df.columns
    and "Task_AI_Suitability" in df.columns
):

    both = (
        (df["AI_Share"] >= 0.60)
        &
        (df["Task_AI_Suitability"] >= 0.60)
    )

    print(
        "Tasks satisfying BOTH thresholds:"
    )

    print(
        f"{both.sum():,}"
    )

if "Work_Model" in df.columns:

    ai_led = (
        df["Work_Model"]
        .astype(str)
        .str.lower()
        .eq("ai-led")
    )

    print(
        f"Actual AI-led tasks: "
        f"{ai_led.sum():,}"
    )


# ============================================================
# 19. REPRESENTATIVE SANITY CASES
# ============================================================

section("19. REPRESENTATIVE SANITY CASES")

base_columns = [
    "Occupation Title",
    "Task",
    "AI_Share",
    "Task_AI_Suitability",
    "Skill_Shadow_Normalized",
    "Capability_Risk_Normalized",
    "Preservation_Pressure",
    "Human_Preservation_Floor",
    "Work_Model",
]


if (
    "Task_AI_Suitability" in df.columns
    and "Preservation_Pressure" in df.columns
):

    show_table(
        df[
            (
                (df["Task_AI_Suitability"] >= 0.70)
                &
                (df["Preservation_Pressure"] <= 0.30)
            )
        ],
        base_columns,
        5
    )


print(
    "\n--- HIGH SUITABILITY + HIGH SKILL SHADOW ---"
)

if (
    "Task_AI_Suitability" in df.columns
    and "Skill_Shadow_Normalized" in df.columns
):

    show_table(
        df[
            (
                (df["Task_AI_Suitability"] >= 0.70)
                &
                (df["Skill_Shadow_Normalized"] >= 0.30)
            )
        ],
        base_columns,
        5
    )


print(
    "\n--- LOW SUITABILITY + HIGH PRESERVATION PRESSURE ---"
)

if (
    "Task_AI_Suitability" in df.columns
    and "Preservation_Pressure" in df.columns
):

    show_table(
        df[
            (
                (df["Task_AI_Suitability"] <= 0.30)
                &
                (df["Preservation_Pressure"] >= 0.70)
            )
        ],
        base_columns,
        5
    )


print(
    "\n--- LOW SUITABILITY + LOW PRESERVATION PRESSURE ---"
)

if (
    "Task_AI_Suitability" in df.columns
    and "Preservation_Pressure" in df.columns
):

    show_table(
        df[
            (
                (df["Task_AI_Suitability"] <= 0.30)
                &
                (df["Preservation_Pressure"] <= 0.30)
            )
        ],
        base_columns,
        5
    )


# ============================================================
# 20. HIGHEST AI ALLOCATION
# ============================================================

section("20. HIGHEST AI ALLOCATIONS")

if "AI_Share" in df.columns:

    show_table(
        df.sort_values(
            "AI_Share",
            ascending=False
        ),
        base_columns,
        15
    )


# ============================================================
# 21. LOWEST AI ALLOCATION
# ============================================================

section("21. LOWEST AI ALLOCATIONS")

if "AI_Share" in df.columns:

    show_table(
        df.sort_values(
            "AI_Share",
            ascending=True
        ),
        base_columns,
        15
    )


# ============================================================
# 22. HIGHEST SKILL SHADOW
# ============================================================

section("22. HIGHEST SKILL SHADOW")

if "Skill_Shadow_Normalized" in df.columns:

    show_table(
        df.sort_values(
            "Skill_Shadow_Normalized",
            ascending=False
        ),
        base_columns,
        15
    )


# ============================================================
# 23. HIGHEST PRESERVATION PRESSURE
# ============================================================

section("23. HIGHEST PRESERVATION PRESSURE")

if "Preservation_Pressure" in df.columns:

    show_table(
        df.sort_values(
            "Preservation_Pressure",
            ascending=False
        ),
        base_columns,
        15
    )


# ============================================================
# 24. TARGET FEASIBILITY
# ============================================================

section("24. TARGET FEASIBILITY")

if "Target_Feasibility" in df.columns:

    print(
        df["Target_Feasibility"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nPercentages:")

    print(
        (
            df["Target_Feasibility"]
            .value_counts(
                normalize=True,
                dropna=False
            )
            * 100
        )
        .round(2)
        .to_string()
    )


# ============================================================
# 25. EFFECTIVE TARGET VS ACTUAL
# ============================================================

section("25. EFFECTIVE TARGET VS ACTUAL AI")

if (
    "Effective_AI_Target" in df.columns
    and "AI_Share" in df.columns
):

    gap = (
        df["Effective_AI_Target"]
        - df["AI_Share"]
    )

    print(
        f"Mean target gap: "
        f"{gap.mean() * 100:.4f} percentage points"
    )

    print(
        f"Median target gap: "
        f"{gap.median() * 100:.4f} percentage points"
    )

    print(
        f"Maximum absolute gap: "
        f"{gap.abs().max() * 100:.4f} percentage points"
    )


# ============================================================
# 26. FINAL SUMMARY
# ============================================================

section("26. FINAL V8 VALIDATION SUMMARY")

print(
    f"Rows                 : {len(df):,}"
)

print(
    f"Columns              : {len(df.columns):,}"
)

if "Task ID" in df.columns:

    print(
        f"Unique Task IDs     : "
        f"{df['Task ID'].nunique():,}"
    )

if "Task" in df.columns:

    print(
        f"Unique Task Text    : "
        f"{df['Task'].nunique():,}"
    )

if "Occupation Title" in df.columns:

    print(
        f"Unique Occupations  : "
        f"{df['Occupation Title'].nunique():,}"
    )

if "AI_Share" in df.columns:

    print(
        f"Mean AI Share       : "
        f"{df['AI_Share'].mean() * 100:.2f}%"
    )

if "Human_Share" in df.columns:

    print(
        f"Mean Human Share    : "
        f"{df['Human_Share'].mean() * 100:.2f}%"
    )

if "Maximum_Safe_AI_Adoption" in df.columns:

    print(
        f"Mean Maximum Safe AI: "
        f"{df['Maximum_Safe_AI_Adoption'].mean() * 100:.2f}%"
    )

if "Work_Model" in df.columns:

    print("\nWork Model:")

    print(
        df["Work_Model"]
        .value_counts()
        .to_string()
    )


print("\n" + "=" * 80)
print("WORKFOLD V8 VALIDATION COMPLETE")
print("=" * 80)