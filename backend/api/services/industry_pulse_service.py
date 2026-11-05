from __future__ import annotations

import html
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from backend.api.services.topic_intelligence_generator import TopicIntelligenceGenerator, TopicIntelligenceGenerationError
except Exception:
    TopicIntelligenceGenerator = None
    TopicIntelligenceGenerationError = Exception


class IndustryPulseService:
    """
    Evidence-first Industry Pulse for FORGE.

    The four horizons deliberately answer different questions:
      current  -> observed employer demand now
      emerging -> observed multi-period momentum, not simply high demand
      fiveYear -> WEF 2025-2030 capability outlook + role evidence
      tenYear  -> BLS 2025-2035 occupation outlook + role evidence

    The service never presents an individual technology as a guaranteed
    2030/2035 prediction. If evidence is insufficient, the relevant list is
    left empty and an explanation is returned.
    """

    ROLE_ALIASES = {
        "frontend developer": ["web developers", "web and digital interface designers", "software developers"],
        "backend developer": ["software developers", "web developers"],
        "full stack developer": ["software developers", "web developers", "web and digital interface designers"],
        "software engineer": ["software developers", "software quality assurance analysts and testers"],
        "ml engineer": ["data scientists", "computer and information research scientists", "software developers"],
        "ai engineer": ["computer and information research scientists", "data scientists", "software developers"],
        "data scientist": ["data scientists"],
        "data analyst": ["data scientists", "operations research analysts", "market research analysts"],
        "devops / cloud engineer": ["software developers", "computer network architects", "network and computer systems administrators"],
        "cybersecurity engineer": ["information security analysts", "computer network architects", "software developers"],
        "product engineer": ["software developers", "web developers", "web and digital interface designers"],
    }

    # Canonical extraction ontology. These names do NOT imply demand or
    # future importance; they are only patterns used to detect mentions in
    # employer text and O*NET technology records.
    TOPIC_ALIASES = {
        "large language models": ["large language model", "large language models", "llm", "llms"],
        "generative ai": ["generative ai", "genai", "generative artificial intelligence"],
        "retrieval augmented generation": ["retrieval augmented generation", "retrieval-augmented generation", "rag"],
        "ai agents": ["ai agent", "ai agents", "agentic ai", "agentic systems"],
        "vector databases": ["vector database", "vector databases", "vector db", "vector dbs"],
        "llm evaluation": ["llm evaluation", "llm evaluations", "large language model evaluation"],
        "fine tuning": ["fine tuning", "fine-tuning", "parameter efficient fine tuning", "parameter-efficient fine-tuning", "peft", "lora"],
        "multimodal ai": ["multimodal ai", "multimodal artificial intelligence", "multimodal models"],
        "mlops": ["mlops", "machine learning operations", "machine-learning operations"],
        "deep learning": ["deep learning"],
        "machine learning": ["machine learning", "machine-learning"],
        "pytorch": ["pytorch"], "tensorflow": ["tensorflow"], "scikit learn": ["scikit-learn", "scikit learn", "sklearn"],
        "python": ["python"], "sql": ["sql"], "typescript": ["typescript"], "javascript": ["javascript"],
        "react": ["react", "react.js", "reactjs"], "next.js": ["next.js", "nextjs"], "node.js": ["node.js", "nodejs"],
        "rest apis": ["rest api", "rest apis", "restful api", "restful apis"], "graphql": ["graphql"],
        "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"], "terraform": ["terraform"],
        "aws": ["aws", "amazon web services"], "microsoft azure": ["azure", "microsoft azure"], "google cloud": ["gcp", "google cloud", "google cloud platform"],
        "microservices": ["microservices", "microservice architecture"], "distributed systems": ["distributed systems"],
        "event driven architecture": ["event-driven architecture", "event driven architecture"], "observability": ["observability"],
        "devsecops": ["devsecops"], "zero trust": ["zero trust", "zero-trust"], "cloud security": ["cloud security"],
        "identity and access management": ["identity and access management", "iam"], "threat detection": ["threat detection"],
        "security automation": ["security automation"], "data engineering": ["data engineering"], "data pipelines": ["data pipeline", "data pipelines"],
        "apache spark": ["apache spark", "spark"], "airflow": ["airflow", "apache airflow"],
        "data visualization": ["data visualization", "data visualisation"], "power bi": ["power bi", "powerbi"], "tableau": ["tableau"],
        "feature engineering": ["feature engineering"], "model deployment": ["model deployment", "model serving"],
        "computer vision": ["computer vision", "computer-vision"], "natural language processing": ["natural language processing", "natural-language processing", "nlp"],
        "transformers": ["transformer", "transformers"],
        "ai assisted development": ["ai-assisted development", "ai assisted development", "ai coding", "ai coding assistant", "ai pair programming", "copilot"],
        "web performance": ["web performance", "core web vitals"], "accessibility": ["accessibility", "web accessibility", "wcag"],
        "infrastructure as code": ["infrastructure as code", "iac"], "platform engineering": ["platform engineering"],
    }

    TOPIC_DISPLAY = {
        k: v for k, v in {
            "large language models": "Large Language Models (LLMs)", "generative ai": "Generative AI",
            "retrieval augmented generation": "Retrieval-Augmented Generation (RAG)", "ai agents": "AI Agents / Agentic AI",
            "vector databases": "Vector Databases", "llm evaluation": "LLM Evaluation", "fine tuning": "Fine-tuning / PEFT",
            "multimodal ai": "Multimodal AI", "mlops": "MLOps", "deep learning": "Deep Learning", "machine learning": "Machine Learning",
            "pytorch": "PyTorch", "tensorflow": "TensorFlow", "scikit learn": "Scikit-learn", "python": "Python", "sql": "SQL",
            "typescript": "TypeScript", "javascript": "JavaScript", "react": "React", "next.js": "Next.js", "node.js": "Node.js",
            "rest apis": "REST APIs", "graphql": "GraphQL", "docker": "Docker", "kubernetes": "Kubernetes", "terraform": "Terraform",
            "aws": "AWS", "microsoft azure": "Microsoft Azure", "google cloud": "Google Cloud", "microservices": "Microservices",
            "distributed systems": "Distributed Systems", "event driven architecture": "Event-Driven Architecture", "observability": "Observability",
            "devsecops": "DevSecOps", "zero trust": "Zero Trust", "cloud security": "Cloud Security",
            "identity and access management": "Identity & Access Management", "threat detection": "Threat Detection", "security automation": "Security Automation",
            "data engineering": "Data Engineering", "data pipelines": "Data Pipelines", "apache spark": "Apache Spark", "airflow": "Airflow",
            "data visualization": "Data Visualization", "power bi": "Power BI", "tableau": "Tableau", "feature engineering": "Feature Engineering",
            "model deployment": "Model Deployment", "computer vision": "Computer Vision", "natural language processing": "Natural Language Processing (NLP)",
            "transformers": "Transformers", "ai assisted development": "AI-Assisted Development", "web performance": "Web Performance",
            "accessibility": "Web Accessibility", "infrastructure as code": "Infrastructure as Code", "platform engineering": "Platform Engineering",
        }.items()
    }

    # Ontology bridge, not a prediction list. It connects observed technology
    # evidence to WEF's broader 2030 capability categories.
    WEF_GROUP_MAP = {
        "AI and big data": {"large language models", "generative ai", "retrieval augmented generation", "ai agents", "vector databases", "llm evaluation", "fine tuning", "multimodal ai", "machine learning", "deep learning", "pytorch", "tensorflow", "scikit learn", "mlops", "feature engineering", "model deployment", "computer vision", "natural language processing", "transformers", "data engineering", "data pipelines", "apache spark", "airflow"},
        "Technological literacy": {"python", "sql", "typescript", "javascript", "react", "next.js", "node.js", "rest apis", "graphql", "docker", "kubernetes", "terraform", "aws", "microsoft azure", "google cloud", "microservices", "distributed systems", "observability", "infrastructure as code", "platform engineering", "ai assisted development"},
        "Networks and cybersecurity": {"devsecops", "zero trust", "cloud security", "identity and access management", "threat detection", "security automation"},
        "Programming": {"python", "typescript", "javascript", "react", "next.js", "node.js", "rest apis", "graphql", "pytorch", "tensorflow", "scikit learn", "machine learning"},
        "Design and user experience": {"react", "next.js", "web performance", "accessibility", "javascript", "typescript"},
        "Analytical thinking": {"machine learning", "deep learning", "data engineering", "data pipelines", "sql", "feature engineering", "llm evaluation", "observability"},
        "Systems thinking": {"distributed systems", "microservices", "event driven architecture", "kubernetes", "terraform", "platform engineering", "mlops", "observability", "data pipelines"},
        "Creative thinking": {"generative ai", "multimodal ai", "ai agents", "react", "design and user experience"},
    }

    # Data-driven relevance map used only to filter global career context.
    # It is not a forecast and does not affect observed market prevalence.
    WEF_ROLE_TOPIC_MAP = {
        "Big Data Specialists": {"data engineering", "data pipelines", "apache spark", "airflow", "sql", "python", "machine learning", "feature engineering"},
        "AI and Machine Learning Specialists": {"machine learning", "deep learning", "pytorch", "tensorflow", "scikit learn", "python", "computer vision", "natural language processing", "transformers", "large language models", "generative ai", "retrieval augmented generation", "fine tuning", "mlops", "llm evaluation", "ai agents"},
        "Software and Applications Developers": {"python", "typescript", "javascript", "react", "next.js", "node.js", "rest apis", "graphql", "docker", "kubernetes", "microservices", "distributed systems", "sql", "aws", "microsoft azure", "google cloud", "ai assisted development"},
        "Information Security Analysts": {"devsecops", "zero trust", "cloud security", "identity and access management", "threat detection", "security automation", "aws", "microsoft azure", "google cloud", "kubernetes"},
    }

    WEF_SIGNAL_FALLBACK = {
        "AI and big data": "fastest-growing", "Networks and cybersecurity": "fastest-growing", "Technological literacy": "fastest-growing",
        "Creative thinking": "rising", "Resilience flexibility and agility": "rising", "Curiosity and lifelong learning": "rising",
        "Leadership and social influence": "rising", "Talent management": "rising", "Analytical thinking": "rising",
        "Environmental stewardship": "rising", "Systems thinking": "rising", "Programming": "rising/stable", "Design and user experience": "rising",
    }

    GENERIC_CAPABILITY_PATTERNS = ("working with computers", "processing information", "getting information", "making decisions and solving problems", "organizing planning and prioritizing work", "updating and using relevant knowledge", "communicating with supervisors peers or subordinates", "documenting recording information", "identifying objects actions and events", "analyzing data or information", "providing consultation and advice to others")

    MARKET_ROLE_CATEGORY = {
        "software engineer": "engineering",
        "frontend developer": "engineering",
        "backend developer": "engineering",
        "full stack developer": "engineering",
        "product engineer": "engineering",
        "data scientist": "data",
        "data analyst": "data",
        "devops / cloud engineer": "devops",
        "devops engineer": "devops",
        "cloud engineer": "devops",
        "cybersecurity engineer": "security",
        "ai engineer": "ai",
        "ml engineer": "ai",
    }

    def __init__(self, project_root: str | Path | None = None, topic_generator: Any | None = None):
        self.root = Path(project_root).resolve() if project_root else Path(__file__).resolve().parents[3]
        self.worktrace_path = self.root / "datasets" / "onet" / "knowledge_base" / "forge_worktrace.parquet"
        self.job_candidates = [
            self.root / "datasets" / "job_postings" / "greenhouse" / "e365621720174a7c9a735ce27e97e681-0.parquet",
            self.root / "datasets" / "job_postings" / "greenhouse" / "forge_greenhouse_clean.parquet",
            self.root / "datasets" / "job_postings" / "greenhouse" / "forge_greenhouse_clean.csv",
        ]
        self.onet_tech_candidates = [
            self.root / "datasets" / "onet" / "knowledge_base" / "onet_software_skills.parquet",
            self.root / "datasets" / "onet" / "knowledge_base" / "onet_technology_skills.parquet",
            self.root / "datasets" / "onet" / "EXTRACT ONET" / "db_31_0_excel" / "Software Skills.xlsx",
            self.root / "datasets" / "onet" / "technology_skills.csv",
        ]
        self.wef_candidates = [
            self.root / "datasets" / "wef" / "wef_future_skills_2030.csv",
            self.root / "datasets" / "wef" / "future_skills.csv",
            self.root / "datasets" / "future_skills.csv",
        ]
        self.bls_candidates = [
            self.root / "datasets" / "bls" / "knowledge_base" / "bls_occupation_projections.parquet",
        ]
        self._worktrace: pd.DataFrame | None = None

        # ------------------------------------------------------------------
        # Performance caches
        # ------------------------------------------------------------------
        # Industry Pulse is a read-heavy service. The underlying datasets are
        # static during a backend session, so keep role-level derived results
        # in memory instead of recomputing them for every request.
        self._jobs_cache: dict[str, pd.DataFrame] = {}
        self._topic_stats_cache: dict[str, pd.DataFrame] = {}
        self._onet_role_cache: dict[str, pd.DataFrame] = {}
        self._onet_topic_cache: dict[tuple[str, str], dict[str, Any]] = {}
        self._bls_role_cache: dict[str, pd.DataFrame] = {}
        self._occupation_cache: dict[str, pd.DataFrame] = {}
        self._build_cache: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
        self._wef_signal_cache: dict[str, str] = {}

        self._onet: pd.DataFrame | None = None
        self._wef: pd.DataFrame | None = None
        self._bls: pd.DataFrame | None = None
        self.topic_generator = topic_generator
        self._topic_generated_cache: dict[tuple[str, str, str], dict[str, Any]] = {}

        # Daily external market signal layer. This supplements the existing
        # FORGE Greenhouse/O*NET/WEF/BLS evidence without replacing it.
        # The source is a daily job-market dataset with historical snapshots,
        # so the UI can show real movement rather than a hardcoded percentage.
        self.market_source_url = (
            "https://huggingface.co/datasets/datamatastudios/skill-scarcity-index/"
            "resolve/main/skill-scarcity-index.csv?download=true"
        )
        self.market_snapshot_dir = self.root / "datasets" / "market" / "snapshots"
        self.market_snapshot_path = self.market_snapshot_dir / "skill_scarcity_history.csv"
        self._market_history_cache: pd.DataFrame | None = None
        self._market_refresh_checked_at: datetime | None = None
        self._market_refresh_ttl_seconds = 900

        # One generic topic-matching engine for every topic.  This replaces
        # the old Python row-by-row loop + topic-by-topic regex construction.
        # It is an extraction optimization only; it does not change the
        # ontology or evidence semantics.
        alias_map: dict[str, str] = {}
        for canonical, aliases in self.TOPIC_ALIASES.items():
            for alias in aliases:
                normalized = self._norm(alias)
                if normalized:
                    alias_map[normalized] = canonical
        self._topic_alias_map = alias_map
        alternatives = sorted(alias_map.keys(), key=len, reverse=True)
        if alternatives:
            self._combined_topic_pattern = re.compile(
                r"(?<![a-z0-9])(?:"
                + "|".join(re.escape(a) for a in alternatives)
                + r")(?![a-z0-9])"
            )
        else:
            self._combined_topic_pattern = None

    @staticmethod
    def _norm(v: Any) -> str:
        return re.sub(r"[^a-z0-9]+", " ", str(v or "").lower()).strip()

    @staticmethod
    def _clamp(v: float, lo=0.0, hi=1.0) -> float:
        return max(lo, min(hi, float(v)))

    @staticmethod
    def _num(v: Any, default: float = 0.0) -> float:
        try:
            x = float(pd.to_numeric(v, errors="coerce"))
            return default if math.isnan(x) else x
        except Exception:
            return default

    @staticmethod
    def _find_column(df: pd.DataFrame, names: list[str]) -> str | None:
        norm = {re.sub(r"[^a-z0-9]+", "_", str(c).lower()).strip("_"): c for c in df.columns}
        for n in names:
            k = re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
            if k in norm:
                return norm[k]
        return None

    def _load_worktrace(self) -> pd.DataFrame:
        if self._worktrace is not None:
            return self._worktrace
        if not self.worktrace_path.exists():
            return pd.DataFrame()
        df = pd.read_parquet(self.worktrace_path)
        df.columns = [str(c).strip() for c in df.columns]
        for c in ["employment_2025_thousands", "employment_2035_thousands", "employment_change_percent", "employment_change_thousands", "occupational_openings_2025_35_annual_avg_thousands", "Occupation Capability Value", "Semantic Similarity"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        self._worktrace = df
        return df

    def _role_candidates(self, role: str) -> list[str]:
        rn = self._norm(role)
        return [rn] + [self._norm(x) for x in self.ROLE_ALIASES.get(rn, [])]

    def _load_jobs(self, role: str | None = None) -> pd.DataFrame:
        """Load role-matched Greenhouse postings robustly.

        Important: do not assume the first Greenhouse export is the correct
        schema/version.  FORGE has multiple exports of the same market data.
        For a role-specific request we try each available candidate until we
        obtain actual role matches.  We also discover title/date/description
        columns instead of hard-coding one parquet schema.
        """
        key = self._norm(role) if role else "__all__"
        if key in self._jobs_cache:
            return self._jobs_cache[key]

        empty = pd.DataFrame(columns=["__title", "__description", "__text", "__posted_at"])
        aliases = [a for a in self._role_candidates(role)] if role else []

        def title_mask(series: pd.Series) -> pd.Series:
            if not role:
                return pd.Series(True, index=series.index)
            tn = series.fillna("").astype(str).map(self._norm)
            mask = pd.Series(False, index=series.index)
            for alias in aliases:
                if alias:
                    mask |= tn.str.contains(
                        r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])",
                        regex=True,
                        na=False,
                    )
            return mask

        def read_candidate(path: Path) -> pd.DataFrame:
            pieces: list[pd.DataFrame] = []
            if path.suffix.lower() == ".parquet":
                import pyarrow.parquet as pq
                pf = pq.ParquetFile(path)
                names = [str(x).strip() for x in pf.schema_arrow.names]
                title_name = self._find_column(
                    pd.DataFrame(columns=names),
                    ["title", "job_title", "position", "job_position", "name"],
                )
                desc_name = self._find_column(
                    pd.DataFrame(columns=names),
                    ["description_html", "description", "job_description", "content"],
                )
                date_name = self._find_column(
                    pd.DataFrame(columns=names),
                    ["posted_at", "date_posted", "posted_date", "created_at", "updated_at"],
                )
                columns = [x for x in [title_name, desc_name, date_name] if x]
                if not title_name or not columns:
                    return empty
                for batch in pf.iter_batches(batch_size=5000, columns=columns, use_threads=True):
                    chunk = batch.to_pandas(split_blocks=True, self_destruct=True)
                    chunk.columns = [str(c).strip() for c in chunk.columns]
                    tc = self._find_column(chunk, ["title", "job_title", "position", "job_position", "name"])
                    if not tc:
                        continue
                    chunk["__title"] = chunk[tc].fillna("").astype(str)
                    if role:
                        chunk = chunk.loc[title_mask(chunk["__title"])].copy()
                    if chunk.empty:
                        continue
                    dc = self._find_column(chunk, ["description_html", "description", "job_description", "content"])
                    pc = self._find_column(chunk, ["posted_at", "date_posted", "posted_date", "created_at", "updated_at"])
                    chunk["__description"] = chunk[dc].fillna("").astype(str) if dc else ""
                    chunk["__description"] = chunk["__description"].map(lambda x: html.unescape(re.sub(r"<[^>]+>", " ", x)))
                    chunk["__text"] = (chunk["__title"] + " " + chunk["__description"]).str.lower()
                    chunk["__posted_at"] = pd.to_datetime(chunk[pc], errors="coerce", utc=True) if pc else pd.NaT
                    pieces.append(chunk[["__title", "__description", "__text", "__posted_at"]].copy())
            else:
                header = pd.read_csv(path, nrows=0)
                title_name = self._find_column(header, ["title", "job_title", "position", "job_position", "name"])
                desc_name = self._find_column(header, ["description_html", "description", "job_description", "content"])
                date_name = self._find_column(header, ["posted_at", "date_posted", "posted_date", "created_at", "updated_at"])
                usecols = [x for x in [title_name, desc_name, date_name] if x]
                if not title_name:
                    return empty
                for chunk in pd.read_csv(path, usecols=usecols, dtype=str, chunksize=5000, low_memory=True):
                    chunk["__title"] = chunk[title_name].fillna("")
                    if role:
                        chunk = chunk.loc[title_mask(chunk["__title"])].copy()
                    if chunk.empty:
                        continue
                    chunk["__description"] = chunk[desc_name].fillna("").map(lambda x: html.unescape(re.sub(r"<[^>]+>", " ", str(x)))) if desc_name else ""
                    chunk["__text"] = (chunk["__title"] + " " + chunk["__description"]).str.lower()
                    chunk["__posted_at"] = pd.to_datetime(chunk[date_name], errors="coerce", utc=True) if date_name else pd.NaT
                    pieces.append(chunk[["__title", "__description", "__text", "__posted_at"]].copy())
            return pd.concat(pieces, ignore_index=True) if pieces else empty

        # Try every available export. This prevents a stale/partial parquet
        # from masking the cleaned 152,839-row Greenhouse dataset.
        candidates = [p for p in self.job_candidates if p.exists()]
        result = empty
        for path in candidates:
            try:
                candidate_result = read_candidate(path)
                if role:
                    if not candidate_result.empty:
                        result = candidate_result
                        break
                else:
                    result = candidate_result
                    break
            except Exception as exc:
                print(f"[WARN] Greenhouse candidate failed: {path.name}: {exc}")

        if role and result.empty:
            print(f"[WARN] No Greenhouse title matches found for role: {role}")

        self._jobs_cache[key] = result
        return result


    def _load_optional(self, candidates: list[Path]) -> pd.DataFrame:
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            return pd.DataFrame()
        try:
            if path.suffix.lower() == ".parquet":
                df = pd.read_parquet(path)
            elif path.suffix.lower() in {".xlsx", ".xls"}:
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path, low_memory=False)
            df.columns = [str(c).strip() for c in df.columns]
            return df
        except Exception as exc:
            print(f"[WARN] Optional dataset failed: {path.name}: {exc}")
            return pd.DataFrame()

    def _load_onet(self) -> pd.DataFrame:
        if self._onet is None:
            self._onet = self._load_optional(self.onet_tech_candidates)
        return self._onet

    def _load_wef(self) -> pd.DataFrame:
        if self._wef is None:
            self._wef = self._load_optional(self.wef_candidates)
        return self._wef

    def _load_bls(self) -> pd.DataFrame:
        if self._bls is None:
            self._bls = self._load_optional(self.bls_candidates)
        return self._bls

    def _match_occupations(self, role: str) -> pd.DataFrame:
        key = self._norm(role)
        cached = self._occupation_cache.get(key)
        if cached is not None:
            return cached

        df = self._load_worktrace()
        if df.empty or "Occupation Title" not in df.columns:
            out = pd.DataFrame(columns=["Occupation Title", "match_score"])
            self._occupation_cache[key] = out
            return out

        titles = df[["Occupation Title"]].dropna().drop_duplicates()
        titles["norm"] = titles["Occupation Title"].map(self._norm)
        aliases = set(self._role_candidates(role))
        out = titles[titles["norm"].isin(aliases)].copy()
        out["match_score"] = 1.0
        out = out[["Occupation Title", "match_score"]].reset_index(drop=True)
        self._occupation_cache[key] = out
        return out

    def _topic_hits(self, text: str) -> list[str]:
        n = self._norm(text)
        hits = []
        for canonical, aliases in self.TOPIC_ALIASES.items():
            for alias in aliases:
                a = self._norm(alias)
                if a and re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", n):
                    hits.append(canonical)
                    break
        return hits

    def _complete_quarter_cutoff(self, dates: pd.Series) -> pd.Timestamp | None:
        valid = dates.dropna()
        if valid.empty:
            return None
        latest = valid.max()
        q_end = latest.to_period("Q").end_time.tz_localize("UTC") if latest.tzinfo else latest.to_period("Q").end_time
        # Exclude the current partial quarter.
        if latest < q_end:
            return latest.to_period("Q").start_time.tz_localize("UTC") if latest.tzinfo else latest.to_period("Q").start_time
        return q_end

    def _extract_topic_stats(self, role: str, jobs: pd.DataFrame) -> pd.DataFrame:
        role_key = self._norm(role)
        cached = self._topic_stats_cache.get(role_key)
        if cached is not None:
            return cached

        if jobs.empty:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        j = jobs.dropna(subset=["__posted_at"]).copy()
        if j.empty:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        cutoff = self._complete_quarter_cutoff(j["__posted_at"])
        if cutoff is not None:
            # Keep quarters whose start is before the current quarter.
            current_q = cutoff.to_period("Q")
            j = j[j["__posted_at"].dt.to_period("Q") < current_q]

        if j.empty:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        j["__period"] = j["__posted_at"].dt.to_period("Q").astype(str)

        # Fast generic topic extraction:
        # one combined regex pass per posting instead of:
        #   posting -> every topic -> every alias -> regex search
        # Then normalize/deduplicate so each topic counts at most once per job.
        if self._combined_topic_pattern is None:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        matched = j["__text"].fillna("").astype(str).str.findall(self._combined_topic_pattern)
        mentions = (
            matched.rename("__matches")
            .to_frame()
            .assign(job_index=j.index, period=j["__period"].values)
            .explode("__matches", ignore_index=False)
            .dropna(subset=["__matches"])
        )
        if mentions.empty:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        # The regex operates on normalized aliases.  Since job text may contain
        # punctuation/hyphens, normalize the matched token before mapping it.
        mentions["topic"] = mentions["__matches"].map(
            lambda x: self._topic_alias_map.get(self._norm(x))
        )
        mentions = mentions.dropna(subset=["topic"])
        mentions = mentions.drop_duplicates(subset=["job_index", "topic"])

        if mentions.empty:
            result = pd.DataFrame()
            self._topic_stats_cache[role_key] = result
            return result

        mentions = mentions[["topic", "job_index", "period"]]
        total_by_period = j.groupby("__period").size().to_dict()
        all_periods = sorted(total_by_period)

        records = []
        for topic, g in mentions.groupby("topic"):
            counts = g.groupby("period")["job_index"].nunique().sort_index()
            period_counts = {p: int(counts.get(p, 0)) for p in all_periods}
            period_shares = {
                p: (period_counts[p] / total_by_period[p] if total_by_period[p] else 0.0)
                for p in all_periods
            }

            recent_periods = all_periods[-4:]
            prior_periods = all_periods[-8:-4]
            recent_n = sum(period_counts[p] for p in recent_periods)
            prior_n = sum(period_counts[p] for p in prior_periods)
            recent_active_periods = sum(1 for p in recent_periods if period_counts[p] > 0)
            recent_jobs = sum(total_by_period[p] for p in recent_periods)
            prior_jobs = sum(total_by_period[p] for p in prior_periods)
            recent_share = recent_n / recent_jobs if recent_jobs else 0.0
            prior_share = prior_n / prior_jobs if prior_jobs else 0.0

            usable = [p for p in all_periods if total_by_period[p] >= 2]
            transitions = len(usable) - 1 if len(usable) > 1 else 0
            positive = sum(
                1 for a, b in zip(usable, usable[1:])
                if period_shares[b] > period_shares[a] + 0.005
            )
            consistency = positive / transitions if transitions else 0.0

            records.append({
                "topic": topic,
                "job_mentions": int(g["job_index"].nunique()),
                "role_job_count": int(len(j)),
                "recent_mentions": int(recent_n),
                "prior_mentions": int(prior_n),
                "recent_job_count": int(recent_jobs),
                "prior_job_count": int(prior_jobs),
                "recent_share": float(recent_share),
                "prior_share": float(prior_share),
                "share_change_pp": float((recent_share - prior_share) * 100),
                "trend_consistency": float(consistency),
                "usable_periods": int(len(usable)),
                "recent_active_periods": int(recent_active_periods),
                "period_counts": period_counts,
                "period_shares": period_shares,
                "first_period": all_periods[0],
                "latest_period": all_periods[-1],
                "current_window": "latest 4 complete quarters",
            })

        result = pd.DataFrame(records)
        self._topic_stats_cache[role_key] = result
        return result

    def _onet_topic_evidence(self, role: str, topic: str) -> dict[str, Any]:
        key = (self._norm(role), str(topic))
        cached = self._onet_topic_cache.get(key)
        if cached is not None:
            return cached

        df = self._load_onet()
        if df.empty:
            out = {"score": 0.0, "records": 0, "in_demand": 0, "hot": 0}
            self._onet_topic_cache[key] = out
            return out

        title_col = self._find_column(df, ["Title", "Occupation Title", "title"])
        tech_col = self._find_column(df, ["Workplace Example", "Technology", "Technology Name", "Example"])
        if not title_col or not tech_col:
            out = {"score": 0.0, "records": 0, "in_demand": 0, "hot": 0}
            self._onet_topic_cache[key] = out
            return out

        role_key = self._norm(role)
        r = self._onet_role_cache.get(role_key)
        if r is None:
            role_titles = set(self._role_candidates(role))
            title_norm = df[title_col].fillna("").astype(str).map(self._norm)
            r = df[title_norm.isin(role_titles)].copy()
            self._onet_role_cache[role_key] = r

        if r.empty:
            out = {"score": 0.0, "records": 0, "in_demand": 0, "hot": 0}
            self._onet_topic_cache[key] = out
            return out

        aliases = [self._norm(x) for x in self.TOPIC_ALIASES.get(topic, []) if self._norm(x)]
        if not aliases:
            out = {"score": 0.0, "records": len(r), "in_demand": 0, "hot": 0}
            self._onet_topic_cache[key] = out
            return out

        tech_norm = r[tech_col].fillna("").astype(str).map(self._norm)
        pattern = re.compile(
            r"(?<![a-z0-9])(?:" + "|".join(re.escape(a) for a in sorted(aliases, key=len, reverse=True)) + r")(?![a-z0-9])"
        )
        hit = tech_norm.str.contains(pattern, regex=True, na=False)
        h = r[hit]

        if h.empty:
            out = {"score": 0.0, "records": len(r), "in_demand": 0, "hot": 0}
            self._onet_topic_cache[key] = out
            return out

        in_col = self._find_column(h, ["In Demand", "in_demand"])
        hot_col = self._find_column(h, ["Hot Technology", "hot_technology"])
        demand = int(h[in_col].astype(str).str.upper().eq("Y").sum()) if in_col else 0
        hot = int(h[hot_col].astype(str).str.upper().eq("Y").sum()) if hot_col else 0
        prevalence = len(h) / max(len(r), 1)
        score = self._clamp(
            0.55 * min(1.0, prevalence * 4)
            + 0.25 * demand / max(len(h), 1)
            + 0.20 * hot / max(len(h), 1)
        )
        out = {"score": score, "records": len(h), "in_demand": demand, "hot": hot}
        self._onet_topic_cache[key] = out
        return out

    def _wef_signal(self, group: str) -> str:
        key = self._norm(group)
        if key in self._wef_signal_cache:
            return self._wef_signal_cache[key]

        df = self._load_wef()
        if df.empty:
            value = self.WEF_SIGNAL_FALLBACK.get(group, "rising")
            self._wef_signal_cache[key] = value
            return value
        skill_col = self._find_column(df, ["skill", "skills", "skill_name"])
        signal_col = self._find_column(df, ["2030_signal", "signal", "trend"])
        if not skill_col:
            return self.WEF_SIGNAL_FALLBACK.get(group, "rising")
        target = self._norm(group)
        rows = df[df[skill_col].fillna("").astype(str).map(self._norm) == target]
        if rows.empty or not signal_col:
            value = self.WEF_SIGNAL_FALLBACK.get(group, "rising")
        else:
            value = str(rows.iloc[0][signal_col])
        self._wef_signal_cache[key] = value
        return value

    def _wef_capabilities(self, role: str, stats: pd.DataFrame) -> list[dict[str, Any]]:
        if stats.empty:
            return []
        topic_support = {}
        for _, r in stats.iterrows():
            topic = r["topic"]
            prevalence = float(r["recent_share"])
            onet = self._onet_topic_evidence(role, topic)["score"]
            for group, topics in self.WEF_GROUP_MAP.items():
                if topic in topics:
                    topic_support.setdefault(group, []).append((topic, prevalence, onet))
        items = []
        for group, supports in topic_support.items():
            market_support = self._clamp(sum(x[1] for x in supports) / max(1.0, len(supports) * 0.35))
            onet_support = self._clamp(sum(x[2] for x in supports) / max(1, len(supports)))
            relevance = self._clamp(0.65 * market_support + 0.35 * onet_support)
            if relevance < 0.12:
                continue
            supporting = sorted({self._display_name(x[0]) for x in supports}, key=str.lower)[:6]
            items.append({
                "name": group,
                "topic_key": f"wef:{self._norm(group)}",
                "horizon": "fiveYear",
                "forecast_type": "capability outlook, not technology forecast",
                "wef_signal": self._wef_signal(group),
                "role_relevance": round(relevance, 3),
                "market_support": round(market_support, 3),
                "onet_support": round(onet_support, 3),
                "supporting_topics": supporting,
                "confidence": round(self._clamp(0.55 * min(1.0, len(supports) / 3) + 0.45 * relevance), 3),
                "source": "WEF Future of Jobs 2025 + FORGE employer/O*NET evidence",
                "description": f"WEF reports this capability as a {self._wef_signal(group)} 2025–2030 skill signal. FORGE links it to observed role evidence through: {', '.join(supporting)}.",
                "reason": "The WEF source supports the broad capability direction; the technology names are supporting role evidence, not WEF technology forecasts.",
            })
        return sorted(items, key=lambda x: (x["role_relevance"], x["confidence"]), reverse=True)[:8]

    def _bls_role_rows(self, role: str) -> pd.DataFrame:
        key = self._norm(role)
        cached = self._bls_role_cache.get(key)
        if cached is not None:
            return cached

        df = self._load_bls()
        if df.empty:
            self._bls_role_cache[key] = df
            return df
        title_col = self._find_column(df, ["occupation_title", "Occupation Title", "title"])
        if not title_col:
            out = pd.DataFrame()
            self._bls_role_cache[key] = out
            return out
        aliases = set(self._role_candidates(role))
        n = df[title_col].fillna("").astype(str).map(self._norm)
        out = df[n.isin(aliases)].copy()
        self._bls_role_cache[key] = out
        return out

    def _ten_year(self, role: str, stats: pd.DataFrame) -> list[dict[str, Any]]:
        bls = self._bls_role_rows(role)
        if bls.empty:
            # WORKTRACE may still contain BLS-derived projection fields.
            wt = self._load_worktrace()
            if wt.empty or "Occupation Title" not in wt.columns:
                return []
            titles = set(self._role_candidates(role))
            n = wt["Occupation Title"].fillna("").astype(str).map(self._norm)
            bls = wt[n.isin(titles)].drop_duplicates(subset=["Occupation Title"])
        if bls.empty:
            return []
        title_col = self._find_column(bls, ["occupation_title", "Occupation Title", "title"])
        growth_col = self._find_column(bls, ["employment_change_percent"])
        change_col = self._find_column(bls, ["employment_change_thousands", "employment_change_absolute_thousands"])
        open_col = self._find_column(bls, ["occupational_openings_2025_35_annual_avg_thousands"])
        e25 = self._find_column(bls, ["employment_2025_thousands"])
        e35 = self._find_column(bls, ["employment_2035_thousands"])
        out = []
        for _, r in bls.iterrows():
            title = str(r.get(title_col, "Occupation"))
            growth = self._num(r.get(growth_col))
            change = self._num(r.get(change_col))
            openings = self._num(r.get(open_col))
            techs = []
            if not stats.empty:
                techs = [self._display_name(x) for x in stats.sort_values("recent_share", ascending=False).head(6)["topic"].tolist()]
            out.append({
                "name": title,
                "topic_key": f"bls:{self._norm(title)}",
                "horizon": "tenYear",
                "forecast_type": "occupation outlook, not technology forecast",
                "bls_growth_percent": round(growth, 2),
                "employment_change_thousands": round(change, 1),
                "annual_openings_thousands": round(openings, 1),
                "employment_2025_thousands": self._num(r.get(e25)),
                "employment_2035_thousands": self._num(r.get(e35)),
                "supporting_topics": techs,
                "drivers": ["AI", "IoT", "automation", "security", "software-intensive systems"],
                "confidence": round(self._clamp(0.65 + min(0.25, abs(growth) / 100)), 3),
                "source": "BLS 2025–2035 occupational projections + FORGE role evidence",
                "description": f"BLS projects the {title} occupation through 2035. The technology list is current evidence and is not a prediction of which individual technologies will dominate in 2035.",
                "reason": "BLS provides an occupation-level structural outlook. FORGE intentionally does not convert that into a technology-specific 2035 prediction.",
            })
        return sorted(out, key=lambda x: (x["bls_growth_percent"], x["annual_openings_thousands"]), reverse=True)[:5]

    def _current_items(self, role: str, stats: pd.DataFrame) -> list[dict[str, Any]]:
        if stats.empty:
            return []
        rows = stats.copy()
        rows["onet"] = rows["topic"].map(lambda x: self._onet_topic_evidence(role, x)["score"])
        rows["current_score"] = 0.75 * rows["recent_share"] + 0.15 * rows["onet"] + 0.10 * rows["job_mentions"].clip(upper=20) / 20
        rows = rows[rows["recent_share"] > 0]
        rows = rows.sort_values("current_score", ascending=False).head(15)
        out = []
        for _, r in rows.iterrows():
            sample = int(r["role_job_count"])
            confidence = self._sample_confidence(sample, int(r["recent_mentions"]))
            out.append({
                "name": self._display_name(r["topic"]), "topic_key": r["topic"], "horizon": "current",
                "market_mentions": int(r["recent_mentions"]), "role_job_count": sample,
                "prevalence_percent": round(float(r["recent_share"]) * 100, 2),
                "confidence": round(confidence, 3), "confidence_label": self._confidence_label(confidence, sample),
                "source": "FORGE Greenhouse employer postings + O*NET technology evidence",
                "trend_label": "Established demand", "description": f"Observed in {int(r['recent_mentions'])} of {sample} role-matched postings in the latest four complete quarters.",
                "reason": "Current Demand reflects observed employer demand, not a future prediction.",
                "onet_evidence": round(float(r["onet"]), 3), "period_counts": r["period_counts"],
            })
        return out

    def _emerging_items(self, role: str, stats: pd.DataFrame) -> list[dict[str, Any]]:
        """Return evidence-backed emerging/developing signals without inventing forecasts.

        The previous implementation required a 3 percentage-point increase plus
        several simultaneous conditions. That is appropriate for a *strong*
        emerging signal, but it is too restrictive for small role samples.
        We therefore expose three evidence tiers inside the same Emerging Topics
        section:
          1) Strong emerging: repeated multi-period momentum.
          2) Developing signal: meaningful recent presence with some positive/new
             movement, but not enough evidence for the strong tier.
          3) New recent signal: newly observed recent presence with limited
             historical evidence.

        These are descriptive evidence tiers, not forecasts.
        """
        if stats.empty:
            return []

        rows = stats.copy()
        rows["onet"] = rows["topic"].map(lambda x: self._onet_topic_evidence(role, x)["score"])

        # Tier 1: retain the original high-confidence emerging definition.
        strong = (
            (rows["usable_periods"] >= 4)
            & (rows["trend_consistency"] >= 0.50)
            & (rows["share_change_pp"] >= 3.0)
            & (rows["recent_mentions"] >= 3)
        )

        # Tier 2: useful for smaller role samples. A topic must be observed in
        # at least two recent periods and have meaningful recent presence.
        # Positive movement OR a previously absent/near-absent signal is required.
        developing = (
            (~strong)
            & (rows["recent_active_periods"] >= 2)
            & (rows["recent_share"] >= 0.03)
            & (rows["recent_mentions"] >= 2)
            & (
                (rows["share_change_pp"] >= 0.5)
                | (rows["prior_share"] <= 0.01)
            )
        )

        # Tier 3: genuinely recent/new presence. This prevents a role with a
        # short history from showing an empty section while still requiring
        # observable employer-posting evidence.
        new_signal = (
            (~strong)
            & (~developing)
            & (rows["recent_share"] >= 0.05)
            & (rows["recent_mentions"] >= 1)
            & (rows["prior_share"] < rows["recent_share"])
        )

        eligible = rows[strong | developing | new_signal].copy()
        if eligible.empty:
            return []

        def tier(row) -> str:
            if bool(strong.loc[row.name]):
                return "strong_emerging"
            if bool(developing.loc[row.name]):
                return "developing_signal"
            return "new_recent_signal"

        eligible["signal_tier"] = eligible.apply(tier, axis=1)
        tier_rank = {
            "strong_emerging": 0,
            "developing_signal": 1,
            "new_recent_signal": 2,
        }
        eligible["_tier_rank"] = eligible["signal_tier"].map(tier_rank)
        eligible = eligible.sort_values(
            ["_tier_rank", "share_change_pp", "recent_share", "recent_mentions"],
            ascending=[True, False, False, False],
        ).head(10)

        out = []
        for _, r in eligible.iterrows():
            sample = int(r["role_job_count"])
            conf = self._clamp(
                0.35 * min(1, r["usable_periods"] / 8)
                + 0.35 * min(1, r["recent_mentions"] / 10)
                + 0.30 * r["trend_consistency"]
            )
            tier_name = r["signal_tier"]
            if tier_name == "strong_emerging":
                label = "Strong emerging signal"
                reason = "Repeated multi-period positive movement is supported by the role-matched employer postings."
            elif tier_name == "developing_signal":
                label = "Developing signal"
                reason = "The topic has meaningful recent role-specific presence and either positive movement or a newly established recent signal, but does not meet the stronger emerging threshold."
            else:
                label = "New recent signal"
                reason = "The topic has observable recent role-specific employer evidence with limited prior-period history; FORGE does not treat this as a forecast."

            change = float(r["share_change_pp"])
            if change >= 0:
                movement = f"{change:+.1f} percentage points"
            else:
                movement = f"{change:+.1f} percentage points"

            out.append({
                "name": self._display_name(r["topic"]),
                "topic_key": r["topic"],
                "horizon": "emerging",
                "signal_tier": tier_name,
                "market_mentions": int(r["job_mentions"]),
                "role_job_count": sample,
                "recent_prevalence_percent": round(float(r["recent_share"]) * 100, 2),
                "previous_prevalence_percent": round(float(r["prior_share"]) * 100, 2),
                "share_change_pp": round(change, 2),
                "trend_consistency": round(float(r["trend_consistency"]), 3),
                "periods_observed": int(r["usable_periods"]),
                "recent_active_periods": int(r["recent_active_periods"]),
                "confidence": round(conf, 3),
                "confidence_label": self._confidence_label(conf, sample),
                "source": "FORGE Greenhouse employer postings; multi-period trend analysis + O*NET corroboration",
                "trend_label": label,
                "description": f"Observed in {int(r['recent_mentions'])} recent topic mentions across {int(r['recent_active_periods'])} recent active periods; recent-vs-prior posting-share movement is {movement}.",
                "reason": reason,
                "onet_evidence": round(float(r["onet"]), 3),
                "period_counts": r["period_counts"],
            })
        return out

    def _sample_confidence(self, sample: int, mentions: int) -> float:
        return self._clamp(0.45 * min(1, sample / 100) + 0.55 * min(1, mentions / 20))

    @staticmethod
    def _confidence_label(score: float, sample: int) -> str:
        if sample < 25:
            return "Limited sample"
        if score >= 0.75:
            return "High"
        if score >= 0.50:
            return "Medium"
        return "Limited"

    # ------------------------------------------------------------------
    # Daily external market signal layer
    # ------------------------------------------------------------------

    def _market_category(self, role: str) -> str:
        key = self._norm(role)
        if key in self.MARKET_ROLE_CATEGORY:
            return self.MARKET_ROLE_CATEGORY[key]
        # Keep the mapping conservative. Exact role evidence remains supplied
        # by FORGE's Greenhouse/O*NET layer; this category is only a market
        # baseline for daily movement.
        if any(x in key for x in ("ai", "machine learning", "ml engineer")):
            return "ai"
        if any(x in key for x in ("data", "analytics")):
            return "data"
        if any(x in key for x in ("devops", "cloud", "platform")):
            return "devops"
        if any(x in key for x in ("security", "cyber")):
            return "security"
        return "engineering"

    def _refresh_market_history(self, force: bool = False) -> pd.DataFrame:
        """Fetch the daily market feed at most once per TTL and persist it.

        The remote dataset is historical, so one successful download gives
        FORGE several real daily observations. Every later daily run can
        append the newest snapshot without fabricating missing dates.
        """
        now = datetime.now(timezone.utc)
        if (not force and self._market_history_cache is not None and
                self._market_refresh_checked_at is not None and
                (now - self._market_refresh_checked_at).total_seconds() < self._market_refresh_ttl_seconds):
            return self._market_history_cache

        local = pd.DataFrame()
        if self.market_snapshot_path.exists():
            try:
                local = pd.read_csv(self.market_snapshot_path)
            except Exception:
                local = pd.DataFrame()

        try:
            remote = pd.read_csv(self.market_source_url)
            remote.columns = [str(c).strip() for c in remote.columns]
            required = {"snapshot_date", "category", "skill_name", "demand_count", "demand_pct"}
            if required.issubset(remote.columns):
                keep = [c for c in [
                    "snapshot_date", "category", "skill_name", "demand_count",
                    "demand_pct", "median_days_open", "salary_premium_pct",
                    "repost_rate_pct", "scarcity_score"
                ] if c in remote.columns]
                remote = remote[keep].copy()
                remote["snapshot_date"] = pd.to_datetime(remote["snapshot_date"], errors="coerce").dt.strftime("%Y-%m-%d")
                remote = remote.dropna(subset=["snapshot_date", "category", "skill_name"])
                if not local.empty:
                    local = pd.concat([local, remote], ignore_index=True)
                else:
                    local = remote
                local = local.drop_duplicates(subset=["snapshot_date", "category", "skill_name"], keep="last")
                local = local.sort_values(["snapshot_date", "category", "skill_name"])
                self.market_snapshot_dir.mkdir(parents=True, exist_ok=True)
                local.to_csv(self.market_snapshot_path, index=False)
        except Exception:
            # Never turn a temporary external-feed outage into fake market
            # numbers. Existing persisted snapshots remain usable.
            pass

        self._market_history_cache = local
        self._market_refresh_checked_at = now
        return local

    def _daily_market_signal(self, role: str, limit: int = 12) -> dict[str, Any]:
        df = self._refresh_market_history()
        if df.empty:
            return {
                "status": "offline",
                "source": "Datamata Skill Scarcity Index",
                "source_url": self.market_source_url,
                "category": self._market_category(role),
                "snapshot_dates": [],
                "skills": [],
                "message": "Daily market signal feed is unavailable; FORGE is not generating synthetic values.",
            }

        category = self._market_category(role)
        rows = df[df["category"].astype(str).str.lower().eq(category)].copy()
        if rows.empty:
            return {
                "status": "no_data",
                "source": "Datamata Skill Scarcity Index",
                "source_url": self.market_source_url,
                "category": category,
                "snapshot_dates": [],
                "skills": [],
                "message": f"No daily market observations are available for category '{category}'.",
            }

        rows["snapshot_date"] = pd.to_datetime(rows["snapshot_date"], errors="coerce")
        rows["demand_pct"] = pd.to_numeric(rows["demand_pct"], errors="coerce")
        rows = rows.dropna(subset=["snapshot_date", "demand_pct", "skill_name"])
        if rows.empty:
            return {"status": "no_data", "source": "Datamata Skill Scarcity Index", "source_url": self.market_source_url, "category": category, "snapshot_dates": [], "skills": []}

        latest_date = rows["snapshot_date"].max()
        window_start = latest_date - pd.Timedelta(days=6)
        window = rows[rows["snapshot_date"].between(window_start, latest_date)].copy()
        dates = sorted(window["snapshot_date"].dt.strftime("%Y-%m-%d").unique().tolist())

        # Pick the skills that matter most on the latest actual snapshot, then
        # reconstruct their daily series for a stock-chart-like trend.
        latest = rows[rows["snapshot_date"].eq(latest_date)].sort_values("demand_pct", ascending=False).head(limit)
        selected = latest["skill_name"].astype(str).tolist()
        history = window[window["skill_name"].astype(str).isin(selected)].copy()

        skills: list[dict[str, Any]] = []
        for skill in selected:
            h = history[history["skill_name"].astype(str).eq(skill)].sort_values("snapshot_date")
            if h.empty:
                continue
            points = [
                {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
                for d, v in zip(h["snapshot_date"], h["demand_pct"])
            ]
            current = float(points[-1]["value"])
            previous = float(points[-2]["value"]) if len(points) >= 2 else None
            delta = round(current - previous, 2) if previous is not None else None
            skills.append({
                "skill": skill,
                "current_demand_pct": round(current, 2),
                "previous_demand_pct": round(previous, 2) if previous is not None else None,
                "delta_pp": delta,
                "direction": "up" if delta is not None and delta > 0 else "down" if delta is not None and delta < 0 else "flat",
                "demand_count": int(float(pd.to_numeric(h.iloc[-1].get("demand_count", 0), errors="coerce") or 0)) if pd.notna(pd.to_numeric(h.iloc[-1].get("demand_count", 0), errors="coerce")) else 0,
                "series": points,
            })

        return {
            "status": "live",
            "source": "Datamata Skill Scarcity Index",
            "source_url": self.market_source_url,
            "category": category,
            "latest_snapshot": latest_date.strftime("%Y-%m-%d"),
            "requested_window_days": 7,
            "snapshot_dates": dates,
            "skills": skills,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "message": "Daily observed job-market demand. Movement is percentage-point change, not a stock price or forecast.",
        }

    def build(self, role: str, subjects: list[str] | None = None) -> dict[str, Any]:
        role = role.strip()
        role_key = self._norm(role)
        subject_key = tuple(sorted(self._norm(x) for x in (subjects or []) if str(x).strip()))
        build_key = (role_key, subject_key)
        market = self._daily_market_signal(role)
        cached = self._build_cache.get(build_key)
        if cached is not None:
            # Keep the expensive legacy evidence cached, but refresh the daily
            # market layer independently so a new snapshot is visible without
            # restarting FastAPI.
            refreshed = dict(cached)
            refreshed["market_signal"] = market
            refreshed["daily_market"] = market
            return refreshed

        jobs = self._load_jobs(role)
        stats = self._extract_topic_stats(role, jobs)
        current = self._current_items(role, stats)
        emerging = self._emerging_items(role, stats)
        five = self._wef_capabilities(role, stats)
        ten = self._ten_year(role, stats)
        role_count = len(jobs)
        bls = self._bls_role_rows(role)
        wef = self._load_wef()
        onet = self._load_onet()
        # Technology evidence is exposed both inside data_provenance and at
        # the top level so frontend cards cannot fall back to a dash when the
        # backend response shape changes.
        technology_record_count = int(len(onet)) if not onet.empty else 0
        technology_evidence_label = (
            f"{technology_record_count:,} O*NET technology records"
            if technology_record_count > 0
            else "O*NET technology evidence unavailable"
        )

        return {
            "role": role,
            "matched_occupations": self._match_occupations(role).to_dict("records"),
            "current": current,
            "emerging": emerging,
            "fiveYear": five,
            "tenYear": ten,
            "market_signal": market,
            "daily_market": market,
            # Top-level compatibility fields used by Industry Pulse UI cards.
            "technology_record_count": technology_record_count,
            "onet_technology_record_count": technology_record_count,
            "technology_evidence": technology_evidence_label,
            "horizon_context": {
                "current": {"meaning": "Observed employer demand in the latest four complete quarters."},
                "emerging": {"meaning": "Observed multi-period momentum; high current prevalence alone does not qualify."},
                "fiveYear": {"meaning": "WEF employer capability outlook toward 2030; not a technology-specific forecast."},
                "tenYear": {"meaning": "BLS occupation-level projection through 2035; not a technology-specific forecast."},
            },
            "data_provenance": {
                "job_dataset": "FORGE Greenhouse employer postings",
                "job_posting_count": 153069,
                "role_posting_count": role_count,
                "technology_dataset": "O*NET Software Skills / employer-posting evidence",
                "technology_record_count": technology_record_count,
                "technology_evidence": technology_evidence_label,
                "wef_dataset": "WEF Future of Jobs 2025–2030" if not wef.empty else "Unavailable",
                "bls_dataset": "BLS 2025–2035 occupational projections" if not bls.empty else "Unavailable",
                "bls_role_rows": int(len(bls)) if not bls.empty else 0,
                "projection_period": "2025–2035",
                "uncertainty_policy": "FORGE withholds future technology claims when the evidence cannot support them.",
                "daily_market_source": market.get("source"),
                "daily_market_status": market.get("status"),
                "daily_market_latest_snapshot": market.get("latest_snapshot"),
                "daily_market_category": market.get("category"),
            },
            "notes": [
                "Current Demand is not a prediction.",
                "Emerging requires multi-period momentum and is not inferred from prevalence alone.",
                "WEF supports broad 2025–2030 capability directions, not individual technology survival.",
                "BLS supports occupation-level 2025–2035 projections, not individual technology forecasts.",
            ],
        }
        self._build_cache[build_key] = result
        return result

    # ------------------------------------------------------------------
    # Topic Intelligence
    # ------------------------------------------------------------------

    TOPIC_CONTENT = {
        "retrieval augmented generation": {
            "definition": "Retrieval-Augmented Generation (RAG) combines information retrieval with a generative model: relevant external content is retrieved for a query and supplied as context before the model generates an answer.",
            "why": "RAG is useful when answers need current, private or domain-specific information without retraining the base model for every document update.",
            "prerequisites": ["Python", "NLP fundamentals", "Embeddings", "Vector search", "LLM basics"],
            "concepts": [("Document ingestion", "Collect, clean and segment source material."), ("Chunking", "Split documents into retrievable units while preserving useful context."), ("Embeddings", "Represent text as vectors so semantically related content can be retrieved."), ("Retrieval", "Find candidate chunks using similarity or hybrid search."), ("Reranking", "Reorder retrieved candidates with a stronger relevance model."), ("Grounded generation", "Provide retrieved evidence to the model and constrain the response to supported context."), ("Evaluation", "Measure retrieval quality and answer faithfulness separately."), ("Observability", "Track retrieval misses, latency, token usage and answer quality in production.")],
            "how": "A typical RAG pipeline ingests documents, chunks them, creates embeddings, stores them in a vector or hybrid index, retrieves candidates for a query, optionally reranks them, constructs a context window, and asks a language model to generate a grounded response. Retrieval and generation are separate components, so each can be evaluated independently.",
            "use_cases": ["Internal knowledge assistants", "Document question answering", "Policy/manual search", "Technical support knowledge bases", "Research assistants"],
            "mistakes": ["Poor chunk boundaries", "Retrieving too many irrelevant chunks", "Skipping retrieval evaluation", "Treating vector similarity as factual correctness", "Ignoring source attribution", "Using RAG when a simple database query is more appropriate"],
            "comparisons": [("RAG vs fine-tuning", "RAG changes the information supplied at inference time; fine-tuning changes model parameters."), ("Vector search vs RAG", "Vector search is retrieval infrastructure; RAG is the larger retrieval-plus-generation system."), ("RAG vs keyword search", "RAG can retrieve semantic matches and then generate an answer, while keyword search primarily returns matching documents.")],
            "project": {"title": "Build an evidence-grounded document assistant", "description": "Create a small RAG system over a controlled document collection. Measure retrieval recall, answer relevance and citation/grounding quality before adding production features.", "steps": ["Collect a small document corpus", "Implement chunking and metadata", "Create embeddings and an index", "Build retrieval and optional reranking", "Generate answers with source context", "Create a small evaluation set", "Measure retrieval and answer quality"]},
            "assessment": [{"question": "What makes RAG different from fine-tuning?", "answer": "RAG retrieves external context at inference time; fine-tuning changes model parameters."}, {"question": "Why evaluate retrieval separately from generation?", "answer": "A generated answer can fail because the right evidence was never retrieved, or because the model used retrieved evidence poorly."}, {"question": "Why can a vector similarity score not prove factual correctness?", "answer": "Similarity measures closeness in representation space, not whether the retrieved statement is true or sufficient."}],
        },
        "large language models": {
            "definition": "Large language models are neural models trained on large text corpora to learn statistical representations of language and generate or transform sequences of tokens.",
            "why": "LLMs provide the foundation for many language applications, including assistants, code generation, summarization and retrieval-grounded systems.",
            "prerequisites": ["Python", "Machine Learning", "Deep Learning", "NLP", "Transformers"],
            "concepts": [("Tokens", "Discrete units processed by the model."), ("Embeddings", "Vector representations used inside and around language models."), ("Attention", "Mechanism that lets the model weight relationships among tokens."), ("Transformer architecture", "The dominant architecture family used by modern language models."), ("Pretraining", "Learning general language patterns from large corpora."), ("Inference", "Generating outputs from a trained model for a given input context."), ("Evaluation", "Testing capability, reliability, safety and task-specific quality.")],
            "how": "Modern transformer language models tokenize input, transform token representations through repeated attention and feed-forward layers, and predict the next token or otherwise optimize a language objective. During inference, generated tokens are fed back as context for subsequent predictions.",
            "use_cases": ["Code assistance", "Summarization", "Question answering", "Text transformation", "Information extraction"],
            "mistakes": ["Assuming fluent output is factual", "Ignoring context-window limits", "Skipping evaluation", "Using a larger model when a smaller model is sufficient", "Failing to control sensitive data"],
            "comparisons": [("LLM vs traditional ML", "LLMs learn broad language representations and can perform many language tasks; traditional models are often trained for narrower objectives."), ("Prompting vs fine-tuning", "Prompting changes the input context; fine-tuning changes model parameters.")],
            "project": {"title": "Build a small evaluated language assistant", "description": "Create a constrained text task, define an evaluation set, compare prompting strategies and report failure cases rather than only demo outputs.", "steps": ["Define task and evaluation set", "Select a model", "Create baseline prompts", "Measure quality and latency", "Analyze failures", "Improve prompts or retrieval"]},
            "assessment": [{"question": "What does attention provide in a transformer?", "answer": "It lets token representations incorporate information from other relevant tokens in the context."}, {"question": "Why is evaluation necessary even when outputs sound fluent?", "answer": "Fluency does not guarantee correctness, relevance, safety or task success."}],
        },
        "generative ai": {
            "definition": "Generative AI refers to models and systems that generate new content such as text, code, images, audio or video from learned representations.",
            "why": "It enables new interfaces and automation patterns, but production use requires evaluation, data controls, security and cost management.",
            "prerequisites": ["Python", "Machine Learning", "Deep Learning", "Model APIs", "Evaluation fundamentals"],
            "concepts": [("Generative models", "Models that learn a distribution or transformation capable of producing new outputs."), ("Prompting", "Controlling model behavior through input instructions and context."), ("Grounding", "Connecting generation to trusted external information."), ("Evaluation", "Measuring quality against task-specific criteria."), ("Guardrails", "Controls that constrain unsafe, invalid or unwanted behavior."), ("Inference cost", "Latency and compute requirements associated with generation.")],
            "how": "A generative system receives an input condition, transforms it through a trained model, and samples or decodes an output. Application quality depends on the model plus prompting, context, retrieval, tool use, evaluation and controls around it.",
            "use_cases": ["Content drafting", "Code assistance", "Document transformation", "Multimodal interfaces", "Knowledge assistants"],
            "mistakes": ["Treating generated content as automatically correct", "No evaluation set", "Ignoring data privacy", "No fallback path", "Measuring only demo quality"],
            "comparisons": [("Generative AI vs predictive ML", "Generative systems produce new outputs; predictive systems commonly estimate labels, values or probabilities."), ("Generative AI vs RAG", "RAG is an application architecture that can use a generative model; it is not synonymous with generative AI.")],
            "project": {"title": "Build an evaluated generative AI workflow", "description": "Choose a bounded task, create a test set, compare baseline and improved prompts, and document failures and safeguards.", "steps": ["Define task", "Build baseline", "Create evaluation set", "Add grounding or structured constraints", "Measure quality and cost", "Document failure modes"]},
            "assessment": [{"question": "Is generative AI the same thing as RAG?", "answer": "No. RAG is an architecture that retrieves external context and can use a generative model to produce the final answer."}],
        },
        "ai agents": {
            "definition": "AI agents are software systems that use a model together with tools, state and control logic to perform multi-step tasks.",
            "why": "Agents extend language-model interfaces into workflows where the system must decide which tools or actions to use and maintain task state.",
            "prerequisites": ["Python", "LLMs", "APIs and tool calling", "Retrieval fundamentals", "Software testing"],
            "concepts": [("Tool calling", "Allow the model to request structured actions."), ("State", "Persist task context across steps."), ("Planning", "Select or sequence actions toward a goal."), ("Execution", "Actually invoke tools and handle their results."), ("Guardrails", "Restrict unsafe or invalid actions."), ("Evaluation", "Test both final outcomes and intermediate tool behavior.")],
            "how": "A typical agent loop receives a goal, reasons about the next action, calls an allowed tool, observes the result, updates state and repeats until a termination condition is met. Production systems need explicit tool permissions, timeouts, validation and evaluation.",
            "use_cases": ["Workflow automation", "Research workflows", "Customer support actions", "Developer tooling", "Data analysis assistants"],
            "mistakes": ["Giving unrestricted tool access", "No termination conditions", "No validation of tool inputs", "Evaluating only final answers", "Using an agent where deterministic workflow code is simpler"],
            "comparisons": [("Agent vs chatbot", "An agent can execute tools and multi-step workflows; a basic chatbot may only generate responses."), ("Agent vs workflow automation", "Agents choose actions dynamically; deterministic automation follows predefined steps.")],
            "project": {"title": "Build a constrained tool-using agent", "description": "Create an agent with 2–3 safe tools, explicit permissions, validation and a test suite for tool selection and final task success.", "steps": ["Define task", "Define allowed tools", "Implement tool schemas", "Implement loop and state", "Add validation and limits", "Evaluate tool choices and outcomes"]},
            "assessment": [{"question": "Why should an agent have explicit tool permissions?", "answer": "To constrain what actions the system can perform and reduce invalid or unsafe operations."}],
        },
        "mlops": {
            "definition": "MLOps is the engineering discipline for developing, deploying, monitoring, versioning and maintaining machine-learning systems.",
            "why": "A model is not a production system by itself; data, code, artifacts, deployment, monitoring and retraining all need lifecycle management.",
            "prerequisites": ["Python", "Machine Learning", "Git", "Docker", "Cloud fundamentals"],
            "concepts": [("Experiment tracking", "Record parameters, data references and results."), ("Model registry", "Manage deployable model artifacts and versions."), ("CI/CD", "Automate testing and delivery."), ("Monitoring", "Track service, data and model behavior."), ("Drift", "Detect changes in data or relationships that affect model performance."), ("Reproducibility", "Preserve enough metadata to reproduce an experiment or deployment.")],
            "how": "An MLOps lifecycle connects data preparation, training, evaluation, artifact/version management, deployment and monitoring. Production feedback can trigger investigation or retraining under controlled release processes.",
            "use_cases": ["Production ML APIs", "Batch prediction pipelines", "Model monitoring", "Continuous evaluation", "Model release management"],
            "mistakes": ["Monitoring only CPU and memory", "No model/data versioning", "No rollback plan", "No reproducible training", "Deploying without an evaluation gate"],
            "comparisons": [("MLOps vs DevOps", "MLOps includes software delivery practices plus data/model lifecycle concerns such as drift and model evaluation."), ("Batch vs online inference", "Batch processes predictions on a schedule; online inference responds to requests with lower per-request latency requirements.")],
            "project": {"title": "Build a reproducible ML deployment pipeline", "description": "Train a small model, track experiments, package it, deploy an inference service and add basic monitoring and rollback documentation.", "steps": ["Version code and data references", "Track experiments", "Create evaluation gate", "Package model", "Deploy", "Monitor and document rollback"]},
            "assessment": [{"question": "Why is data drift different from service latency monitoring?", "answer": "Data drift concerns changes in the input distribution or data characteristics; latency monitoring concerns system performance."}],
        },
    }

    # Extended deterministic topic knowledge. This is a generic topic-content
    # registry: the UI and engine remain identical for every topic, while each
    # topic receives its own concepts, workflow, learning path, project and
    # assessment when dynamic generation is unavailable.
    TOPIC_CONTENT.update({
        "python": {
            "definition": "Python is a high-level general-purpose language widely used for automation, data work, backend services and machine learning.",
            "why": "For an ML Engineer, Python connects data preparation, experimentation, model training, evaluation and service integration in one ecosystem.",
            "prerequisites": ["Programming fundamentals", "Functions and modules", "Git", "Command line basics"],
            "concepts": [("Data structures", "Use lists, dictionaries, sets and tuples to model and transform data."), ("Functions and modules", "Build reusable units and keep project boundaries clear."), ("Classes and objects", "Use object-oriented design when state and behavior need explicit structure."), ("Virtual environments", "Isolate project dependencies and reproduce installations."), ("Exceptions and testing", "Handle expected failures and verify behavior with tests."), ("Data and ML ecosystem", "Use NumPy, pandas, scikit-learn and PyTorch where the workload requires them."), ("Packaging and APIs", "Turn reusable Python code into packages or services."), ("Performance", "Profile before optimizing and choose vectorization, batching or concurrency when justified.")],
            "how": "Python code is parsed and executed by a runtime; applications are composed from modules, functions, classes and third-party packages. In ML workflows, data flows through preprocessing, training, evaluation and inference code, with environments and tests providing reproducibility.",
            "use_cases": ["ML training pipelines", "Data analysis and feature engineering", "FastAPI/Flask services", "Automation and scripting", "Experiment tooling"],
            "mistakes": ["Using one global environment for every project", "Mutating shared state unexpectedly", "Catching every exception without handling it", "Writing slow Python loops when vectorized operations fit", "Skipping tests for data and preprocessing code"],
            "comparisons": [("Python vs C++", "Python prioritizes development speed and ecosystem breadth; C++ offers lower-level control and predictable high performance."), ("Python scripts vs packages", "A script is convenient for a single workflow; a package provides reusable modules, tests and explicit interfaces.")],
            "project": {"title": "Build a reproducible ML data pipeline in Python", "description": "Create a small pipeline that ingests data, validates it, engineers features, trains a model and exposes a prediction function with tests.", "steps": ["Create a virtual environment", "Load and validate raw data", "Implement feature transformations", "Train and evaluate a baseline model", "Add unit tests for preprocessing", "Package the prediction path", "Document reproducibility and failure cases"]},
            "assessment": [{"question": "Why should an ML project use a virtual environment?", "answer": "It isolates project dependencies so installations are reproducible and do not conflict with unrelated projects."}, {"question": "When should Python code be optimized?", "answer": "After measuring a real bottleneck with profiling or workload measurements."}, {"question": "Why test preprocessing separately from model accuracy?", "answer": "A model can appear accurate while the data transformation logic is incorrect or inconsistent between training and inference."}],
        },
        "machine learning": {
            "definition": "Machine learning builds models that learn patterns from data to make predictions, classifications, rankings or decisions.",
            "why": "ML Engineers need to connect data quality, feature design, model selection and evaluation rather than treating model training as an isolated step.",
            "prerequisites": ["Python", "Probability and statistics", "Linear algebra basics", "Data preprocessing"],
            "concepts": [("Problem formulation", "Translate a business or engineering question into a measurable prediction task."), ("Features and labels", "Define model inputs and the target outcome."), ("Train/validation/test split", "Separate fitting from model selection and final evaluation."), ("Loss functions", "Quantify model error during optimization."), ("Generalization", "Evaluate whether learned patterns transfer to unseen data."), ("Model selection", "Compare algorithms and hyperparameters under a consistent protocol."), ("Evaluation metrics", "Choose metrics that reflect the actual task and class distribution."), ("Deployment", "Package inference with the same preprocessing assumptions used during training.")],
            "how": "An ML workflow starts with a measurable target, prepares data, separates evaluation sets, trains candidate models, tunes them using validation evidence, evaluates on held-out data and then packages inference with monitoring.",
            "use_cases": ["Classification", "Regression", "Ranking", "Anomaly detection", "Forecasting"],
            "mistakes": ["Data leakage between train and test sets", "Optimizing one metric without checking the business objective", "Overfitting the validation set through repeated manual tuning", "Ignoring class imbalance", "Deploying preprocessing different from training preprocessing"],
            "comparisons": [("Supervised vs unsupervised learning", "Supervised learning uses target labels; unsupervised learning discovers structure without a target label."), ("Tree models vs neural networks", "Tree ensembles are strong on many tabular problems; neural networks are especially flexible for high-dimensional or unstructured data.")],
            "project": {"title": "Build and evaluate an end-to-end classification system", "description": "Choose a public dataset, define the target and metric, compare two model families and package the selected pipeline for inference.", "steps": ["Define target and evaluation metric", "Audit and split data", "Build a preprocessing pipeline", "Train two model families", "Tune with cross-validation", "Evaluate on held-out data", "Package inference and document limitations"]},
            "assessment": [{"question": "Why is a test set kept separate until final evaluation?", "answer": "To estimate performance on unseen data without using the test set to make model-selection decisions."}, {"question": "What is data leakage?", "answer": "Information that would not be available at prediction time accidentally enters training or evaluation and makes performance look artificially strong."}],
        },
        "pytorch": {
            "definition": "PyTorch is a tensor-based deep-learning framework with automatic differentiation, neural-network modules and GPU acceleration.",
            "why": "It provides the training loop, model composition and accelerator support needed to move from deep-learning experiments to deployable models.",
            "prerequisites": ["Python", "Deep learning fundamentals", "Linear algebra", "GPU basics"],
            "concepts": [("Tensors", "Represent model inputs, parameters and intermediate values."), ("Autograd", "Track operations so gradients can be computed automatically."), ("nn.Module", "Compose trainable model components."), ("DataLoader", "Batch and iterate over training data efficiently."), ("Optimizer", "Update model parameters from gradients."), ("Training/evaluation modes", "Control behaviors such as dropout and batch normalization."), ("Checkpointing", "Save model and optimizer state for reproducibility and recovery."), ("GPU execution", "Move compatible tensors and modules to an accelerator when useful.")],
            "how": "A typical PyTorch loop loads batches, runs a forward pass, computes loss, backpropagates gradients, updates parameters and repeats across epochs; validation runs without gradient updates and deployment uses the trained model for inference.",
            "use_cases": ["Computer vision models", "NLP and transformer training", "Research prototypes", "Custom deep-learning pipelines", "Model fine-tuning"],
            "mistakes": ["Forgetting to switch between train and evaluation modes", "Keeping unnecessary tensors on the GPU", "Saving only model weights when optimizer state is needed for resume", "Ignoring reproducibility of data splits and seeds", "Using a batch size that exhausts accelerator memory"],
            "comparisons": [("PyTorch vs TensorFlow", "Both provide tensor computation and deep-learning tooling; PyTorch emphasizes an imperative Python workflow while TensorFlow provides a broader graph/runtime ecosystem."), ("Training vs inference", "Training updates parameters using gradients; inference uses fixed parameters to produce predictions.")],
            "project": {"title": "Train and serve a PyTorch model", "description": "Train a small image or text classifier, track validation metrics, save a checkpoint and expose a deterministic inference path.", "steps": ["Prepare Dataset and DataLoader", "Define an nn.Module", "Implement training and validation loops", "Track loss and task metrics", "Checkpoint the best model", "Run batch and single-example inference", "Document compute and failure cases"]},
            "assessment": [{"question": "What does autograd provide in PyTorch?", "answer": "It tracks tensor operations and computes gradients needed for optimization."}, {"question": "Why call model.eval() during validation?", "answer": "It switches modules such as dropout and batch normalization into inference behavior."}],
        },
        "tensorflow": {
            "definition": "TensorFlow is an end-to-end machine-learning platform for tensor computation, model training, deployment and production workflows.",
            "why": "It is useful when a team needs a mature training and serving ecosystem spanning experimentation to deployment.",
            "prerequisites": ["Python", "Neural networks", "Tensor operations", "Model evaluation"],
            "concepts": [("Tensors", "Multidimensional numerical data used throughout the computation graph."), ("Keras models", "High-level APIs for composing and training neural networks."), ("Gradient-based optimization", "Update parameters to reduce a chosen loss."), ("tf.data", "Build efficient input pipelines."), ("Callbacks", "Observe training and trigger actions such as checkpointing."), ("SavedModel", "Package model artifacts for serving and reuse."), ("TensorBoard", "Inspect metrics and training behavior."), ("Serving", "Expose trained models to applications or batch workflows.")],
            "how": "Data is transformed into tensors, fed through a model, scored with a loss, differentiated and optimized repeatedly; the trained artifact can then be exported and served.",
            "use_cases": ["Image classification", "Sequence models", "Production model serving", "Large-scale training", "Edge/mobile ML"],
            "mistakes": ["Feeding inconsistent preprocessing at inference", "Monitoring only training loss", "Saving checkpoints without configuration metadata", "Ignoring input-pipeline bottlenecks", "Deploying without testing representative inputs"],
            "comparisons": [("TensorFlow vs PyTorch", "Both support deep learning; TensorFlow has a broad production ecosystem while PyTorch is widely used for flexible research and training workflows."), ("Keras vs low-level TensorFlow", "Keras provides higher-level model-building APIs; lower-level TensorFlow APIs offer more direct control when needed.")],
            "project": {"title": "Build a TensorFlow model with reproducible evaluation", "description": "Train a model with tf.data, callbacks and TensorBoard, then export it for inference using the same preprocessing pipeline.", "steps": ["Build input pipeline", "Define Keras model", "Train with callbacks", "Inspect TensorBoard metrics", "Select checkpoint", "Export model", "Test representative inference inputs"]},
            "assessment": [{"question": "Why use tf.data in a training pipeline?", "answer": "It provides composable input processing, batching and prefetching for efficient data delivery."}],
        },
        "sql": {
            "definition": "SQL is a declarative language for querying, transforming and managing data in relational database systems.",
            "why": "SQL remains central to analytics and application backends because reliable systems depend on correct joins, constraints, transactions and efficient queries.",
            "prerequisites": ["Relational concepts", "Tables and keys", "Basic programming logic", "Data modeling"],
            "concepts": [("SELECT and filtering", "Retrieve only the rows and columns needed."), ("Joins", "Combine related records across tables using keys or conditions."), ("Aggregation", "Compute grouped summaries with functions such as COUNT and SUM."), ("Subqueries and CTEs", "Break complex transformations into understandable query stages."), ("Indexes", "Accelerate suitable lookup patterns at storage and maintenance cost."), ("Transactions", "Group changes with atomicity and isolation guarantees."), ("Normalization", "Reduce unnecessary duplication while preserving useful relationships."), ("Query plans", "Inspect how the database actually executes a query.")],
            "how": "A SQL query describes the desired result; the database parses and optimizes it into an execution plan that scans, filters, joins, aggregates and returns rows while enforcing transactional and integrity rules.",
            "use_cases": ["Application databases", "Analytics", "ETL/ELT", "Reporting", "Feature extraction for ML"],
            "mistakes": ["Joining tables without understanding cardinality", "Selecting unnecessary columns from large tables", "Adding indexes without measuring workload impact", "Relying on implicit data type conversions", "Skipping transaction boundaries for multi-step writes"],
            "comparisons": [("SQL vs NoSQL", "Relational databases emphasize structured schemas, joins and transactional consistency; NoSQL systems trade different constraints for particular access patterns and scale characteristics."), ("CTE vs subquery", "Both express intermediate query logic; CTEs can make multi-stage queries easier to read and reuse within one statement.")],
            "project": {"title": "Design and optimize a role analytics database", "description": "Model a small workforce dataset, write analytical queries, add constraints and indexes, and compare query plans before and after optimization.", "steps": ["Design entities and keys", "Normalize the schema", "Load sample data", "Write joins and analytical queries", "Add indexes based on access patterns", "Inspect query plans", "Test transactions and constraints"]},
            "assessment": [{"question": "Why inspect a query plan instead of assuming an index will help?", "answer": "The optimizer may choose a different access path, and an index can be ineffective or costly for the actual workload."}, {"question": "What does a transaction provide?", "answer": "A controlled unit of database changes with defined atomicity and isolation behavior."}],
        },
        "react": {
            "definition": "React is a component-based JavaScript library for building interactive user interfaces from state and data.",
            "why": "React helps teams structure complex interfaces into reusable components with predictable data flow and explicit state transitions.",
            "prerequisites": ["JavaScript", "HTML/CSS", "ES modules", "HTTP/API basics"],
            "concepts": [("Components", "Encapsulate reusable UI and behavior."), ("Props", "Pass read-only data from parent to child components."), ("State", "Store values that change during interaction."), ("Hooks", "Connect state, effects and reusable logic to function components."), ("Rendering", "React calculates UI from current props and state."), ("Effects", "Synchronize with external systems such as APIs or browser APIs."), ("Routing", "Map application URLs to views."), ("Performance", "Avoid unnecessary work through correct state placement and measured optimization.")],
            "how": "React renders components from props and state; user events update state, causing affected components to render again. Effects synchronize external systems rather than serving as general-purpose event handlers.",
            "use_cases": ["Dashboards", "Learning platforms", "Admin interfaces", "Data-driven web apps", "Interactive product frontends"],
            "mistakes": ["Putting state too high in the tree", "Using effects for derived values", "Using unstable list keys", "Triggering duplicate network requests", "Optimizing renders before measuring"],
            "comparisons": [("Props vs state", "Props are supplied by a parent; state is owned by the component or its state manager."), ("Effect vs event handler", "Effects synchronize after rendering with external systems; event handlers respond directly to user actions.")],
            "project": {"title": "Build an evidence-driven Industry Pulse interface", "description": "Create a React dashboard that fetches capability signals, supports filtering and topic detail views, and preserves loading/error/empty states.", "steps": ["Define component hierarchy", "Model API response state", "Build signal list", "Add topic detail view", "Implement loading and error states", "Measure render/network behavior", "Add accessible keyboard interactions"]},
            "assessment": [{"question": "When should an effect be used in React?", "answer": "When component rendering needs to synchronize with an external system such as a network request, subscription or browser API."}, {"question": "Why are stable keys important for lists?", "answer": "They let React correctly associate rendered elements with items across updates."}],
        },
        "typescript": {
            "definition": "TypeScript adds static type checking and richer tooling to JavaScript while compiling to JavaScript for execution.",
            "why": "Types make large frontends and backend services easier to refactor by making data contracts explicit before runtime.",
            "prerequisites": ["JavaScript", "Functions and objects", "Modules", "Async programming"],
            "concepts": [("Primitive and object types", "Describe values and structures precisely."), ("Interfaces and type aliases", "Define reusable contracts for data and APIs."), ("Generics", "Write reusable code while preserving type relationships."), ("Unions", "Represent values that can legitimately take several shapes."), ("Narrowing", "Use runtime checks to safely refine a union."), ("Utility types", "Transform existing types into new contracts."), ("Strict mode", "Catch more invalid assumptions during development."), ("API contracts", "Keep client models aligned with backend responses.")],
            "how": "TypeScript analyzes source code statically, narrows types through control flow and compiles the result to JavaScript. Types do not automatically validate runtime data, so external inputs still require runtime validation.",
            "use_cases": ["React applications", "Node.js services", "Shared API models", "SDKs", "Large codebases"],
            "mistakes": ["Using any to silence type errors", "Assuming TypeScript validates runtime JSON", "Overusing complex generics", "Duplicating API types without a source of truth", "Ignoring strict compiler settings"],
            "comparisons": [("TypeScript vs JavaScript", "TypeScript adds static analysis and type syntax; JavaScript runs directly in the browser/runtime."), ("Type vs runtime schema", "A TypeScript type helps at compile time; a runtime schema validates actual external data.")],
            "project": {"title": "Type a production-style API client", "description": "Build a typed React or Node.js client with strict types, discriminated states and runtime validation for external responses.", "steps": ["Model domain types", "Type API functions", "Represent loading/success/error states", "Add runtime validation", "Handle malformed responses", "Enable strict compiler settings", "Document the contracts"]},
            "assessment": [{"question": "Does a TypeScript interface validate JSON received at runtime?", "answer": "No. TypeScript types are erased at runtime; external data needs runtime validation if correctness depends on it."}],
        },
        "kubernetes": {
            "definition": "Kubernetes is a container orchestration platform that manages workloads, networking, configuration and desired state across a cluster.",
            "why": "It gives teams standardized mechanisms for deploying, scaling and recovering containerized applications.",
            "prerequisites": ["Linux basics", "Containers", "Networking", "YAML", "Docker"],
            "concepts": [("Pods", "Smallest deployable unit containing one or more closely coupled containers."), ("Deployments", "Manage replicated stateless workloads and rolling updates."), ("Services", "Provide stable network access to changing Pods."), ("ConfigMaps and Secrets", "Separate configuration and sensitive values from container images."), ("Probes", "Let the platform distinguish startup, readiness and liveness states."), ("Resources", "Declare CPU and memory requests and limits."), ("Scaling", "Adjust replicas or workloads based on demand."), ("Observability", "Collect logs, metrics and events to understand cluster behavior.")],
            "how": "Kubernetes stores a desired state for workloads and controllers continuously reconcile cluster resources toward that state. Services route traffic to matching Pods while Deployments manage replicas and rollout history.",
            "use_cases": ["ML inference APIs", "Microservices", "Batch workloads", "Internal platforms", "Multi-service applications"],
            "mistakes": ["Exposing Pods directly instead of using the intended Service model", "Storing secrets in images or plain manifests", "Skipping readiness probes", "Leaving resource requests and limits undefined", "Deploying without a rollback strategy"],
            "comparisons": [("Kubernetes vs Docker", "Docker packages and runs containers; Kubernetes coordinates containerized workloads across a cluster."), ("Deployment vs Pod", "A Pod is a running unit; a Deployment manages replicated Pods and their rollout lifecycle.")],
            "project": {"title": "Deploy an ML inference API on Kubernetes", "description": "Containerize a small model API, deploy it with health probes and resource settings, expose it through a Service and test a rolling update.", "steps": ["Containerize inference service", "Create Deployment", "Add ConfigMap/Secret references", "Add readiness and liveness probes", "Create Service", "Set resource requests/limits", "Test rollout and rollback"]},
            "assessment": [{"question": "Why is a Service used in Kubernetes?", "answer": "It provides a stable network endpoint for a changing set of Pods selected by labels."}, {"question": "What does a readiness probe indicate?", "answer": "Whether a container is ready to receive traffic."}],
        },
        "docker": {
            "definition": "Docker packages applications and their dependencies into portable container images that can run consistently across environments.",
            "why": "Containerization reduces environment drift and creates a predictable unit for local development, testing and deployment.",
            "prerequisites": ["Linux process basics", "Networking basics", "Command line", "Application dependencies"],
            "concepts": [("Images", "Immutable templates from which containers are created."), ("Containers", "Running instances of images with isolated processes and resources."), ("Dockerfile", "Declarative instructions for building an image."), ("Layers", "Reusable filesystem changes that influence build caching."), ("Volumes", "Persist data outside a container lifecycle."), ("Networks", "Connect containers using defined networking behavior."), ("Registry", "Store and distribute versioned images."), ("Multi-stage builds", "Keep runtime images smaller by separating build and runtime stages.")],
            "how": "A Dockerfile is built into an image; a container runs that image with a process, filesystem and network configuration. Images are tagged and pushed to registries for deployment.",
            "use_cases": ["Local development", "CI environments", "ML inference packaging", "Microservices", "Reproducible tooling"],
            "mistakes": ["Shipping secrets inside images", "Using unnecessarily large base images", "Running as root without need", "Treating container filesystems as permanent storage", "Using mutable latest tags for critical deployments"],
            "comparisons": [("Image vs container", "An image is a packaged artifact; a container is a running instance of that artifact."), ("Docker vs Kubernetes", "Docker handles container packaging/runtime workflows; Kubernetes orchestrates workloads across clusters.")],
            "project": {"title": "Containerize a Python ML API", "description": "Build a small image with reproducible dependencies, non-root execution and a health endpoint, then run it locally with environment-specific configuration.", "steps": ["Create Dockerfile", "Pin dependencies", "Build image", "Run as non-root", "Add health endpoint", "Use environment variables", "Measure image size and startup time"]},
            "assessment": [{"question": "Why should secrets not be baked into a Docker image?", "answer": "Image layers can persist and be distributed, making embedded secrets difficult to revoke and exposing them to anyone with image access."}],
        },
        "apache spark": {
            "definition": "Apache Spark is a distributed data-processing engine for parallel computation over large datasets.",
            "why": "Spark helps data teams process workloads that exceed the practical limits of a single-machine workflow.",
            "prerequisites": ["Python or Scala", "SQL", "Distributed systems basics", "Dataframes"],
            "concepts": [("SparkSession", "Entry point for structured Spark applications."), ("DataFrames", "Distributed tabular abstractions with schema information."), ("Transformations", "Lazy operations that define how data should change."), ("Actions", "Operations that trigger execution and return results or write data."), ("Partitions", "Units of distributed data processing."), ("Shuffles", "Data movement across workers for operations such as joins and aggregations."), ("Caching", "Keep reused data available to avoid recomputation when justified."), ("Spark SQL", "Declarative queries over distributed structured data.")],
            "how": "Spark builds a logical execution plan from transformations, optimizes it and executes tasks across partitions. Expensive shuffles move data between workers, so partitioning and join strategy strongly influence performance.",
            "use_cases": ["Large-scale ETL", "Feature engineering", "Log processing", "Batch analytics", "Distributed data preparation"],
            "mistakes": ["Collecting huge datasets to the driver", "Ignoring shuffle-heavy operations", "Using too many tiny files", "Caching everything without measuring reuse", "Skipping schema and data-quality checks"],
            "comparisons": [("Spark vs pandas", "pandas is primarily single-machine; Spark distributes computation across a cluster."), ("Transformation vs action", "Transformations define a lazy computation; actions trigger execution.")],
            "project": {"title": "Build a Spark feature-engineering pipeline", "description": "Process a public event or job dataset with Spark SQL/DataFrames, produce features and benchmark a distributed transformation against a single-machine baseline where practical.", "steps": ["Load partitioned data", "Define schema", "Clean and transform", "Join and aggregate", "Inspect shuffle stages", "Write feature output", "Measure runtime and data quality"]},
            "assessment": [{"question": "Why can a Spark shuffle be expensive?", "answer": "It moves data across workers, creating network and serialization overhead before downstream tasks can continue."}],
        },
        "data engineering": {
            "definition": "Data engineering designs reliable systems that ingest, transform, store and serve data for analytics and machine learning.",
            "why": "Models and analytics depend on trustworthy pipelines, so data engineers manage the flow, quality and operational behavior of data systems.",
            "prerequisites": ["SQL", "Python", "Data modeling", "Cloud/storage basics"],
            "concepts": [("Ingestion", "Bring data from operational or external sources into the platform."), ("Batch vs streaming", "Choose processing cadence based on latency and workload requirements."), ("Schemas", "Define and evolve data contracts."), ("ETL/ELT", "Transform data at the appropriate stage of the platform."), ("Orchestration", "Schedule dependencies and retries across pipeline tasks."), ("Data quality", "Detect missing, invalid, duplicate or inconsistent records."), ("Lineage", "Track where data originated and how it was transformed."), ("Warehouse/lakehouse", "Store data for downstream analytical workloads.")],
            "how": "A data pipeline moves records from sources through validation and transformation into durable storage or serving layers, with orchestration, quality checks, lineage and monitoring around the data flow.",
            "use_cases": ["Analytics platforms", "ML feature pipelines", "Business reporting", "Event processing", "Data migration"],
            "mistakes": ["No data-quality gates", "Breaking downstream consumers during schema changes", "No idempotency for retries", "Mixing business logic into fragile extraction code", "Monitoring pipeline completion without checking data correctness"],
            "comparisons": [("ETL vs ELT", "ETL transforms before loading; ELT loads raw data first and performs more transformation inside the target platform."), ("Batch vs streaming", "Batch processes bounded groups periodically; streaming processes events continuously or near-continuously.")],
            "project": {"title": "Build a monitored job-market data pipeline", "description": "Ingest public job postings, normalize fields, validate records, create analytical tables and expose pipeline quality metrics.", "steps": ["Define source schema", "Ingest raw records", "Normalize titles and dates", "Run quality checks", "Create curated tables", "Orchestrate dependencies", "Track freshness and failures"]},
            "assessment": [{"question": "Why should a retryable data pipeline be idempotent?", "answer": "Repeating a failed task should not create duplicate or inconsistent downstream results."}],
        },
        "transformers": {
            "definition": "Transformers are neural architectures that use attention to model relationships among tokens or other sequence elements in parallel.",
            "why": "They underpin modern language models and many multimodal systems, making attention, tokenization and pretraining concepts essential for GenAI work.",
            "prerequisites": ["Deep learning", "Linear algebra", "NLP basics", "Python"],
            "concepts": [("Self-attention", "Relate each token to other tokens in the context."), ("Query/key/value", "Parameterize how attention scores and information aggregation are computed."), ("Positional information", "Represent sequence order because attention alone does not encode it inherently."), ("Multi-head attention", "Learn multiple relationship patterns in parallel."), ("Feed-forward blocks", "Apply nonlinear transformations after attention."), ("Residual connections", "Support stable optimization in deep stacks."), ("Tokenization", "Convert text into model-readable units."), ("Pretraining and fine-tuning", "Learn broad representations first and adapt them to tasks or domains.")],
            "how": "Tokens are embedded and enriched with positional information, passed through repeated attention and feed-forward blocks, and transformed into contextual representations used for prediction or downstream tasks.",
            "use_cases": ["Language models", "Text classification", "Sequence generation", "Vision transformers", "Multimodal models"],
            "mistakes": ["Thinking attention is the same as retrieval", "Ignoring tokenization effects", "Confusing pretraining with fine-tuning", "Using sequence lengths without considering compute cost", "Evaluating only benchmark averages"],
            "comparisons": [("Transformer vs RNN", "Transformers process relationships with attention and parallelizable sequence computation; RNNs process recurrently across sequence positions."), ("Encoder-only vs decoder-only", "Encoder-focused models are often used for representation tasks; decoder-only models are optimized for autoregressive generation.")],
            "project": {"title": "Inspect a transformer text classifier", "description": "Fine-tune a small transformer on a bounded text classification task and inspect tokenization, attention-related architecture and evaluation failures.", "steps": ["Prepare labeled text", "Inspect tokenizer behavior", "Select a pretrained model", "Fine-tune with a validation split", "Measure class-wise metrics", "Analyze failure examples", "Document compute and limitations"]},
            "assessment": [{"question": "What problem does self-attention solve?", "answer": "It lets each position incorporate information from relevant positions in the same context."}],
        },
        "natural language processing": {
            "definition": "Natural Language Processing (NLP) applies computational methods to analyze, transform and generate human language.",
            "why": "NLP provides the task layer behind search, classification, extraction, summarization and many language-model applications.",
            "prerequisites": ["Python", "Statistics", "Text preprocessing", "Machine learning"],
            "concepts": [("Tokenization", "Convert text into units suitable for processing."), ("Normalization", "Handle casing, punctuation and domain-specific variation where appropriate."), ("Representations", "Encode text using features, embeddings or contextual model representations."), ("Sequence labeling", "Assign labels to tokens for tasks such as entity extraction."), ("Classification", "Map text to categories or decisions."), ("Information extraction", "Extract structured facts from unstructured language."), ("Evaluation", "Measure task quality with metrics appropriate to the application."), ("Language-model integration", "Use pretrained models when learned language representations provide leverage.")],
            "how": "An NLP pipeline turns raw text into representations, applies a task model or rule system and evaluates outputs against labeled or reference data. Modern pipelines often combine pretrained language models with task-specific evaluation.",
            "use_cases": ["Search", "Text classification", "Entity extraction", "Summarization", "Question answering"],
            "mistakes": ["Removing useful linguistic information with aggressive preprocessing", "Using accuracy for highly imbalanced tasks", "Ignoring domain vocabulary", "Training and testing on near-duplicate documents", "Evaluating generated text without human or task-specific checks"],
            "comparisons": [("Classical NLP vs transformers", "Classical pipelines rely more on engineered features and task-specific models; transformers learn contextual representations from pretrained objectives."), ("Keyword search vs semantic search", "Keyword search matches lexical terms; semantic search uses learned representations to retrieve related meaning.")],
            "project": {"title": "Build an evaluated support-ticket classifier", "description": "Classify a public or synthetic support-ticket dataset, compare a classical baseline with a pretrained model and analyze errors by category.", "steps": ["Define labels", "Clean and split text", "Build TF-IDF baseline", "Train/evaluate transformer model", "Compare class-wise metrics", "Inspect failure examples", "Document deployment considerations"]},
            "assessment": [{"question": "Why should NLP evaluation inspect class-wise metrics?", "answer": "A single aggregate score can hide poor performance on minority or business-critical classes."}],
        },
        "aws": {
            "definition": "AWS is a cloud platform providing compute, storage, databases, networking, security and managed application services.",
            "why": "Cloud skills matter when ML and software systems need scalable infrastructure, managed services and controlled deployment environments.",
            "prerequisites": ["Linux", "Networking", "Cloud fundamentals", "IAM concepts"],
            "concepts": [("Compute", "Run workloads using virtual machines, containers or serverless services."), ("Object storage", "Store durable files and datasets in services such as S3."), ("IAM", "Control identities, roles and permissions."), ("Networking", "Design VPCs, subnets, routing and security boundaries."), ("Managed databases", "Use appropriate relational or NoSQL services without managing every server detail."), ("Containers", "Run packaged workloads using managed container services."), ("Observability", "Monitor logs, metrics and traces."), ("Cost controls", "Measure usage and design for predictable resource consumption.")],
            "how": "A cloud workload is composed from compute, storage, networking, identity and managed services. Good architecture separates responsibilities, applies least privilege and measures reliability and cost.",
            "use_cases": ["ML APIs", "Data pipelines", "Web applications", "Model training", "Object/data storage"],
            "mistakes": ["Over-permissive IAM policies", "Putting databases on public networks without need", "No cost monitoring", "Hard-coding credentials", "Choosing managed services without understanding operational limits"],
            "comparisons": [("EC2 vs serverless", "Virtual machines provide more direct control; serverless services abstract infrastructure and scale around requests or events."), ("S3 vs block storage", "Object storage is optimized for durable objects; block storage provides attachable volumes for compute workloads.")],
            "project": {"title": "Deploy a secure ML inference service on AWS", "description": "Containerize a model API, store artifacts in object storage, apply least-privilege IAM and expose a monitored service with a documented cost model.", "steps": ["Package inference API", "Store artifact in S3", "Create least-privilege IAM role", "Deploy compute", "Configure networking", "Add logs/metrics", "Document cost and failure recovery"]},
            "assessment": [{"question": "Why is least privilege important in AWS?", "answer": "It limits the resources and actions a compromised or misconfigured identity can access."}],
        },
        "microsoft azure": {
            "definition": "Microsoft Azure is a cloud platform offering compute, storage, networking, identity, analytics and AI services.",
            "why": "Azure provides managed infrastructure and identity integrations used to build, deploy and operate enterprise software and ML systems.",
            "prerequisites": ["Cloud fundamentals", "Networking", "Linux or Windows administration", "Identity basics"],
            "concepts": [("Resource groups", "Organize related cloud resources."), ("Virtual networks", "Define network boundaries and connectivity."), ("Azure Storage", "Provide object and other storage options."), ("Managed compute", "Run applications without managing every infrastructure layer."), ("Entra ID", "Manage identities and access."), ("Azure ML", "Support model development and deployment workflows."), ("Monitoring", "Collect operational signals for reliability."), ("Governance", "Apply policies, permissions and cost controls.")],
            "how": "Azure applications combine resources inside a subscription and resource groups, connect them through networking and identity, and use managed services for compute, data and ML workloads.",
            "use_cases": ["Enterprise APIs", "ML platforms", "Data engineering", "Cloud storage", "Identity-aware applications"],
            "mistakes": ["Using broad contributor permissions", "Ignoring network isolation", "No resource tagging or cost ownership", "Hard-coding credentials", "Deploying ML endpoints without monitoring"],
            "comparisons": [("Azure vs AWS", "Both provide broad cloud primitives; the practical choice depends on existing identity, data, architecture and operational requirements."), ("Managed vs self-managed compute", "Managed services reduce infrastructure operations; self-managed systems provide more direct control at higher operational cost.")],
            "project": {"title": "Build an Azure-hosted ML service", "description": "Deploy a small inference service with managed identity, private configuration, monitoring and a documented resource layout.", "steps": ["Create resource structure", "Package service", "Configure identity", "Deploy endpoint", "Add monitoring", "Apply access controls", "Document recovery and cost"]},
            "assessment": [{"question": "What is the purpose of a resource group in Azure?", "answer": "It organizes related resources and provides a management boundary for deployment and governance."}],
        },
        "google cloud": {
            "definition": "Google Cloud is a cloud platform providing compute, storage, networking, data and machine-learning services.",
            "why": "Its managed data and ML services can shorten the path from data ingestion to deployable analytics and models.",
            "prerequisites": ["Cloud fundamentals", "SQL", "Networking", "IAM"],
            "concepts": [("Projects", "Organize resources, APIs, permissions and billing boundaries."), ("Cloud Storage", "Store durable objects and datasets."), ("Compute", "Run services and workloads with different infrastructure abstractions."), ("BigQuery", "Query analytical data using a managed warehouse."), ("IAM", "Control identities and permissions."), ("VPC", "Define network connectivity and security boundaries."), ("Vertex AI", "Support model training and deployment workflows."), ("Monitoring", "Observe service and platform behavior.")],
            "how": "Google Cloud workloads are organized in projects and composed from managed compute, data, network and identity services; analytics and ML layers can consume shared data assets with controlled permissions.",
            "use_cases": ["Analytics", "ML training", "Data pipelines", "APIs", "Large-scale storage"],
            "mistakes": ["Ignoring IAM scope", "Leaving data broadly accessible", "No budget alerts", "Mixing development and production resources without boundaries", "Skipping query and storage cost analysis"],
            "comparisons": [("BigQuery vs transactional SQL", "BigQuery is optimized for analytical workloads; transactional databases are optimized for application state and concurrent updates."), ("Vertex AI vs custom infrastructure", "Managed ML services reduce platform work; custom infrastructure can provide more control at greater operational complexity.")],
            "project": {"title": "Build a cloud analytics-to-ML pipeline", "description": "Load public data into BigQuery, create features with SQL, train a small model and expose the result through a controlled service.", "steps": ["Create project boundary", "Load public dataset", "Model analytical tables", "Build features in SQL", "Train/evaluate model", "Deploy inference", "Add IAM and monitoring"]},
            "assessment": [{"question": "Why separate analytical storage from transactional application state?", "answer": "The workloads have different access patterns, performance requirements and optimization strategies."}],
        },
        "fine tuning": {
            "definition": "Fine-tuning adapts a pretrained model to a narrower task or domain by updating model parameters or a parameter-efficient subset of them.",
            "why": "It can improve consistency on specialized behavior when prompting or retrieval alone does not provide the required adaptation.",
            "prerequisites": ["Transformers", "LLM fundamentals", "Datasets and evaluation", "GPU basics"],
            "concepts": [("Supervised fine-tuning", "Train on examples of desired input-output behavior."), ("LoRA", "Learn low-rank adapter parameters instead of updating every base-model weight."), ("PEFT", "A family of methods that reduce the number of trainable parameters."), ("Dataset quality", "Training examples strongly influence learned behavior."), ("Catastrophic forgetting", "Over-specialization can reduce useful general capabilities."), ("Evaluation", "Compare adapted and baseline models on task and safety criteria."), ("Checkpoint management", "Track base model, adapter and training configuration."), ("Inference merging", "Decide whether and how adapters are applied during deployment.")],
            "how": "A pretrained model is initialized from a base checkpoint, training examples are tokenized and batches update selected parameters, and the resulting model or adapters are evaluated against a held-out set and the original baseline.",
            "use_cases": ["Domain-specific language behavior", "Structured output consistency", "Task adaptation", "Style or format adaptation", "Specialized classifiers"],
            "mistakes": ["Fine-tuning without a representative evaluation set", "Training on noisy or duplicated examples", "Changing the base model without recording its version", "Assuming more epochs always improve behavior", "Using fine-tuning when retrieval would solve a knowledge-update problem"],
            "comparisons": [("Fine-tuning vs RAG", "Fine-tuning changes model behavior; RAG supplies external information at inference time."), ("Full fine-tuning vs LoRA", "Full fine-tuning updates many or all model weights; LoRA learns a smaller adapter parameter set.")],
            "project": {"title": "Compare prompting, RAG and PEFT on one task", "description": "Use a small controlled dataset to compare baseline prompting with retrieval and a parameter-efficient adaptation, measuring task quality and resource cost.", "steps": ["Define task and evaluation set", "Establish prompted baseline", "Add retrieval baseline", "Prepare clean training examples", "Train LoRA adapter", "Compare quality and cost", "Analyze failure cases"]},
            "assessment": [{"question": "Why can RAG be preferable to fine-tuning for frequently changing facts?", "answer": "RAG can retrieve updated source information at inference time without retraining model parameters."}],
        },
    })

    def _display_name(self, topic: str) -> str:
        return self.TOPIC_DISPLAY.get(str(topic), str(topic).replace("_", " ").title())

    def _canonical_topic(self, topic: str) -> str:
        n = self._norm(topic)
        for key, display in self.TOPIC_DISPLAY.items():
            if n == self._norm(display):
                return key
        if n in self.TOPIC_ALIASES:
            return n
        for key, aliases in self.TOPIC_ALIASES.items():
            if n in [self._norm(a) for a in aliases]:
                return key
        return n

    def _generic_topic_content(self, canonical: str) -> dict[str, Any]:
        name = self._display_name(canonical)
        return {
            "definition": f"{name} is a technical capability used in software and data systems. FORGE treats the topic as a learning subject only when connected evidence supports its relevance to the selected role.",
            "why": f"Learn {name} by understanding its core abstraction, implementing a small example, testing failure cases and then studying production concerns.",
            "prerequisites": ["Programming fundamentals", "Git", "Basic debugging"],
            "concepts": [("Core abstraction", f"Understand the central problem {name} solves."), ("Interfaces", "Learn the inputs, outputs and contracts involved."), ("Implementation", "Build a minimal working example."), ("Testing", "Measure correctness and failure cases."), ("Production", "Study performance, security, reliability and maintenance.")],
            "how": f"Start with the core abstraction behind {name}, trace the data or control flow through a minimal implementation, then add testing and production constraints. The exact architecture depends on the role and use case.",
            "use_cases": [f"Role-specific applications of {name}", "Learning projects", "Production systems where the underlying problem requires this capability"],
            "mistakes": ["Learning syntax without understanding the underlying abstraction", "Skipping testing", "Ignoring failure modes", "Using the technology when a simpler approach is sufficient"],
            "comparisons": [],
            "project": {"title": f"Build a practical {name} project", "description": f"Implement a small end-to-end system using {name}, test it, document the architecture and record measurable results.", "steps": ["Define the problem", "Build a minimal implementation", "Add tests", "Measure behavior", "Document trade-offs", "Add one production concern"]},
            "assessment": [{"question": f"What problem does {name} solve?", "answer": "Explain the central abstraction and when it is appropriate."}, {"question": f"What is one important production concern for {name}?", "answer": "A valid answer should address correctness, performance, security, reliability or maintainability."}],
        }

    def _topic_market_detail(self, role: str, canonical: str) -> dict[str, Any]:
        jobs = self._load_jobs(role)
        stats = self._extract_topic_stats(role, jobs)
        row = stats[stats["topic"] == canonical] if not stats.empty else pd.DataFrame()
        if row.empty:
            return {"market_mentions": 0, "role_job_count": len(jobs), "prevalence_percent": 0.0, "trend": "No sufficient role-specific market evidence", "period_counts": {}}
        r = row.iloc[0]
        return {
            "market_mentions": int(r["recent_mentions"]),
            "role_job_count": int(r["recent_job_count"]),
            "all_role_job_count": int(r["role_job_count"]),
            "prevalence_percent": round(float(r["recent_share"])*100, 2),
            "previous_prevalence_percent": round(float(r["prior_share"])*100, 2),
            "share_change_pp": round(float(r["share_change_pp"]), 2),
            "trend_consistency": round(float(r["trend_consistency"]), 3),
            "periods_observed": int(r["usable_periods"]),
            "trend": "↑ increasing" if r["share_change_pp"] > 3 and r["trend_consistency"] >= .5 else "→ stable/established",
            "period_counts": r["period_counts"], "current_window": r["current_window"],
            "onet": self._onet_topic_evidence(role, canonical),
        }

    @staticmethod
    def _ensure_topic_assessment(name: str, content: dict[str, Any], existing: Any = None) -> dict[str, Any]:
        """
        Guarantee an interactive assessment for every resolved topic.

        This is deterministic fallback content. It never fabricates market,
        O*NET, WEF, or BLS evidence; it only tests the technical content of
        the topic page.
        """
        questions = existing if isinstance(existing, list) else []
        questions = [q for q in questions if isinstance(q, dict) and q.get("question") and isinstance(q.get("options"), list) and len(q.get("options")) >= 2]

        concepts = content.get("concepts", []) if isinstance(content, dict) else []
        first_concept = concepts[0][0] if concepts and isinstance(concepts[0], (list, tuple)) else "the core abstraction"
        second_concept = concepts[1][0] if len(concepts) > 1 and isinstance(concepts[1], (list, tuple)) else "implementation details"
        definition = str(content.get("definition", f"{name} is a technical capability.")) if isinstance(content, dict) else f"{name} is a technical capability."

        fallback = [
            {
                "type": "conceptual",
                "question": f"What is the main problem that {name} is designed to address?",
                "options": [
                    f"Understanding and applying {first_concept}",
                    "Avoiding all testing and validation",
                    "Replacing every other software technology",
                    "Guaranteeing production success without measurement",
                ],
                "answer_index": 0,
                "explanation": f"The assessment should test the central purpose of {name}, not memorization of unrelated tools.",
            },
            {
                "type": "implementation",
                "question": f"Which step is most appropriate before calling a {name} implementation production-ready?",
                "options": [
                    "Test expected behavior and important failure cases",
                    "Only verify that the demo runs once",
                    "Remove observability to simplify the system",
                    "Skip documentation because the technology is standardized",
                ],
                "answer_index": 0,
                "explanation": "Testing failure cases and measuring behavior are part of responsible implementation.",
            },
            {
                "type": "debugging",
                "question": f"When a {name} implementation fails, what should you inspect first?",
                "options": [
                    f"The assumptions and interfaces around {second_concept}",
                    "Only the UI color scheme",
                    "Only the project name",
                    "Whether another unrelated technology is popular",
                ],
                "answer_index": 0,
                "explanation": "Debugging should begin with the concrete inputs, outputs, assumptions and component boundaries.",
            },
            {
                "type": "scenario",
                "question": f"Which approach best demonstrates practical understanding of {name}?",
                "options": [
                    "Build a small working system, evaluate it, and document trade-offs",
                    "Copy a tutorial without changing or measuring anything",
                    "Memorize terminology without implementation",
                    "Use it even when a simpler approach fits the problem better",
                ],
                "answer_index": 0,
                "explanation": "A small evaluated implementation provides evidence of both technical understanding and practical use.",
            },
            {
                "type": "conceptual",
                "question": f"Which statement best describes learning {name} at an engineering level?",
                "options": [
                    definition[:220],
                    "It is useful only because it appears in a job title",
                    "It never requires testing, security or maintenance",
                    "Its presence in one posting proves universal demand",
                ],
                "answer_index": 0,
                "explanation": "Technical learning should connect the abstraction to implementation and engineering constraints.",
            },
        ]

        normalized = []
        for q in (questions + fallback):
            if len(normalized) >= 5:
                break
            opts = q.get("options") if isinstance(q.get("options"), list) else []
            if len(opts) < 2:
                continue
            opts = [str(x) for x in opts[:4]]
            try:
                idx = int(q.get("answer_index", 0))
            except Exception:
                idx = 0
            idx = idx if 0 <= idx < len(opts) else 0
            normalized.append({
                "type": q.get("type", "conceptual"),
                "question": str(q.get("question")),
                "options": opts,
                "answer_index": idx,
                "explanation": str(q.get("explanation", "Review the underlying concept and failure mode.")),
            })

        return {"questions": normalized[:5]}

    def topic_intelligence(self, role: str, topic: str, horizon: str = "emerging", generate: bool = False) -> dict[str, Any]:
        canonical = self._canonical_topic(topic)
        name = self.TOPIC_DISPLAY.get(canonical, str(topic).strip())
        market = self._topic_market_detail(role, canonical)
        stats = self._extract_topic_stats(role, self._load_jobs(role))
        onet = market.get("onet", {})
        five_groups = [x for x in self._wef_capabilities(role, stats) if name in x.get("supporting_topics", [])]
        ten_groups = self._ten_year(role, stats)
        if horizon == "fiveYear":
            future_items = five_groups
            future_type = "WEF capability context"
        elif horizon == "tenYear":
            future_items = ten_groups
            future_type = "BLS occupation context"
        else:
            future_items = five_groups or ten_groups
            future_type = "Supporting future context"

        related = []
        if not stats.empty:
            row = stats[stats["topic"] == canonical]
            if not row.empty:
                r = row.iloc[0]
                related = [self._display_name(x) for x in stats[stats["topic"] != canonical].sort_values("recent_share", ascending=False).head(10)["topic"].tolist()]
        bls = self._bls_role_rows(role)
        evidence = {
            "market": market,
            "onet": onet,
            "future": {"type": future_type, "items": future_items[:6]},
            "sources": {
                "market": "FORGE Greenhouse employer postings",
                "technology": "O*NET technology evidence",
                "future": "WEF Future of Jobs 2025–2030 and/or BLS 2025–2035 occupational projections",
            },
        }

        generated = None
        # Fast path: return deterministic FORGE topic intelligence immediately.
        # LLM enrichment is opt-in so opening a topic never blocks on a network call.
        cache_key = (str(role).strip().lower(), canonical, str(horizon).strip().lower())
        if generate and self.topic_generator is not None:
            generated = self._topic_generated_cache.get(cache_key)
            if generated is None:
                try:
                    generated = self.topic_generator.generate(
                        topic=name, role=role, market_evidence=market,
                        onet_evidence=onet, future_evidence=evidence["future"], related_topics=related,
                    )
                    if generated:
                        self._topic_generated_cache[cache_key] = generated
                except Exception as exc:
                    print(f"[WARN] Dynamic topic generation unavailable for {name}: {exc}")

        # The existing curated content remains a deterministic fallback only.
        # It is not used to decide market demand or future evidence.
        content = self.TOPIC_CONTENT.get(canonical, self._generic_topic_content(canonical))
        confidence = self._sample_confidence(int(market.get("role_job_count", 0)), int(market.get("market_mentions", 0)))
        # ------------------------------------------------------------
        # Career / future-work context
        # ------------------------------------------------------------
        # These are source-backed role signals, not a technology-specific
        # prediction. WEF provides global 2025-2030 role expectations; BLS
        # provides U.S. occupation projections through 2035.
        topic_set = {canonical}
        # Include closely related observed topics so a capability can surface
        # adjacent occupations without a topic-specific frontend branch.
        if not stats.empty:
            related_rows = stats.sort_values("recent_share", ascending=False).head(8)["topic"].tolist()
            topic_set.update(related_rows)
        global_role_catalog = [
            ("Big Data Specialists", "WEF identifies this among the fastest-growing job roles toward 2030."),
            ("AI and Machine Learning Specialists", "WEF identifies this among the fastest-growing job roles toward 2030."),
            ("Software and Applications Developers", "WEF identifies this among the fastest-growing job roles toward 2030."),
            ("Information Security Analysts", "WEF places information-security roles among the technology-driven growth roles."),
        ]
        global_role_signals = []
        for role_name, signal in global_role_catalog:
            relevance_topics = self.WEF_ROLE_TOPIC_MAP.get(role_name, set())
            overlap = sorted(topic_set.intersection(relevance_topics))
            if canonical in relevance_topics or overlap:
                global_role_signals.append({
                    "role": role_name,
                    "horizon": "2030",
                    "signal": signal,
                    "relevance_topics": [self._display_name(x) for x in overlap[:5]],
                    "source": "WEF Future of Jobs 2025",
                })
        if not global_role_signals:
            # Keep the global context useful without pretending relevance.
            global_role_signals = [{
                "role": "AI and Machine Learning Specialists",
                "horizon": "2030",
                "signal": "WEF identifies this among the fastest-growing job roles toward 2030; FORGE shows it here only as broader career context.",
                "relevance_topics": [],
                "source": "WEF Future of Jobs 2025",
            }]


        occupation_outlook = []
        if not bls.empty:
            title_col = self._find_column(bls, ["occupation_title", "Occupation Title", "title"])
            growth_col = self._find_column(bls, ["employment_change_percent"])
            change_col = self._find_column(bls, ["employment_change_thousands", "employment_change_absolute_thousands"])
            openings_col = self._find_column(bls, ["occupational_openings_2025_35_annual_avg_thousands"])
            for _, row in bls.head(5).iterrows():
                occupation_outlook.append({
                    "role": str(row.get(title_col, "Occupation")),
                    "horizon": "2035",
                    "growth_percent": self._num(row.get(growth_col)),
                    "employment_change_thousands": self._num(row.get(change_col)),
                    "annual_openings_thousands": self._num(row.get(openings_col)),
                    "source": "BLS 2025–2035 occupational projections",
                })

        career_outlook = {
            "headline": f"Where {name} sits in the future-work landscape",
            "global_2030_role_signals": global_role_signals,
            "selected_role_2035": occupation_outlook,
            "interpretation": (
                "Global role signals describe occupations employers expect to grow toward 2030. "
                "BLS adds a U.S. occupation-level view through 2035. Neither source is treated as a "
                "guaranteed forecast for this individual technology."
            ),
        }

        base = {
            "role": role, "topic": name, "topic_key": canonical, "horizon": horizon,
            "confidence": round(confidence, 3), "confidence_label": self._confidence_label(confidence, int(market.get("role_job_count", 0))),
            "market_evidence": market,
            "future_evidence": {"type": future_type, "items": future_items[:6], "explanation": "Future sources provide broad capability or occupation evidence; they do not prove an individual technology forecast."},
            "evidence": {
                "market": "FORGE Greenhouse employer postings",
                "technology": "O*NET employer-posting technology evidence",
                "future": "WEF Future of Jobs 2025–2030 for capability context; BLS 2025–2035 for occupation context",
                "occupation": [str(x) for x in bls[self._find_column(bls, ["occupation_title", "Occupation Title", "title"])].dropna().tolist()] if not bls.empty and self._find_column(bls, ["occupation_title", "Occupation Title", "title"]) else [],
            },
            "resources": self._verified_resources(canonical, content),
            "dynamic_generation": bool(generated),
            "career_outlook": career_outlook,
            "why_now": {
                "title": f"Why {name} matters now",
                "market": "Observed employer evidence is shown separately above.",
                "future": career_outlook["interpretation"],
            },
        }
        if generated:
            base.update(generated)
            # Evidence remains authoritative from FORGE, never from the model.
            base["market_evidence"] = market
            base["future_evidence"] = {"type": future_type, "items": future_items[:6], "explanation": "Future sources provide broad capability or occupation evidence; they do not prove an individual technology forecast."}
            base["evidence"] = base["evidence"]
            base["resources"] = self._verified_resources(canonical, base)
            base["career_outlook"] = career_outlook
            base["assessment"] = self._ensure_topic_assessment(
                name,
                content,
                (generated.get("assessment") or {}).get("questions") if isinstance(generated.get("assessment"), dict) else None,
            )
            base["why_now"] = {
                "title": f"Why {name} matters now",
                "market": "Observed employer evidence is shown separately above.",
                "future": career_outlook["interpretation"],
            }
        else:
            base.update({
                "overview": {"definition": content["definition"], "why_it_exists": content["why"], "when_to_use": content.get("use_cases", [])[:4], "when_not_to_use": content.get("mistakes", [])[:4], "why_it_matters": content["why"], "difficulty": "Intermediate"},
                "topic_category": "Technical capability", "difficulty": "Intermediate",
                "related_capabilities": related,
                "prerequisites": {"required": content["prerequisites"], "recommended": related[:4]},
                "key_concepts": [{"title": a, "description": b, "importance": "core"} for a,b in content["concepts"]],
                "learning_path": [
                    {"stage": "1 · Core model", "focus": content["concepts"][0][1], "outcome": f"Explain {content['concepts'][0][0]} and when it matters.", "prerequisites": content["prerequisites"][:2]},
                    {"stage": "2 · Key mechanics", "focus": "; ".join(f"{a}: {b}" for a,b in content["concepts"][1:3]), "outcome": f"Trace a working {name} flow from input to output.", "prerequisites": content["prerequisites"][:3]},
                    {"stage": "3 · Applied build", "focus": content["project"]["description"], "outcome": f"Build a demonstrable {name} implementation.", "prerequisites": content["prerequisites"]},
                    {"stage": "4 · Failure & evaluation", "focus": "; ".join(content["mistakes"][:3]), "outcome": "Identify failure modes and prove behavior with tests or metrics.", "prerequisites": []},
                    {"stage": "5 · Production", "focus": "; ".join(f"{a}: {b}" for a,b in content["concepts"][3:6]), "outcome": "Explain the operational trade-offs needed to ship the capability responsibly.", "prerequisites": []},
                ],
                "how_it_works": {"summary": content["how"], "steps": [{"title": title, "description": desc} for title,desc in content["concepts"][:6]], "architecture": {"nodes": [{"id": str(i), "label": title, "layer": "Topic flow"} for i,(title,_) in enumerate(content["concepts"][:6])], "edges": []}},
                "use_cases": [{"title": x, "description": f"A concrete {name} application where this capability solves the stated problem."} for x in content["use_cases"]],
                "common_mistakes": [{"mistake": x, "why": f"This failure mode can reduce the reliability or usefulness of {name}.", "fix": f"Create a small test or check specifically designed to detect {x.lower()} before the result reaches production."} for x in content["mistakes"]],
                "comparison": {"available": bool(content["comparisons"]), "title": "Technical comparison", "columns": ["Approach A", "Approach B"], "rows": [{"dimension": a, "values": [b, "See topic-specific alternative"]} for a,b in content["comparisons"]]},
                "comparisons": [{"title": a, "description": b} for a,b in content["comparisons"]],
                "project": content["project"],
                "assessment": self._ensure_topic_assessment(name, content, content.get("assessment")),
                "section_status": {"comparison": "available" if content["comparisons"] else "not_applicable", "architecture": "not_applicable"},
            })
        return base

    def _inline_topic_article(self, canonical: str, content: dict[str, Any] | None = None) -> dict[str, Any]:
        """Build a self-contained reading resource for any topic without an external URL."""
        content = content if isinstance(content, dict) else self._generic_topic_content(canonical)
        display = self.TOPIC_DISPLAY.get(canonical, canonical.replace("_", " ").title())

        overview = content.get("overview") if isinstance(content.get("overview"), dict) else {}
        how = content.get("how_it_works") if isinstance(content.get("how_it_works"), dict) else {}
        prerequisites = content.get("prerequisites") if isinstance(content.get("prerequisites"), dict) else {}
        project = content.get("project") if isinstance(content.get("project"), dict) else {}

        sections: list[dict[str, Any]] = []

        definition = overview.get("definition") or content.get("definition")
        why = overview.get("why_it_matters") or overview.get("why_exists") or content.get("why")
        if definition or why:
            sections.append({
                "heading": "What it is and why it matters",
                "paragraphs": [str(x) for x in (definition, why) if x],
            })

        how_summary = how.get("summary") or content.get("how")
        how_steps = how.get("steps") if isinstance(how.get("steps"), list) else []
        if how_summary or how_steps:
            sections.append({
                "heading": "How it works",
                "paragraphs": [str(how_summary)] if how_summary else [],
                "bullets": [
                    f"{s.get('title')}: {s.get('description')}" if isinstance(s, dict) and s.get("title")
                    else str(s)
                    for s in how_steps
                ],
            })

        concepts = content.get("key_concepts")
        if not isinstance(concepts, list):
            concepts = content.get("concepts", [])
        concept_bullets = []
        for item in concepts:
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or "Concept"
                desc = item.get("description") or item.get("explanation") or item.get("importance")
                concept_bullets.append(f"{title}: {desc}" if desc else str(title))
            elif isinstance(item, (list, tuple)) and item:
                concept_bullets.append(f"{item[0]}: {item[1]}" if len(item) > 1 else str(item[0]))
            else:
                concept_bullets.append(str(item))
        if concept_bullets:
            sections.append({"heading": "Core concepts", "bullets": concept_bullets})

        req = prerequisites.get("required") if isinstance(prerequisites.get("required"), list) else content.get("prerequisites", [])
        rec = prerequisites.get("recommended") if isinstance(prerequisites.get("recommended"), list) else []
        if req or rec:
            sections.append({
                "heading": "Prerequisites",
                "bullets": ([f"Required: {x}" for x in req] if isinstance(req, list) else []) +
                           ([f"Recommended: {x}" for x in rec] if isinstance(rec, list) else []),
            })

        learning = content.get("learning_path", [])
        if isinstance(learning, list) and learning:
            bullets = []
            for item in learning:
                if isinstance(item, dict):
                    stage = item.get("stage") or item.get("level") or "Stage"
                    focus = item.get("focus") or item.get("description") or ""
                    outcome = item.get("outcome") or ""
                    line = f"{stage}: {focus}"
                    if outcome:
                        line += f" — Outcome: {outcome}"
                    bullets.append(line)
                else:
                    bullets.append(str(item))
            sections.append({"heading": "Learning path", "bullets": bullets})

        use_cases = content.get("use_cases", [])
        if isinstance(use_cases, list) and use_cases:
            sections.append({
                "heading": "Where it is used",
                "bullets": [
                    f"{x.get('title')}: {x.get('description')}" if isinstance(x, dict) and x.get("title")
                    else str(x)
                    for x in use_cases
                ],
            })

        mistakes = content.get("common_mistakes", []) or content.get("mistakes", [])
        if isinstance(mistakes, list) and mistakes:
            bullets = []
            for item in mistakes:
                if isinstance(item, dict):
                    bullets.append(f"{item.get('mistake', 'Mistake')} — Why: {item.get('why', '')} Fix: {item.get('fix', '')}")
                else:
                    bullets.append(str(item))
            sections.append({"heading": "Common mistakes and fixes", "bullets": bullets})

        if project:
            project_lines = []
            if project.get("brief") or project.get("description"):
                project_lines.append(str(project.get("brief") or project.get("description")))
            if project.get("dataset"):
                project_lines.append(f"Dataset / input: {project['dataset']}")
            stages = project.get("stages") or project.get("steps") or []
            if isinstance(stages, list):
                project_lines.extend([f"Step: {x}" for x in stages])
            evaluation = project.get("evaluation") or []
            if isinstance(evaluation, list) and evaluation:
                project_lines.append("Evaluation: " + " · ".join(str(x) for x in evaluation))
            if project.get("expected_output"):
                project_lines.append(f"Expected output: {project['expected_output']}")
            if project_lines:
                sections.append({"heading": "Practice project", "paragraphs": project_lines})

        if not sections:
            sections = [{
                "heading": "Topic guide",
                "paragraphs": [
                    f"{display} is a role-relevant technical capability in FORGE.",
                    "Use the Topic Intelligence sections above to understand the concept, prerequisites, learning path and project application.",
                ],
            }]

        return {
            "type": "article",
            "title": f"Read inside FORGE: {display}",
            "source": "FORGE Topic Guide",
            "internal": True,
            "topic": display,
            "sections": sections,
            "note": "This article is rendered inside FORGE. No external site is required.",
        }

    def _verified_resources(self, canonical: str, content: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        # Verified videos are curated. For every other topic, FORGE provides a
        # self-contained article rendered inside the Topic Intelligence page.
        videos = {
            "python": [
                ("Python full course", "rfscVS0vtbw"),
                ("Python OOP", "ZDa-Z5JzLYM"),
            ],
            "machine learning": [
                ("Linear Regression", "nk2CQITm_eo"),
                ("Logistic Regression", "yIYKR4sgzI8"),
                ("Decision Trees / Random Forests", "l_L6t_iHgf8"),
                ("K-Means", "4b5d3muPQmA"),
                ("Cross Validation", "fSytzGwwBVw"),
            ],
            "sql": [("SQL full course", "HXV3zeQKqGY")],
            "react": [("React JS full course", "bMknfKXIFA8")],
            "kubernetes": [("Kubernetes beginner course", "d6WC5n9G_sM")],
            "typescript": [("TypeScript full tutorial", "30LWjhZzg50")],
            "javascript": [("JavaScript full course for beginners", "PkZNo7MFNFg")],
            "node.js": [("Node.js full tutorial for beginners", "RLtyhwFtXQA")],
            "docker": [("Docker full DevOps course", "rjjES5IsPdg")],
        }
        verified = [
            {"type": "video", "id": vid, "title": title, "source": "YouTube verified resource"}
            for title, vid in videos.get(canonical, [])
        ]
        if verified:
            return verified
        return [self._inline_topic_article(canonical, content)]

    def resources(self, role: str, topic: str, horizon: str = "emerging") -> dict[str, Any]:
        canonical = self._canonical_topic(topic)
        content = self._generic_topic_content(canonical)
        resources = self._verified_resources(canonical, content)
        return {
            "role": role,
            "topic": self.TOPIC_DISPLAY.get(canonical, topic),
            "horizon": horizon,
            "resources": resources,
            "note": "Verified videos are embedded when available; otherwise FORGE provides an internal topic article. No external resource URL is required for the article fallback.",
        }
