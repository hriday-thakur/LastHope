# Prompt Sheet: Prompt 3 (P3) — Content Verification Assistant
**Project:** LastHope — AI Lecture-to-Revision Assistant  
**Pipeline Stage:** Stage 04 / 05 (Content Verification & Fact-Check Audit)  
**Implementation Source:** [`prompts/content_verifier.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/content_verifier.py)  
**Client Wrapper:** [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py)  
**Version Documented:** Implemented Baseline (v1.0)  

---

## 1. Prompt Name and Purpose

- **Identifier:** `Prompt 3 (P3): Content Verification Assistant`
- **Primary Function:** Acts as an independent academic auditor, fact-checker, and calculation reviewer that evaluates both AI-generated lecture revision notes (P1) and practice questions (P2) against the original lecture source text.
- **Specific Objectives:**
  - Establish the original lecture text as the strict primary source of truth.
  - Detect unsupported factual claims, curriculum extrapolations, and hallucinations.
  - Independently re-compute all mathematical equations, cycle calculations, and numerical formulas from scratch.
  - Cross-examine multiple-choice answer keys for internal label contradictions.
  - Assign an overall quality verdict: `PASS`, `PASS WITH WARNINGS`, or `NEEDS REVISION`.
  - Provide actionable, transparent recommendations and explicit disclaimers.

---

## 2. Application Workflow Integration

In the LastHope Streamlit application ([`app.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/app.py)), P3 operates at **Stage 04 (Tab 4: Content Audit)**:

```
[Stage 01: Parsed Lecture] ──┐
[Stage 02: P1 Notes] ────────┼─▶ verify_content(lecture, analysis, questions)
[Stage 03: P2 Questions] ────┘                  │
                                                ▼
                             [Stage 04: Content Audit] ──▶ st.session_state.p3_verification
                                                                        │
                                                                        ▼
                                                           [Stage 05: Export Study Pack]
```

- **Trigger:** The user navigates to Tab 4 and clicks `🛡️ RUN CONTENT VERIFICATION →`.
- **Prerequisites:** All three prior stages must be present: Stage 01 (`parsed_doc`), Stage 02 (`p1_analysis`), and Stage 03 (`p2_questions`).
- **State Updates:** Writes the audit report into `st.session_state.p3_verification`.
- **UI Parsing:** The application dynamically inspects the returned Markdown report to:
  1. Extract the overall status string (`PASS`, `PASS WITH WARNINGS`, or `NEEDS REVISION`).
  2. Parse the count of verified items (`✅`), warnings (`⚠️`), and errors/unsupported claims (`❌`).
  3. Render the dynamic brutalist **VERDICT BOARD HEADER** with color-coded badges (Green for PASS, Amber for WARNINGS, Red for NEEDS REVISION).
  4. Provide interactive filter pills: `ALL FINDINGS`, `GROUNDED ONLY`, `FLAGGED ITEMS`.

---

## 3. Actual System Prompt

The complete, verbatim system prompt implemented in [`prompts/content_verifier.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/content_verifier.py) (`P3_SYSTEM_PROMPT`):

```markdown
You are a rigorous academic content reviewer, auditor, and fact-checking assistant.
Your mission is to audit AI-generated lecture summaries (P1) and practice questions (P2) against the original lecture source text, ensuring factual precision, syllabus fidelity, and mathematical correctness.

### Core Directives:
1. Primary Source of Truth: The Original Lecture Text is the ONLY ground truth. If a claim in P1 or P2 is not supported by or contradicts the Original Lecture Text, flag it as unsupported or inaccurate—regardless of whether it sounds plausible or is generally true in external textbooks.
2. Independent Verification: Never assume a claim is verified simply because P1 and P2 agree with each other. Both are AI-generated; evaluate both strictly against the source text.
3. Mathematical & Calculation Auditing: Re-calculate all mathematical formulas, numeric problems, and cycle counts step by step. If an answer key or problem statement has arithmetic discrepancies or contradictory option letters, highlight the error and provide the corrected calculation.
4. Non-Fabrication of Corrections: If a concept in the generated materials is ambiguous or missing in the source text, state clearly that it is unsupported or requires instructor clarification. Never invent source citations or fabricate citations not present in the original text.
5. Uncertainty & Manual Review: If a claim cannot be verified with high confidence from the provided excerpt, explicitly mark it as: "[MANUAL REVIEW REQUIRED]".
6. Transparent Disclaimer: You must explicitly state in your report that this review is an AI-assisted quality assessment and does not constitute a 100% guarantee of factual perfection.
7. Structured Markdown Report: Format your findings following the required schema below.

### Output Structure:
# 🛡️ Content Verification & Fact-Check Report

> **Disclaimer:** *This is an AI-assisted academic verification report intended to aid revision quality. It does not provide an absolute guarantee of correctness. Students and educators should cross-reference original course materials for high-stakes exam preparation.*

## 1. Executive Verification Summary
- Overall assessment of alignment between generated materials and original lecture notes.
- Summary of verified points vs. flagged concerns.
- **Audit Verdict:** [PASS / PASS WITH WARNINGS / NEEDS REVISION]

## 2. Verified Claims & Grounded Concepts
List key concepts, definitions, and questions that are fully supported by the lecture text:
- ✅ **[Claim / Concept]**: Confirmed grounded. *(Source: [Page X])*

## 3. Unsupported or Inaccurate Claims
List any points in P1 or P2 that introduce outside facts, misrepresent concepts, or lack source backing:
- ❌ **[Claim / Statement]**: Explanation of why it is unsupported or inaccurate based on the lecture text. *(Source: [Page X] or "Absent from Source")*

## 4. Mathematical & Calculation Checks
Re-compute all formulas, numeric questions, and answer keys:
- 🧮 **[Problem / Formula Checked]**:
  - *Given in Generated Material:* [Original formula / problem statement]
  - *Step-by-Step Verification:* [Calculations]
  - *Verdict:* [Correct / Calculation Error Detected]
  - *Corrected Solution (if needed):* [Clear breakdown]

## 5. Context Gaps & Ambiguities
- Note any oversimplified definitions, omitted caveats, or deferred topics that may mislead students if taken without context.

## 6. Actionable Recommended Corrections
- Concrete, bulleted recommendations to correct P1 notes or P2 questions before final study.

## 7. Final Review Status
- **Final Status:** **[PASS | PASS WITH WARNINGS | NEEDS REVISION]**
- **Justification:** Clear 1-2 sentence conclusion explaining the assigned status.
```

---

## 4. Actual User Prompt & Dynamic Population

The complete user prompt template implemented in [`prompts/content_verifier.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/content_verifier.py) (`P3_USER_PROMPT_TEMPLATE`):

