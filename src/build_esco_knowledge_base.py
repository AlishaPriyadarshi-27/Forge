import pandas as pd
from pathlib import Path

# ============================================================
# FORGE - ESCO KNOWLEDGE BASE BUILDER
# ============================================================

ESCO_DIR = Path(
    "datasets/esco/ESCO_EXTRACTED"
)

OUTPUT_DIR = Path(
    "datasets/esco/knowledge_base"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 70)
print("FORGE - BUILDING ESCO KNOWLEDGE BASE")
print("=" * 70)

# ============================================================
# 1. LOAD ESCO OCCUPATIONS
# ============================================================

print("\n[1/4] Loading occupations...")

occupations = pd.read_csv(
    ESCO_DIR / "occupations_en.csv",
    encoding="utf-8-sig"
)

print(
    f"Occupations loaded: {len(occupations):,}"
)

# Keep useful occupation information
occupations = occupations[
    [
        "conceptUri",
        "preferredLabel",
        "altLabels",
        "description",
        "code",
        "iscoGroup"
    ]
].copy()

occupations = occupations.rename(
    columns={
        "conceptUri": "occupation_uri",
        "preferredLabel": "occupation_label",
        "altLabels": "occupation_alt_labels",
        "description": "occupation_description",
        "code": "occupation_code",
        "iscoGroup": "isco_group"
    }
)


# ============================================================
# 2. LOAD ESCO SKILLS
# ============================================================

print("\n[2/4] Loading skills...")

skills = pd.read_csv(
    ESCO_DIR / "skills_en.csv",
    encoding="utf-8-sig"
)

print(
    f"Skills loaded: {len(skills):,}"
)

skills = skills[
    [
        "conceptUri",
        "skillType",
        "reuseLevel",
        "preferredLabel",
        "altLabels",
        "description"
    ]
].copy()

skills = skills.rename(
    columns={
        "conceptUri": "skill_uri",
        "skillType": "skill_type",
        "reuseLevel": "reuse_level",
        "preferredLabel": "skill_label",
        "altLabels": "skill_alt_labels",
        "description": "skill_description"
    }
)


# ============================================================
# 3. LOAD OCCUPATION-SKILL RELATIONSHIPS
# ============================================================

print("\n[3/4] Loading occupation-skill relationships...")

relations = pd.read_csv(
    ESCO_DIR / "occupationSkillRelations_en.csv",
    encoding="utf-8-sig"
)

print(
    f"Relationships loaded: {len(relations):,}"
)

relations = relations[
    [
        "occupationUri",
        "occupationLabel",
        "relationType",
        "skillType",
        "skillUri",
        "skillLabel"
    ]
].copy()

relations = relations.rename(
    columns={
        "occupationUri": "occupation_uri",
        "occupationLabel": "relation_occupation_label",
        "relationType": "relation_type",
        "skillType": "relation_skill_type",
        "skillUri": "skill_uri",
        "skillLabel": "relation_skill_label"
    }
)


# ============================================================
# 4. BUILD MASTER OCCUPATION-SKILL TABLE
# ============================================================

print("\n[4/4] Building master knowledge base...")

knowledge_base = relations.merge(
    occupations,
    on="occupation_uri",
    how="left"
)

knowledge_base = knowledge_base.merge(
    skills,
    on="skill_uri",
    how="left"
)

# Remove exact duplicate relationships
knowledge_base = knowledge_base.drop_duplicates(
    subset=[
        "occupation_uri",
        "skill_uri",
        "relation_type"
    ]
)

# ============================================================
# 5. SAVE KNOWLEDGE BASE
# ============================================================

output_file = (
    OUTPUT_DIR /
    "esco_occupation_skill_knowledge_base.parquet"
)

knowledge_base.to_parquet(
    output_file,
    index=False
)

# Also save a CSV for easy inspection
csv_output = (
    OUTPUT_DIR /
    "esco_occupation_skill_knowledge_base.csv"
)

knowledge_base.to_csv(
    csv_output,
    index=False,
    encoding="utf-8"
)


# ============================================================
# 6. REPORT
# ============================================================

print("\n" + "=" * 70)
print("ESCO KNOWLEDGE BASE COMPLETE")
print("=" * 70)

print(
    f"\nMaster relationships: "
    f"{len(knowledge_base):,}"
)

print(
    f"Unique occupations: "
    f"{knowledge_base['occupation_uri'].nunique():,}"
)

print(
    f"Unique skills: "
    f"{knowledge_base['skill_uri'].nunique():,}"
)

print("\nRelation types:")

print(
    knowledge_base["relation_type"]
    .value_counts(dropna=False)
)

print("\nSkill types:")

print(
    knowledge_base["skill_type"]
    .value_counts(dropna=False)
)

print("\nExample records:")

print(
    knowledge_base[
        [
            "occupation_label",
            "skill_label",
            "relation_type",
            "skill_type"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nSaved files:")

print(output_file)
print(csv_output)

print("\n" + "=" * 70)
print("FORGE ESCO KNOWLEDGE BASE READY")
print("=" * 70)