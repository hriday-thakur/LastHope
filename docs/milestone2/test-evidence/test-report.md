# Milestone 2: Comprehensive Test Report & Verification Evidence
**Project:** LastHope — AI Lecture-to-Revision Assistant  
**Course:** SCSE4041 Mini Project (Milestone 2)  
**Date:** November 2026  
**Status:** Complete & Verified Against Empirical Evidence  

---

## 1. Testing Summary & Quality Assurance Strategy

The quality assurance methodology for LastHope Milestone 2 follows a multi-tiered verification hierarchy designed to ensure high academic accuracy, robust error tolerance, and zero silent failures:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Tier 4: Browser-Level Verification                   │
│   (Live Streamlit UI, DOM interactions, downloads, session state)      │
├────────────────────────────────────────────────────────────────────────┤
│                   Tier 3: End-to-End Workflow Pipeline                 │
│   (Intake ──▶ P1 Analysis ──▶ P2 Questions ──▶ P3 Audit ──▶ Export)     │
├────────────────────────────────────────────────────────────────────────┤
│                   Tier 2: Live LLM Prompt Evaluations                  │
│   (Groq gpt-oss-120b: P1 Revision Notes, P2 Practice Qs, P3 Auditor)   │
├────────────────────────────────────────────────────────────────────────┤
│                   Tier 1: Unit & Edge-Case Test Suites                 │
│   (Document parser, PyMuPDF, encodings, Groq client exceptions)        │
└────────────────────────────────────────────────────────────────────────┘
```

### Key Quantitative Verification Metrics:
- **Document Parser Test Suite ([`test_document_parser.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py)):** **15 / 15 Tests Passed (100%)**, covering multi-page extraction, whitespace normalization, CP1252/Latin-1 encoding fallbacks, and 5 distinct failure edge cases.
- **Groq Client Integration Suite ([`test_groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_groq_client.py)):** **3 / 3 Tests Passed (100%)**, verifying configuration loading, live text completion, and custom `ModelNotFoundError` interception.
- **End-to-End Application Pipeline Suite ([`test_app_workflow.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_app_workflow.py)):** **5 / 5 Pipeline Stages Verified (100%)**, proving end-to-end data propagation from parsed input through P1, P2, P3, and conditional study-pack export.
- **Live LLM Audit Verification:** 3 genuine outputs recorded ([`test_p1_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p1_output.md), [`test_p2_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p2_output.md), [`test_p3_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md)), proving that P3 independently detected arithmetic discrepancies (Q7b) and label contradictions (Q4) in P2.
- **Browser-Level Verification:** Genuine UI interaction verified across all 5 tabs on `http://localhost:8501`, confirmed by 6 screenshot artifacts and 2 downloaded study-pack files (`.md` and `.txt`).

---

## 2. Comprehensive Test Case Matrix

The following matrix documents 16 distinct test cases executed across the LastHope system. Every actual result is grounded in recorded script logs, saved markdown outputs, or genuine browser evidence.

| Test ID | Test Tier | Component | Input / Scenario | Expected Behavior | Actual Observed Result | Status | Primary Evidence Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Unit | Parser | Excessive blank lines, tabs, and Windows `\r\n` line endings. | Normalize multiple blank lines to at most two `\n\n`, strip trailing line whitespace. | Clean text returned with exact formatting: `"Line 1\n\nLine 2\n\nLine 3"`. | **PASS** | [`test_document_parser.py#L75-L80`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L75-L80) |
| **TC-02** | Unit | Parser | Standard 2-page in-memory lecture PDF created via PyMuPDF. | Extract text from both pages, preserve `--- [Page 1] ---` and `--- [Page 2] ---` markers, compute page & word counts. | Total pages = 2, word count > 20, both page delimiters preserved with lecture text. | **PASS** | [`test_document_parser.py#L81-L88`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L81-L88) |
| **TC-03** | Unit | Parser | File-like `io.BytesIO` binary stream of a valid PDF. | Successfully parse binary stream buffer without requiring a physical disk path. | Total pages = 2, text correctly extracted without I/O exceptions. | **PASS** | [`test_document_parser.py#L89-L93`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L89-L93) |
| **TC-04** | Unit | Parser | Standard UTF-8 encoded text document (`notes.txt`). | Parse as 1-page document with `--- [Page 1] ---` marker, compute word count. | Parsed successfully: 1 page, exact word count = 13 words. | **PASS** | [`test_document_parser.py#L94-L99`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L94-L99) |
| **TC-05** | Unit | Parser | Latin-1 encoded text containing French accents and pound symbol (`£`). | Gracefully fall back from UTF-8 to Latin-1 and decode text cleanly. | Accented characters decoded without error: `"Thème: Intelligence Artificielle..."`. | **PASS** | [`test_document_parser.py#L100-L104`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L100-L104) |
| **TC-06** | Unit | Parser | Windows-1252 (CP1252) encoded text containing Euro symbol (`€` / `0x80`). | Detect CP1252 before Latin-1 fallback to prevent Euro character corruption. | Extracted text correctly preserved `"50€ TTC"`. | **PASS** | [`test_document_parser.py#L105-L109`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L105-L109) |
| **TC-07** | **Edge Case** | Parser | Scanned / Image-only 2-page PDF containing zero extractable text layer. | Detect absence of text, raise `EmptyDocumentError` advising user that OCR is required. | Raised `EmptyDocumentError: "PDF contains 2 page(s) but no extractable text layer..."`. | **PASS** | [`test_document_parser.py#L110-L117`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L110-L117) |
| **TC-08** | **Edge Case** | Parser | Completely empty 0-byte file buffer (`b""`). | Intercept 0-byte upload and raise `EmptyDocumentError` before invoking PyMuPDF. | Raised `EmptyDocumentError: "The uploaded file 'empty.pdf' is empty (0 bytes)."`. | **PASS** | [`test_document_parser.py#L118-L124`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L118-L124) |
| **TC-09** | **Edge Case** | Parser | Corrupt PDF header (`%PDF-1.4 corrupt junk content...`). | Intercept PyMuPDF parsing failure and wrap into `DocumentParsingError`. | Raised `DocumentParsingError: "Failed to parse PDF document 'corrupt.pdf'..."`. | **PASS** | [`test_document_parser.py#L125-L131`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L125-L131) |
| **TC-10** | **Edge Case** | Parser | Text file consisting solely of whitespace, tabs, and newlines (`b" \n\n\t \n "`). | Strip whitespace, detect zero substantive content, and raise `EmptyDocumentError`. | Raised `EmptyDocumentError: "The text document 'blank.txt' contains no readable text."`. | **PASS** | [`test_document_parser.py#L132-L138`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L132-L138) |
| **TC-11** | **Edge Case** | Parser | Unsupported file type (e.g., Word document `document.docx` or zip header). | Validate extension and reject unsupported format with `UnsupportedFormatError`. | Raised `UnsupportedFormatError: "Unsupported file format '.docx'. Supported formats: .pdf, .txt"`. | **PASS** | [`test_document_parser.py#L139-L145`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_document_parser.py#L139-L145) |
| **TC-12** | Integration | Groq Client | API request specifying an invalid or nonexistent model name (`invalid-model-xyz`). | Catch Groq `NotFoundError` and raise structured `ModelNotFoundError`. | Caught `ModelNotFoundError: Model 'invalid-model-xyz' was not found...`. | **PASS** | [`test_groq_client.py#L56-L71`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_groq_client.py#L56-L71) |
| **TC-13** | Live LLM | P1 Analyzer | 2-page CS301 Cache Memory lecture text ingested into `analyze_lecture()`. | Generate 5-part structured Markdown notes with `[Page X]` attributions and gap detection. | Generated 83-line structured notes; correctly cited `[Page 1]` and `[Page 2]`; identified deferred cache coherence. | **PASS** | [`test_p1_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p1_output.md) |
| **TC-14** | Live LLM | P2 Generator | Ingest lecture text and P1 notes into `generate_questions(num_questions=10)`. | Generate tiered MCQs, Short-Answer, and Conceptual questions with unspoilered answer key. | Generated 8 practice questions across Easy/Medium/Hard tiers; separated into Part 1 (Questions) and Part 2 (Answers). | **PASS** | [`test_p2_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p2_output.md) |
| **TC-15** | Live LLM | P3 Verifier | Cross-examine P1 and P2 against original lecture text in `verify_content()`. | Audit claims, check calculations step by step, detect answer key bugs, assign status. | Correctly detected P2 Q4 label contradiction and Q7b hit-cycle arithmetic error; assigned **PASS WITH WARNINGS**. | **PASS** | [`test_p3_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md) |
| **TC-16** | Browser UI | Full App | Upload `sample_lecture.txt` on `localhost:8501`, execute P1, P2, P3, and download Study Pack. | Render Brutalist UI, preserve session state without re-querying Groq API, export `.md` and `.txt` bundles. | Genuine browser download captured; study packs verified on disk (20,154 bytes each); UI state persisted across tabs. | **PASS** | [`LastHope_sample_lecture_StudyPack_20261122_1930.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/LastHope_sample_lecture_StudyPack_20261122_1930.md) & [`brutalist_verified_browser.png`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/screenshots/brutalist_verified_browser.png) |

---

## 3. Deep-Dive: Edge-Case Handling & Robustness

The system's fault-tolerance was tested against five critical edge cases. Each scenario is handled deterministically by custom exceptions defined in [`utils/document_parser.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/document_parser.py) and caught cleanly in [`app.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/app.py):

### Edge Case 1: Scanned / Image-Only PDF (No Text Layer)
- **Scenario:** A user uploads a multi-page PDF created by scanning physical lecture handouts without running OCR. The PDF container has valid pages, but PyMuPDF extracts 0 characters.
- **Handling:** Rather than proceeding silently to the LLM (which would cause hallucinations on empty input) or crashing, `parse_pdf()` detects that cumulative extracted text is empty and raises `EmptyDocumentError`:
  ```
  EmptyDocumentError: PDF contains 2 page(s) but no extractable text layer.
  The file appears to be a scanned document or image-only PDF. OCR is required before analysis.
  ```
- **UI Behavior:** In `app.py`, this is caught and rendered as an editorial error banner: `DOCUMENT EMPTY: ...`, preventing wasted API calls.

### Edge Case 2: Zero-Byte & Whitespace-Only Documents
- **Scenario:** An empty 0-byte file or a text document containing only spaces, tabs, and carriage returns (`b"   \n\n\t  \n  "`).
- **Handling:** Intercepted immediately before file parsing. `parse_document()` verifies file length > 0, and `clean_text()` strips non-substantive whitespace. If length remains 0, `EmptyDocumentError` is raised.

### Edge Case 3: Corrupted File Structure
- **Scenario:** A truncated or malformed PDF file where the PDF header or cross-reference table is damaged.
- **Handling:** PyMuPDF exceptions (`pymupdf.FileDataError`) are intercepted by `parse_pdf()` and re-raised as `DocumentParsingError`, providing clear remediation instructions without dumping Python tracebacks to the user.

### Edge Case 4: Non-UTF8 Text Encodings (CP1252 and Latin-1)
- **Scenario:** Text files saved on legacy Windows machines or European keyboards containing special symbols (e.g., Euro currency symbol `€` at byte `0x80` or French accents `é`, `è`).
- **Handling:** The parser executes an ordered multi-encoding fallback:
  `encodings = ["utf-8", "utf-8-sig", "cp1252", "iso-8859-1", "latin-1"]`
  Prioritizing `cp1252` before `latin-1` ensures that single-byte characters in the `0x80-0x9F` range (such as `€`) are decoded accurately.

### Edge Case 5: Unsupported Document Formats
- **Scenario:** A user uploads a Word document (`.docx`), spreadsheet (`.xlsx`), or image (`.png`).
- **Handling:** Validates file extension against `ALLOWED_EXTENSIONS = {".pdf", ".txt"}` and raises `UnsupportedFormatError` with a list of permitted file extensions.

---

## 4. Verification of Live LLM Testing & Verification Logic

Live LLM evaluations were conducted using the Groq API running `openai/gpt-oss-120b`. The testing sequence validated the cooperative verification pipeline:

```
┌────────────────────────────────┐
│  Original Lecture Text (Truth) │
└───────┬────────────────┬───────┘
        │                │
        ▼                ▼
   ┌─────────┐      ┌─────────┐
   │ P1:     │      │ P2:     │
   │ Analyzer│      │ Question│
   │ Notes   │      │ Gen     │
   └────┬────┘      └────┬────┘
        │                │
        └───────┬────────┘
                ▼
        ┌──────────────┐
        │ P3: Content  │ ──▶ Cross-examines P1 & P2 against Source
        │ Verification │ ──▶ Recomputes arithmetic from first principles
        │ Assistant    │ ──▶ Detects answer-key label mismatches
        └──────────────┘
```

### Empirical Audit Results from `test_p3_output.md`:
1. **Mathematical Audit Verification:**
   - In P2 Question 4, the model computed $\text{AMAT} = 2 + (0.04 \times 120) = 6.8\text{ cycles}$ (Option A). However, the answer key wrote `Correct Answer: B` before self-correcting in prose. P3 audited this and flagged a **Label Contradiction**.
   - In P2 Question 7(b), the miss rate was halved from 2% to 1%. P2 updated miss cycles ($0.8 \times 10^9$) but left hit cycles unchanged at $2.94 \times 10^9$, arriving at $3.74 \times 10^9$. P3 independently recalculated from first principles:
     $$\text{Hits} = 10^9 - 10^7 = 9.9 \times 10^8 \implies \text{Hit Cycles} = 9.9 \times 10^8 \times 3 = 2.97 \times 10^9\text{ cycles}$$
     $$\text{Total Cycles} = 2.97 \times 10^9 + 0.8 \times 10^9 = 3.77 \times 10^9\text{ cycles}$$
     P3 successfully flagged the 30-million-cycle calculation omission.
2. **Factual Grounding Audit:**
   - P3 verified 10 core concepts as fully grounded with page citations (SRAM vs. DRAM, temporal/spatial locality, AMAT formula, 3 C's of misses).
   - P3 correctly flagged that P2 Question 3 (cache associativity) and Question 8 (sequential traversal miss dominance) were outside the lecture scope.
   - P3 assigned an overall verdict of **PASS WITH WARNINGS**, ensuring students are alerted to unverified items before high-stakes exam revision.

---

## 5. End-to-End Workflow Pipeline Verification

The automated integration script [`test_app_workflow.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_app_workflow.py) simulates the entire application pipeline programmatically without UI overhead:

1. **Step 1 (Document Parser):** Successfully parsed sample BST lecture text (1 page, 142 words).
2. **Step 2 (P1 Analysis):** Invoked `analyze_lecture()`, received structured revision notes covering BST properties, AVL trees, and rotation rules.
3. **Step 3 (P2 Practice Questions):** Invoked `generate_questions(num_questions=5)`, generating 5 balanced questions with an unspoilered answer key.
4. **Step 4 (P3 Content Verification):** Invoked `verify_content()`, produced audit report with formal review status and academic disclaimer.
5. **Step 5 (Study Pack Assembly Logic):** Verified export assembly logic under two operational conditions:
   - *Condition A (Without P3):* Assembly contains only Part I (P1) and Part II (P2); correctly excludes Part III.
   - *Condition B (With P3):* Assembly contains all three parts (P1, P2, and Part III audit); total size verified at >20 KB.

---

## 6. Browser-Level Verification & Export Evidence

Live browser testing was conducted against the running Streamlit server (`http://localhost:8501`) using automated browser automation, verifying frontend behavior, styling, and file downloads:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Browser Evidence Artifacts Archived in Repository:                      │
│                                                                         │
│ 1. docs/milestone2/screenshots/brutalist_verified_browser.png           │
│    - Shows Stage 04 Content Audit with brutalist VERDICT BOARD HEADER:  │
│      "STATUS: PASS WITH WARNINGS", 10 Grounded, 1 Warnings, 4 Flagged.  │
│                                                                         │
│ 2. docs/milestone2/screenshots/demo_verified_browser.png                │
│    - Shows Stage 03 Practice Questions in active Exam Mode.             │
│                                                                         │
│ 3. docs/milestone2/screenshots/final_step_16.png                        │
│    - Shows Stage 01 Document Intake Receipt for sample_lecture.txt.     │
│                                                                         │
│ 4. docs/milestone2/screenshots/final_step_41.png                        │
│    - Shows Stage 02 Revision Notes generated with Page 1/Page 2 tags.   │
│                                                                         │
│ 5. docs/milestone2/screenshots/final_step_51.png                        │
│    - Shows Stage 05 Export Study Pack docket with live download buttons.│
│                                                                         │
│ 6. docs/milestone2/test-evidence/LastHope_sample_lecture_StudyPack_*.md │
│    - Genuine downloaded 20,154-byte Markdown study pack bundle.         │
│                                                                         │
│ 7. docs/milestone2/test-evidence/LastHope_sample_lecture_StudyPack_*.txt│
│    - Genuine downloaded 20,154-byte Plaintext study pack bundle.        │
└─────────────────────────────────────────────────────────────────────────┘
```

### Verified Browser Behaviors:
- **Zero Duplicate API Calls:** Tab navigation between Stages 01, 02, 03, 04, and 05 does not re-trigger API requests or erase previously generated state.
- **Exam Mode Toggle:** Interacting with the "EXAM MODE" toggle dynamically hides the answer key into an unspoilered drawer without wiping session state.
- **Genuine Download Execution:** Clicking `DOWNLOAD STUDY PACK (.MD)` and `DOWNLOAD STUDY PACK (.TXT)` successfully delivered the 20,154-byte composite bundle containing the complete P1 notes, P2 practice questions, and P3 audit report.

---

## 7. Known Limitations & Unverified Behaviors

To maintain full transparency, the following boundaries and unverified behaviors are explicitly noted:

| Dimension | Current Verification Status | Operational Limitation / Reason |
| :--- | :--- | :--- |
| **Multi-File Batch Upload** | **Unverified / Not Supported** | The application explicitly enforces single-file upload (`st.file_uploader(accept_multiple_files=False)`). Ingesting multiple files simultaneously was not tested. |
| **Optical Character Recognition (OCR)** | **Verified Rejection** | The system detects scanned image-only PDFs and raises `EmptyDocumentError`, but it does *not* perform OCR itself. Scanned PDFs must be pre-processed with external OCR tools. |
| **Prompt Iterations v2 & v3** | **Untested Design Proposals** | Versions 2.0 and 3.0 in `prompts/versions/` were formulated based on observed errors, but remain untested against live API calls in Milestone 2 to avoid fabricating performance claims. |
| **Ultra-Large Documents (>100 Pages)** | **Unverified** | Tests were conducted on typical lecture decks (2–10 pages). Documents exceeding 100 pages may approach model context limits and have not been benchmarked. |
