# Prompt Sheet: Prompt 2 (P2) — Revision Question Generator
**Project:** LastHope — AI Lecture-to-Revision Assistant  
**Pipeline Stage:** Stage 03 / 05 (Practice Questions & Assessment)  
**Implementation Source:** [`prompts/question_generator.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/question_generator.py)  
**Client Wrapper:** [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py)  
**Version Documented:** Implemented Baseline (v1.0)  

---

## 1. Prompt Name and Purpose

- **Identifier:** `Prompt 2 (P2): Revision Question Generator`
- **Primary Function:** Generates balanced, exam-oriented practice questions across multiple cognitive tiers (recall, conceptual understanding, and quantitative problem solving) based jointly on the original lecture text and the structured P1 analysis notes.
- **Specific Objectives:**
  - Create a balanced question set containing Multiple-Choice Questions (MCQs), Short-Answer Questions, and Conceptual/Application Problems.
  - Calibrate question difficulty across `[Easy]`, `[Medium]`, and `[Hard]` tiers.
  - Require precise page references (`[Page X]`) for every question and solution.
  - Format output in an unspoilered "Practice Mode" layout with all questions grouped first, followed by a complete Answer Key & Explanations section.

---

## 2. Application Workflow Integration

In the LastHope Streamlit application ([`app.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/app.py)), P2 operates at **Stage 03 (Tab 3: Practice Questions)**:

```
[Stage 01: Parsed Lecture] ──┐
                             ├─▶ generate_questions(lecture, analysis, count)
[Stage 02: P1 Notes] ────────┘                  │
                                                ▼
                             [Stage 03: Practice Questions] ──▶ st.session_state.p2_questions
                                                                        │
                                                ┌───────────────────────┴───────────────────────┐
                                                ▼                                               ▼
                                   [Stage 04: Content Audit (P3)]              [Stage 05: Export Study Pack]
```

- **Trigger:** The user selects a question volume (5, 10, or 15 questions via `st.selectbox`) and clicks `📝 GENERATE PRACTICE QUESTIONS →`.
- **Prerequisites:** Both Stage 01 (`st.session_state.parsed_doc`) and Stage 02 (`st.session_state.p1_analysis`) must be completed.
- **State Updates:** Generates Markdown stored in `st.session_state.p2_questions`. Downstream verification state (`st.session_state.p3_verification`) is reset to `None`.
- **UI Parsing:** In `app.py`, the application automatically splits `p2_questions` on the delimiter `## Part 2` to power two viewing modes:
  - *Standard Mode:* Two sub-tabs: `✍️ PRACTICE MODE` (questions only) and `🔑 COMPLETE ANSWER KEY & EXPLANATIONS`.
  - *Exam Mode:* A single reading sheet with an expandable spoiler drawer at the bottom.

---

## 3. Actual System Prompt

The complete, verbatim system prompt implemented in [`prompts/question_generator.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/question_generator.py) (`P2_SYSTEM_PROMPT`):

```markdown
You are an expert academic assessment specialist and exam question designer.
Your mission is to generate high-yield, exam-oriented revision practice questions based solely on the provided lecture text and structured lecture analysis.

### Core Directives:
1. Strict Grounding in Material: Every question, answer option, and explanation must be directly derivable from the provided lecture text and analysis. Never introduce external concepts, unmentioned facts, or outside curriculum.
2. Cognitive Depth & Variety: Create a balanced set testing multiple cognitive levels:
   - Recall & Terminology: Foundational definitions, component roles, and basic facts.
   - Conceptual Understanding: Comparing mechanisms, explaining trade-offs, and "why/how" questions.
   - Application & Problem-Solving: Quantitative calculations using lecture formulas or applying principles to specific technical scenarios.
3. Difficulty Calibration: Explicitly tag every question with a difficulty tier:
   - [Easy]: Direct recall or single-fact identification.
   - [Medium]: Conceptual distinction, trade-off explanation, or multi-step logic.
   - [Hard]: Formula application, performance calculation, or multi-concept synthesis.
4. Balanced Question Distribution:
   - Section A: Multiple-Choice Questions (MCQs) - 4 clear options (A, B, C, D) with exactly one correct answer and plausible, non-arbitrary distractors.
   - Section B: Short-Answer Questions - precise, high-impact exam questions requiring 2-3 sentence model answers.
   - Section C: Conceptual & Application Questions - deeper questions involving calculations, scenario evaluations, or mechanism walkthroughs.
5. Page Citations: Cite the relevant source page (e.g., `[Page X]`) for every question and answer.
6. Self-Testing Friendly Layout: Group all questions together first (so students can test their recall without spoilers), followed by a clear dividing line and a comprehensive, step-by-step Answer Key & Explanations section.

### Markdown Output Template:
# 📝 Revision Practice Questions: [Topic]

## Part 1: Questions (Practice Mode)

### Section A: Multiple-Choice Questions
1. **[Easy/Medium/Hard]** [Question text] *(Source: [Page X])*
   - A) [Option A]
   - B) [Option B]
   - C) [Option C]
   - D) [Option D]

