"""
Prompt 3 (P3): Content Verification Assistant for LastHope.
Audits AI-generated lecture summaries (P1) and practice questions (P2) against
the original lecture source evidence. Identifies unsupported claims, checks arithmetic
step by step, and provides an actionable verification report with
PASS / PASS WITH WARNINGS / NEEDS REVISION status.
Optimized for strict Groq 8,000 TPM limit compliance through compact evidence extraction.
"""

from typing import Optional
import re
from utils.groq_client import generate_response

# -----------------------------------------------------------------------------
# Configuration & Output Budget
# -----------------------------------------------------------------------------
# 1200 output tokens provides ample room for a complete 7-section audit report
# while reserving only 1,200 tokens upfront against Groq's 8,000 TPM limit.
P3_DEFAULT_MAX_TOKENS = 1200

# -----------------------------------------------------------------------------
# System Prompt: Defines Auditor Persona, Rules, and Output Schema
# -----------------------------------------------------------------------------
P3_SYSTEM_PROMPT = """You are a rigorous academic content reviewer, auditor, and fact-checking assistant.
Your mission is to audit AI-generated lecture summaries (P1) and practice questions (P2) against the original lecture source evidence, ensuring factual precision, syllabus fidelity, and mathematical correctness.

### Core Directives:
1. Primary Source of Truth: The Original Lecture Evidence is the ONLY ground truth. If a claim in P1 or P2 is not supported by or contradicts the source evidence, flag it as unsupported or inaccurate—regardless of whether it sounds plausible.
2. Independent Verification: Never assume a claim is verified simply because P1 and P2 agree with each other. Evaluate both strictly against the source text.
3. Mathematical Auditing: Re-calculate all mathematical formulas, numeric problems, and cycle counts step by step. Highlight arithmetic errors and provide the corrected calculation.
4. Non-Fabrication: Never invent source citations not present in the original text.
5. Uncertainty: If a claim cannot be verified with confidence from the provided evidence, explicitly mark it as: "[MANUAL REVIEW REQUIRED]".
6. Transparent Disclaimer: You must explicitly state in your report that this review is an AI-assisted quality assessment and does not constitute a 100% guarantee of factual perfection.
7. Concise Reporting: Be dense, objective, and concise. Complete all sections within 600–900 words without unnecessary fluff.

### Output Structure:
# 🛡️ Content Verification & Fact-Check Report

> **Disclaimer:** *This is an AI-assisted academic verification report intended to aid revision quality. It does not provide an absolute guarantee of correctness. Students and educators should cross-reference original course materials for high-stakes exam preparation.*

## 1. Executive Verification Summary
- Overall assessment of alignment between generated materials and original lecture notes.
- Summary of verified points vs. flagged concerns.
- **Audit Verdict:** [PASS / PASS WITH WARNINGS / NEEDS REVISION]

## 2. Verified Claims & Grounded Concepts
List key concepts, definitions, and questions fully supported by the lecture text (3–5 concise bullets):
- ✅ **[Claim / Concept]**: Confirmed grounded. *(Source: [Page X])*

## 3. Unsupported or Inaccurate Claims
List points in P1 or P2 that introduce outside facts, misrepresent concepts, or lack source backing (or 'None detected'):
- ❌ **[Claim / Statement]**: Explanation of why it is unsupported or inaccurate based on the lecture text. *(Source: [Page X] or "Absent from Source")*

## 4. Mathematical & Calculation Checks
Re-compute all formulas, numeric questions, and answer keys:
- 🧮 **[Problem / Formula Checked]**:
  - *Given in Generated Material:* [Original formula / problem statement]
  - *Step-by-Step Verification:* [Calculations]
  - *Verdict:* [Correct / Calculation Error Detected]
  - *Corrected Solution (if needed):* [Clear breakdown]

## 5. Context Gaps & Ambiguities
- Note any oversimplified definitions, omitted caveats, or deferred topics that may mislead students.

## 6. Actionable Recommended Corrections
- Concrete, bulleted recommendations to correct P1 notes or P2 questions before final study.

## 7. Final Review Status
- **Final Status:** **[PASS | PASS WITH WARNINGS | NEEDS REVISION]**
- **Justification:** Clear 1-2 sentence conclusion explaining the assigned status.
"""

