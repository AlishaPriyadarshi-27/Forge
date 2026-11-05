import os
import json
import re
import time
import hashlib
from pathlib import Path

import pandas as pd
from groq import Groq


# ============================================================
# FORGE — LATTICE V4.2
# Safe 5-Record Pilot
# Micro-Apprenticeship + Capability Verification
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_ready.parquet"
)

OUTPUT_PARQUET = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v4_2_pilot.parquet"
)

OUTPUT_CSV = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v4_2_pilot.csv"
)

BACKUP_CSV = (
    ROOT
    / "datasets"
    / "lattice"
    / "forge_lattice_llm_v4_2_partial.csv"
)

MODEL = "openai/gpt-oss-20b"

# ------------------------------------------------------------
# IMPORTANT
# Keep this at 5 for pilot.
# Do NOT increase until quality is approved.
# ------------------------------------------------------------

PILOT_SIZE = 5

MAX_RETRIES = 1

DELAY_SECONDS = 5


# ============================================================
# GROQ CLIENT
# ============================================================

API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY is missing from this PowerShell session."
    )

client = Groq(
    api_key=API_KEY
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading LATTICE source...")

df = pd.read_parquet(INPUT)

required_columns = [
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
    "Task_AI_Suitability",
    "AI_Share",
    "Human_Share",
    "Human_Practice_Signal",
    "AI_Transformation_Signal",
    "Task_Practice_Relevance",
    "Practice_Intent",
    "LATTICE_Goal",
    "Assessment_Focus",
]

missing = [
    c
    for c in required_columns
    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing required columns: {missing}"
    )

print(
    f"Records loaded: {len(df):,}"
)


# ============================================================
# SOURCE CLEANING
# ============================================================

source = df[
    df["Occupation Title"].notna()
    & df["Capability Name"].notna()
    & df["Task"].notna()
].copy()

print(
    f"Valid source records: {len(source):,}"
)


# ============================================================
# DIVERSE PILOT
# ============================================================

source = source.sort_values(
    [
        "LATTICE_Priority",
        "Task_Practice_Relevance",
        "Task Capability Weight",
    ],
    ascending=False,
)

pilot = (
    source
    .drop_duplicates(
        subset=["Occupation Title"]
    )
    .head(PILOT_SIZE)
    .copy()
)

print(
    f"Pilot size: {len(pilot)}"
)

print(
    f"Unique occupations: "
    f"{pilot['Occupation Title'].nunique()}"
)

print("\nPilot occupations:")

for i, occupation in enumerate(
    pilot["Occupation Title"],
    1
):

    print(
        f"{i:02d}. {occupation}"
    )


# ============================================================
# HELPERS
# ============================================================

def clean_string(value):

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, (list, dict)):

        return json.dumps(
            value,
            ensure_ascii=False
        )

    return str(value)


def normalize(value):

    return re.sub(
        r"\s+",
        " ",
        clean_string(value).lower()
    ).strip()


def json_string(value):

    if isinstance(value, str):
        return value.strip()

    return json.dumps(
        value,
        ensure_ascii=False
    )


# ============================================================
# FORBIDDEN CONTENT
# ============================================================

