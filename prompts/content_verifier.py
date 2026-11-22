"""
Prompt 3 (P3): Content Verification Assistant for LastHope.
Audits AI-generated lecture summaries (P1) and practice questions (P2) against
the original lecture text. Identifies unsupported claims, checks arithmetic step by step,
and provides an actionable verification report with PASS / PASS WITH WARNINGS / NEEDS REVISION status.
"""

from typing import Optional
from utils.groq_client import generate_response

# -----------------------------------------------------------------------------
# System Prompt: Defines Auditor Persona, Rules, and Output Schema
# -----------------------------------------------------------------------------
P3_SYSTEM_PROMPT = """You are a rigorous academic content reviewer, auditor, and fact-checking assistant.
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
"""

# -----------------------------------------------------------------------------
# User Prompt Template
# -----------------------------------------------------------------------------
P3_USER_PROMPT_TEMPLATE = """Please perform a rigorous academic audit and fact-check of the following AI-generated revision materials against the original lecture source text.

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
"""


def format_p3_user_prompt(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
) -> str:
    """Formats the P3 user prompt with lecture text, P1 analysis, and P2 questions."""
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


def verify_content(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
    model: Optional[str] = None,
    temperature: float = 0.1,
    timeout: float = 120.0,
) -> str:
    """
    Executes Prompt 3 (P3): Cross-examines generated P1 analysis and P2 questions
    against the original lecture text, verifies calculations, detects hallucinated
    claims, and outputs a structured verification audit.

    Args:
        lecture_text: The primary ground truth source text.
        analysis_text: The structured notes generated by Prompt 1.
        questions_text: The questions and answer key generated by Prompt 2.
        model: Optional model override (defaults to GROQ_MODEL in .env).
        temperature: Low temperature (0.1) for rigorous, objective auditing.
        timeout: Request timeout in seconds.

    Returns:
        Structured Markdown verification report with status and recommendations.
    """
    user_prompt = format_p3_user_prompt(
        lecture_text=lecture_text,
        analysis_text=analysis_text,
        questions_text=questions_text,
    )

    return generate_response(
        system_prompt=P3_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        timeout=timeout,
    )
