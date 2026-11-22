# Prompt Sheet: Prompt 1 (P1) — Lecture Content Analyzer
**Project:** LastHope — AI Lecture-to-Revision Assistant  
**Pipeline Stage:** Stage 02 / 05 (Lecture Analysis & Revision Notes)  
**Implementation Source:** [`prompts/lecture_analyzer.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/lecture_analyzer.py)  
**Client Wrapper:** [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py)  
**Version Documented:** Implemented Baseline (v1.0)  

---

## 1. Prompt Name and Purpose

- **Identifier:** `Prompt 1 (P1): Lecture Content Analyzer`
- **Primary Function:** Ingests raw, page-annotated text extracted from lecture slides or lecture notes (PDF or TXT formats) and transforms it into structured, academically rigorous revision notes.
- **Specific Objectives:**
  - Synthesize a high-level executive overview of the lecture scope and objectives.
  - Produce a topic-by-topic conceptual breakdown citing exact source pages (`[Page X]`).
  - Catalog key terminology, definitions, and formulas without altering original notations.
  - Formulate high-yield revision takeaways for exam preparation.
  - Explicitly identify ambiguities, incomplete slides, and deferred topics without hallucinating unmentioned concepts.

---

## 2. Application Workflow Integration

In the LastHope Streamlit application ([`app.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/app.py)), P1 operates at **Stage 02 (Tab 2: Revision Notes)**:

```
[Stage 01: Intake & Parse] ──▶ st.session_state.parsed_doc
                                     │
                                     ▼
                      [User clicks: "GENERATE REVISION NOTES →"]
                                     │
                                     ▼
                       analyze_lecture(extracted_text)
                                     │
                                     ▼
[Stage 02: Revision Notes] ──▶ st.session_state.p1_analysis
                                     │
             ┌───────────────────────┴───────────────────────┐
             ▼                                               ▼
[Stage 03: Practice Questions (P2)]          [Stage 05: Export Study Pack]
```

- **Trigger:** The user navigates to Tab 2 and clicks the `🔍 GENERATE REVISION NOTES →` action button.
- **Prerequisite:** Stage 01 document intake must be complete (`st.session_state.parsed_doc is not None`).
- **State Updates:** Upon successful completion, the raw Markdown output is stored in `st.session_state.p1_analysis`. Downstream stages (P2 and P3) are invalidated (`None`) to maintain end-to-end data consistency if a new lecture analysis is run.

---

## 3. Actual System Prompt

The complete, verbatim system prompt implemented in [`prompts/lecture_analyzer.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/lecture_analyzer.py) (`P1_SYSTEM_PROMPT`):

```markdown
You are an expert academic lecture analyst and revision assistant.
Your job is to analyze extracted lecture notes and slide decks to produce structured, accurate, and student-friendly revision notes.

### Core Directives:
1. Strict Factual Grounding: Rely strictly and solely on the provided lecture text. Do not invent facts, introduce unsupported external assumptions, or hallucinate concepts not present in the input.
2. Technical Accuracy: Preserve all original technical terms, formula names, algorithm names, and notations verbatim.
3. Clarity for Students: Explain terse or difficult concepts in clear, accessible academic language without changing or oversimplifying their technical meaning.
4. Page Attribution: The lecture text contains page markers in the format `--- [Page X] ---`. You must cite these page numbers (e.g., `[Page 1]`, `[Pages 2-3]`) whenever referencing specific definitions, topics, or formulas.
5. Explicit Gaps & Ambiguities: If a note or slide is incomplete, lacks context, contains an undefined variable, or is ambiguous, explicitly flag it under "Topics Needing Clarification" rather than guessing.
6. Structured Markdown Output: Format your output in clean, professional GitHub-flavored Markdown following the exact required sections below.

### Output Structure:
# 📚 Lecture Revision Notes: [Topic Title]

## 1. Executive Overview
- High-level summary of the lecture scope and primary objectives.
- Estimated source coverage (e.g., Pages 1 to N).

## 2. Topic-by-Topic Breakdown
For each distinct topic or subtopic covered in the lecture:
### [Topic Name] *(Source: [Page X])*
- **Core Concept**: Student-friendly explanation grounded strictly in the text.
- **Key Details & Mechanisms**: Bullet points explaining how it functions, properties, or trade-offs.
- **Formulas / Algorithms / Rules** (if present): Stated with exact notation from the text.

## 3. Key Terminology & Definitions
| Term / Concept | Definition & Explanation (Grounded in Lecture) | Source Page |
| :--- | :--- | :--- |
| ... | ... | [Page X] |

## 4. High-Yield Revision Takeaways
- Top 3 to 5 critical takeaways essential for exam revision or conceptual mastery.

## 5. Topics Needing Clarification & Potential Gaps
- Any points in the lecture text that were incomplete, tersely stated without full context, or suggested questions the student should clarify with their professor.
```

---

## 4. Actual User Prompt & Dynamic Population

The complete user prompt template implemented in [`prompts/lecture_analyzer.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/lecture_analyzer.py) (`P1_USER_PROMPT_TEMPLATE`):

```markdown
Please analyze the following extracted lecture material and generate the complete structured revision notes according to your instructions.

--- BEGIN LECTURE MATERIAL ---
{lecture_text}
--- END LECTURE MATERIAL ---
```