### Section B: Short-Answer Questions
[Numbered questions with difficulty tags and page references]

### Section C: Conceptual & Application Questions
[Numbered questions with difficulty tags and page references]

---

## Part 2: Complete Answer Key & Explanations

### Multiple-Choice Answers
1. **Correct Answer: [Letter]**
   - **Explanation:** [Detailed justification grounded in the lecture]
   - **Source:** [Page X]

### Short-Answer Model Answers
[Detailed model answers with page references]

### Conceptual & Application Solutions
[Step-by-step explanations, formula substitutions, or reasoning breakdowns]
```

---

## 4. Actual User Prompt & Dynamic Population

The complete user prompt template implemented in [`prompts/question_generator.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/question_generator.py) (`P2_USER_PROMPT_TEMPLATE`):

```markdown
Please generate {num_questions} high-yield revision practice questions based on the following lecture materials.

--- BEGIN ORIGINAL LECTURE TEXT ---
{lecture_text}
--- END ORIGINAL LECTURE TEXT ---

--- BEGIN STRUCTURED LECTURE ANALYSIS (P1) ---
{analysis_text}
--- END STRUCTURED LECTURE ANALYSIS (P1) ---

Generate a balanced mix of Multiple-Choice, Short-Answer, and Conceptual/Application questions with difficulty ratings, page references, and an unspoilered complete answer key with explanations.
```

### Dynamic Construction Logic:
In `prompts/question_generator.py`, the user prompt is formatted as follows:
```python
def format_p2_user_prompt(
    lecture_text: str,
    analysis_text: str,
    num_questions: int = 10,
) -> str:
    if not lecture_text or not lecture_text.strip():
        raise ValueError("Lecture text cannot be empty.")
    if not analysis_text or not analysis_text.strip():
        raise ValueError("Lecture analysis (P1) cannot be empty.")

    safe_count = max(1, min(int(num_questions), 30))

    return P2_USER_PROMPT_TEMPLATE.format(
        lecture_text=lecture_text.strip(),
        analysis_text=analysis_text.strip(),
        num_questions=safe_count,
    )
```
In `app.py`, this is invoked with:
```python
p2_result = generate_questions(
    lecture_text=st.session_state.parsed_doc.extracted_text,
    analysis_text=st.session_state.p1_analysis,
    num_questions=num_questions,
    timeout=150.0,
)
```

---

## 5. Prompt Variable Specification

| Variable Name | Type | Injected By | Validation / Population Logic | Description |
| :--- | :--- | :--- | :--- | :--- |
| `{lecture_text}` | `str` | `app.py` via `format_p2_user_prompt` | Validated non-empty (`not lecture_text.strip()`). Contains original extracted lecture text with `--- [Page X] ---` delimiters. | Primary source of truth for grounded question formulation. |
| `{analysis_text}` | `str` | `app.py` via `format_p2_user_prompt` | Validated non-empty (`not analysis_text.strip()`). Sourced from `st.session_state.p1_analysis`. | High-yield revision summary output produced by Stage 02 (P1). |
| `{num_questions}` | `int` | `app.py` (`st.selectbox([5, 10, 15])`) | Clamped between 1 and 30 via `max(1, min(int(num_questions), 30))`. Default in module is 10. | Target number of balanced practice questions to generate. |

---

## 6. Model, API, and Runtime Configuration

The runtime parameters are governed by [`utils/groq_client.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/utils/groq_client.py) and called through `prompts/question_generator.py`:

| Parameter | Implemented Value | Source of Truth | Operational Notes |
| :--- | :--- | :--- | :--- |
| **Model** | `openai/gpt-oss-120b` | `.env` via `get_configured_model()` | Groq cloud model configured via environment variable `GROQ_MODEL`. |
| **Temperature** | `0.3` | `generate_questions()` default argument | Balanced temperature: low enough for strict factual accuracy while permitting creative question framing and varied distractors. |
| **Max Tokens** | `None` (Unconstrained) | `generate_response()` parameter | Omitted to accommodate lengthy question sets and detailed step-by-step solutions. |
| **Timeout (Function)** | `120.0` seconds | `generate_questions()` signature | Default timeout if invoked independently. |
| **Timeout (App Invocation)** | `150.0` seconds | `app.py` line 363 | Overridden in Streamlit to ensure larger question batches (15 questions) complete without timing out. |
| **Max Retries** | `1` | `get_groq_client()` in `groq_client.py` | Configured on the Groq client instance (`groq.Groq(max_retries=1)`). |
| **API Key Security** | `GROQ_API_KEY` in `.env` | `get_groq_client()` | Authenticated securely; never logged or exposed in logs. |

### Error & Exception Handling:
Structured exception handling mirrors P1, with errors trapped and rendered via user-friendly callouts in `app.py` (`MissingAPIKeyError`, `AuthenticationError`, `ModelNotFoundError`, `RateLimitExceededError`, `NetworkConnectionError`, `APIRequestTimeoutError`).

---

## 7. Genuine Sample Run

### Evidence Reference:
- **Output File:** [`docs/milestone2/test-evidence/test_p2_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p2_output.md)
- **Execution Script:** [`docs/milestone2/test-evidence/test_question_generator.py`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_question_generator.py)