FORBIDDEN_TERMS = [

    # Dashboard / generic presentation
    "dashboard",
    "power bi",
    "tableau",
    "slide deck",
    "presentation",
    "slides",

    # Large projects
    "entire project",
    "large project",
    "multi-day",
    "full project",
    "curriculum",
    "course",

    # High-stakes medical
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "treatment decision",
    "medical decision",

    # Legal
    "legal advice",
    "legal decision",

    # Financial
    "investment recommendation",
    "financial transaction",
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the LATTICE micro-apprenticeship designer inside FORGE.

The target capability has ALREADY been selected by FORGE.

You MUST NOT change the target capability.

Your job is to create ONE small synthetic apprenticeship
work sample that allows a HUMAN to practice that exact
capability.

============================================================
CORE PRINCIPLE
============================================================

AI prepares a preliminary input.

THE HUMAN performs the target capability.

The human must produce an observable result.

The human must NOT simply:
- approve AI
- proofread AI
- check whether AI is correct
- repeat AI's conclusion

Instead, AI gives incomplete or preliminary material,
and the human independently performs the target capability.

============================================================
TASK SIZE
============================================================

The task should take approximately 20–60 minutes.

It must contain:

- one focused objective
- 3–5 human actions
- synthetic/non-sensitive data
- exactly one main output
- 2–4 observable evidence signals
- a 4-part rubric
- one measurable verification signal

============================================================
CAPABILITY GROUNDING
============================================================

The target capability is fixed.

The human action must visibly demonstrate it.

For:

Analyzing Data or Information:
the human should independently compare values,
identify patterns, calculate or interpret evidence,
and reach a supported finding.

Processing Information:
the human should transform, organize, classify,
structure, or validate information according to rules.

Working with Computers:
the human should perform a concrete technical
operation, configuration, investigation, or
structured computer-based task.

Drafting, Laying Out, and Specifying Technical Devices,
Parts, and Equipment:
the human should convert dimensions/specifications
into a concrete layout, coordinate list, drawing,
or technical specification.

Assisting and Caring for Others:
use only low-stakes synthetic resource/navigation
tasks. Never create diagnosis or treatment decisions.

============================================================
AI ROLE
============================================================

AI may provide:

- preliminary observations
- candidate classifications
- small synthetic datasets
- proposed relationships
- flagged records
- incomplete draft inputs
- preliminary calculations

BUT the human must independently perform
the target capability.

============================================================
DO NOT CREATE
============================================================

Do not create:

- dashboards
- Power BI/Tableau tasks
- presentations
- slide decks
- courses
- full projects
- broad strategy projects
- generic long reports
- diagnosis
- treatment decisions
- legal decisions
- investment decisions

Do not use vague tasks such as:

"Analyze the situation."

"Review the AI result."

"Check whether the AI is correct."

"Prepare a report."

The human action must be concrete.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

No markdown.
No explanation outside JSON.
"""


# ============================================================
# USER PROMPT
# ============================================================

def make_prompt(row):

    return f"""
Create ONE micro-apprenticeship task.

============================================================
SOURCE
============================================================

Occupation:
{clean_string(row["Occupation Title"])}

TARGET CAPABILITY:
{clean_string(row["Capability Name"])}

Capability Type:
{clean_string(row["Capability Type"])}

Original O*NET Task:
{clean_string(row["Task"])}

Related Work Activity:
{clean_string(row["DWA Element Name"])}

============================================================
FORGE LATTICE SIGNALS
============================================================

Skill Shadow:
{row["Skill_Shadow"]}

Capability Risk:
{row["Capability_Risk"]}

Capability Criticality:
{row["Capability_Criticality"]}

Capability Preservation Pressure:
{row["Capability_Preservation_Pressure"]}

Task Preservation Pressure:
{row["Task_Preservation_Pressure"]}

LATTICE Priority:
{row["LATTICE_Priority"]}

Task Capability Weight:
{row["Task Capability Weight"]}

Task AI Suitability:
{row["Task_AI_Suitability"]}

Human Share:
{row["Human_Share"]}

Human Practice Signal:
{row["Human_Practice_Signal"]}

Task Practice Relevance:
{row["Task_Practice_Relevance"]}

LATTICE Goal:
{clean_string(row["LATTICE_Goal"])}

Assessment Focus:
{clean_string(row["Assessment_Focus"])}

============================================================
CRITICAL REQUIREMENT
============================================================

The human MUST visibly perform:

{clean_string(row["Capability Name"])}

Do not merely ask the human to review AI output.

AI provides a preliminary input.

Human performs the capability.

Human produces one observable output.

============================================================
RETURN EXACTLY THIS JSON
============================================================

{{
  "title": "short concrete task title",
  "scenario": "2-3 sentence synthetic work situation",
  "ai_input": "small incomplete or preliminary AI-generated input",
  "human_task": "3-5 numbered actions that the human performs",
  "expected_output": "exactly one main human output",
  "evidence": [
    "observable evidence 1",
    "observable evidence 2",
    "observable evidence 3"
  ],
  "rubric": {{
    "capability": "0-3 scoring criterion",
    "reasoning": "0-3 scoring criterion",
    "accuracy": "0-3 scoring criterion",
    "evidence_use": "0-3 scoring criterion"
  }},
  "verification_signal": "one measurable verification rule"
}}
"""


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    text = clean_string(text)

    # Remove markdown fences if present
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # Direct parse
    try:

        return json.loads(text)

    except Exception:

        pass

    # Search for JSON object
    start = text.find("{")
    end = text.rfind("}")

    if (
        start >= 0
        and end > start
    ):

        candidate = text[
            start:end + 1
        ]

        return json.loads(candidate)

    raise ValueError(
        "No valid JSON object found."
    )


# ============================================================
# QUALITY GATE
# ============================================================

def quality_gate(obj, row):

    problems = []

    if not isinstance(obj, dict):

        return [
            "invalid_json"
        ]

    required = [
        "title",
        "scenario",
        "ai_input",
        "human_task",
        "expected_output",
        "evidence",
        "rubric",
        "verification_signal",
    ]

    for key in required:

        if key not in obj:

            problems.append(
                f"missing:{key}"
            )

    if problems:

        return problems

    # --------------------------------------------------------
    # Full text
    # --------------------------------------------------------

    full_text = normalize(
        json.dumps(
            obj,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Forbidden content
    # --------------------------------------------------------

    for term in FORBIDDEN_TERMS:

        if term in full_text:

            problems.append(
                f"forbidden:{term}"
            )

    # --------------------------------------------------------
    # Title quality
    # --------------------------------------------------------

    title = normalize(
        obj.get("title", "")
    )

    bad_title_words = [
        "report",
        "presentation",
        "dashboard",
        "project",
        "strategy",
        "plan",
    ]

    for word in bad_title_words:

        if word in title:

            problems.append(
                f"weak_title:{word}"
            )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = obj.get(
        "evidence"
    )

    if not isinstance(
        evidence,
        list
    ):

        problems.append(
            "evidence_not_list"
        )

    elif not (
        2 <= len(evidence) <= 4
    ):

        problems.append(
            "evidence_count_invalid"
        )

    # --------------------------------------------------------
    # Rubric
    # --------------------------------------------------------

    rubric = obj.get(
        "rubric"
    )

    rubric_keys = [
        "capability",
        "reasoning",
        "accuracy",
        "evidence_use",
    ]

    if not isinstance(
        rubric,
        dict
    ):

        problems.append(
            "rubric_not_dict"
        )

    else:

        for key in rubric_keys:

            if key not in rubric:

                problems.append(
                    f"missing_rubric:{key}"
                )

    # --------------------------------------------------------
    # Capability grounding
    # --------------------------------------------------------

    capability = normalize(
        row["Capability Name"]
    )

    capability_words = [
        w
        for w in re.findall(
            r"[a-zA-Z]{4,}",
            capability
        )
    ]

    human_text = normalize(
        obj.get(
            "human_task",
            ""
        )
    )

    output_text = normalize(
        obj.get(
            "expected_output",
            ""
        )
    )

    searchable = (
        human_text
        + " "
        + output_text
        + " "
        + normalize(
            obj.get(
                "evidence",
                ""
            )
        )
    )

    exact_match = (
        capability in searchable
    )

    word_match = any(
        word in searchable
        for word in capability_words
    )

    if not (
        exact_match
        or word_match
    ):

        problems.append(
            "target_capability_not_visible"
        )

    # --------------------------------------------------------
    # Human task length
    # --------------------------------------------------------

    if len(human_text) < 100:

        problems.append(
            "human_task_too_short"
        )

    if len(human_text) > 1800:

        problems.append(
            "human_task_too_long"
        )

    # --------------------------------------------------------
    # Human-only-review detection
    # --------------------------------------------------------

    review_patterns = [
        "review the ai",
        "check the ai",
        "verify the ai answer",
        "approve the ai",
        "confirm the ai result",
        "validate the ai result",
        "check whether ai is correct",
    ]

    review_hits = sum(
        pattern in human_text
        for pattern in review_patterns
    )

    if review_hits >= 2:

        problems.append(
            "human_only_reviews_ai"
        )

    # --------------------------------------------------------
    # AI input
    # --------------------------------------------------------

    ai_input = normalize(
        obj.get(
            "ai_input",
            ""
        )
    )

    if len(ai_input) < 30:

        problems.append(
            "ai_input_too_short"
        )

    # --------------------------------------------------------
    # Main output
    # --------------------------------------------------------

    expected = normalize(
        obj.get(
            "expected_output",
            ""
        )
    )

    if len(expected) < 20:

        problems.append(
            "expected_output_too_short"
        )

    # --------------------------------------------------------
    # Multiple deliverables
    # --------------------------------------------------------

    multiple_terms = [
        "and a report",
        "and presentation",
        "and slides",
        "plus a report",
        "plus a presentation",
        "two separate files",
        "multiple reports",
        "report and",
        "presentation and",
    ]

    if any(
        term in expected
        for term in multiple_terms
    ):

        problems.append(
            "multiple_deliverables"
        )

    return sorted(
        set(problems)
    )


# ============================================================
# LLM CALL
# ============================================================

def call_llm(row):

    prompt = make_prompt(row)

    for attempt in range(
        1,
        MAX_RETRIES + 2
    ):

        try:

            response = (
                client
                .chat
                .completions
                .create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    reasoning_effort="low",
                    temperature=0.2,
                    max_completion_tokens=700,
                )
            )

            message = (
                response
                .choices[0]
                .message
            )

            raw = message.content

            if not raw:

                raise ValueError(
                    "Model returned empty content."
                )

            raw = clean_string(
                raw
            )

            obj = extract_json(
                raw
            )

            problems = quality_gate(
                obj,
                row
            )

            if not problems:

                print(
                    "  SUCCESS: "
                    + clean_string(
                        obj.get(
                            "title",
                            "Untitled"
                        )
                    )
                )

                return {
                    "status": "success",
                    "attempts": attempt,
                    "error": "",
                    "raw": raw,
                    "object": obj,
                }

            # ------------------------------------------------
            # Quality failed
            # ------------------------------------------------

            print(
                "  QUALITY REVIEW: "
                + " | ".join(problems)
            )

            if attempt <= MAX_RETRIES:

                prompt = (
                    make_prompt(row)
                    + f"""

QUALITY CHECK FAILED.

Problems:
{problems}

Regenerate the task.

The human MUST perform the target capability.

The human must NOT merely review AI.

The task must have one concrete output.

Do not use the word "report" in the title.

Return ONLY valid JSON.
"""
                )

                continue

            return {
                "status": "review",
                "attempts": attempt,
                "error": ";".join(problems),
                "raw": raw,
                "object": obj,
            }

        except Exception as e:

            error_text = str(e)

            print(
                f"  ERROR attempt {attempt}: "
                f"{error_text[:300]}"
            )

            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if (
                "429" in error_text
                or "rate limit"
                in error_text.lower()
                or "tokens per day"
                in error_text.lower()
            ):

                return {
                    "status": "rate_limited",
                    "attempts": attempt,
                    "error": error_text,
                    "raw": "",
                    "object": {},
                }

            # ------------------------------------------------
            # Other error
            # ------------------------------------------------

            if attempt <= MAX_RETRIES:

                time.sleep(2)

                continue

            return {
                "status": "error",
                "attempts": attempt,
                "error": error_text,
                "raw": "",
                "object": {},
            }


# ============================================================
# NORMALIZE GENERATED FIELDS
# ============================================================

def normalize_generated_object(obj):

    if not isinstance(
        obj,
        dict
    ):

        return {
            "title": "",
            "scenario": "",
            "ai_input": "",
            "human_task": "",
            "expected_output": "",
            "evidence": [],
            "rubric": {},
            "verification_signal": "",
        }

    return {
        "title": clean_string(
            obj.get(
                "title",
                ""
            )
        ),

        "scenario": clean_string(
            obj.get(
                "scenario",
                ""
            )
        ),

        "ai_input": clean_string(
            obj.get(
                "ai_input",
                ""
            )
        ),

        "human_task": clean_string(
            obj.get(
                "human_task",
                ""
            )
        ),

        "expected_output": clean_string(
            obj.get(
                "expected_output",
                ""
            )
        ),

        "evidence": (
            obj.get(
                "evidence",
                []
            )
            if isinstance(
                obj.get(
                    "evidence",
                    []
                ),
                list
            )
            else [
                clean_string(
                    obj.get(
                        "evidence",
                        ""
                    )
                )
            ]
        ),

        "rubric": (
            obj.get(
                "rubric",
                {}
            )
            if isinstance(
                obj.get(
                    "rubric",
                    {}
                ),
                dict
            )
            else {}
        ),

        "verification_signal": clean_string(
            obj.get(
                "verification_signal",
                ""
            )
        ),
    }


# ============================================================
# BUILD RECORD
# ============================================================

def build_record(row, result):

    obj = normalize_generated_object(
        result.get(
            "object",
            {}
        )
    )

    record = row.to_dict()

    # --------------------------------------------------------
    # Stable ID
    # --------------------------------------------------------

    raw_id = (
        str(row["O*NET-SOC Code"])
        + "|"
        + str(row["Task ID"])
        + "|"
        + str(row["Capability ID"])
    )

    record["lattice_record_id"] = (
        hashlib.sha1(
            raw_id.encode()
        ).hexdigest()[:16]
    )

    # --------------------------------------------------------
    # LLM metadata
    # --------------------------------------------------------

    record["llm_provider"] = "Groq"

    record["llm_model"] = MODEL

    record["llm_status"] = (
        result.get(
            "status",
            ""
        )
    )

    record["llm_attempts"] = (
        result.get(
            "attempts",
            0
        )
    )

    record["llm_error"] = (
        result.get(
            "error",
            ""
        )
    )

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    problems = (
        quality_gate(
            obj,
            row
        )
        if result.get("object")
        else ["not_generated"]
    )

    if (
        result.get("status")
        == "success"
        and not problems
    ):

        record["quality_status"] = "PASS"

    elif result.get("status") == "review":

        record["quality_status"] = "REVIEW"

    else:

        record["quality_status"] = (
            "NOT_CHECKED"
        )

    record["quality_problems"] = (
        " | ".join(
            problems
        )
    )

    # --------------------------------------------------------
    # Generated fields
    # --------------------------------------------------------

    record["title"] = obj["title"]

    record["scenario"] = obj["scenario"]

    record["ai_input"] = obj["ai_input"]

    record["human_task"] = obj["human_task"]

    record["expected_output"] = (
        obj["expected_output"]
    )

    record["evidence"] = json.dumps(
        obj["evidence"],
        ensure_ascii=False
    )

    record["rubric"] = json.dumps(
        obj["rubric"],
        ensure_ascii=False
    )

    record["verification_signal"] = (
        obj["verification_signal"]
    )

    record["raw_llm_output"] = (
        result.get(
            "raw",
            ""
        )
    )

    return record


# ============================================================
# SAFE SAVE
# ============================================================

def safe_save(records):

    if not records:

        return

    temp = pd.DataFrame(
        records
    )

    # --------------------------------------------------------
    # Force generated fields to strings
    # --------------------------------------------------------

    string_columns = [
        "lattice_record_id",
        "llm_provider",
        "llm_model",
        "llm_status",
        "llm_error",
        "quality_status",
        "quality_problems",
        "title",
        "scenario",
        "ai_input",
        "human_task",
        "expected_output",
        "evidence",
        "rubric",
        "verification_signal",
        "raw_llm_output",
    ]

    for column in string_columns:

        if column in temp.columns:

            temp[column] = (
                temp[column]
                .map(clean_string)
            )

    # --------------------------------------------------------
    # CSV backup first
    # --------------------------------------------------------

    temp.to_csv(
        BACKUP_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # Parquet
    # --------------------------------------------------------

    temp.to_parquet(
        OUTPUT_PARQUET,
        index=False
    )

    # --------------------------------------------------------
    # Final CSV
    # --------------------------------------------------------

    temp.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )


# ============================================================
# MAIN LOOP
# ============================================================

results = []

for idx, (_, row) in enumerate(
    pilot.iterrows(),
    1
):

    print("\n")
    print(
        "=" * 90
    )

    print(
        f"RECORD {idx}/{len(pilot)}"
    )

    print(
        "=" * 90
    )

    print(
        "Occupation : "
        + clean_string(
            row["Occupation Title"]
        )
    )

    print(
        "Capability : "
        + clean_string(
            row["Capability Name"]
        )
    )

    print(
        "Task       : "
        + clean_string(
            row["Task"]
        )
    )

    result = call_llm(
        row
    )

    record = build_record(
        row,
        result
    )

    results.append(
        record
    )

    # --------------------------------------------------------
    # SAVE IMMEDIATELY
    # --------------------------------------------------------

    try:

        safe_save(
            results
        )

        print(
            "  Saved partial progress."
        )

    except Exception as save_error:

        print(
            "  SAVE ERROR: "
            + str(save_error)
        )

    # --------------------------------------------------------
    # Stop if rate limited
    # --------------------------------------------------------

    if (
        result["status"]
        == "rate_limited"
    ):

        print("\n")
        print(
            "RATE LIMIT DETECTED."
        )

        print(
            "Stopping immediately."
        )

        break

    time.sleep(
        DELAY_SECONDS
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print(
    "=" * 90
)

print(
    "FORGE LATTICE V4.2 PILOT COMPLETE"
)

print(
    "=" * 90
)

print(
    f"Records processed: "
    f"{len(results)}"
)

if results:

    result_df = pd.DataFrame(
        results
    )

    print("\nLLM status:")

    print(
        result_df[
            "llm_status"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print("\nQuality status:")

    print(
        result_df[
            "quality_status"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    print("\nTasks generated:")

    successful = result_df[
        result_df[
            "llm_status"
        ] == "success"
    ]

    for i, title in enumerate(
        successful["title"],
        1
    ):

        print(
            f"{i:02d}. "
            f"{clean_string(title)}"
        )

print("\nFiles:")

print(
    f"Parquet : {OUTPUT_PARQUET}"
)

print(
    f"CSV     : {OUTPUT_CSV}"
)

print(
    f"Backup  : {BACKUP_CSV}"
)

print("\nDone.")