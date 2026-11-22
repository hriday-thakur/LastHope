"""
Prompt 2 (P2): Revision Question Generator for LastHope.
Generates balanced, exam-oriented practice questions (MCQ, Short Answer, Conceptual)
with difficulty ratings, page references, and an unspoilered answer key based on
original lecture text and P1 analysis.
"""

from typing import Optional
from utils.groq_client import generate_response

# -----------------------------------------------------------------------------
# System Prompt: Defines Assessment Persona, Rules, and Output Layout
# -----------------------------------------------------------------------------
P2_SYSTEM_PROMPT = """You are an expert academic assessment specialist and exam question designer.
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
"""

# -----------------------------------------------------------------------------
# User Prompt Template
# -----------------------------------------------------------------------------
P2_USER_PROMPT_TEMPLATE = """Please generate {num_questions} high-yield revision practice questions based on the following lecture materials.

--- BEGIN ORIGINAL LECTURE TEXT ---
{lecture_text}
--- END ORIGINAL LECTURE TEXT ---

--- BEGIN STRUCTURED LECTURE ANALYSIS (P1) ---
{analysis_text}
--- END STRUCTURED LECTURE ANALYSIS (P1) ---

Generate a balanced mix of Multiple-Choice, Short-Answer, and Conceptual/Application questions with difficulty ratings, page references, and an unspoilered complete answer key with explanations.
"""


def format_p2_user_prompt(
    lecture_text: str,
    analysis_text: str,
    num_questions: int = 10,
) -> str:
    """Formats the P2 user prompt with lecture text, P1 analysis, and question count."""
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


def generate_questions(
    lecture_text: str,
    analysis_text: str,
    num_questions: int = 10,
    model: Optional[str] = None,
    temperature: float = 0.3,
    timeout: float = 120.0,
) -> str:
    """
    Executes Prompt 2 (P2): Generates revision questions across difficulty tiers
    and cognitive levels with answers and explanations.

    Args:
        lecture_text: The original cleaned lecture text with page numbers.
        analysis_text: The structured notes generated by Prompt 1.
        num_questions: Total number of practice questions desired (default 10).
        model: Optional model override.
        temperature: Temperature setting (default 0.3 for balanced creativity & precision).
        timeout: Request timeout in seconds.

    Returns:
        Structured Markdown text containing practice questions and answer key.
    """
    user_prompt = format_p2_user_prompt(
        lecture_text=lecture_text,
        analysis_text=analysis_text,
        num_questions=num_questions,
    )

    return generate_response(
        system_prompt=P2_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        timeout=timeout,
    )
