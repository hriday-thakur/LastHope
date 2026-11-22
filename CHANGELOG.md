# Changelog — LastHope

All notable development changes, architectural implementations, and documentation milestones for **LastHope** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Milestone 2] - 2026-11-22

### Added

#### Document Parsing & Ingestion Subsystem (`utils/document_parser.py`)
- In-memory PDF text extraction using PyMuPDF (`pymupdf`) with page-number boundary tagging (`--- [Page N] ---`).
- Multi-encoding plain text parser with automatic fallback hierarchy (`UTF-8` → `Latin-1` → `CP1252`) supporting European accents and currency symbols (`€`, `£`).
- Whitespace cleaning and carriage return normalization (`\r\n` to `\n`, deduplication of excessive line breaks).
- Custom exception hierarchy: `DocumentParsingError`, `EmptyDocumentError`, and `UnsupportedFormatError`.
- Deterministic edge-case detection and rejection:
  - Scanned / image-only PDFs with no extractable text.
  - 0-byte empty file buffers.
  - Corrupt or invalid PDF binaries.
  - Whitespace-only text files.
  - Unsupported file extensions (e.g., `.docx`).

#### LLM Inference Client (`utils/groq_client.py`)
- Official Groq Cloud SDK wrapper (`groq`) configured and tested with runtime model `openai/gpt-oss-120b`.
- Environment variable configuration loader via `python-dotenv`.
- Clear separation between `.env` (private active credentials, excluded by `.gitignore`) and `.env.example` (tracked safe template with placeholder variables).
- Dedicated client exception hierarchy: `GroqClientError`, `MissingAPIKeyError`, `AuthenticationError`, `RateLimitError`, and `ModelNotFoundError`.
- Deterministic per-module temperature controls (P1: `0.2`, P2: `0.3`, P3: `0.1`).
- Transient network resilience with `max_retries=1` and explicit timeout overrides.

#### Core Prompt Architecture (`prompts/`)
- **Prompt 1 (`prompts/lecture_analyzer.py`)**: Academic lecture analyzer producing structured revision notes, an Examinable Concept Matrix, definitional tables, and syllabus gap analysis with mandatory `[Page X]` citations.
- **Prompt 2 (`prompts/question_generator.py`)**: Tiered revision assessment designer generating configurable questions across cognitive tiers (`[Easy]`, `[Medium]`, `[Hard]`), with separated Part A (practice mode) and Part B (answer key with step-by-step arithmetic).
- **Prompt 3 (`prompts/content_verifier.py`)**: Adversarial fact-checking auditor cross-examining P1 and P2 against raw lecture text as the sole ground truth, detecting outside hallucinations, recomputing calculations from first principles, and verifying answer-key option-letter alignment.
- **Archived Prompt Catalog (`prompts/versions/`)**: Nine versioned prompt files documenting iteration history:
  - `P1_v1.txt` (Active/Tested on Groq API), `P1_v2.txt` (Untested proposed refinement: negative boundary rules), `P1_v3.txt` (Untested proposed refinement: dual gap categorization).
  - `P2_v1.txt` (Active/Tested on Groq API), `P2_v2.txt` (Untested proposed refinement: two-pass derivation), `P2_v3.txt` (Untested proposed refinement: 4-step scratchpad derivation).
  - `P3_v1.txt` (Active/Tested on Groq API), `P3_v2.txt` (Untested proposed refinement: dual audit tables), `P3_v3.txt` (Untested proposed refinement: JSON schema matrix).

#### Swiss Brutalist User Interface (`ui/` & `app.py`)
- Reactive Streamlit frontend structured across 5 distinct pipeline stages: Ingestion, Analysis, Questions, Verification, and Export.
- Swiss Brutalist editorial design system (`ui/styles.css`, `ui/theme.py`, `ui/components.py`) featuring:
  - Cream canvas (`#F3F0E8`), dark slate text (`#121212`), and "Red Pen" editorial accent (`#D9381E`).
  - High-contrast card widgets, monospaced metadata badges, and hairline borders.
  - Dynamic **Verdict Board** with status pills (`PASS`, `PASS WITH WARNINGS`, `FAIL`) and interactive severity filters (`All`, `Flagged Only`, `Grounded Only`).
  - **Exam Practice Mode**: Anti-spoiler drawer hiding answers and derivations during self-testing.
  - **Study Pack Export Docket**: Manifest summary card with one-click `.md` and `.txt` bundle downloads.

#### Test Suite & Empirical Evidence (`docs/milestone2/test-evidence/`)
- 15/15 unit test suite for document parser and edge cases (`test_document_parser.py`), executable offline with zero API calls.
- 16-case empirical test matrix (`test-report.md`) covering unit parsing, prompt execution, adversarial verification, UI persistence, and Study Pack export.
- Live execution output logs from Groq Cloud API: `test_p1_output.md`, `test_p2_output.md`, `test_p3_output.md` (all using `openai/gpt-oss-120b`).
- Generated and downloaded sample study pack bundles: `LastHope_sample_lecture_StudyPack_20261122_1930.md` and `.txt`.
- 6 genuine browser verification screenshots in `docs/milestone2/screenshots/`.

#### Academic Milestone 2 Documentation (`docs/milestone2/`)
- **Primary Milestone 2 Report**: 14-page PDF and Markdown source covering all seven mandated sections, screenflow diagram, prompt sheets, test matrix, and contribution table.
- **Supporting Technical Report**: 10-page academic technical report with multi-layer system architecture diagram and prompt engineering analysis.
- **Prompt Iteration Log (`iteration-log.md`)**: Empirical rationale, observed failure modes, and proposed refinements for all 9 prompt versions.
- **Prompt Sheets (`P1-prompt-sheet.md`, `P2-prompt-sheet.md`, `P3-prompt-sheet.md`)**: Comprehensive specification sheets with full system and user templates, variable definitions, and model hyperparameters.

---

## [Initial Setup] - 2026-11-22

### Added
- Initial project repository creation on branch `main` (`581573b`).
- Base `README.md` introducing the project vision.
