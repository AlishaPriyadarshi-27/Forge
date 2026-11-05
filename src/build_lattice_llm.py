# ============================================================
# FORGE — LATTICE MICRO-APPRENTICESHIP ENGINE V3
# Diverse Pilot + Compact JSON + Quality Gate
# ============================================================

import os
import json
import re
import hashlib
from pathlib import Path

import pandas as pd
from openai import OpenAI


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    BASE_DIR
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_ready.parquet"
)

OUTPUT_PARQUET = (
    BASE_DIR
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v3_pilot.parquet"
)

OUTPUT_CSV = (
    BASE_DIR
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v3_pilot.csv"
)

PROMPT_PARQUET = (
    BASE_DIR
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v3_prompts.parquet"
)


# ============================================================
# SETTINGS
# ============================================================

PILOT_SIZE = 20

MODEL = os.getenv(
    "FORGE_LLM_MODEL",
    "openai/gpt-oss-20b"
)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

MAX_TOKENS = 900

MAX_RETRIES = 3


# ============================================================
# REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "O*NET-SOC Code",
    "Task ID",
    "Occupation Title",
    "Capability Name",
    "Capability Type",
    "Capability ID",
    "Task",
    "DWA Element Name",
    "Skill_Shadow",
    "Capability_Risk",
    "Capability_Criticality",
    "Capability_Preservation_Pressure",
    "Task_Preservation_Pressure",
    "LATTICE_Priority",
    "Task Capability Weight",
    "Task_Evidence_Signal",
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Human_Practice_Signal",
    "AI_Transformation_Signal",
    "Task_Practice_Relevance",
    "Practice_Intent",
    "LATTICE_Goal",
    "Assessment_Focus",
    "LLM_Task_Input",
    "Semantic_Similarity_Recovered",
]


# ============================================================
# COMPACT JSON SCHEMA
# ============================================================

RESPONSE_SCHEMA = {
    "type": "object",

    "properties": {

        "title": {
            "type": "string"
        },

        "scenario": {
            "type": "string"
        },

        "human_task": {
            "type": "string"
        },

        "expected_output": {
            "type": "string"
        },

        "evidence": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "rubric": {
            "type": "object",

            "properties": {

                "capability": {
                    "type": "string"
                },

                "reasoning": {
                    "type": "string"
                },

                "accuracy": {
                    "type": "string"
                },

                "communication": {
                    "type": "string"
                }
            },

            "required": [
                "capability",
                "reasoning",
                "accuracy",
                "communication"
            ],

            "additionalProperties": False
        },

        "verification_signal": {
            "type": "string"
        }
    },

    "required": [
        "title",
        "scenario",
        "human_task",
        "expected_output",
        "evidence",
        "rubric",
        "verification_signal"
    ],

    "additionalProperties": False
}


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def make_record_id(row):

    raw = "|".join([
        safe_text(row["O*NET-SOC Code"]),
        safe_text(row["Task ID"]),
        safe_text(row["Occupation Title"]),
        safe_text(row["Capability Type"]),
        safe_text(row["Capability ID"]),
    ])

    return (
        "LATTICE-"
        + hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:16]
    )


def clean_json_text(text):

    if not text:
        return ""

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    return text.strip()


# ============================================================
# QUALITY GATE
# ============================================================

FORBIDDEN_TERMS = [

    # Large / generic deliverables
    "dashboard",
    "power bi",
    "tableau",
    "slide deck",
    "presentation",
    "ppt",
    "build a course",
    "entire project",
    "full project",
    "multi-day",

    # Medical high-stakes
    "final diagnosis",
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "medication order",
    "treatment plan",
    "surgery",

    # Legal / financial high-stakes
    "legal ruling",
    "legal decision",
    "execute a trade",
    "financial transaction",
    "investment decision",
]


