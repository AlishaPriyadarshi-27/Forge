import os
import json
import re
import time
import hashlib
from pathlib import Path

import pandas as pd
from groq import Groq


# ============================================================
# FORGE — LATTICE V4.1
# 5-Record Safe Pilot
# Micro-Apprenticeship + Capability Verification
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "datasets" / "lattice" / "forge_lattice_llm_ready.parquet"
OUTPUT_PARQUET = ROOT / "datasets" / "lattice" / "forge_lattice_llm_v4_1_pilot.parquet"
OUTPUT_CSV = ROOT / "datasets" / "lattice" / "forge_lattice_llm_v4_1_pilot.csv"

MODEL = "openai/gpt-oss-20b"

PILOT_SIZE = 5
MAX_RETRIES = 1
DELAY_SECONDS = 3

API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing from the current PowerShell session."
    )

client = Groq(api_key=API_KEY)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_parquet(INPUT)

required = [
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

missing = [c for c in required if c not in df.columns]

if missing:
    raise ValueError(f"Missing required columns: {missing}")

print(f"Records loaded: {len(df):,}")


# ============================================================
# VALID SOURCE
# ============================================================

source = df[
    df["Occupation Title"].notna()
    & df["Capability Name"].notna()
    & df["Task"].notna()
].copy()

print(f"Valid source records: {len(source):,}")


# ============================================================
# DIVERSE 5-RECORD PILOT
# ============================================================

# Sort by LATTICE priority so selected records are meaningful,
# but retain one record per occupation for diversity.

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
    .drop_duplicates(subset=["Occupation Title"])
    .head(PILOT_SIZE)
    .copy()
)

print(f"Pilot size: {len(pilot)}")
print(f"Unique occupations: {pilot['Occupation Title'].nunique()}")

print("\nPilot occupations:")
for i, occ in enumerate(pilot["Occupation Title"], 1):
    print(f"{i:02d}. {occ}")


# ============================================================
# FORBIDDEN TERMS
# ============================================================

FORBIDDEN = [
    "dashboard",
    "power bi",
    "tableau",
    "slide deck",
    "presentation",
    "course",
    "curriculum",
    "entire project",
    "large project",
    "multi-day",
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "treatment decision",
    "medical decision",
    "legal advice",
    "investment recommendation",
    "financial transaction",
]


def norm(x):
    return re.sub(r"\s+", " ", str(x).lower()).strip()


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the LATTICE micro-apprenticeship designer inside FORGE.

The target capability has ALREADY been selected by FORGE.
You MUST NOT change or reinterpret the target capability.

Create ONE small synthetic work sample.

CORE RULE:

AI prepares a preliminary input.
THE HUMAN performs the target capability.

The human must do meaningful cognitive or practical work.
Do NOT make the human merely proofread, approve, or verify
an AI answer.

The task should take approximately 20–60 minutes.

The task must:
- use synthetic/non-sensitive data
- have one focused objective
- contain 3–5 human actions
- have one main output
- have 2–4 observable evidence signals
- have a 4-part scoring rubric
- have one measurable verification signal

The target capability must be visible in the HUMAN ACTION.

Examples:

For "Analyzing Data or Information":
human independently compares values, identifies a pattern,
calculates a metric, and explains evidence.

For "Processing Information":
human organizes, transforms, validates, or structures
provided information according to explicit rules.

For "Working with Computers":
human performs a concrete technical operation or configuration
using a supplied synthetic environment.

For "Drafting, Laying Out, and Specifying Technical Devices,
Parts, and Equipment":
human converts dimensions/specifications into a concrete layout,
drawing, coordinate list, or specification.

AI may provide:
- preliminary observations
- candidate classifications
- small synthetic datasets
- proposed relationships
- draft inputs
- flagged records

BUT the human must perform the target capability.

DO NOT create:
- dashboards
- Power BI/Tableau tasks
- presentations
- slide decks
- courses
- full projects
- broad business strategies
- generic long reports
- patient diagnosis
- medical treatment decisions
- legal decisions
- financial/investment decisions

Return ONLY valid JSON.
"""


# ============================================================
# USER PROMPT
# ============================================================

def make_prompt(row):

    return f"""
Create ONE micro-apprenticeship task.

OCCUPATION:
{row['Occupation Title']}

TARGET CAPABILITY:
{row['Capability Name']}

CAPABILITY TYPE:
{row['Capability Type']}

ORIGINAL WORK TASK:
{row['Task']}

RELATED WORK ACTIVITY:
{row['DWA Element Name']}

FORGE PRACTICE GOAL:
{row['LATTICE_Goal']}

ASSESSMENT FOCUS:
{row['Assessment_Focus']}