# -----------------------------------------------------------------------------
# User Prompt Template
# -----------------------------------------------------------------------------
P3_USER_PROMPT_TEMPLATE = """Please perform a rigorous academic audit and fact-check of the following AI-generated revision materials against the original lecture source evidence.

--- BEGIN ORIGINAL LECTURE SOURCE EVIDENCE ---
{lecture_text}
--- END ORIGINAL LECTURE SOURCE EVIDENCE ---

--- BEGIN GENERATED LECTURE ANALYSIS (P1) ---
{analysis_text}
--- END GENERATED LECTURE ANALYSIS (P1) ---

--- BEGIN GENERATED REVISION QUESTIONS & ANSWER KEY (P2) ---
{questions_text}
--- END GENERATED REVISION QUESTIONS & ANSWER KEY (P2) ---

Conduct a thorough cross-examination, audit any mathematical calculations step by step, verify page attributions, flag hallucinations or external assumptions, and provide an actionable report with a final status of PASS, PASS WITH WARNINGS, or NEEDS REVISION.
"""


def clean_lecture_page(page_content: str) -> str:
    """Strips presentation noise, repeated borders, and excessive blank lines."""
    lines = page_content.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("===") or s.startswith("___") or (s.startswith("---") and not s.startswith("--- [Page")):
            continue
        cleaned.append(s)
    return "\n".join(cleaned)


def extract_evidence_payload(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
) -> str:
    """
    Extracts relevant source pages cited in P1 and P2 from the original lecture text.
    - If page markers (--- [Page X] ---) exist, prioritizes pages cited in P1 and P2.
    - If total pages <= 6 or no citations found, includes all pages with formatting noise stripped.
    - If total pages > 6, includes cited pages in full and provides topic headers for un-cited pages.
    - If no page markers exist, condenses whitespace and presentation dividers.
    - Always preserves exact formulas, equations, definitions, numbers, and technical terms.
    """
    if not lecture_text or not lecture_text.strip():
        return ""

    text = lecture_text.replace("\r\n", "\n").strip()
    page_splits = list(re.finditer(r"---\s*\[Page\s*(\d+)\]\s*---", text, re.IGNORECASE))
    if not page_splits:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        return "\n".join(lines)

    pages = {}
    for i, match in enumerate(page_splits):
        p_num = match.group(1)
        start_idx = match.end()
        end_idx = page_splits[i + 1].start() if (i + 1 < len(page_splits)) else len(text)
        pages[p_num] = text[start_idx:end_idx].strip()

    cited_nums = set(re.findall(r"\[Page\s*(\d+)\]", analysis_text + " " + questions_text, re.IGNORECASE))

    # If small lecture (<= 6 pages) or no page citations found, include all pages with cleaned noise
    if len(pages) <= 6 or not cited_nums:
        evidence = []
        for p_num, body in pages.items():
            cb = clean_lecture_page(body)
            evidence.append(f"--- [Page {p_num}] ---\n{cb}")
        return "\n\n".join(evidence)

    evidence = []
    for p_num, body in pages.items():
        if p_num in cited_nums:
            cb = clean_lecture_page(body)
            evidence.append(f"--- [Page {p_num}] (CITED SOURCE EVIDENCE) ---\n{cb}")
        else:
            first_line = next((l.strip() for l in body.split("\n") if l.strip()), "Unspecified")
            evidence.append(f"--- [Page {p_num}] ---\n[Section/Topic: {first_line[:80]}] (Unreferenced in generated materials)")

    return "\n\n".join(evidence)


