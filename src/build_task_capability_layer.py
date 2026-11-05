import os
import gc
import time

import numpy as np
import pandas as pd
import faiss

from sentence_transformers import SentenceTransformer


# ============================================================
# FORGE
# TASK → CAPABILITY SEMANTIC INTELLIGENCE LAYER
# ============================================================

TASK_FILE = (
    "datasets/onet/knowledge_base/"
    "onet_tasks.parquet"
)

TASK_DWA_FILE = (
    "datasets/onet/knowledge_base/"
    "onet_task_dwa_master.parquet"
)

CAPABILITY_FILE = (
    "datasets/onet/knowledge_base/"
    "onet_capability_master.parquet"
)

OUTPUT_DIR = (
    "datasets/onet/knowledge_base"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "onet_task_capability_layer.parquet"
)

OUTPUT_CSV = os.path.join(
    OUTPUT_DIR,
    "onet_task_capability_layer.csv"
)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

BATCH_SIZE = 256

TOP_K = 10

SIMILARITY_THRESHOLD = 0.35


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_series(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
        .str.strip()
    )


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
print("FORGE — TASK → CAPABILITY SEMANTIC LAYER")
print("=" * 75)


# ============================================================
# [1/8] LOAD TASKS
# ============================================================

print("\n[1/8] Loading O*NET tasks...")

tasks = pd.read_parquet(
    TASK_FILE
)

print(
    f"Task records loaded: "
    f"{len(tasks):,}"
)

required_task_columns = [
    "O*NET-SOC Code",
    "Task ID",
    "Task"
]

missing = [
    c
    for c in required_task_columns
    if c not in tasks.columns
]

if missing:
    raise ValueError(
        f"Missing task columns: {missing}"
    )


# One unique task per occupation
tasks = (
    tasks
    .drop_duplicates(
        subset=[
            "O*NET-SOC Code",
            "Task ID"
        ]
    )
    .copy()
)

tasks["Task"] = clean_series(
    tasks["Task"]
)

print(
    f"Unique occupation-task pairs: "
    f"{len(tasks):,}"
)


# ============================================================
# [2/8] LOAD TASK → DWA
# ============================================================

print("\n[2/8] Loading Task → DWA relationships...")

task_dwa = pd.read_parquet(
    TASK_DWA_FILE
)

print(
    f"Task-DWA records: "
    f"{len(task_dwa):,}"
)

required_dwa_columns = [
    "O*NET-SOC Code",
    "Task ID",
    "DWA Element ID",
    "DWA Element Name"
]

missing = [
    c
    for c in required_dwa_columns
    if c not in task_dwa.columns
]

if missing:
    raise ValueError(
        f"Missing Task-DWA columns: {missing}"
    )


task_dwa = (
    task_dwa[
        required_dwa_columns
    ]
    .drop_duplicates()
    .copy()
)

task_dwa["DWA Element Name"] = clean_series(
    task_dwa["DWA Element Name"]
)


# ============================================================
# TASK + DWA
# ============================================================

task_structure = tasks.merge(
    task_dwa,
    on=[
        "O*NET-SOC Code",
        "Task ID"
    ],
    how="left"
)

print(
    f"Task-DWA structure records: "
    f"{len(task_structure):,}"
)


# ============================================================
# [3/8] LOAD CAPABILITIES
# ============================================================

print("\n[3/8] Loading O*NET capabilities...")

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
    "Capability Name",
    "Capability Value"
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


# Clean capability fields
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


capabilities[
    "Capability Value"
] = pd.to_numeric(
    capabilities[
        "Capability Value"
    ],
    errors="coerce"
)


# ============================================================
# UNIQUE CAPABILITY CATALOG
# ============================================================

capability_catalog = (
    capabilities[
        [
            "Capability Type",
            "Capability ID",
            "Capability Name"
        ]
    ]
    .drop_duplicates(
        subset=[
            "Capability Type",
            "Capability ID"
        ]
    )
    .reset_index(drop=True)
)

print(
    f"Unique capability identities: "
    f"{len(capability_catalog):,}"
)


# ============================================================
# [4/8] LOAD SENTENCE TRANSFORMER
# ============================================================

print("\n[4/8] Loading Sentence Transformer...")

model = SentenceTransformer(
    MODEL_NAME
)

print(
    f"Model loaded: {MODEL_NAME}"
)


# ============================================================
# [5/8] CREATE CAPABILITY EMBEDDINGS
# ============================================================

print(
    "\n[5/8] Creating capability embeddings..."
)

capability_texts = (
    capability_catalog[
        "Capability Type"
    ]
    + ": "
    + capability_catalog[
        "Capability Name"
    ]
).tolist()


capability_embeddings = model.encode(
    capability_texts,
    batch_size=BATCH_SIZE,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)

capability_embeddings = np.asarray(
    capability_embeddings,
    dtype="float32"
)

print(
    "Capability embedding shape:"
)

print(
    capability_embeddings.shape
)


# ============================================================
# [6/8] BUILD FAISS INDEX
# ============================================================

print(
    "\n[6/8] Building FAISS capability index..."
)

