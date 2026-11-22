# Milestone 2: Prompt Iteration & Refinement Log
**Project:** LastHope — AI Lecture-to-Revision Assistant  
**Course:** SCSE4041 Mini Project  
**Date:** November 2026  
**Status:** Complete (9 version files archived; live test evidence linked)

---

## 1. Executive Summary

This document records the systematic design, testing, evaluation, and iterative refinement of the three core prompt pipelines powering the LastHope system:
1. **Prompt 1 (P1): Lecture Content Analyzer** — Transforms raw extracted lecture text/slides into structured, student-friendly revision notes with page attributions.
2. **Prompt 2 (P2): Revision Question Generator** — Synthesizes exam-oriented practice questions across cognitive tiers (MCQs, Short-Answer, and Quantitative/Application problems).
3. **Prompt 3 (P3): Content Verification Assistant** — Performs an independent audit and fact-check of generated materials against the source lecture text to detect hallucinations, label discrepancies, and arithmetic errors.

Each prompt was evolved across three distinct iterations (**v1.0**, **v2.0**, and **v3.0**). All refinements were driven directly by empirical findings and edge cases observed during the live Groq API testing of Version 1.0 (`openai/gpt-oss-120b`).

---

## 2. Testing & Execution Status Matrix

To ensure absolute academic integrity and transparency, the operational and verification status of each prompt version is documented below:

| Prompt Version | File Path | Testing Status | Evidence Reference |
| :--- | :--- | :--- | :--- |
| **P1 v1.0** | `prompts/versions/P1_v1.txt` | **Executed & Verified (Live Groq API)** | [test_p1_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p1_output.md) |
| **P1 v2.0** | `prompts/versions/P1_v2.txt` | **Untested / Proposed Iteration** | Synthesized based on P1 v1 observation log |
| **P1 v3.0** | `prompts/versions/P1_v3.txt` | **Untested / Proposed Iteration** | Synthesized based on P1 v2 architectural design |
| **P2 v1.0** | `prompts/versions/P2_v1.txt` | **Executed & Verified (Live Groq API)** | [test_p2_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p2_output.md) |
| **P2 v2.0** | `prompts/versions/P2_v2.txt` | **Untested / Proposed Iteration** | Synthesized based on P2 v1 calculation/label bugs |
| **P2 v3.0** | `prompts/versions/P2_v3.txt` | **Untested / Proposed Iteration** | Synthesized based on P2 v2 scratchpad protocol |
| **P3 v1.0** | `prompts/versions/P3_v1.txt` | **Executed & Verified (Live Groq API)** | [test_p3_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md) |
| **P3 v2.0** | `prompts/versions/P3_v2.txt` | **Untested / Proposed Iteration** | Synthesized based on P3 v1 audit output |
| **P3 v3.0** | `prompts/versions/P3_v3.txt` | **Untested / Proposed Iteration** | Synthesized based on P3 v2 JSON schema integration |

> **Important Disclosure on v2 & v3 Status:** Per project guidelines, Version 1.0 represents the active production baseline evaluated against live Groq API infrastructure during Milestone 2. Versions 2.0 and 3.0 are archival design iterations formulated to systematically mitigate observed defects; they remain **untested** against live API calls in this milestone to prevent data fabrication.

---

## 3. Prompt 1 (P1): Lecture Content Analyzer

### 3.1 Version 1.0 Overview & Empirical Observations
- **Implementation File:** [P1_v1.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P1_v1.txt) / [lecture_analyzer.py](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/lecture_analyzer.py)
- **Live Test Evidence:** [test_p1_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p1_output.md)
- **Empirical Findings from Live Run:**
  1. *Factual Grounding Strengths:* P1 v1 accurately captured memory hierarchy concepts, SRAM vs. DRAM differences, temporal and spatial locality, the AMAT equation, and the 3 C's of cache misses with accurate page markers (`[Page 1]`, `[Page 2]`).
  2. *Observed Defect (External Extrapolation in Gaps):* In Section 5 ("Topics Needing Clarification & Potential Gaps"), the model introduced external textbook concepts such as "Replacement Policies (LRU, FIFO, Random)" and "Associativity Impact on Conflict Misses". While pedagogically valid in general computer architecture courses, these concepts were entirely absent from the provided 2-page source slides. As audited in `test_p3_output.md`, P3 flagged these as ungrounded external assumptions.
  3. *Formula Context Limitation:* The AMAT formula `AMAT = Hit_Time + (Miss_Rate × Miss_Penalty)` was defined, but typical parameter ranges and variable units were embedded inside prose rather than formalized in a dedicated reference block.