def quality_check(result, source_row):

    problems = []

    title = safe_text(
        result.get("title")
    )

    scenario = safe_text(
        result.get("scenario")
    )

    human_task = safe_text(
        result.get("human_task")
    )

    expected_output = safe_text(
        result.get("expected_output")
    )

    verification = safe_text(
        result.get("verification_signal")
    )

    capability = safe_text(
        source_row["Capability Name"]
    )

    combined = " ".join([
        title.lower(),
        scenario.lower(),
        human_task.lower(),
        expected_output.lower(),
        verification.lower(),
    ])

    # --------------------------------------------------------
    # Required content
    # --------------------------------------------------------

    required = [
        "title",
        "scenario",
        "human_task",
        "expected_output",
        "evidence",
        "rubric",
        "verification_signal",
    ]

    for field in required:

        if field not in result:

            problems.append(
                f"missing:{field}"
            )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = result.get(
        "evidence",
        []
    )

    if not isinstance(evidence, list):

        problems.append(
            "evidence_not_list"
        )

    elif len(evidence) < 2:

        problems.append(
            "insufficient_evidence"
        )

    elif len(evidence) > 4:

        problems.append(
            "too_many_evidence_items"
        )

    # --------------------------------------------------------
    # Rubric
    # --------------------------------------------------------

    rubric = result.get(
        "rubric",
        {}
    )

    if not isinstance(rubric, dict):

        problems.append(
            "rubric_not_object"
        )

    else:

        for key in [
            "capability",
            "reasoning",
            "accuracy",
            "communication",
        ]:

            if not safe_text(
                rubric.get(key)
            ):

                problems.append(
                    f"missing_rubric:{key}"
                )

    # --------------------------------------------------------
    # Target capability should appear
    # --------------------------------------------------------

    capability_words = [
        word.lower()
        for word in re.findall(
            r"[A-Za-z]+",
            capability
        )
        if len(word) > 3
    ]

    if capability_words:

        matched = sum(
            word in combined
            for word in capability_words
        )

        if matched == 0:

            problems.append(
                "target_capability_not_visible"
            )

    # --------------------------------------------------------
    # Forbidden terms
    # --------------------------------------------------------

    for term in FORBIDDEN_TERMS:

        if term in combined:

            problems.append(
                f"forbidden:{term}"
            )

    # --------------------------------------------------------
    # Too much text
    # --------------------------------------------------------

    if len(human_task) > 1800:

        problems.append(
            "task_too_long"
        )

    if len(scenario) > 1000:

        problems.append(
            "scenario_too_long"
        )

    if len(expected_output) > 600:

        problems.append(
            "output_too_long"
        )

    # --------------------------------------------------------
    # Multiple deliverables
    # --------------------------------------------------------

    multi_patterns = [

        "pdf and",
        "and pdf",
        "word and",
        "and word",
        "report and",
        "and report",
        "presentation and",
        "and presentation",
        "plus a",
        "as well as",
    ]

    for pattern in multi_patterns:

        if pattern in expected_output.lower():

            problems.append(
                f"multiple_deliverables:{pattern}"
            )

    return problems


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are FORGE's LATTICE Micro-Apprenticeship Designer.

Create ONE small work-based apprenticeship task whose purpose
is to preserve ONE human capability that may lose practice
because AI performs part of the work.

CORE FORMULA:

ONE CAPABILITY
→ ONE SMALL WORK SAMPLE
→ ONE AI INPUT
→ ONE HUMAN ACTION
→ ONE OBSERVABLE OUTPUT
→ ONE VERIFICATION SIGNAL

STRICT RULES:

1. The task must be small enough for approximately 20–60 minutes.

2. Use exactly 3–5 concise task steps.

3. AI performs a preliminary or routine part.

4. The HUMAN must perform the target capability.

5. The human must verify, interpret, reason, correct,
   prioritize, or contextualize the AI output.

6. Do not create an entire project.

7. Do not create a dashboard.

8. Do not create a presentation.

9. Do not create a course.