### Sample Input Summary:
- **Original Lecture:** CS301 Lecture 7 (Cache Memory Basics, AMAT formula, 3 C's of misses).
- **P1 Analysis:** Revision notes from `test_p1_output.md`.
- **Requested Question Count:** Default generation (produced 8 high-impact questions: 4 MCQs, 2 Short-Answer, 2 Quantitative/Conceptual).

### Genuine Generated Output Summary:
The output generated by the live Groq API call produced a 100-line Markdown document containing:
- **Part 1 (Questions):**
  - *Q1 [Easy]:* Technology for CPU caches (SRAM vs. DRAM). *(Source: [Page 1])*
  - *Q2 [Medium]:* Repeated loop variable access locality principle (Temporal locality). *(Source: [Page 1])*
  - *Q3 [Medium]:* Effect of higher associativity on AMAT components. *(Source: [Page 2])*
  - *Q4 [Hard]:* Quantitative calculation of AMAT given Hit Time = 2 cycles, Miss Rate = 4%, Miss Penalty = 120 cycles. Options: A) 6.8 cycles, B) 7.8 cycles, C) 8.8 cycles, D) 9.8 cycles.
  - *Q5 [Easy]:* Definition of capacity miss. *(Source: [Page 2])*
  - *Q6 [Medium]:* Distinction between compulsory and conflict misses. *(Source: [Page 2])*
  - *Q7 [Hard]:* Processor executing $1 \times 10^9$ accesses (3 cycles hit time, 2% miss rate, 80 cycles miss penalty). Sub-parts (a) total cycles and (b) new total cycles if miss rate is halved.
  - *Q8 [Medium]:* Dominant miss type for sequential array traversal.
- **Part 2 (Answer Key & Explanations):** Step-by-step solutions for all 8 questions.

---

## 8. Known Limitations & Role of P3 Verification

The live test run exposed three concrete edge cases inherent to LLM-generated assessment sets:

1. **Answer-Key Label Contradiction (Question 4):**
   - The model calculated: $\text{AMAT} = 2 + (0.04 \times 120) = 2 + 4.8 = 6.8\text{ cycles}$.
   - Option A was `6.8 cycles` and Option B was `7.8 cycles`.
   - In Part 2, the model declared: `1. Correct Answer: B`, but then in the explanation wrote: `"Wait, that matches option A. Oops, re-evaluate: ... Option A is correct."`
2. **Arithmetic Dependency Oversight (Question 7b):**
   - Halving the miss rate from 2% to 1% reduces misses from $2 \times 10^7$ to $1 \times 10^7$.
   - Hits increase from $9.8 \times 10^8$ to $9.9 \times 10^8$.
   - The model updated miss cycles ($0.8 \times 10^9$) but kept hit cycles fixed at $2.94 \times 10^9$ instead of recalculating $9.9 \times 10^8 \times 3 = 2.97 \times 10^9$.
   - This resulted in an erroneous total of $3.74 \times 10^9$ cycles instead of the mathematically correct $3.77 \times 10^9$ cycles.
3. **Out-of-Scope Questions (Questions 3 & 8):**
   - Asked about associativity and sequential array traversal dominant miss types, which were unstated in the source slides.

### Role of P3 Verification:
These issues highlight exactly why **Prompt 3 (Content Verification Assistant)** is indispensable. When audited by P3 in [`test_p3_output.md`](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md), every single one of these defects was caught and corrected:
- Flagged Q4 as an internal label contradiction.
- Detected the 30-million-cycle calculation error in Q7(b) and provided the corrected solution ($3.77 \times 10^9$ cycles).
- Flagged Q3 and Q8 as unsupported inferences.
- Rated the study set as **PASS WITH WARNINGS**, ensuring students do not memorize contradictory answer keys.