---

### 3.2 Iteration v1.0 $\rightarrow$ v2.0 (Boundary Enforcement & Granular Attribution)
- **Archived File:** [P1_v2.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P1_v2.txt)
- **Key Prompt Changes:**
  1. **Negative Boundary Directives for Clarification Section:** Added explicit negative constraints instructing the model that Section 5 must *only* flag concepts or terms explicitly named in the lecture text that lack detail or are deferred (e.g., "Cache Coherence is deferred to Chapter 8"). Explicitly prohibited bringing in external textbook terms (e.g., replacement algorithms, associativity) that are absent from the source.
  2. **Granular Page Attribution:** Mandated verbatim bracketed page markers `[Page X]` for every individual topic bullet, definition, and takeaway, rather than general page ranges.
  3. **Formula Integrity Mandate:** Directed the model to explicitly define each formula variable alongside its lecture-provided units and stated typical ranges (e.g., Hit Time: 1–4 cycles, Miss Penalty: 50–200 cycles).
- **Rationale Linked to Evidence:** Directly eliminates the external hallucinations identified by P3 where the model tried to "fill in" standard computer architecture syllabus gaps that the lecture deck intentionally deferred or omitted.

---

### 3.3 Iteration v2.0 $\rightarrow$ v3.0 (Structured Formula Schema & Dual Gap Categorization)
- **Archived File:** [P1_v3.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P1_v3.txt)
- **Key Prompt Changes:**
  1. **Dual Gap Categorization:** Re-architected Section 5 into two strictly governed subsections:
     - `5.1 Source-Referenced Gaps & Deferred Topics`: Strictly captures points the slides themselves declare as incomplete or deferred.
     - `5.2 Clarification Questions for the Lecturer`: Directed questions testing boundary conditions of covered concepts without injecting unmentioned external terms.
  2. **Standardized Formula Specification Block:** Formalized formulas into a structured schema containing LaTeX equations, variable definitions, stated typical ranges, and explicit slide limitations.
  3. **Comparative Analysis Matrix:** Enforced comparative relationship tracking in the definitions table (e.g., SRAM vs. DRAM, Temporal vs. Spatial Locality) to improve study utility for exam comparison questions.
  4. **Zero-Extrapolation Fallback:** Added explicit directive: "If a parameter or mechanism is not specified in the lecture slides, output 'Not specified in lecture slides' rather than guessing."
- **Rationale Linked to Evidence:** Prevents confusion between course syllabus scope and general domain knowledge while elevating the pedagogical utility of revision notes for exam preparation.

---

## 4. Prompt 2 (P2): Revision Question Generator

### 4.1 Version 1.0 Overview & Empirical Observations
- **Implementation File:** [P2_v1.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P2_v1.txt) / [question_generator.py](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/question_generator.py)
- **Live Test Evidence:** [test_p2_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p2_output.md)
- **Empirical Findings from Live Run:**
  1. *Answer-Key Label Contradiction (Question 4):*  
     In Section A, Question 4 calculated:  
     $$\text{AMAT} = 2 + (0.04 \times 120) = 2 + 4.8 = 6.8\text{ cycles}$$  
     In the question prompt, Option A was `6.8 cycles` and Option B was `7.8 cycles`.  
     However, Part 2 of the answer key declared:  
     `4. Correct Answer: B`  
     Then, in the explanation, the model calculated $2 + 4.8 = 6.8$ and added:  
     `"Wait, that matches option A. Oops, re-evaluate: Option A is correct."`  
     This produced an unacceptable internal contradiction between the declared label (`B`) and the explanation (`A`).
  2. *Arithmetic Recalculation Defect (Question 7b):*  
     In Question 7, a processor executes $1 \times 10^9$ accesses with a 2% miss rate (Hit Time = 3 cycles, Miss Penalty = 80 cycles). Total accesses = $10^9$, Hits = $9.8 \times 10^8$, Misses = $2 \times 10^7$.  
     In sub-question (b), the miss rate was halved to 1% ($1 \times 10^7$ misses). The model computed the new miss cycles correctly as $0.8 \times 10^9$, but **failed to update the hit count**, keeping hit cycles at $2.94 \times 10^9$ (corresponding to $9.8 \times 10^8$ hits) instead of recalculating for the new $9.9 \times 10^8$ hits ($= 2.97 \times 10^9$ cycles). This caused the reported total cycle count to be $3.74 \times 10^9$ cycles instead of the mathematically correct $3.77 \times 10^9$ cycles.
  3. *Ungrounded Question Scope (Questions 3 & 8):*  
     Question 3 asked how increasing cache associativity affects the AMAT equation, and Question 8 asked which miss type dominates sequential array traversal. Neither concept was covered in the source lecture slides.