10. Do not create a multi-day assignment.

11. Produce ONE observable final output.

12. The verification signal must measure performance,
    not whether a particular phrase appears.

13. Keep the task grounded in the occupation and source task.

14. If the source task is broad, extract ONE small component.

15. Use synthetic data where needed.

16. Never require real patient diagnosis, treatment,
    prescribing, legal decisions, financial transactions,
    or other high-stakes decisions.

IMPORTANT:

The source task is evidence about the occupation.
It is NOT automatically proof that the target capability
is directly present.

The generated task must deliberately practice the TARGET
CAPABILITY.

Return ONLY valid JSON matching the schema.
Keep every field concise.
"""


# ============================================================
# USER PROMPT
# ============================================================

def build_prompt(row):

    return f"""
Create ONE focused FORGE micro-apprenticeship.

OCCUPATION:
{safe_text(row["Occupation Title"])}

SOURCE TASK:
{safe_text(row["Task"])}

WORK ACTIVITY:
{safe_text(row["DWA Element Name"])}

TARGET CAPABILITY:
{safe_text(row["Capability Name"])}

CAPABILITY TYPE:
{safe_text(row["Capability Type"])}

PRACTICE INTENT:
{safe_text(row["Practice_Intent"])}

LATTICE GOAL:
{safe_text(row["LATTICE_Goal"])}

ASSESSMENT FOCUS:
{safe_text(row["Assessment_Focus"])}

SKILL SHADOW:
{safe_text(row["Skill_Shadow"])}

CAPABILITY RISK:
{safe_text(row["Capability_Risk"])}

LATTICE PRIORITY:
{safe_text(row["LATTICE_Priority"])}

TASK CAPABILITY WEIGHT:
{safe_text(row["Task Capability Weight"])}

TASK AI SUITABILITY:
{safe_text(row["Task_AI_Suitability"])}

HUMAN SHARE:
{safe_text(row["Human_Share"])}

TASK PRACTICE RELEVANCE:
{safe_text(row["Task_Practice_Relevance"])}

SEMANTIC SIMILARITY:
{safe_text(row["Semantic_Similarity_Recovered"])}

DESIGN THIS WAY:

AI gives the apprentice ONE preliminary result.

The apprentice checks that result using a small synthetic
work sample and applies the TARGET CAPABILITY.

The apprentice then creates ONE final artifact.

Example pattern:

AI flags 5 unusual records.
Human checks the source values.
Human decides which flags are valid.
Human records corrected results and short evidence.

Do NOT expand this into a report, dashboard, presentation,
strategy project, or large analysis.

Return exactly these fields:

