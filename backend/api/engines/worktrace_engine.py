from pathlib import Path
import pandas as pd


# ============================================================
# FORGE WORKTRACE ENGINE
# ============================================================

ROOT = Path(__file__).resolve().parents[3]

WORKTRACE_PATH = (
    ROOT
    / "datasets"
    / "onet"
    / "knowledge_base"
    / "forge_worktrace.parquet"
)


class WorkTraceEngine:

    def __init__(self):
        print("\n[WORKTRACE] Loading intelligence layer...")

        self.df = pd.read_parquet(WORKTRACE_PATH)

        print(
            f"[WORKTRACE] Records: "
            f"{len(self.df):,}"
        )

        print(
            f"[WORKTRACE] Occupations: "
            f"{self.df['Occupation Title'].nunique():,}"
        )

        print(
            f"[WORKTRACE] Tasks: "
            f"{self.df['Task ID'].nunique():,}"
        )

        print(
            f"[WORKTRACE] Capabilities: "
            f"{self.df['Capability Name'].nunique():,}"
        )

    # ========================================================
    # LIST ALL OCCUPATIONS
    # ========================================================

    def list_occupations(self, limit: int = 1000):

        occupations = (
            self.df["Occupation Title"]
            .dropna()
            .drop_duplicates()
            .sort_values()
            .head(limit)
            .tolist()
        )

        return occupations

    # ========================================================
    # SEARCH OCCUPATIONS
    # ========================================================

    def search_occupations(
        self,
        query: str,
        limit: int = 20
    ):

        query = query.strip().lower()

        if not query:
            return self.list_occupations(limit)

        mask = (
            self.df["Occupation Title"]
            .fillna("")
            .str.lower()
            .str.contains(
                query,
                regex=False
            )
        )

        occupations = (
            self.df.loc[
                mask,
                "Occupation Title"
            ]
            .drop_duplicates()
            .sort_values()
            .head(limit)
            .tolist()
        )

        return occupations

    # ========================================================
    # OCCUPATION INTELLIGENCE
    # ========================================================

    def get_occupation(self, occupation: str):

        occupation = occupation.strip()

        mask = (
            self.df["Occupation Title"]
            .fillna("")
            .str.lower()
            .eq(occupation.lower())
        )

        subset = self.df.loc[mask].copy()

        if subset.empty:
            return None

        # ----------------------------------------------------
        # TASK INTELLIGENCE
        # ----------------------------------------------------

        task_columns = [
            "Task ID",
            "Task",
            "DWA Element Name",
            "Task Capability Weight",
            "Task_AI_Suitability",
            "AI_Share",
            "Human_Share",
        ]

        task_columns = [
            column
            for column in task_columns
            if column in subset.columns
        ]

        tasks = (
            subset[task_columns]
            .drop_duplicates(
                subset=["Task ID"]
            )
            .copy()
        )

        # ----------------------------------------------------
        # CAPABILITY INTELLIGENCE
        # ----------------------------------------------------

        capability_columns = [
            "Capability Type",
            "Capability ID",
            "Capability Name",
            "Occupation Capability Value",
        ]

        capability_columns = [
            column
            for column in capability_columns
            if column in subset.columns
        ]

        capabilities = (
            subset[capability_columns]
            .drop_duplicates()
            .copy()
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        result = {
            "occupation": occupation,

            "record_count": int(
                len(subset)
            ),

            "task_count": int(
                subset["Task ID"].nunique()
            ),

            "capability_count": int(
                subset["Capability Name"].nunique()
            ),

            "tasks": (
                tasks
                .where(
                    pd.notna(tasks),
                    None
                )
                .to_dict(
                    orient="records"
                )
            ),

            "capabilities": (
                capabilities
                .where(
                    pd.notna(capabilities),
                    None
                )
                .to_dict(
                    orient="records"
                )
            ),
        }

        return result

    # ========================================================
    # WORKTRACE SUMMARY
    # ========================================================

    def summary(self):

        return {
            "records": int(
                len(self.df)
            ),

            "occupations": int(
                self.df["Occupation Title"].nunique()
            ),

            "tasks": int(
                self.df["Task ID"].nunique()
            ),

            "capabilities": int(
                self.df["Capability Name"].nunique()
            ),
        }


# ============================================================
# SINGLE ENGINE INSTANCE
# ============================================================

worktrace_engine = WorkTraceEngine()