FORGE SIGNALS:
Skill Shadow = {row['Skill_Shadow']}
Capability Risk = {row['Capability_Risk']}
Capability Criticality = {row['Capability_Criticality']}
Capability Preservation Pressure = {row['Capability_Preservation_Pressure']}
Task Preservation Pressure = {row['Task_Preservation_Pressure']}
LATTICE Priority = {row['LATTICE_Priority']}
Task Capability Weight = {row['Task Capability Weight']}
Task AI Suitability = {row['Task_AI_Suitability']}
Human Share = {row['Human_Share']}
Human Practice Signal = {row['Human_Practice_Signal']}
Task Practice Relevance = {row['Task_Practice_Relevance']}

CRITICAL REQUIREMENT:

The HUMAN must visibly perform:

{row['Capability Name']}

Do not make the task simply:
"review the AI output"
"validate the AI answer"
"check whether AI is correct"

Instead:
AI provides a small preliminary input,
then HUMAN independently performs the target capability
using the provided synthetic evidence.

Return exactly:

{{
  "title": "short title",
  "scenario": "2-3 sentence synthetic situation",
  "ai_input": "small preliminary AI input",
  "human_task": "3-5 numbered human actions",
  "expected_output": "ONE main human output",
  "evidence": [
    "observable evidence 1",
    "observable evidence 2",
    "observable evidence 3"
  ],
  "rubric": {{
    "capability": "0-3 criterion",
    "reasoning": "0-3 criterion",
    "accuracy": "0-3 criterion",
    "evidence_use": "0-3 criterion"
  }},
  "verification_signal": "one measurable rule"
}}
"""


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    text = str(text).strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.I
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])

    raise ValueError("No valid JSON object found.")


# ============================================================
# QUALITY GATE
# ============================================================

def quality_gate(obj, row):

    problems = []

    if not isinstance(obj, dict):
        return ["invalid_json"]

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
            problems.append(f"missing:{key}")

    if problems:
        return problems

    full = norm(
        json.dumps(
            obj,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # Forbidden content
    # --------------------------------------------------------

    for term in FORBIDDEN:
        if term in full:
            problems.append(f"forbidden:{term}")

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    evidence = obj.get("evidence")

    if not isinstance(evidence, list):
        problems.append("evidence_not_list")

    elif not 2 <= len(evidence) <= 4:
        problems.append("evidence_count_invalid")

    # --------------------------------------------------------
    # Rubric
    # --------------------------------------------------------

    rubric = obj.get("rubric")

    rubric_keys = [
        "capability",
        "reasoning",
        "accuracy",
        "evidence_use",
    ]

    if not isinstance(rubric, dict):
        problems.append("rubric_not_dict")

    else:
        for key in rubric_keys:
            if key not in rubric:
                problems.append(
                    f"missing_rubric:{key}"
                )

    # --------------------------------------------------------
    # Target capability grounding
    # --------------------------------------------------------

    capability = norm(row["Capability Name"])

    capability_words = [
        w for w in re.findall(
            r"[a-zA-Z]{4,}",
            capability
        )
    ]

    searchable = norm(
        " ".join(
            [
                str(obj.get("title", "")),
                str(obj.get("scenario", "")),
                str(obj.get("human_task", "")),
                str(obj.get("expected_output", "")),
                str(obj.get("evidence", "")),
            ]
        )
    )

    # Exact phrase OR meaningful capability word
    exact_match = capability in searchable

    word_match = any(
        w in searchable
        for w in capability_words
    )

    if not exact_match and not word_match:
        problems.append(
            "target_capability_not_visible"
        )

    # --------------------------------------------------------
    # Human action check
    # --------------------------------------------------------

    human = norm(
        obj.get("human_task", "")
    )

    if len(human) < 100:
        problems.append(
            "human_task_too_short"
        )

    # Prevent "only review AI"
    review_only_patterns = [
        "review the ai",
        "check the ai",
        "verify the ai answer",
        "approve the ai",
        "confirm the ai result",
    ]

    review_hits = sum(
        p in human
        for p in review_only_patterns
    )

    if review_hits >= 2:
        problems.append(
            "human_only_reviews_ai"
        )

    # --------------------------------------------------------
    # AI input
    # --------------------------------------------------------

    ai_input = norm(
        obj.get("ai_input", "")
    )

    if len(ai_input) < 30:
        problems.append(
            "ai_input_too_short"
        )

    # --------------------------------------------------------
    # Main output
    # --------------------------------------------------------

    expected = norm(
        obj.get("expected_output", "")
    )

    if len(expected) < 20:
        problems.append(
            "expected_output_too_short"
        )

    # --------------------------------------------------------
    # Prevent multiple deliverables
    # --------------------------------------------------------

    multiple = [
        "and a report",
        "and presentation",
        "and slides",
        "plus a report",
        "plus a presentation",
        "two separate files",
        "multiple reports",
    ]

    if any(x in expected for x in multiple):
        problems.append(
            "multiple_deliverables"
        )

    return sorted(set(problems))


# ============================================================
# LLM CALL
# ============================================================

def call_llm(row):

    prompt = make_prompt(row)

    for attempt in range(1, MAX_RETRIES + 2):

        try:

            response = client.chat.completions.create(
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

            raw = response.choices[0].message.content

            if not raw or not raw.strip():
                raise ValueError(
                    "Model returned empty content."
                )

            obj = extract_json(raw)

            problems = quality_gate(
                obj,
                row
            )

            if not problems:

                print(
                    f"  SUCCESS: "
                    f"{obj.get('title', 'Untitled')}"
                )

                return {
                    "status": "success",
                    "attempts": attempt,
                    "error": "",
                    "raw": raw,
                    "object": obj,
                }

            print(
                "  QUALITY REVIEW: "
                + " | ".join(problems)
            )

            if attempt <= MAX_RETRIES:

                prompt = make_prompt(row) + f"""

