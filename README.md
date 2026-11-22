# LastHope — AI Lecture-to-Revision Assistant

> **Transform dense academic slides and terse lecture notes into structured revision packs, tiered practice exams, and adversarially verified study guides.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: Streamlit](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Inference: Groq Cloud](https://img.shields.io/badge/inference-Groq%20Cloud-F55036.svg)](https://groq.com/)
[![PDF Engine: PyMuPDF](https://img.shields.io/badge/pdf-PyMuPDF-2E7D32.svg)](https://pymupdf.readthedocs.io/)
[![Course: SCSE4041](https://img.shields.io/badge/course-SCSE4041%20Prompt%20Engineering-darkslateblue.svg)](#academic-metadata)

---

## 1. Project Overview

**LastHope** is a modular, AI-assisted study companion engineered to address the critical challenges students face during exam preparation: extracting coherent conceptual narratives from fragmented lecture slides, generating syllabus-aligned practice questions without spoilers, and detecting AI hallucinations or mathematical errors before studying.

Developed as the **Milestone 2** submission for **SCSE4041: Prompt Engineering** at **Bennett University**, LastHope implements a deterministic, multi-stage pipeline powered by three specialized prompt architectures and an adversarial verification auditor.

---

## 2. Key Features & Upload-to-Export Workflow

LastHope guides students through a 5-stage sequential workflow:

```
[ Stage 01: Ingestion ] ──> [ Stage 02: Analysis (P1) ] ──> [ Stage 03: Questions (P2) ]
                                                                       │
[ Stage 05: Export ] <── [ Stage 04: Verification (P3) ] <─────────────┘
```

1. **Stage 01: Multi-Page Ingestion & Normalization**
   - Ingests lecture slide decks (PDF) and text notes (TXT).
   - Preserves exact page boundaries using `--- [Page N] ---` headers for precise downstream source attribution.
   - Robust encoding fallback hierarchy (UTF-8 → Latin-1 → CP1252) and deterministic edge-case rejection (scanned/image-only PDFs, 0-byte buffers, corrupt files).
2. **Stage 02: Structured Revision Extraction (Prompt 1)**
   - Synthesizes fragmented slides into clear conceptual sections.
   - Generates an Examinable Concept Matrix with explicit page citations (e.g., `[Page 1]`, `[Page 2]`).
   - Identifies mathematical formulas, definitions, and syllabus gaps requiring supplementary reading.
3. **Stage 03: Tiered Practice Exam Generation (Prompt 2)**
   - Generates configurable quantities (1–30, default 5) of tiered revision questions.
   - Cognitive tiering across **[Easy]** (definitional recall), **[Medium]** (conceptual application), and **[Hard]** (multi-step quantitative derivation).
   - **Exam Practice Mode**: Hides answer keys and full explanations inside a collapsible drawer to eliminate accidental spoilers during active recall practice.
4. **Stage 04: Adversarial Content Verification Audit (Prompt 3)**
   - Operates as an independent auditor evaluating P1 notes and P2 questions against raw lecture text as the single source of truth.
   - Cross-examines claims to detect unsupported statements, misattributed pages, and answer-key label contradictions.
   - Independently recalculates mathematical derivations from first principles.
   - Outputs a Swiss Brutalist **Verdict Board** (`PASS` / `PASS WITH WARNINGS` / `FAIL`) with interactive filter pills.
5. **Stage 05: Study Pack Assembly & Export**
   - Compiles notes, questions, answer keys, and verification logs into unified Markdown (`.md`) and plain text (`.txt`) packages.
   - Deterministic timestamped naming format: `LastHope_<filename>_StudyPack_<timestamp>.<ext>`.

---

## 3. Technology Stack

| Layer | Technology | Version | Role in Architecture |
| :--- | :--- | :--- | :--- |
| **Language** | Python | `>=3.10` | Core pipeline runtime and execution logic |
| **Frontend UI** | Streamlit | `>=1.38.0` | Reactive Swiss Brutalist editorial interface ("Red Pen" aesthetic) |
| **Document Ingestion** | PyMuPDF (`pymupdf`) | `>=1.24.0` | In-memory text extraction, coordinate inspection, page tagging |
| **LLM Inference** | Groq Cloud SDK (`groq`) | `>=0.11.0` | Low-latency inference via tested active runtime model `openai/gpt-oss-120b` |
| **Configuration** | python-dotenv | `>=1.0.0` | Secure environment variable management via local `.env` |

---

## 4. Three Prompt Components

The application coordinates three specialized prompt agents with independent temperature configurations:

```
prompts/
├── lecture_analyzer.py      # P1: Lecture Content Analyzer (Temp: 0.2)
├── question_generator.py    # P2: Revision Question Generator (Temp: 0.3)
├── content_verifier.py      # P3: Adversarial Content Verifier (Temp: 0.1)
└── versions/                # 9-version catalog (v1 tested live; v2 & v3 untested proposed refinements)
```

### P1: Lecture Content Analyzer (`prompts/lecture_analyzer.py`)
- **Role**: Academic revision specialist that extracts structured outlines, core definitions, and examinable formulas.
- **Temperature**: `0.2` (Low temperature for factual, grounded extraction).
- **Key Directive**: Every key concept and formula must cite its originating page using `[Page X]` tags. Gaps not covered in the lecture are explicitly marked as supplementary.

### P2: Revision Question Generator (`prompts/question_generator.py`)
- **Role**: Assessment designer that synthesizes high-yield practice questions.
- **Temperature**: `0.3` (Slightly relaxed for diverse question phrasing while preserving technical rigor).
- **Key Directive**: Questions are split into two decoupled sections: Part A (unspoilered questions with page references) and Part B (complete answer key with rationale and step-by-step arithmetic derivations).

### P3: Content Verification Assistant (`prompts/content_verifier.py`)
- **Role**: Independent adversarial fact-checker and mathematical auditor.
- **Temperature**: `0.1` (Minimum temperature for deterministic, skeptical auditing).
- **Key Directive**: The raw lecture text is the **only** ground truth. Never assumes a claim is true just because P1 and P2 agree. Recalculates all arithmetic and checks option-letter label consistency (e.g., catching when the explanation says 9 cycles but the letter says Option B: 8 cycles).

### Prompt Version Catalog (`prompts/versions/`)
The repository preserves nine prompt version files documenting the engineering process:
- **Tested Active Versions (v1)**: `P1_v1.txt`, `P2_v1.txt`, and `P3_v1.txt` were tested live on the Groq Cloud API; their genuine outputs and test matrices are preserved in `docs/milestone2/test-evidence/`.
- **Untested Proposed Refinements (v2 & v3)**: `P1_v2.txt`, `P1_v3.txt`, `P2_v2.txt`, `P2_v3.txt`, `P3_v2.txt`, and `P3_v3.txt` are proposed iterative refinements designed to address failure modes identified in v1 testing (e.g., negative boundary rules, two-pass arithmetic derivation, and JSON schema output). They remain untested proposals preserved for academic documentation.

---

## 5. Prerequisites & Installation

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- A valid Groq Cloud API Key ([console.groq.com/keys](https://console.groq.com/keys))

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hriday-thakur/LastHope.git
   cd LastHope
   ```

2. **Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (Command Prompt):**
     ```cmd
     python -m venv venv
     venv\Scripts\activate.bat
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Install version-constrained dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 6. Environment Configuration (`.env` vs `.env.example`)

LastHope manages configuration through environment variables loaded via `python-dotenv`.

### Git Rules & Secret Security:
- **`.env` (Private Secrets — Ignored by Git)**: Stores your actual private `GROQ_API_KEY`. The repository's [`.gitignore`](.gitignore#L2) explicitly ignores `.env` (`.gitignore:2:.env`) so credentials are never tracked, staged, or pushed to GitHub.
- **`.env.example` (Template — Tracked in Git)**: A safe configuration template committed to version control with placeholder values to show required environment keys without exposing secrets.

### Setup Instructions:

1. **Copy the example configuration file:**
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*

2. **Edit `.env` and fill in your actual Groq API credentials:**
   ```env
   # Your private Groq API Key from https://console.groq.com/keys
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here

   # Tested active runtime model
   GROQ_MODEL=openai/gpt-oss-120b
   ```

---

## 7. Running the Application

Launch the Streamlit interactive dashboard:

```bash
streamlit run app.py
```

The application will start on `http://localhost:8501`.

### Quickstart Revision Workflow:
1. Upload a lecture PDF (e.g., `CS301_Cache_Memory.pdf`) or plain text lecture note (`.txt`).
2. Review the document preview and word count metric.
3. Click **"Analyze Lecture"** to run Prompt 1.
4. Select the question count (default: 5) and click **"Generate Revision Questions"** to run Prompt 2.
5. Click **"Run Content Verification Audit"** to run Prompt 3 and inspect the Verdict Board.
6. Click **"Download Study Pack (.md)"** or **"Download Study Pack (.txt)"** in the Export Docket.

---

## 8. Running the Offline Test Suite

LastHope includes a comprehensive offline test suite in `test_document_parser.py` that validates all ingestion pipelines and edge cases with **zero external API calls**:

```bash
python test_document_parser.py
```

### Coverage (15/15 Tests Passed):
- Whitespace cleaning and carriage return normalization
- Multi-page in-memory PDF extraction and page boundary tagging
- In-memory binary stream / `io.BytesIO` buffer parsing
- UTF-8, Latin-1 (accented characters), and CP1252 (Euro/Pound currency) encoding fallbacks
- Edge Case: Scanned / image-only PDF detection (`EmptyDocumentError`)
- Edge Case: 0-byte empty file handling (`EmptyDocumentError`)
- Edge Case: Corrupt PDF binary handling (`DocumentParsingError`)
- Edge Case: Unsupported file format rejection (`UnsupportedFormatError`)

*(Note: Live Groq API end-to-end tests require network access and valid credentials; their execution evidence is recorded in `docs/milestone2/test-evidence/test-report.md`).*

---

## 9. Repository Structure

```
LastHope/
├── .env.example                               # Safe template for Groq credentials (tracked)
├── .gitignore                                 # Excludes .env, __pycache__, and temp files
├── .streamlit/
│   └── config.toml                            # Swiss Brutalist theme configuration
├── app.py                                     # Main reactive Streamlit application
├── CHANGELOG.md                               # Project development and milestone history
├── README.md                                  # Repository overview and instructions
├── requirements.txt                           # Version-constrained dependencies
├── test_document_parser.py                    # 15/15 unit test suite (offline)
├── prompts/
│   ├── __init__.py
│   ├── lecture_analyzer.py                    # Prompt 1 execution harness (Temp: 0.2)
│   ├── question_generator.py                  # Prompt 2 execution harness (Temp: 0.3)
│   ├── content_verifier.py                    # Prompt 3 execution harness (Temp: 0.1)
│   └── versions/                              # 9-version catalog (v1 tested; v2/v3 untested proposed refinements)
│       ├── P1_v1.txt, P1_v2.txt, P1_v3.txt
│       ├── P2_v1.txt, P2_v2.txt, P2_v3.txt
│       └── P3_v1.txt, P3_v2.txt, P3_v3.txt
├── ui/
│   ├── __init__.py
│   ├── theme.py                               # Brutalist theme injector
│   ├── components.py                          # Modular UI cards, badges, verdict boards
│   └── styles.css                             # Swiss editorial typography and CSS rules
├── utils/
│   ├── __init__.py
│   ├── document_parser.py                     # Multi-page parser with page preservation
│   └── groq_client.py                         # Groq Cloud SDK wrapper and error hierarchy
└── docs/
    └── milestone2/
        ├── main-report/
        │   ├── main-report.md                 # Primary Milestone 2 report (Markdown)
        │   └── LastHope_Milestone2_Main_Report.pdf  # 14-page university submission PDF
        ├── supporting-report/
        │   ├── technical-report.md            # Extended technical report (Markdown)
        │   └── LastHope_Technical_Report_Milestone2.pdf # 10-page technical PDF
        ├── prompt-iterations/
        │   ├── iteration-log.md               # Empirical prompt refinement log
        │   ├── P1-prompt-sheet.md             # Complete P1 specification sheet
        │   ├── P2-prompt-sheet.md             # Complete P2 specification sheet
        │   └── P3-prompt-sheet.md             # Complete P3 specification sheet
        ├── test-evidence/
        │   ├── test-report.md                 # 16-case empirical test matrix report
        │   ├── test_document_parser.py        # Archived parser unit test suite
        │   ├── test_groq_client.py            # API client integration test
        │   ├── test_app_workflow.py           # 5-stage pipeline integration test
        │   ├── test_lecture_analyzer.py       # P1 standalone runner
        │   ├── test_question_generator.py     # P2 standalone runner
        │   ├── test_content_verifier.py       # P3 standalone runner
        │   ├── test_p1_output.md              # Live Groq API P1 output
        │   ├── test_p2_output.md              # Live Groq API P2 output
        │   ├── test_p3_output.md              # Live Groq API P3 output
        │   ├── LastHope_sample_lecture_StudyPack_20261122_1930.md  # Downloaded study pack
        │   └── LastHope_sample_lecture_StudyPack_20261122_1930.txt # Downloaded study pack
        └── screenshots/                       # 6 genuine browser evidence captures
            ├── brutalist_verified_browser.png
            ├── demo_verified_browser.png
            ├── final_step_16.png
            ├── final_step_41.png
            ├── final_step_43.png
            └── final_step_51.png
```

---

## 10. Milestone 2 Submission Documentation

| Document | Format | Description | File Link |
| :--- | :---: | :--- | :--- |
| **Milestone 2 Main Report** | PDF | 14-page primary report with seven mandated sections, screenflow diagram, prompts, test matrix, and screenshots | [LastHope_Milestone2_Main_Report.pdf](docs/milestone2/main-report/LastHope_Milestone2_Main_Report.pdf) |
| **Milestone 2 Main Report** | Markdown | Full Markdown source of the primary report | [main-report.md](docs/milestone2/main-report/main-report.md) |
| **Supporting Technical Report** | PDF | 10-page academic technical report with multi-layer system architecture diagram | [LastHope_Technical_Report_Milestone2.pdf](docs/milestone2/supporting-report/LastHope_Technical_Report_Milestone2.pdf) |
| **Supporting Technical Report** | Markdown | Full Markdown source of the technical report | [technical-report.md](docs/milestone2/supporting-report/technical-report.md) |
| **Prompt Iteration Log** | Markdown | Empirical evolution log across tested v1 implementations and untested proposed refinements (v2, v3) for P1, P2, and P3 | [iteration-log.md](docs/milestone2/prompt-iterations/iteration-log.md) |
| **P1 Prompt Specification** | Markdown | Formal engineering sheet for Lecture Content Analyzer | [P1-prompt-sheet.md](docs/milestone2/prompt-iterations/P1-prompt-sheet.md) |
| **P2 Prompt Specification** | Markdown | Formal engineering sheet for Revision Question Generator | [P2-prompt-sheet.md](docs/milestone2/prompt-iterations/P2-prompt-sheet.md) |
| **P3 Prompt Specification** | Markdown | Formal engineering sheet for Content Verification Assistant | [P3-prompt-sheet.md](docs/milestone2/prompt-iterations/P3-prompt-sheet.md) |
| **Test Matrix & Evidence Report** | Markdown | Empirical 16-case test suite report with edge case coverage | [test-report.md](docs/milestone2/test-evidence/test-report.md) |

---

## 11. Academic Metadata & Team Details

- **Project Title:** LastHope — AI Lecture-to-Revision Assistant
- **Team Name:** Temperature 0
- **Team ID:** PE-B65-36
- **Course Code & Title:** SCSE4041 — Prompt Engineering
- **Batch / Section / Group:** Batch 80 / Section 40 / Group 20
- **Faculty Guide / Mentor:** Dr. Sonal Kukreja
- **Institution:** School of Computer Science Engineering & Technology, Bennett University
- **Submission Date:** 22 November 2026

### Team Members & Contributions

| Member Name | Enrollment ID | Contribution |
| :--- | :--- | :---: |
| **Hriday Thakur** | `S24CSEU2000` | **33.34%** |
| **Keshav Kumar** | `S24CSEU1998` | **33.33%** |
| **Rudransh Jiyala** | `S24CSEU2013` | **33.33%** |
| **Total** | — | **100.00%** |

*Note: Team members operated collaboratively across prompt design, verification architecture, and evaluation. Shared task allocation details remain subject to internal team confirmation.*