```markdown
Please perform a rigorous academic audit and fact-check of the following AI-generated revision materials against the original lecture source text.

--- BEGIN ORIGINAL LECTURE TEXT (PRIMARY SOURCE OF TRUTH) ---
{lecture_text}
--- END ORIGINAL LECTURE TEXT ---

--- BEGIN GENERATED LECTURE ANALYSIS (P1) ---
{analysis_text}
--- END GENERATED LECTURE ANALYSIS (P1) ---

--- BEGIN GENERATED REVISION QUESTIONS & ANSWER KEY (P2) ---
{questions_text}
--- END GENERATED REVISION QUESTIONS & ANSWER KEY (P2) ---

Conduct a thorough cross-examination, audit any mathematical calculations step by step, verify page attributions, flag hallucinations or external assumptions, and provide an actionable report with a final status of PASS, PASS WITH WARNINGS, or NEEDS REVISION.
```

### Dynamic Construction Logic:
In `prompts/content_verifier.py`, the user prompt is populated with strict validation:
```python
def format_p3_user_prompt(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
) -> str:
    if not lecture_text or not lecture_text.strip():
        raise ValueError("Original lecture text cannot be empty.")
    if not analysis_text or not analysis_text.strip():
        raise ValueError("Lecture analysis (P1) cannot be empty.")
    if not questions_text or not questions_text.strip():
        raise ValueError("Questions and answer key (P2) cannot be empty.")

    return P3_USER_PROMPT_TEMPLATE.format(
        lecture_text=lecture_text.strip(),
        analysis_text=analysis_text.strip(),
        questions_text=questions_text.strip(),
    )
```
In `app.py`, this is invoked via:
```python
p3_result = verify_content(
    lecture_text=st.session_state.parsed_doc.extracted_text,
    analysis_text=st.session_state.p1_analysis,
    questions_text=st.session_state.p2_questions,
    timeout=150.0,
)
```

---

## 5. Prompt Variable Specification

| Variable Name | Type | Injected By | Validation / Population Logic | Description |
| :--- | :--- | :--- | :--- | :--- |
| `{lecture_text}` | `str` | `app.py` via `format_p3_user_prompt` | Non-empty string check. Contains original parsed lecture with page markers. | The absolute ground truth against which all generated statements are judged. |
| `{analysis_text}` | `str` | `app.py` via `format_p3_user_prompt` | Non-empty string check. Sourced from `st.session_state.p1_analysis`. | Generated P1 revision outline, definitions, and takeaways being audited. |
| `{questions_text}` | `str` | `app.py` via `format_p3_user_prompt` | Non-empty string check. Sourced from `st.session_state.p2_questions`. | Generated P2 practice questions, answer options, and step-by-step solutions being audited. |

---

## 6. Model, API, and Runtime Configuration

The runtime parameters are governed by [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py) and called through `prompts/content_verifier.py`:

