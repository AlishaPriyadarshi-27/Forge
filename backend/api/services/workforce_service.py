from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from functools import lru_cache


# ---------------------------------------------------------
# FORGE — ROLE RADAR WORKFORCE INTELLIGENCE
# ---------------------------------------------------------

# workforce_service.py is located at:
# backend/api/services/workforce_service.py
#
# Role Radar data is located at:
# backend/data/role_radar/
#
# Therefore:
# parents[0] -> backend/api/services
# parents[1] -> backend/api
# parents[2] -> backend
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "role_radar"


def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Role Radar dataset file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_profiles() -> list[dict]:
    data = _load_json("synthetic_profiles.json")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("profiles", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


@lru_cache(maxsize=1)
def load_jobs() -> list[dict]:
    data = _load_json("scraped_jobs.json")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("jobs", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


@lru_cache(maxsize=1)
def load_labels() -> list[dict]:
    data = _load_json("phase3_labels.json")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("labels", "pairs", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


@lru_cache(maxsize=1)
def load_gold_labels() -> list[dict]:
    data = _load_json("gold_labels.json")

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("labels", "pairs", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]

    return []


# ---------------------------------------------------------
# BASIC WORKFORCE METRICS
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_workforce_metrics() -> dict:
    profiles = load_profiles()
    jobs = load_jobs()
    labels = load_labels()
    gold = load_gold_labels()

    roles = set()
    skills = set()
    seniorities = set()

    for profile in profiles:

        for role in profile.get("roles", []) or []:
            roles.add(str(role).strip())

        for skill in profile.get("skills_primary", []) or []:
            skills.add(str(skill).strip().lower())

        for skill in profile.get("skills_secondary", []) or []:
            skills.add(str(skill).strip().lower())

        seniority = profile.get("seniority")
        if seniority:
            seniorities.add(str(seniority))

    return {
        "workforce_profiles": len(profiles),
        "jobs": len(jobs),
        "roles": len(roles),
        "skills": len(skills),
        "labeled_pairs": len(labels),
        "gold_eval_pairs": len(gold),
        "seniority_levels": len(seniorities),
    }


# ---------------------------------------------------------
# ROLE DISTRIBUTION
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_role_distribution() -> list[dict]:
    profiles = load_profiles()

    counts: dict[str, int] = {}

    for profile in profiles:
        for role in profile.get("roles", []) or []:
            role_name = str(role).strip()

            if not role_name:
                continue

            counts[role_name] = counts.get(role_name, 0) + 1

    result = [
        {
            "role": role,
            "count": count,
        }
        for role, count in counts.items()
    ]

    result.sort(key=lambda x: x["count"], reverse=True)

    return result[:20]


# ---------------------------------------------------------
# SKILL DISTRIBUTION
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_skill_distribution() -> list[dict]:
    profiles = load_profiles()

    counts: dict[str, int] = {}

    for profile in profiles:

        skills = []

        skills.extend(profile.get("skills_primary", []) or [])
        skills.extend(profile.get("skills_secondary", []) or [])

        for skill in skills:

            skill_name = str(skill).strip()

            if not skill_name:
                continue

            key = skill_name.lower()

            counts[key] = counts.get(key, 0) + 1

    result = [
        {
            "skill": skill,
            "count": count,
        }
        for skill, count in counts.items()
    ]

    result.sort(key=lambda x: x["count"], reverse=True)

    return result[:20]


# ---------------------------------------------------------
# JOB / MARKET SIGNAL
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_market_metrics() -> dict:
    jobs = load_jobs()

    industries = set()
    locations = set()
    role_families = set()

    for job in jobs:

        if job.get("industry"):
            industries.add(str(job["industry"]))

        if job.get("location"):
            locations.add(str(job["location"]))

        if job.get("role_family_hint"):
            role_families.add(str(job["role_family_hint"]))

    return {
        "job_count": len(jobs),
        "industries": len(industries),
        "locations": len(locations),
        "role_families": len(role_families),
    }


# ---------------------------------------------------------
# WORKFORCE TRANSFORMATION / TREND SIGNALS
# ---------------------------------------------------------

def _job_year(job: dict) -> int | None:
    """Resolve a year from messy Role Radar job records.

    The Role Radar export has changed field names across snapshots. We inspect
    both top-level and nested metadata and accept common ISO, year-only,
    Unix-second, Unix-millisecond and human-readable date strings.
    """
    date_key_re = re.compile(
        r"(?:^|[_\-])(?:posted|posting|publish|published|created|updated|date|timestamp|time)(?:$|[_\-])",
        re.I,
    )

    candidates: list[Any] = []

    def walk(value: Any, key_hint: str = "") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
                if date_key_re.search(key_text) or any(
                    token in key_text for token in (
                        "posted_at", "post_date", "publication", "published", "created_at",
                        "updated_at", "date_posted", "posting_date", "timestamp", "datetime",
                    )
                ):
                    if child not in (None, "", [], {}):
                        candidates.append(child)
                if isinstance(child, (dict, list, tuple)):
                    walk(child, key_text)
        elif isinstance(value, (list, tuple)):
            for child in value:
                if isinstance(child, (dict, list, tuple)):
                    walk(child, key_hint)

    walk(job)

    # Also try a few common direct fields first for speed.
    for key in (
        "posted_at", "posted_date", "date_posted", "posting_date", "published_at",
        "publication_date", "created_at", "updated_at", "date", "timestamp", "datetime",
        "posted", "published", "created", "updated",
    ):
        if job.get(key) not in (None, ""):
            candidates.insert(0, job.get(key))

    for raw in candidates:
        try:
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                value = float(raw)
                if 1900 <= value <= 2100:
                    return int(value)
                if value > 10_000_000_000:
                    value /= 1000.0
                if 500_000_000 < value < 5_000_000_000:
                    return datetime.fromtimestamp(value).year

            text = str(raw).strip()
            if not text:
                continue

            # YYYY is sufficient when the source only stores a year.
            match = re.search(r"(?<!\d)(19|20)\d{2}(?!\d)", text)
            if match:
                year = int(match.group(0))
                if 1990 <= year <= 2100:
                    return year

            normalized = text.replace("Z", "+00:00")
            for fmt in (
                "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
                "%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
            ):
                try:
                    return datetime.strptime(text[:19], fmt).year
                except ValueError:
                    pass

            try:
                return datetime.fromisoformat(normalized).year
            except ValueError:
                pass
        except Exception:
            continue

    return None


def _job_text(job: dict) -> str:
    parts = []
    for key in (
        "title", "job_title", "position", "description", "description_html",
        "role_family_hint", "industry", "skills", "required_skills",
        "technologies", "technology", "keywords",
    ):
        value = job.get(key)
        if isinstance(value, (list, tuple, set)):
            parts.extend(str(x) for x in value)
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts).lower()


def _profile_skill_vocabulary(profiles: list[dict]) -> list[str]:
    skills = set()
    for profile in profiles:
        for key in ("skills_primary", "skills_secondary"):
            for skill in profile.get(key, []) or []:
                text = str(skill).strip().lower()
                if len(text) >= 2:
                    skills.add(text)
    return sorted(skills, key=len, reverse=True)


def _build_role_transformation_series(jobs: list[dict], limit: int = 8) -> dict:
    """Build a plotted role-level transformation signal when historical dates are absent.

    Current = observed job records per role family.
    AI/automation = observed job records containing AI/automation evidence.
    Future demand = AI-adjusted demand signal (current + AI/automation evidence),
    explicitly a signal/proxy rather than a time-series forecast.
    """
    ai_terms = (
        "artificial intelligence", "generative ai", "genai", "machine learning",
        "deep learning", "automation", "llm", "large language model",
        "ai engineer", "ai/ml", "robotics"
    )
    buckets: dict[str, dict[str, int]] = {}
    for job in jobs:
        role = job.get("role_family_hint") or job.get("role_family") or job.get("title")
        if not role:
            continue
        role = str(role).strip()
        if not role:
            continue
        b = buckets.setdefault(role, {"current": 0, "ai": 0})
        b["current"] += 1
        if any(term in _job_text(job) for term in ai_terms):
            b["ai"] += 1

    ranked = sorted(buckets.items(), key=lambda kv: kv[1]["current"], reverse=True)[:limit]
    categories = [name for name, _ in ranked]
    current = [vals["current"] for _, vals in ranked]
    ai = [vals["ai"] for _, vals in ranked]
    # This is intentionally a demand SIGNAL, not a fabricated forecast.
    future = [vals["current"] + vals["ai"] for _, vals in ranked]
    return {
        "categories": categories,
        "series": {"current": current, "post_ai": ai, "future_demand": future},
        "mode": "role_signal",
        "future_label": "Future demand signal",
        "note": "Historical posting dates are unavailable; this role-level view uses observed job volume and AI/automation evidence instead of fabricating a time series."
    }


@lru_cache(maxsize=1)
def get_workforce_transformation() -> dict:
    """Build a transparent, dataset-derived transformation view.

    Current = observed yearly job-signal volume.
    Post-AI = yearly job records containing AI/automation evidence.
    Future demand = least-squares trend projection of the observed signal.

    Role and skill movement are also derived from the dated job evidence:
    roles are distinct role-family signals; skills are distinct known profile
    skills found in the job evidence for that period. No dashboard numbers
    are hard-coded.
    """
    jobs = load_jobs()
    by_year: dict[int, int] = {}
    ai_by_year: dict[int, int] = {}
    locations_by_year: dict[int, set[str]] = {}
    role_families_by_year: dict[int, set[str]] = {}
    # Skill totals are computed independently from connected workforce profiles.
    # Do not run a profile-skill regex scan across every job here; it makes the
    # transformation endpoint unnecessarily slow without changing the plotted
    # job/AI signals.

    ai_terms = (
        "artificial intelligence", "generative ai", "genai", "machine learning",
        "deep learning", "automation", "llm", "large language model", "ai engineer",
        "ai/ml", "robotics"
    )

    for job in jobs:
        year = _job_year(job)
        if year is None:
            continue

        by_year[year] = by_year.get(year, 0) + 1
        locations_by_year.setdefault(year, set())
        role_families_by_year.setdefault(year, set())

        location = job.get("location") or job.get("locations")
        if isinstance(location, (list, tuple, set)):
            locations_by_year[year].update(str(x).strip() for x in location if str(x).strip())
        elif location:
            locations_by_year[year].add(str(location).strip())

        role_family = job.get("role_family_hint") or job.get("role_family")
        if role_family:
            role_families_by_year[year].add(str(role_family).strip())

        text = _job_text(job)
        if any(term in text for term in ai_terms):
            ai_by_year[year] = ai_by_year.get(year, 0) + 1

    observed_years = sorted(by_year)
    if not observed_years:
        role_view = _build_role_transformation_series(jobs)
        return {
            "years": [],
            "series": {"current": [], "post_ai": [], "future_demand": []},
            "role_series": role_view,
            "last_observed_year": None,
            "historical_years": [],
            "projection_years": [],
            "signal_changes": {"jobs": None, "locations": None, "role_families": None, "skills": None},
        }

    historical = observed_years[-8:]
    last_year = historical[-1]
    future_years = [last_year + 1, last_year + 2]
    years = historical + future_years

    current_hist = [by_year.get(y, 0) for y in historical]
    post_hist = [ai_by_year.get(y, 0) for y in historical]

    n = len(current_hist)
    if n > 1:
        xs = list(range(n))
        mx = sum(xs) / n
        my = sum(current_hist) / n
        denom = sum((x - mx) ** 2 for x in xs) or 1
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, current_hist)) / denom
        intercept = my - slope * mx
    else:
        slope = 0.0
        intercept = float(current_hist[0] if current_hist else 0)

    future_values = [max(0, round(intercept + slope * x)) for x in range(n + len(future_years))]
    current = current_hist + [current_hist[-1]] * len(future_years)
    post_ai = post_hist + [post_hist[-1] if post_hist else 0] * len(future_years)

    latest = historical[-1]
    previous = historical[-2] if len(historical) > 1 else None

    def pct_change(now: float, old: float | None) -> float | None:
        if old is None or old == 0:
            return None
        return round(((now - old) / old) * 100, 1)

    return {
        "years": years,
        "series": {
            "current": current,
            "post_ai": post_ai,
            "future_demand": future_values,
        },
        "role_series": _build_role_transformation_series(jobs),
        "last_observed_year": last_year,
        "historical_years": historical,
        "projection_years": future_years,
        "signal_changes": {
            "jobs": pct_change(by_year.get(latest, 0), by_year.get(previous, 0) if previous else None),
            "locations": pct_change(len(locations_by_year.get(latest, set())), len(locations_by_year.get(previous, set())) if previous else None),
            "role_families": pct_change(len(role_families_by_year.get(latest, set())), len(role_families_by_year.get(previous, set())) if previous else None),
            "skills": None,
        },
        "signal_counts": {
            "latest_jobs": by_year.get(latest, 0),
            "previous_jobs": by_year.get(previous, 0) if previous else None,
            "latest_roles": len(role_families_by_year.get(latest, set())),
            "previous_roles": len(role_families_by_year.get(previous, set())) if previous else None,
            "latest_skills": None,
            "previous_skills": None,
            "latest_locations": len(locations_by_year.get(latest, set())),
            "previous_locations": len(locations_by_year.get(previous, set())) if previous else None,
        },
    }