---

### 4.2 Iteration v1.0 $\rightarrow$ v2.0 (Label Alignment & Two-Pass Verification)
- **Archived File:** [P2_v2.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P2_v2.txt)
- **Key Prompt Changes:**
  1. **Strict Answer Key Label Alignment Directive:** Enforced that the letter specified in `Correct Answer: [Letter]` must strictly match the exact option letter corresponding to the calculated correct choice in Section A. Prohibited self-contradictory answers or post-hoc corrections in explanations.
  2. **Two-Pass Quantitative Calculation Verification:** Required the model to compute the full numerical derivation step by step *before* assigning multiple-choice options or writing the answer key.
  3. **Multi-Variable Arithmetic Conservation Check:** Mandated that when altering one parameter (e.g., miss rate), all dependent variables must be recomputed:
     $$\text{Total Accesses} = \text{Hits} + \text{Misses} \implies \text{Hits} = \text{Total Accesses} \times (1 - \text{Miss Rate})$$
     $$\text{Total Cycles} = (\text{Hits} \times \text{Hit Time}) + (\text{Misses} \times \text{Miss Penalty})$$
  4. **Strict Scope Enforcement:** Explicitly forbade generating questions testing concepts outside the provided slides (e.g., cache associativity, replacement policies).
- **Rationale Linked to Evidence:** Directly addresses and cures the Question 4 label contradiction and the Question 7(b) variable-dependency calculation error documented in `test_p3_output.md`.

---

### 4.3 Iteration v2.0 $\rightarrow$ v3.0 (Structured Calculation Scratchpad & Distractor Rationale)
- **Archived File:** [P2_v3.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P2_v3.txt)
- **Key Prompt Changes:**
  1. **Mandatory 4-Step Solution Schema for Quantitative Problems:**
     - `Given Parameters:` Explicitly enumerate all variables.
     - `Formula & Conservation Check:` Verify $\text{Hits} + \text{Misses} = \text{Total Accesses}$.
     - `Step-by-Step Arithmetic:` Show explicit multiplication and addition steps.
     - `Verified Result with Units:` Display final answer clearly with cycle/time units.
  2. **Distractor Quality & Systematic Analysis:** Required Section A explanations to provide explicit distractor analysis explaining why each incorrect option is mathematically or conceptually flawed (e.g., common pitfalls like failing to convert percentage to decimal or forgetting hit time latency).
  3. **Self-Contained Problem Statements:** Mandated that every question prompt explicitly specify all given numerical values without requiring students to guess unspecified hardware constants.
- **Rationale Linked to Evidence:** Prevents students from practicing with inconsistent or mathematically unsound exam questions, providing a predictable self-study environment.

---

## 5. Prompt 3 (P3): Content Verification Assistant

### 5.1 Version 1.0 Overview & Empirical Observations
- **Implementation File:** [P3_v1.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P3_v1.txt) / [content_verifier.py](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/content_verifier.py)
- **Live Test Evidence:** [test_p3_output.md](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/docs/milestone2/test-evidence/test_p3_output.md)
- **Empirical Findings from Live Run:**
  1. *Auditing Effectiveness:* P3 v1 performed exceptionally well during live testing. It independently caught:
     - The ungrounded associativity claim in P2 Question 3.
     - The ungrounded sequential array traversal inference in P2 Question 8.
     - The internal label contradiction in P2 Question 4 (Option A vs. Option B).
     - The hit-cycle calculation omission in P2 Question 7(b) ($3.74 \times 10^9$ vs. correct $3.77 \times 10^9$).
  2. *Formatting Inconsistency:* The live output used unbracketed text like `Page 1` rather than standardized bracketed markers `[Page 1]`.
  3. *Unstructured Categorization:* Mathematical checks and factual grounding checks were combined in broad sections without programmatic summary metrics, making programmatic downstream evaluation difficult.