{{
  "title": "short task title",

  "scenario": "short synthetic workplace scenario",

  "human_task": "3-5 numbered concise steps",

  "expected_output": "ONE observable final artifact",

  "evidence": [
    "observable evidence 1",
    "observable evidence 2",
    "observable evidence 3"
  ],

  "rubric": {{
    "capability": "observable capability criterion",
    "reasoning": "observable reasoning criterion",
    "accuracy": "observable accuracy criterion",
    "communication": "observable communication criterion"
  }},

  "verification_signal": "ONE measurable performance signal"
}}
"""


# ============================================================
# LOAD DATA
# ============================================================

print("\n" + "=" * 75)
print("FORGE — LATTICE MICRO-APPRENTICESHIP ENGINE V3")
print("=" * 75)

print(
    f"\nLoading: {INPUT_PATH}"
)

if not INPUT_PATH.exists():

    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_PATH}"
    )

df = pd.read_parquet(
    INPUT_PATH
)

print(
    f"Records loaded: {len(df):,}"
)


# ============================================================
# COLUMN CHECK
# ============================================================

missing = [
    c
    for c in REQUIRED_COLUMNS
    if c not in df.columns
]

if missing:

    raise ValueError(
        "Missing required columns:\n"
        + "\n".join(missing)
    )

print(
    "Required columns: OK"
)


# ============================================================
# VALID SOURCE ROWS
# ============================================================

important_fields = [
    "Occupation Title",
    "Task",
    "Capability Name",
    "Capability Type",
    "Practice_Intent",
    "LATTICE_Goal",
    "Assessment_Focus",
]

mask = pd.Series(
    True,
    index=df.index
)

for column in important_fields:

    mask &= (
        df[column]
        .notna()
    )

    mask &= (
        df[column]
        .astype(str)
        .str.strip()
        .ne("")
    )

df = (
    df.loc[mask]
    .copy()
    .reset_index(drop=True)
)

print(
    f"Valid source records: {len(df):,}"
)


# ============================================================
# IDS
# ============================================================

df["lattice_record_id"] = df.apply(
    make_record_id,
    axis=1
)

if df[
    "lattice_record_id"
].duplicated().any():

    raise ValueError(
        "Duplicate LATTICE IDs found."
    )

print(
    "LATTICE IDs: unique"
)


# ============================================================
# DIVERSE PILOT SELECTION
# ============================================================

print("\nSelecting diverse pilot...")

ranked = (
    df
    .sort_values(
        by=[
            "LATTICE_Priority",
            "Task_Practice_Relevance",
            "Semantic_Similarity_Recovered",
        ],
        ascending=False
    )
    .copy()
)

selected_indices = []

used_occupations = set()

# First pass:
# Prefer one record per occupation.
for idx, row in ranked.iterrows():

    occupation = safe_text(
        row["Occupation Title"]
    )

    if occupation not in used_occupations:

        selected_indices.append(idx)

        used_occupations.add(
            occupation
        )

    if len(selected_indices) >= PILOT_SIZE:

        break


# Second pass if fewer than 20 unique occupations.
if len(selected_indices) < PILOT_SIZE:

    for idx in ranked.index:

        if idx in selected_indices:

            continue

        selected_indices.append(
            idx
        )

        if len(selected_indices) >= PILOT_SIZE:

            break


pilot_df = (
    ranked
    .loc[selected_indices]
    .copy()
)

print(
    f"Pilot size: {len(pilot_df)}"
)

print(
    f"Unique occupations: "
    f"{pilot_df['Occupation Title'].nunique()}"
)

print("\nPilot occupations:")

print(
    pilot_df[
        "Occupation Title"
    ]
    .to_string(index=False)
)


# ============================================================
# PROMPTS
# ============================================================

prompt_records = []

for _, row in pilot_df.iterrows():

    prompt_records.append({

        "lattice_record_id":
            row["lattice_record_id"],

        "occupation":
            row["Occupation Title"],

        "capability":
            row["Capability Name"],

        "system_prompt":
            SYSTEM_PROMPT.strip(),

        "user_prompt":
            build_prompt(row),
    })

prompt_df = pd.DataFrame(
    prompt_records
)

prompt_df.to_parquet(
    PROMPT_PARQUET,
    index=False
)

print(
    f"\nPrompts saved: {PROMPT_PARQUET}"
)


# ============================================================
# API KEY
# ============================================================

api_key = os.getenv(
    "GROQ_API_KEY"
)

if not api_key:

    raise RuntimeError(
        "GROQ_API_KEY is not set in this PowerShell session."
    )

client = OpenAI(
    api_key=api_key,
    base_url=GROQ_BASE_URL
)


# ============================================================
# GENERATE
# ============================================================

results = []

for number, (_, source_row) in enumerate(
    pilot_df.iterrows(),
    start=1
):

    record_id = source_row[
        "lattice_record_id"
    ]

    prompt_row = prompt_df[
        prompt_df[
            "lattice_record_id"
        ]
        == record_id
    ].iloc[0]

    print(
        f"\nGenerating {number}/{len(pilot_df)}..."
    )

    result = {

        "lattice_record_id":
            record_id,

        "llm_provider":
            "Groq",

        "llm_model":
            MODEL,

        "llm_status":
            "error",

        "llm_attempts":
            0,

        "llm_error":
            "",

        "quality_status":
            "NOT_CHECKED",

        "quality_problems":
            "",

        "title":
            "",

        "scenario":
            "",

        "human_task":
            "",

        "expected_output":
            "",

        "evidence":
            "",

        "rubric":
            "",

        "verification_signal":
            "",

        "raw_llm_output":
            "",
    }


    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        result[
            "llm_attempts"
        ] = attempt

        try:

            response = (
                client
                .chat
                .completions
                .create(

                    model=MODEL,

                    messages=[

                        {
                            "role":
                                "system",

                            "content":
                                prompt_row[
                                    "system_prompt"
                                ],
                        },

                        {
                            "role":
                                "user",

                            "content":
                                prompt_row[
                                    "user_prompt"
                                ],
                        },
                    ],

                    response_format={
                        "type":
                            "json_schema",

                        "json_schema": {

                            "name":
                                "forge_micro_task",

                            "strict":
                                True,

                            "schema":
                                RESPONSE_SCHEMA,
                        },
                    },

                    max_tokens=MAX_TOKENS,
                )
            )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if not content:

                raise ValueError(
                    "Empty model response."
                )

            content = clean_json_text(
                content
            )

            parsed = json.loads(
                content
            )

            problems = quality_check(
                parsed,
                source_row
            )

            result[
                "llm_status"
            ] = "success"

            result[
                "quality_problems"
            ] = " | ".join(
                problems
            )

            if problems:

                result[
                    "quality_status"
                ] = "REVIEW"

                print(
                    "GENERATED — QUALITY REVIEW:",
                    ", ".join(problems)
                )

            else:

                result[
                    "quality_status"
                ] = "PASS"

                print(
                    "SUCCESS:",
                    parsed["title"]
                )

            result[
                "title"
            ] = parsed[
                "title"
            ]

            result[
                "scenario"
            ] = parsed[
                "scenario"
            ]

            result[
                "human_task"
            ] = parsed[
                "human_task"
            ]

            result[
                "expected_output"
            ] = parsed[
                "expected_output"
            ]

            result[
                "evidence"
            ] = json.dumps(
                parsed[
                    "evidence"
                ],
                ensure_ascii=False
            )

            result[
                "rubric"
            ] = json.dumps(
                parsed[
                    "rubric"
                ],
                ensure_ascii=False
            )

            result[
                "verification_signal"
            ] = parsed[
                "verification_signal"
            ]

            result[
                "raw_llm_output"
            ] = content

            break


        except Exception as exc:

            result[
                "llm_error"
            ] = str(exc)

            if attempt < MAX_RETRIES:

                print(
                    f"Retrying... "
                    f"{attempt + 1}/{MAX_RETRIES}"
                )

            else:

                print(
                    "ERROR:",
                    str(exc)
                )


    results.append(
        result
    )


# ============================================================
# MERGE
# ============================================================

generated_df = pd.DataFrame(
    results
)

final_df = pilot_df.merge(
    generated_df,
    on="lattice_record_id",
    how="left"
)


# ============================================================
# SAVE
# ============================================================

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
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("V3 MICRO-APPRENTICESHIP PILOT COMPLETE")
print("=" * 75)

print(
    f"Total records: {len(final_df)}"
)

print("\nLLM status:")

print(
    final_df[
        "llm_status"
    ]
    .value_counts(
        dropna=False
    )
    .to_string()
)

print("\nQuality status:")

print(
    final_df[
        "quality_status"
    ]
    .value_counts(
        dropna=False
    )
    .to_string()
)

print(
    "\nOutput:"
)

print(
    OUTPUT_PARQUET
)

print(
    "\nFull 11,127-record generation NOT performed."
)

print(
    "\nFORGE LATTICE V3 FINISHED."
)