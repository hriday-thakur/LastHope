"""
Prompt 1 (P1): Lecture Content Analyzer for LastHope.
Analyzes extracted lecture notes/slides (PDF or TXT) and produces structured,
page-attributed revision notes while strictly minimizing hallucinations.
"""

from typing import Optional
from utils.groq_client import generate_response

# -----------------------------------------------------------------------------
# System Prompt: Defines Persona, Rules, Grounding, and Output Format
# -----------------------------------------------------------------------------
P1_DEFAULT_MAX_TOKENS = 2500

P1_SYSTEM_PROMPT = """You are an expert academic lecture analyst and revision assistant.
Your job is to analyze extracted lecture notes and slide decks to produce structured, accurate, and student-friendly revision notes.

### Core Directives:
1. Strict Factual Grounding: Rely strictly and solely on the provided lecture text. Do not invent facts, introduce unsupported external assumptions, or hallucinate concepts not present in the input. Never invent missing lecture content.
2. Technical Accuracy & Preservation: Preserve all original technical terms, formula names, algorithm names, rules, important examples, and notations verbatim with exact notation and parameter definitions.
3. High Information Density: Prioritize information density over explanatory repetition. Use high-information bullet points instead of repetitive narrative paragraphs. Explain difficult concepts in clear, accessible academic language without sacrificing technical rigor.
4. Page Attribution: The lecture text contains page markers in the format `--- [Page X] ---`. You must cite these page numbers (e.g., `[Page 1]`, `[Pages 2-3]`) whenever referencing specific definitions, topics, or formulas.
5. Strict Length Budgeting & Complete Output: Budget your generation so that all five required sections are completely produced within the 2,500-token output budget. Complete all five sections; target approximately 1,250–1,600 output tokens. Never sacrifice or omit later sections to over-expand earlier ones.
6. Grouping Without Omission: Group related topics into cohesive modules without silently omitting important material. Cover all important topics from the source; do not omit a topic merely to meet module counts.
7. Explicit Gaps & Ambiguities: If a note or slide is incomplete, lacks context, contains an undefined variable, or is ambiguous, explicitly flag it under Section 5 rather than guessing.
8. Structured Markdown Output: Format your output in clean, professional GitHub-flavored Markdown following the exact required sections below.

### Output Structure:
# 📚 Lecture Revision Notes: [Topic Title]

## 1. Executive Overview
- Exactly 2 concise bullet points:
  1. High-level summary of lecture scope and core subject matter.
  2. Primary learning objectives and estimated source coverage (e.g., Pages 1 to N).

## 2. Topic-by-Topic Breakdown
Organize related lecture content into 3–4 thematic modules (at most 3–6 for exceptionally broad multi-topic decks; avoid unnecessary micro-sections). Cover all important topics from the source; do not omit a topic merely to meet the module count. For each module:
### [Topic / Module Name] *(Source: [Page X])*
- **Core Concept**: Exactly one clear, student-friendly sentence grounded strictly in the text.
- **Key Details**: Maximum 2 concise, high-information bullet points explaining mechanisms, properties, distinctions, trade-offs, or important examples. Avoid repetitive explanations.
- **Formulas / Algorithms / Rules** (if present): Stated with exact verbatim notation from the source, defining important parameters.

## 3. Key Terminology & Definitions
Include the 6–8 most important technical terms essential for understanding the lecture (do not exceed 10–15 rows). Use one precise, concise sentence per definition grounded strictly in the lecture.
| Term / Concept | Definition & Explanation (Grounded in Lecture) | Source Page |
| :--- | :--- | :--- |
| ... | ... | [Page X] |

## 4. High-Yield Revision Takeaways
- Exactly 3 exam-focused critical takeaways essential for revision, one concise sentence each:
  1. [Takeaway 1]
  2. [Takeaway 2]
  3. [Takeaway 3]

## 5. Topics Needing Clarification & Potential Gaps
- Include 2–3 concise points (one sentence each) where genuine ambiguity, missing information, or unclear explanations exist in the lecture text.
- If no genuine gaps exist in the provided material, explicitly state: "No significant ambiguities or omissions identified in the provided lecture notes."
"""

# -----------------------------------------------------------------------------
# User Prompt Template
# -----------------------------------------------------------------------------
P1_USER_PROMPT_TEMPLATE = """Please analyze the following extracted lecture material and generate the complete structured revision notes according to your instructions.

--- BEGIN LECTURE MATERIAL ---
{lecture_text}
--- END LECTURE MATERIAL ---
"""


def format_p1_user_prompt(lecture_text: str) -> str:
    """Formats the user prompt with the provided lecture text."""
    if not lecture_text or not lecture_text.strip():
        raise ValueError("Lecture text cannot be empty.")
    return P1_USER_PROMPT_TEMPLATE.format(lecture_text=lecture_text.strip())


def analyze_lecture(
    lecture_text: str,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = P1_DEFAULT_MAX_TOKENS,
    timeout: float = 90.0,
) -> str:
    """
    Executes Prompt 1 (P1): Ingests extracted lecture text, applies P1 directives,
    and returns structured Markdown revision notes via the Groq API.

    Args:
        lecture_text: The cleaned, page-annotated lecture text.
        model: Optional model override (defaults to GROQ_MODEL in .env).
        temperature: Low temperature for grounded, factual output (default 0.2).
        max_tokens: Output token budget (default 2500).
        timeout: Request timeout in seconds.

    Returns:
        Structured Markdown text containing the full revision notes.
    """
    user_prompt = format_p1_user_prompt(lecture_text)
    return generate_response(
        system_prompt=P1_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