---

### 5.2 Iteration v1.0 $\rightarrow$ v2.0 (Dual Audit Tables & Label Contradiction Protocol)
- **Archived File:** [P3_v2.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P3_v2.txt)
- **Key Prompt Changes:**
  1. **Dedicated Answer-Key Label Contradiction Protocol:** Added an explicit directive instructing P3 to compare the letter declared in `Correct Answer: [Letter]` against the option text in Section A and the explanation text. Declared any mismatch as a critical `[LABEL CONTRADICTION]`.
  2. **Independent Arithmetic First-Principles Recalculation:** Instructed the auditor to independently recalculate all cycle counts from first principles using parameter conservation rules ($\text{Hits} + \text{Misses} = \text{Total Accesses}$).
  3. **Dual Audit Tables:** Separated findings into two structured Markdown tables:
     - *Table 1:* Factual Grounding & Hallucinations Audit.
     - *Table 2:* Mathematical & Answer-Key Consistency Audit (Given, Recalculated, Discrepancy, Verdict).
  4. **Strict Bracketed Citations:** Enforced `[Page X]` or `[Absent from Source]` formatting for all audit citations.
- **Rationale Linked to Evidence:** Systematizes the exact auditing capabilities demonstrated in `test_p3_output.md` into repeatable, structured audit procedures.

---

### 5.3 Iteration v2.0 $\rightarrow$ v3.0 (Programmatic JSON Schema & Objective Decision Matrix)
- **Archived File:** [P3_v3.txt](file:///e:/College/Academics/Sem%205/Prompt/LastHope-main/LastHope-main/prompts/versions/P3_v3.txt)
- **Key Prompt Changes:**
  1. **Strict Objective Status Decision Matrix:** Replaced subjective evaluation with a deterministic rule set:
     - `PASS`: 0 factual hallucinations, 0 calculation errors, 0 label contradictions, 100% verified citations.
     - `PASS WITH WARNINGS`: 0 fatal errors, 0 mathematical bugs; minor ungrounded terminology in clarification sections or non-blocking pedagogical ambiguities.
     - `NEEDS REVISION`: Any calculation error in questions/solutions, any answer-key label contradiction, or any major factual inaccuracy.
  2. **Machine-Readable JSON Summary Block:** Mandated an appended JSON block at the conclusion of the markdown report:
     ```json
     {
       "audit_version": "3.0",
       "verdict": "PASS | PASS WITH WARNINGS | NEEDS REVISION",
       "total_claims_audited": 0,
       "grounded_claims": 0,
       "unsupported_claims": 0,
       "arithmetic_errors": 0,
       "label_contradictions": 0,
       "manual_review_items": 0
     }
     ```
  3. **Side-by-Side Correction Table:** Added Section 5 providing direct side-by-side remediation:
     `Item | Generated Content | Audited Truth / Correct Calculation | Impact on Student Revision`.
  4. **Anti-False-Positive Directive:** Instructed the auditor to distinguish harmless pedagogical phrasing from genuine factual hallucination.
- **Rationale Linked to Evidence:** Transforms P3 from a purely human-readable report into an automated verification gate that can programmatically drive UI alerts and block invalid study packs from being exported.

---

## 6. Summary of Version Files Catalog

The nine prompt version files are permanently archived in the repository as follows:

```
prompts/versions/
├── P1_v1.txt   (Analyzed live on Groq gpt-oss-120b; baseline revision notes generator)
├── P1_v2.txt   (Refined boundary rules, zero-hallucination clarification constraints)
├── P1_v3.txt   (Dual gap categorization, comparative matrices, standardized formula blocks)
├── P2_v1.txt   (Analyzed live on Groq gpt-oss-120b; practice question generator)
├── P2_v2.txt   (Two-pass verification, label alignment guarantee, conservation checks)
├── P2_v3.txt   (4-step calculation scratchpad schema, distractor analysis, self-contained prompts)
├── P3_v1.txt   (Analyzed live on Groq gpt-oss-120b; content verification auditor)
├── P3_v2.txt   (Dual audit tables, explicit label contradiction protocol, bracketed citations)
└── P3_v3.txt   (Machine-readable JSON schema block, objective decision matrix, side-by-side corrections)
```

All source code files in the production workspace remain aligned with the tested v1 baseline, ensuring system stability while documenting a clear, academically sound evolutionary trajectory for future iterations.
