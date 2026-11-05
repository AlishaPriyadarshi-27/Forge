from pathlib import Path
import io
import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = PROJECT_ROOT / "datasets" / "market" / "snapshots"
HISTORY_FILE = SNAPSHOT_DIR / "skill_demand_history.csv"

DATASET_URL = (
    "https://huggingface.co/datasets/"
    "datamatastudios/skill-scarcity-index/resolve/main/skill-scarcity-index.csv?download=true"
)

REQUEST_TIMEOUT = 60


def log(message):
    print(f"[FORGE MARKET] {message}")


def download_latest_snapshot():
    log("Fetching latest public market snapshot...")

    response = requests.get(
        DATASET_URL,
        timeout=REQUEST_TIMEOUT,
        headers={"User-Agent": "FORGE-Industry-Pulse/1.0"},
    )
    response.raise_for_status()

    df = pd.read_csv(io.BytesIO(response.content))

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    required = {
        "snapshot_date",
        "category",
        "skill_name",
        "demand_count",
        "demand_pct",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "The downloaded dataset does not contain the expected columns. "
            f"Missing: {', '.join(sorted(missing))}. "
            f"Received: {', '.join(df.columns)}"
        )

    return df


def clean_snapshot(df):
    df = df.copy()

    df = df.rename(
        columns={
            "skill_name": "skill",
        }
    )

    df["snapshot_date"] = pd.to_datetime(
        df["snapshot_date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df["demand_pct"] = pd.to_numeric(
        df["demand_pct"],
        errors="coerce"
    )

    df["demand_count"] = pd.to_numeric(
        df["demand_count"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "snapshot_date",
            "category",
            "skill",
            "demand_pct",
        ]
    )

    return df


def update_history(snapshot):
    SNAPSHOT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    latest_date = snapshot["snapshot_date"].max()

    if HISTORY_FILE.exists():
        history = pd.read_csv(HISTORY_FILE)

        if not history.empty:
            history.columns = [
                str(c).strip().lower().replace(" ", "_")
                for c in history.columns
            ]

            existing_dates = set(
                history["snapshot_date"]
                .astype(str)
                .str[:10]
            )

            if latest_date in existing_dates:
                log(
                    f"Snapshot {latest_date} already exists. "
                    "Skipping duplicate."
                )
                return history

            combined = pd.concat(
                [history, snapshot],
                ignore_index=True
            )
        else:
            combined = snapshot
    else:
        combined = snapshot

    key_columns = [
        "snapshot_date",
        "category",
        "skill",
    ]

    combined = combined.drop_duplicates(
        subset=key_columns,
        keep="last"
    )

    combined["snapshot_date"] = pd.to_datetime(
        combined["snapshot_date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    combined = combined.sort_values(
        ["snapshot_date", "category", "skill"]
    )

    combined.to_csv(
        HISTORY_FILE,
        index=False
    )

    return combined


def main():
    log(f"Project root: {PROJECT_ROOT}")
    log(f"History file: {HISTORY_FILE}")

    try:
        snapshot = download_latest_snapshot()
        snapshot = clean_snapshot(snapshot)

        if snapshot.empty:
            raise RuntimeError(
                "Downloaded dataset contains no usable rows."
            )

        latest_date = snapshot["snapshot_date"].max()

        log(
            f"Downloaded snapshot date: {latest_date}"
        )

        history = update_history(snapshot)

        dates = sorted(
            history["snapshot_date"]
            .dropna()
            .astype(str)
            .unique()
        )

        log(f"Stored snapshots: {len(dates)}")

        if dates:
            log(f"Earliest: {dates[0]}")
            log(f"Latest:   {dates[-1]}")

        log("Market-data update completed successfully.")

    except requests.RequestException as exc:
        log(f"Network error while fetching market data: {exc}")
        raise SystemExit(1)

    except Exception as exc:
        log(f"Update failed: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