@lru_cache(maxsize=1)
def get_role_skill_gaps() -> list[dict]:
    """Observed skill coverage gaps grouped by workforce role."""
    profiles = load_profiles()
    role_profiles: dict[str, int] = {}
    role_skills: dict[str, dict[str, int]] = {}

    for profile in profiles:
        roles = [str(r).strip() for r in (profile.get("roles", []) or []) if str(r).strip()]
        skills = []
        skills.extend(profile.get("skills_primary", []) or [])
        skills.extend(profile.get("skills_secondary", []) or [])
        normalized = {str(x).strip().lower() for x in skills if str(x).strip()}
        for role in roles:
            role_profiles[role] = role_profiles.get(role, 0) + 1
            bucket = role_skills.setdefault(role, {})
            for skill in normalized:
                bucket[skill] = bucket.get(skill, 0) + 1

    result = []
    for role, count in sorted(role_profiles.items(), key=lambda x: x[1], reverse=True)[:20]:
        bucket = role_skills.get(role, {})
        gaps = []
        for skill, seen in bucket.items():
            gap = max(0, round((1 - seen / max(1, count)) * 100))
            gaps.append({"skill": skill, "observed": seen, "gap": gap})
        gaps.sort(key=lambda x: (x["gap"], -x["observed"]), reverse=True)
        result.append({"role": role, "profiles": count, "gaps": gaps[:8]})
    return result


# ---------------------------------------------------------
# DASHBOARD OVERVIEW
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_workforce_overview() -> dict:

    metrics = get_workforce_metrics()
    market = get_market_metrics()

    transformation = get_workforce_transformation()
    changes = transformation.get("signal_changes", {})
    market["job_signal_change"] = changes.get("jobs")
    market["location_signal_change"] = changes.get("locations")
    metrics["role_signal_change"] = changes.get("role_families")
    metrics["skill_signal_change"] = changes.get("skills")

    return {
        "metrics": metrics,
        "market": market,
        "top_roles": get_role_distribution()[:8],
        "top_skills": get_skill_distribution()[:10],
        "transformation": transformation,
        "role_skill_gaps": get_role_skill_gaps(),
    }