### Dynamic Construction Logic:
In `prompts/lecture_analyzer.py`, the user prompt is constructed by:
```python
def format_p1_user_prompt(lecture_text: str) -> str:
    if not lecture_text or not lecture_text.strip():
        raise ValueError("Lecture text cannot be empty.")
    return P1_USER_PROMPT_TEMPLATE.format(lecture_text=lecture_text.strip())
```
In `app.py`, this is populated directly from the parsed document:
```python
p1_result = analyze_lecture(
    st.session_state.parsed_doc.extracted_text,
    timeout=120.0,
)
```

---

## 5. Prompt Variable Specification

| Variable Name | Type | Injected By | Validation / Population Logic | Description |
| :--- | :--- | :--- | :--- | :--- |
| `{lecture_text}` | `str` | `app.py` via `format_p1_user_prompt` | Pre-processed by `utils/document_parser.py`. Validated non-empty (`not lecture_text.strip()`). Contains normalized whitespace and page delimiters `--- [Page X] ---`. | The entire extracted, page-delimited text from the uploaded PDF or TXT lecture file. |

---

## 6. Model, API, and Runtime Configuration

The runtime parameters are governed by [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py) and called through `prompts/lecture_analyzer.py`:

| Parameter | Implemented Value | Source of Truth | Operational Notes |
| :--- | :--- | :--- | :--- |
| **Model** | `openai/gpt-oss-120b` | `.env` via `get_configured_model()` | Groq cloud model configured via environment variable `GROQ_MODEL`. |
| **Temperature** | `0.2` | `analyze_lecture()` default argument | Kept intentionally low to ensure deterministic, highly grounded factual extraction. |
| **Max Tokens** | `None` (Unconstrained) | `generate_response()` parameter | Omitted from API request kwargs; allows the model's native maximum completion window. |
| **Timeout (Function)** | `90.0` seconds | `analyze_lecture()` signature | Default timeout if called independently. |
| **Timeout (App Invocation)** | `120.0` seconds | `app.py` line 282 | Overridden in Streamlit to accommodate larger PDF decks and network latency. |
| **Max Retries** | `1` | `get_groq_client()` in `groq_client.py` | Configured on the Groq client instance (`groq.Groq(max_retries=1)`) to avoid infinite retry loops. |
| **API Key Security** | `GROQ_API_KEY` in `.env` | `get_groq_client()` | Loaded securely via `dotenv`; never printed, logged, or serialized to frontend UI. |

### Error & Exception Handling:
The Groq client maps SDK exceptions to structured application errors caught by `app.py`:
- `groq.AuthenticationError` $\rightarrow$ `AuthenticationError` (Notifies user to check API key in `.env`).
- `groq.NotFoundError` $\rightarrow$ `ModelNotFoundError` (Warns if model ID is invalid).
- `groq.RateLimitError` $\rightarrow$ `RateLimitExceededError` (Advises cooldown period).
- `groq.APITimeoutError` $\rightarrow$ `APIRequestTimeoutError` (Handles slow or stalled network requests).
- `groq.APIConnectionError` $\rightarrow$ `NetworkConnectionError` (Flags internet/DNS disconnection).

---

## 7. Genuine Sample Run

### Evidence Reference:
- **Output File:** [`docs/milestone2/test-evidence/test_p1_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p1_output.md)
- **Execution Script:** [`docs/milestone2/test-evidence/test_lecture_analyzer.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_lecture_analyzer.py)

### Sample Input Summary:
- **Source Lecture:** 2-page sample lecture text titled *"CS301: Computer Architecture — Lecture 7: Cache Memory & Memory Hierarchy Basics"*.
- **Content:**
  - *Page 1:* Memory wall, SRAM (cache: fast, expensive, volatile) vs. DRAM (main memory: slower, cheaper, periodic refresh), temporal locality (loops), spatial locality (sequential arrays).
  - *Page 2:* AMAT equation ($\text{AMAT} = \text{Hit\_Time} + (\text{Miss\_Rate} \times \text{Miss\_Penalty})$), typical ranges (1–4 cycles hit, 50–200 cycles miss penalty), 3 C's of cache misses (Compulsory, Capacity, Conflict), and a note stating multi-core cache coherence is deferred to Chapter 8.

### Genuine Generated Output Summary:
The output generated by the live Groq API call produced an 83-line Markdown document containing:
1. **Executive Overview:** Accurately captured lecture scope across Pages 1–2.
2. **Topic-by-Topic Breakdown:** High-fidelity explanations of SRAM vs. DRAM, temporal vs. spatial locality, the AMAT formula, and the 3 C's of misses with explicit `[Page 1]` and `[Page 2]` citations.
3. **Key Terminology Table:** 10 core definitions accurately mapped to their source slides.
4. **Takeaways:** 5 critical revision takeaways.
5. **Topics Needing Clarification:** Flagged the deferred cache coherence topic, but also introduced unmentioned external concepts (replacement policies LRU/FIFO, associativity impact on hit time).

---

## 8. Known Limitations & Role of P3 Verification

- **External Syllabus Extrapolation in Gaps:** While P1 adheres strictly to the text in sections 1–4, under Section 5 ("Topics Needing Clarification & Potential Gaps"), the model tends to extrapolate common course curriculum topics (e.g., replacement policies, set associativity) that were not present in the slides.
- **Role of P3 Verification:**
  - Prompt 3 (Content Verification Assistant) audits P1 against the source text.
  - In the live test run ([`test_p3_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md)), P3 confirmed that P1’s core content was 100% grounded, but successfully flagged the ungrounded assumptions regarding associativity and replacement policies.
  - This cross-verification prevents students from mistaking external concepts for examinable material specified by the lecturer.