dimension = (
    capability_embeddings.shape[1]
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
# [7/8] TASK → CAPABILITY MATCHING
# ============================================================

print(
    "\n[7/8] Matching tasks to capabilities..."
)

# Create semantic text
task_structure[
    "Task"
] = clean_series(
    task_structure["Task"]
)

task_structure[
    "DWA Element Name"
] = clean_series(
    task_structure[
        "DWA Element Name"
    ]
)


task_structure[
    "Semantic Text"
] = (
    "Task: "
    + task_structure["Task"]
    + " | Work Activity: "
    + task_structure[
        "DWA Element Name"
    ]
)


total_records = len(
    task_structure
)

total_batches = (
    total_records
    + BATCH_SIZE
    - 1
) // BATCH_SIZE


print(
    f"Records to process: "
    f"{total_records:,}"
)

print(
    f"Total batches: "
    f"{total_batches:,}"
)


results = []

processing_start = time.time()


for batch_number, start in enumerate(
    range(
        0,
        total_records,
        BATCH_SIZE
    ),
    start=1
):

    end = min(
        start + BATCH_SIZE,
        total_records
    )

    batch = task_structure.iloc[
        start:end
    ]


    # --------------------------------------------------------
    # TASK EMBEDDINGS
    # --------------------------------------------------------

    task_texts = (
        batch[
            "Semantic Text"
        ]
        .tolist()
    )


    task_embeddings = model.encode(
        task_texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    task_embeddings = np.asarray(
        task_embeddings,
        dtype="float32"
    )


    # --------------------------------------------------------
    # FAISS SEARCH
    # --------------------------------------------------------

    similarities, indices = index.search(
        task_embeddings,
        TOP_K
    )


    # --------------------------------------------------------
    # SAVE MATCHES
    # --------------------------------------------------------

    for i in range(
        len(batch)
    ):

        source = batch.iloc[i]

        for rank in range(
            TOP_K
        ):

            capability_index = int(
                indices[i, rank]
            )

            similarity = float(
                similarities[i, rank]
            )


            if capability_index < 0:
                continue


            if similarity < SIMILARITY_THRESHOLD:
                continue


            capability = (
                capability_catalog.iloc[
                    capability_index
                ]
            )


            results.append({

                "O*NET-SOC Code":
                    source[
                        "O*NET-SOC Code"
                    ],

                "Task ID":
                    source[
                        "Task ID"
                    ],

                "Task":
                    source[
                        "Task"
                    ],

                "DWA Element ID":
                    source[
                        "DWA Element ID"
                    ],

                "DWA Element Name":
                    source[
                        "DWA Element Name"
                    ],

                "Capability Type":
                    capability[
                        "Capability Type"
                    ],

                "Capability ID":
                    capability[
                        "Capability ID"
                    ],

                "Capability Name":
                    capability[
                        "Capability Name"
                    ],

                "Semantic Similarity":
                    round(
                        similarity,
                        4
                    ),

                "Match Quality":
                    match_quality(
                        similarity
                    )
            })


    # --------------------------------------------------------
    # PROGRESS
    # --------------------------------------------------------

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
        total_records
        - processed
    )

    eta_seconds = (
        remaining / speed
        if speed > 0
        else 0
    )


    print(
        f"[Batch "
        f"{batch_number:>3}/"
        f"{total_batches}] "
        f"Records: "
        f"{processed:,}/"
        f"{total_records:,} "
        f"| Matches: "
        f"{len(results):,} "
        f"| Speed: "
        f"{speed:.1f} records/s "
        f"| ETA: "
        f"{eta_seconds / 60:.1f} min"
    )


    del task_texts
    del task_embeddings
    del similarities
    del indices

    gc.collect()


# ============================================================
# [8/8] ADD OCCUPATION CAPABILITY STRENGTH
# ============================================================

print(
    "\n[8/8] Adding occupation capability strength..."
)

matches = pd.DataFrame(
    results
)


if matches.empty:

    raise RuntimeError(
        "No task-capability matches generated."
    )


# ============================================================
# OCCUPATION-LEVEL CAPABILITY VALUE
# ============================================================

occupation_capability = (
    capabilities
    .groupby(
        [
            "O*NET-SOC Code",
            "Capability Type",
            "Capability ID"
        ],
        as_index=False
    )[
        "Capability Value"
    ]
    .mean()
)


occupation_capability = (
    occupation_capability
    .rename(
        columns={
            "Capability Value":
                "Occupation Capability Value"
        }
    )
)


# ============================================================
# MERGE
# ============================================================

matches = matches.merge(

    occupation_capability,

    on=[
        "O*NET-SOC Code",
        "Capability Type",
        "Capability ID"
    ],

    how="left"
)


# ============================================================
# FINAL ANALYTICAL WEIGHT
# ============================================================

matches[
    "Occupation Capability Value"
] = pd.to_numeric(
    matches[
        "Occupation Capability Value"
    ],
    errors="coerce"
)


matches[
    "Task Capability Weight"
] = (
    matches[
        "Semantic Similarity"
    ]
    *
    matches[
        "Occupation Capability Value"
    ]
)


# ============================================================
# SAVE PARQUET
# ============================================================

print(
    "\nSaving Parquet..."
)

matches.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    f"✓ Saved:\n{OUTPUT_FILE}"
)


# ============================================================
# SAVE CSV
# ============================================================

print(
    "\nSaving CSV..."
)

matches.to_csv(
    OUTPUT_CSV,
    index=False
)

print(
    f"✓ Saved:\n{OUTPUT_CSV}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

runtime = (
    time.time()
    - start_time
)

print(
    "\n" + "=" * 75
)

print(
    "FORGE TASK → CAPABILITY LAYER COMPLETE"
)

print(
    "=" * 75
)

print(
    f"Task-DWA records: "
    f"{total_records:,}"
)

print(
    f"Task-capability matches: "
    f"{len(matches):,}"
)

print(
    f"Unique occupations: "
    f"{matches['O*NET-SOC Code'].nunique():,}"
)

print(
    f"Unique tasks: "
    f"{matches['Task ID'].nunique():,}"
)

print(
    f"Unique capabilities: "
    f"{matches['Capability ID'].nunique():,}"
)

print(
    f"Runtime: "
    f"{runtime / 60:.2f} minutes"
)

print(
    "\nOutput:"
)

print(
    OUTPUT_FILE
)

print(
    "=" * 75
)