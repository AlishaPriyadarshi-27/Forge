import os
import gc
import time

import numpy as np
import pandas as pd
import faiss
import torch

from sentence_transformers import SentenceTransformer


# ============================================================
# FORGE JOB → CAPABILITY MATCHING
# Optimized CPU semantic retrieval
# ============================================================

JOB_FILE = (
    "datasets/job_postings/knowledge_base/"
    "forge_job_market.parquet"
)

CAPABILITY_FILE = (
    "datasets/onet/knowledge_base/"
    "onet_capability_master.parquet"
)

OUTPUT_DIR = (
    "datasets/job_postings/knowledge_base"
)

OUTPUT_PARQUET = os.path.join(
    OUTPUT_DIR,
    "job_capability_matches.parquet"
)

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "job_capability_matches.csv"
)

CHECKPOINT_FILE = os.path.join(
    OUTPUT_DIR,
    "job_capability_matches_checkpoint.parquet"
)


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# SEMANTIC TEXT SETTINGS
# ============================================================

# MiniLM has a limited input sequence length.
# Extremely long job descriptions do not provide proportional
# additional information.

TITLE_WEIGHT = True

MAX_DESCRIPTION_CHARS = 1800


# ============================================================
# CPU SETTINGS
# ============================================================

CPU_CORES = os.cpu_count() or 4

# Leave one core for Windows / VS Code
TORCH_THREADS = max(
    1,
    CPU_CORES - 1
)

torch.set_num_threads(
    TORCH_THREADS
)

# Prevent thread oversubscription
torch.set_num_interop_threads(
    min(4, TORCH_THREADS)
)


if torch.cuda.is_available():

    DEVICE = "cuda"

    EMBEDDING_BATCH_SIZE = 512

else:

    DEVICE = "cpu"

    EMBEDDING_BATCH_SIZE = 256


JOB_BATCH_SIZE = EMBEDDING_BATCH_SIZE


# ============================================================
# MATCHING
# ============================================================

TOP_K = 10

SIMILARITY_THRESHOLD = 0.35


# Save checkpoint every N batches
CHECKPOINT_EVERY = 20


# ============================================================
# HELPERS
# ============================================================

def match_quality(score):

    if score >= 0.70:
        return "strong"

    elif score >= 0.55:
        return "moderate"

    elif score >= 0.45:
        return "weak"

    else:
        return "low"


# ============================================================
# START
# ============================================================

start_time = time.time()

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

print("\n" + "=" * 75)
print("FORGE — JOB → CAPABILITY SEMANTIC INTELLIGENCE")
print("=" * 75)

print(
    f"\nDevice: {DEVICE}"
)

print(
    f"CPU cores detected: {CPU_CORES}"
)

print(
    f"PyTorch CPU threads: {TORCH_THREADS}"
)

print(
    f"Embedding batch size: {EMBEDDING_BATCH_SIZE}"
)

print(
    f"Description characters used for embedding: "
    f"{MAX_DESCRIPTION_CHARS}"
)


# ============================================================
# [1/9] LOAD JOBS
# ============================================================

print("\n[1/9] Loading job market...")

jobs = pd.read_parquet(
    JOB_FILE
)

print(
    f"Jobs loaded: {len(jobs):,}"
)

required_job_columns = [
    "id",
    "title",
    "description"
]

missing = [
    c
    for c in required_job_columns
    if c not in jobs.columns
]

if missing:

    raise ValueError(
        f"Missing job columns: {missing}"
    )


# ============================================================
# [2/9] LOAD CAPABILITIES
# ============================================================

print("\n[2/9] Loading O*NET capabilities...")

capabilities = pd.read_parquet(
    CAPABILITY_FILE
)

print(
    f"Capability records loaded: "
    f"{len(capabilities):,}"
)

required_capability_columns = [
    "O*NET-SOC Code",
    "Capability Type",
    "Capability ID",
    "Capability Name"
]

missing = [
    c
    for c in required_capability_columns
    if c not in capabilities.columns
]

if missing:

    raise ValueError(
        f"Missing capability columns: {missing}"
    )


# ============================================================
# [3/9] UNIQUE CAPABILITIES
# ============================================================

print("\n[3/9] Preparing unique capabilities...")