The previous generation failed these quality checks:

{problems}

Regenerate it.

The HUMAN must actually perform the target capability.
Do not make the human merely review AI output.

Return ONLY valid JSON.
"""

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
                f"{error_text[:220]}"
            )

            # IMPORTANT:
            # Stop immediately on rate-limit errors.
            if (
                "429" in error_text
                or "rate limit" in error_text.lower()
            ):
                return {
                    "status": "rate_limited",
                    "attempts": attempt,
                    "error": error_text,
                    "raw": "",
                    "object": {},
                }

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
# RUN PILOT
# ============================================================

results = []

for idx, (_, row) in enumerate(
    pilot.iterrows(),
    1
):

    print("\n" + "=" * 90)
    print(
        f"RECORD {idx}/{len(pilot)}"
    )
    print("=" * 90)

    print(
        f"Occupation : {row['Occupation Title']}"
    )

    print(
        f"Capability : {row['Capability Name']}"
    )

    print(
        f"Task       : {row['Task']}"
    )

    result = call_llm(row)

    obj = result["object"]

    record = row.to_dict()

    record["lattice_record_id"] = hashlib.sha1(
        (
            str(row["O*NET-SOC Code"])
            + "|"
            + str(row["Task ID"])
            + "|"
            + str(row["Capability ID"])
        ).encode()
    ).hexdigest()[:16]

    record["llm_provider"] = "Groq"
    record["llm_model"] = MODEL
    record["llm_status"] = result["status"]
    record["llm_attempts"] = result["attempts"]
    record["llm_error"] = result["error"]

    problems = (
        quality_gate(obj, row)
        if obj
        else ["not_generated"]
    )

    if (
        result["status"] == "success"
        and not problems
    ):
        record["quality_status"] = "PASS"

    elif result["status"] == "review":
        record["quality_status"] = "REVIEW"

    else:
        record["quality_status"] = "NOT_CHECKED"

    record["quality_problems"] = (
        " | ".join(problems)
    )

    record["title"] = obj.get(
        "title",
        ""
    )

    record["scenario"] = obj.get(
        "scenario",
        ""
    )

    record["ai_input"] = obj.get(
        "ai_input",
        ""
    )

    record["human_task"] = obj.get(
        "human_task",
        ""
    )

    record["expected_output"] = obj.get(
        "expected_output",
        ""
    )

    record["evidence"] = json.dumps(
        obj.get("evidence", []),
        ensure_ascii=False
    )

    record["rubric"] = json.dumps(
        obj.get("rubric", {}),
        ensure_ascii=False
    )

    record["verification_signal"] = obj.get(
        "verification_signal",
        ""
    )

    record["raw_llm_output"] = result["raw"]

    results.append(record)

    # Stop entire pilot if rate limit appears
    if result["status"] == "rate_limited":

        print("\nRATE LIMIT DETECTED.")
        print("Stopping pilot to avoid wasting API calls.")

        break

    time.sleep(DELAY_SECONDS)


# ============================================================
# SAVE
# ============================================================

out = pd.DataFrame(results)

out.to_parquet(
    OUTPUT_PARQUET,
    index=False
)

out.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n")
print("=" * 90)
print("FORGE LATTICE V4.1 PILOT COMPLETE")
print("=" * 90)

print(
    f"Records generated: {len(out)}"
)

print("\nLLM status:")

if len(out):
    print(
        out["llm_status"]
        .value_counts(dropna=False)
        .to_string()
    )

print("\nQuality status:")

if len(out):
    print(
        out["quality_status"]
        .value_counts(dropna=False)
        .to_string()
    )

print("\nGenerated tasks:")

if len(out):

    successful = out[
        out["llm_status"] == "success"
    ]

    for i, title in enumerate(
        successful["title"],
        1
    ):
        print(
            f"{i:02d}. {title}"
        )

print("\nSaved:")
print(OUTPUT_PARQUET)
print(OUTPUT_CSV)