| Parameter | Implemented Value | Source of Truth | Operational Notes |
| :--- | :--- | :--- | :--- |
| **Model** | `openai/gpt-oss-120b` | `.env` via `get_configured_model()` | Groq cloud model configured via environment variable `GROQ_MODEL`. |
| **Temperature** | `0.1` | `verify_content()` default argument | Set to minimum (0.1) to enforce maximum determinism, critical scrutiny, and strict factual cross-examination. |
| **Max Tokens** | `None` (Unconstrained) | `generate_response()` parameter | Omitted to ensure the comprehensive cross-examination report is not truncated. |
| **Timeout (Function)** | `120.0` seconds | `verify_content()` signature | Default timeout if invoked independently. |
| **Timeout (App Invocation)** | `150.0` seconds | `app.py` line 463 | Overridden in Streamlit to accommodate multi-document cross-examination latency. |
| **Max Retries** | `1` | `get_groq_client()` in `groq_client.py` | Configured on the Groq client instance (`groq.Groq(max_retries=1)`). |
| **API Key Security** | `GROQ_API_KEY` in `.env` | `get_groq_client()` | Authenticated securely; never logged or exposed. |

### Error & Exception Handling:
Structured exception classes catch API failures and surface clear error notifications in Streamlit without application crashes (`MissingAPIKeyError`, `AuthenticationError`, `RateLimitExceededError`, `NetworkConnectionError`, `APIRequestTimeoutError`).

---

## 7. Genuine Sample Run

### Evidence Reference:
- **Output File:** [`docs/milestone2/test-evidence/test_p3_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md)
- **Execution Script:** [`docs/milestone2/test-evidence/test_content_verifier.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_content_verifier.py)

### Sample Input Summary:
- **Source Lecture Text:** CS301 Lecture 7 (Cache Memory Basics, AMAT formula, 3 C's of misses).
- **P1 Input:** Complete notes from `test_p1_output.md`.
- **P2 Input:** Complete questions and answer key from `test_p2_output.md`.

### Genuine Generated Output Summary:
The output generated by the live Groq API call produced a 68-line Markdown verification report containing:
1. **Executive Verification Summary:** Found P1 notes to be fully grounded. Diagnosed multiple critical errors in P2 questions and answer keys. Assigned an overall verdict of **PASS WITH WARNINGS**.
2. **Verified Claims & Grounded Concepts:** Tabulated 10 verified claims with page numbers (SRAM vs. DRAM, locality definitions, AMAT formula, typical latency ranges, Q1/Q2/Q5/Q6 answers, and Q7(a) numerical calculation).
3. **Unsupported or Inaccurate Claims:**
   - *P2 Q3:* Flagged assumption that associativity directly reduces miss rate (absent from source slides).
   - *P2 Q8:* Flagged claim that capacity misses dominate sequential array traversal as an educated guess without slide support.
   - *P2 Q4 Answer Key:* Caught internal contradiction where the key declared Option B as correct but showed Option A (6.8 cycles) in calculations.
   - *P2 Q7(b) Calculation:* Caught hit-cycle oversight where hit count was not recalculated after halving the miss rate.
4. **Mathematical & Calculation Checks:** Table detailing step-by-step recomputations for Q4 AMAT, Q7(a) Total Cycles, and Q7(b) Halved Miss Rate, presenting the exact corrected total ($3.77 \times 10^9$ cycles vs. reported $3.74 \times 10^9$ cycles).
5. **Context Gaps & Ambiguities:** Noted ungrounded assumptions regarding cache associativity and workload-specific miss rankings.

---

## 8. Known Limitations & Auditor Boundaries

While Prompt 3 is an essential quality assurance layer, its role and boundaries must be clearly understood:

1. **AI-Assisted Quality Assessment, Not a Formal Proof:**  
   P3 is itself an LLM-powered auditor. While operating at a very low temperature (0.1) minimizes hallucinations, it cannot provide an absolute mathematical guarantee. As mandated by Directive 6, every report prominently renders an academic disclaimer:
   > *"This is an AI-assisted academic verification report intended to aid revision quality. It does not provide an absolute guarantee of correctness. Students and educators should cross-reference original course materials for high-stakes exam preparation."*
2. **Dependent on Ingestion Quality:**  
   If the document parser fails to extract text cleanly or omits mathematical symbols from scanned or corrupt PDFs, P3's primary source of truth is degraded, which can lead to false-positive hallucination flags.
3. **Auditor Truncation Safeguard:**  
   Because P3 ingests the original text, P1 output, and P2 output simultaneously, input prompt length is larger. Generous request timeouts (150s in `app.py`) and unconstrained `max_tokens` are configured in LastHope to prevent partial report generation.
4. **System Value:**  
   P3's primary value is eliminating silent failures: rather than allowing students to unknowingly study mathematically flawed calculations or contradictory answer keys, P3 surfaces discrepancies transparently, enabling students to revise with confidence.
