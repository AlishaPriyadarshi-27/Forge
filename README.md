# FORGE
### AI-Powered Career Intelligence & Workforce Transformation Platform

**A data-driven platform for intelligent career discovery, skill gap analysis, workforce intelligence, and career scenario planning.**

<p align="center">
  <b>Capstone Project | CSE – Artificial Intelligence & Machine Learning</b>
</p>

---

## Overview

FORGE is an AI-powered career intelligence platform designed to bridge the gap between evolving industry demands and individual skill development.

The platform aims to transform fragmented labor-market data, job postings, and occupational skill information into actionable career insights.

By combining machine learning, data engineering, occupational taxonomies, and intelligent analytics, FORGE helps users understand career opportunities, identify skill gaps, explore career pathways, and make informed career decisions.

Rather than simply matching candidates with job descriptions, FORGE focuses on understanding how skills, occupations, and industry requirements evolve over time.

## Core Architecture

FORGE is organized into four interconnected modules:

### 1. WORKTRACE
**Labor Market Intelligence**

- Analyzes job market data and employment trends.
- Extracts industry-relevant information from job postings.
- Identifies emerging skill demands.
- Tracks changes in occupational requirements.

### 2. SKILL SHADOW
**Skill Intelligence & Gap Analysis**

- Maps skills to occupational requirements.
- Identifies skill gaps between current capabilities and career goals.
- Uses occupational skill taxonomies for structured skill analysis.
- Supports data-driven skill development recommendations.

### 3. WORKFOLD
**Career Scenario Intelligence**

- Explores alternative career pathways.
- Analyzes career transitions and skill requirements.
- Evaluates potential career scenarios.
- Connects occupational requirements with individual career goals.

### 4. LATTICE
**Connected Career Intelligence**

- Connects insights across the FORGE ecosystem.
- Integrates labor-market intelligence with skill and career information.
- Aims to provide a unified view of career opportunities and workforce trends.

---

## System Architecture

```text
             DATA SOURCES
                  |
        +---------+---------+
        |         |         |
      ESCO      O*NET     BLS
        |         |         |
        +---------+---------+
                  |
          GREENHOUSE DATA
                  |
                  v
          DATA PROCESSING
                  |
          FEATURE ENGINEERING
                  |
                  v
          ML & ANALYTICS LAYER
                  |
       +----------+----------+
       |          |          |
   WORKTRACE  SKILL SHADOW  WORKFOLD
       |          |          |
       +----------+----------+
                  |
                LATTICE
                  |
                  v
          CAREER INTELLIGENCE
```

## Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Backend | FastAPI |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Data Sources | ESCO, O*NET, BLS |
| Job Market Data | Greenhouse Job Postings |
| API Development | REST APIs |
| Frontend | React (where implemented) |
| Version Control | Git & GitHub |

## Datasets

FORGE leverages publicly available occupational and labor-market datasets.

| Dataset | Purpose |
|---|---|
| ESCO | European skills, competencies and occupations |
| O*NET | Occupational information and skill requirements |
| BLS | Labor market and employment statistics |
| Greenhouse Job Postings | Real-world job posting analysis |

**Data Processing:** Job posting data undergoes inspection, cleaning, preprocessing, and transformation before being used in downstream analytical workflows.

## Project Structure

```text
FORGE/
│
├── backend/
│   ├── api/
│   ├── models/
│   └── services/
│
├── datasets/
│   ├── job_postings/
│   ├── market/
│   └── ...
│
├── frontend/
│
├── notebooks/
│
├── docs/
│
├── research/
│
├── requirements.txt
├── .gitignore
└── README.md
```

*Note: Directory structure is a high-level representation. Refer to the actual repository for the complete implementation.*

## Installation & Setup

### Prerequisites

- Python 3.12
- Git
- pip
- Node.js and npm (if running the frontend)

### 1. Clone the Repository

```bash
git clone https://github.com/AlishaPriyadarshi-27/FORGE.git
```

### 2. Navigate to the Project

```bash
cd FORGE
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the Backend

```bash
uvicorn backend.api.main:app --reload
```

### 7. Access API Documentation

```text
http://127.0.0.1:8000/docs
```

*Run the commands from the project root. Frontend setup and additional configuration may depend on the current implementation.*

---

## Key Objectives

- Bridge the gap between industry skill demands and workforce capabilities.
- Enable structured skill gap identification.
- Provide data-driven career exploration.
- Analyze changing labor-market requirements.
- Support informed career planning through intelligent analytics.

## Future Scope

- Integration of Large