capabilities = capabilities.copy()

for column in [
    "Capability Type",
    "Capability ID",
    "Capability Name"
]:

    capabilities[column] = (
        capabilities[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# IMPORTANT:
# Capability Type + Capability ID
# define the identity.

capabilities = (
    capabilities
    .drop_duplicates(
        subset=[
            "Capability Type",
            "Capability ID"
        ]
    )
    .reset_index(drop=True)
)

print(
    f"Unique capabilities: "
    f"{len(capabilities):,}"
)


# ============================================================
# [4/9] LOAD MODEL
# ============================================================

print("\n[4/9] Loading Sentence Transformer...")

model = SentenceTransformer(
    MODEL_NAME,
    device=DEVICE
)

print(
    f"Model: {MODEL_NAME}"
)

print(
    f"Model device: {DEVICE}"
)


# ============================================================
# [5/9] CAPABILITY TEXT
# ============================================================

print("\n[5/9] Preparing capability text...")

capability_texts = (
    capabilities["Capability Type"]
    + ": "
    + capabilities["Capability Name"]
).tolist()

print(
    f"Capability texts: "
    f"{len(capability_texts):,}"
)


# ============================================================
# [6/9] CAPABILITY EMBEDDINGS
# ============================================================

print("\n[6/9] Creating capability embeddings...")

capability_embeddings = model.encode(
    capability_texts,

    batch_size=EMBEDDING_BATCH_SIZE,

    show_progress_bar=True,

    convert_to_numpy=True,

    normalize_embeddings=True
)

capability_embeddings = np.asarray(
    capability_embeddings,
    dtype="float32"
)

print(
    "\nCapability embedding shape:"
)

print(
    capability_embeddings.shape
)


# ============================================================
# [7/9] FAISS INDEX
# ============================================================

print("\n[7/9] Building FAISS vector index...")

dimension = (
    capability_embeddings.shape[1]
)

print(
    f"Embedding dimension: {dimension}"
)

index = faiss.IndexFlatIP(
    dimension
)

index.add(
    capability_embeddings
)

print(
    f"FAISS index contains "
    f"{index.ntotal:,} capability vectors."
)


# ============================================================
# [8/9] JOB → CAPABILITY SEARCH
# ============================================================

print(
    "\n[8/9] Searching semantic capability matches..."
)

total_jobs = len(jobs)

total_batches = (
    total_jobs
    + JOB_BATCH_SIZE
    - 1
) // JOB_BATCH_SIZE

print(
    f"Total jobs: {total_jobs:,}"
)

print(
    f"Total batches: {total_batches:,}"
)

print(
    f"Top-K capabilities: {TOP_K}"
)

print(
    f"Similarity threshold: "
    f"{SIMILARITY_THRESHOLD}"
)

print(
    "\nStarting processing...\n"
)


results = []

processing_start = time.time()


for batch_number, start in enumerate(
    range(
        0,
        total_jobs,
        JOB_BATCH_SIZE
    ),
    start=1
):

    end = min(
        start + JOB_BATCH_SIZE,
        total_jobs
    )

    batch = jobs.iloc[
        start:end
    ]


    # ========================================================
    # FAST TEXT CONSTRUCTION
    # ========================================================

    titles = (
        batch["title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    descriptions = (
        batch["description"]
        .fillna("")
        .astype(str)
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
        .str.strip()
        .str.slice(
            0,
            MAX_DESCRIPTION_CHARS
        )
    )


    # Title + description.
    # Full descriptions remain untouched in source dataset.

    job_texts = (
        "Job Title: "
        + titles
        + "\nWork Description: "
        + descriptions
    ).tolist()


    # ========================================================
    # EMBEDDING
    # ========================================================

    job_embeddings = model.encode(
        job_texts,

        batch_size=EMBEDDING_BATCH_SIZE,

        show_progress_bar=False,

        convert_to_numpy=True,

        normalize_embeddings=True
    )

    job_embeddings = np.asarray(
        job_embeddings,
        dtype="float32"
    )


    # ========================================================
    # FAISS SEARCH
    # ========================================================

    similarities, indices = index.search(
        job_embeddings,
        TOP_K
    )


    # ========================================================
    # VECTORISED RESULT PREPARATION
    # ========================================================

    job_ids = (
        batch["id"]
        .tolist()
    )

    job_titles = (
        titles.tolist()
    )


    for row_number in range(
        len(batch)
    ):

        for rank in range(
            TOP_K
        ):

            capability_index = int(
                indices[
                    row_number,
                    rank
                ]
            )

            similarity = float(
                similarities[
                    row_number,
                    rank
                ]
            )

            if (
                capability_index < 0
            ):
                continue

            if (
                similarity
                < SIMILARITY_THRESHOLD
            ):
                continue


            capability = (
                capabilities.iloc[
                    capability_index
                ]
            )


            results.append({

                "job_id":
                    job_ids[row_number],

                "job_title":
                    job_titles[row_number],

                "capability_type":
                    capability[
                        "Capability Type"
                    ],

                "capability_id":
                    capability[
                        "Capability ID"
                    ],

                "capability_name":
                    capability[
                        "Capability Name"
                    ],

                "similarity_score":
                    round(
                        similarity,
                        4
                    ),

                "match_quality":
                    match_quality(
                        similarity
                    )
            })


    # ========================================================
    # PROGRESS
    # ========================================================

    processed = end

    elapsed = (
        time.time()
        - processing_start
    )

    speed = (
        processed / elapsed
        if elapsed > 0
        else 0
    )

    remaining = (
        total_jobs
        - processed
    )

    eta_seconds = (
        remaining / speed
        if speed > 0
        else 0
    )

    eta_minutes = (
        eta_seconds / 60
    )


    print(
        f"[Batch "
        f"{batch_number:>3}/"
        f"{total_batches}] "
        f"Jobs: "
        f"{processed:>7,}/"
        f"{total_jobs:,} "
        f"| Matches: "
        f"{len(results):,} "
        f"| Speed: "
        f"{speed:.1f} jobs/s "
        f"| ETA: "
        f"{eta_minutes:.1f} min"
    )


    # ========================================================
    # CHECKPOINT
    # ========================================================

    if (
        batch_number
        % CHECKPOINT_EVERY
        == 0
    ):

        checkpoint = pd.DataFrame(
            results
        )

        checkpoint.to_parquet(
            CHECKPOINT_FILE,
            index=False
        )

        print(
            f"    ✓ Checkpoint saved "
            f"({len(checkpoint):,} matches)"
        )

        del checkpoint


    # ========================================================
    # MEMORY CLEANUP
    # ========================================================

    del job_texts
    del job_embeddings
    del similarities
    del indices
    del batch

    gc.collect()


# ============================================================
# [9/9] SAVE
# ============================================================

print(
    "\n[9/9] Saving final results..."
)

results_df = pd.DataFrame(
    results
)

if results_df.empty:

    raise RuntimeError(
        "No matches generated."
    )


print(
    f"Total matches generated: "
    f"{len(results_df):,}"
)


# ============================================================
# PARQUET
# ============================================================

results_df.to_parquet(
    OUTPUT_PARQUET,
    index=False
)

print(
    "\n✓ Parquet saved:"
)

print(
    OUTPUT_PARQUET
)


# ============================================================
# CSV
# ============================================================

results_df.to_csv(
    OUTPUT_CSV,
    index=False
)

print(
    "\n✓ CSV saved:"
)

print(
    OUTPUT_CSV
)


# ============================================================
# CHECKPOINT CLEANUP
# ============================================================

if os.path.exists(
    CHECKPOINT_FILE
):

    os.remove(
        CHECKPOINT_FILE
    )

    print(
        "\n✓ Checkpoint removed."
    )


# ============================================================
# FINAL
# ============================================================

total_time = (
    time.time()
    - start_time
)

print(
    "\n" + "=" * 75
)

print(
    "FORGE JOB → CAPABILITY MATCHING COMPLETE"
)

print(
    "=" * 75
)

print(
    f"Jobs processed: "
    f"{total_jobs:,}"
)

print(
    f"Capabilities: "
    f"{len(capabilities):,}"
)

print(
    f"Total semantic matches: "
    f"{len(results_df):,}"
)

print(
    f"Total runtime: "
    f"{total_time / 60:.2f} minutes"
)

print(
    "=" * 75
)