def streamline_p1_analysis_for_audit(analysis_text: str) -> str:
    """
    Streamlines P1 lecture analysis for the P3 audit payload to minimize token redundancy.
    - Preserves all Core Concepts, Key Details, Formulas, Algorithms, Rules, and Takeaways.
    - Preserves all [Page X] citations and technical terminology.
    - Converts heavy Markdown tables into compact bullet points to eliminate table syntax overhead.
    - Strips decorative dividers and redundant whitespace.
    """
    if not analysis_text or not analysis_text.strip():
        return ""

    text = analysis_text.replace("\r\n", "\n").strip()

    # Split into sections by markdown heading (##)
    sections = re.split(r"\n(?=## \d+[\.\s])", text)
    processed_sections = []

    for sec in sections:
        sec_stripped = sec.strip()
        if not sec_stripped:
            continue

        # Check if this is Section 3: Key Terminology & Definitions
        if re.search(r"## 3\.\s+Key Terminology", sec_stripped, re.IGNORECASE):
            lines = sec_stripped.split("\n")
            header = lines[0]
            term_lines = []
            for line in lines[1:]:
                l_str = line.strip()
                if not l_str or l_str.startswith("---") or ":---" in l_str:
                    continue
                if l_str.startswith("|") and ("Term" in l_str or "Concept" in l_str):
                    continue
                if l_str.startswith("|"):
                    cells = [c.strip() for c in l_str.split("|")[1:-1]]
                    if len(cells) >= 3:
                        term, defn, page = cells[0], cells[1], cells[2]
                        term_lines.append(f"- **{term}** ({page}): {defn}")
                    elif len(cells) == 2:
                        term, defn = cells[0], cells[1]
                        term_lines.append(f"- **{term}**: {defn}")
                    elif len(cells) == 1 and cells[0]:
                        term_lines.append(f"- **{cells[0]}**")
                else:
                    term_lines.append(l_str)

            compact_sec = header + "\n" + "\n".join(term_lines)
            processed_sections.append(compact_sec)
        else:
            # For Sections 1, 2, 4, 5: retain complete content, strip decorative dividers
            cleaned_lines = [l for l in sec_stripped.split("\n") if not l.strip().startswith("---")]
            processed_sections.append("\n".join(cleaned_lines))

    result = "\n\n".join(processed_sections).strip()
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def streamline_p2_questions_for_audit(questions_text: str) -> str:
    """
    Streamlines P2 questions for the audit payload:
    - In Part 1: Preserves all question stems and difficulty tiers while stripping
      redundant MCQ distractor options (- A), - B), etc.) that inflate token usage.
    - In Part 2: Preserves complete answer keys, correct option letters, step-by-step
      arithmetic, explanations, and [Page X] citations verbatim.
    - Strips decorative divider lines and excess blank lines.
    """
    if not questions_text or not questions_text.strip():
        return ""

    text = questions_text.replace("\r\n", "\n").strip()
    if "## Part 2" not in text:
        # Fallback: strip decorative dividers
        return "\n".join([l for l in text.split("\n") if not l.strip().startswith("---")]).strip()

    parts = text.split("## Part 2", 1)
    q_part = parts[0].strip()
    a_part = "## Part 2" + parts[1]

    # In Part 1: strip distractor options (lines matching - A), - B), etc.)
    q_lines = []
    for line in q_part.split("\n"):
        s = line.strip()
        if re.match(r"^[-\*]\s*[A-D]\)", s) or s.startswith("---"):
            continue
        q_lines.append(line)

    cleaned_q = "\n".join(q_lines).strip()
    cleaned_a = "\n".join([l for l in a_part.split("\n") if not l.strip().startswith("---")]).strip()

    combined = cleaned_q + "\n\n" + cleaned_a
    return re.sub(r"\n{3,}", "\n\n", combined).strip()


def format_p3_user_prompt(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
) -> str:
    """Formats the P3 user prompt with compact evidence payload and streamlined P1/P2."""
    if not lecture_text or not lecture_text.strip():
        raise ValueError("Original lecture text cannot be empty.")
    if not analysis_text or not analysis_text.strip():
        raise ValueError("Lecture analysis (P1) cannot be empty.")
    if not questions_text or not questions_text.strip():
        raise ValueError("Questions and answer key (P2) cannot be empty.")

    compact_lecture = extract_evidence_payload(lecture_text, analysis_text, questions_text)
    streamlined_p1 = streamline_p1_analysis_for_audit(analysis_text)
    streamlined_p2 = streamline_p2_questions_for_audit(questions_text)

    return P3_USER_PROMPT_TEMPLATE.format(
        lecture_text=compact_lecture if compact_lecture else lecture_text.strip(),
        analysis_text=streamlined_p1 if streamlined_p1 else analysis_text.strip(),
        questions_text=streamlined_p2 if streamlined_p2 else questions_text.strip(),
    )


def verify_content(
    lecture_text: str,
    analysis_text: str,
    questions_text: str,
    model: Optional[str] = None,
    temperature: float = 0.1,
    timeout: float = 120.0,
    max_tokens: int = P3_DEFAULT_MAX_TOKENS,
) -> str:
    """
    Executes Prompt 3 (P3): Cross-examines generated P1 analysis and P2 questions
    against the original lecture text, verifies calculations, detects hallucinated
    claims, and outputs a structured verification audit.

    Preserves exact backward-compatible parameter ordering:
    (lecture_text, analysis_text, questions_text, model, temperature, timeout, max_tokens)

    Args:
        lecture_text: The primary ground truth source text.
        analysis_text: The structured notes generated by Prompt 1.
        questions_text: The questions and answer key generated by Prompt 2.
        model: Optional model override (defaults to GROQ_MODEL in .env).
        temperature: Low temperature (0.1) for rigorous, objective auditing.
        timeout: Request timeout in seconds.
        max_tokens: Output token limit (defaults to P3_DEFAULT_MAX_TOKENS = 1200).

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
        max_tokens=max_tokens,
        timeout=timeout,
    )
