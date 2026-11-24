"""
Prompt 2 (P2): Revision Question Generator for LastHope.
Generates balanced, exam-oriented practice questions (MCQ, Short Answer, Conceptual)
with difficulty ratings, page references, and an unspoilered answer key based on
the structured P1 lecture analysis as the primary ground truth.
"""

from typing import Optional
from utils.groq_client import generate_response, OutputTruncatedError


class MissingAnalysisError(ValueError):
    """Raised when structured lecture analysis (P1) is missing or empty."""
    pass


class IncompleteQuestionSetError(ValueError):
    """Raised when generated questions are incomplete or missing the required answer key."""
    pass


def calculate_p2_max_tokens(num_questions: int) -> int:
    """
    Dynamically scales max_tokens based on requested question volume:
    - 5 questions: 1200 tokens
    - 10 questions: 2048 tokens
    - 15 questions: 2800 tokens
    """
    count = int(num_questions)
    if count <= 5:
        return 1200
    elif count <= 10:
        return 2048
    else:
        return 2800


# -----------------------------------------------------------------------------
# System Prompt: Defines Assessment Persona, Rules, and Output Layout
# -----------------------------------------------------------------------------
P2_SYSTEM_PROMPT = """You are an expert academic assessment specialist and exam question designer.
Your mission is to generate high-yield, exam-oriented revision practice questions based solely on the provided structured lecture analysis.

### Core Directives:
1. Strict Grounding in Material: Every question, answer option, and explanation must be directly derivable from the provided structured lecture analysis. The analysis contains verified lecture concepts, mechanisms, definitions, formulas, and source page citations ([Page X]). Never introduce external concepts, unmentioned facts, or outside curriculum.
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
5. Page Citations: Preserve and cite the relevant source page (e.g., `[Page X]`) from the structured analysis for every question and answer.
6. Self-Testing Friendly Layout: Group all questions together first (so students can test their recall without spoilers), followed by a clear dividing line and a comprehensive, step-by-step Answer Key & Explanations section.
7. Completeness & Concise Pacing:
   - Prioritize completing every single requested question AND its corresponding complete model answer or explanation.
   - Never omit questions or truncate the answer key to save space.
   - Keep justifications and model answers concise, focused, and technically exact (e.g., 1-2 focused sentences per MCQ explanation, 2 concise sentences for short answers, and clear step-by-step arithmetic) so all sections and the complete answer key conclude cleanly within the generation window.

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
P2_USER_PROMPT_TEMPLATE = """Please generate {num_questions} high-yield revision practice questions based on the following structured lecture analysis.

--- BEGIN STRUCTURED LECTURE ANALYSIS (P1) ---
{analysis_text}
--- END STRUCTURED LECTURE ANALYSIS (P1) ---

Requirements:
- Generate a balanced mix of Multiple-Choice, Short-Answer, and Conceptual/Application questions totaling {num_questions} questions.
- Preserve [Page X] citations from the analysis for every question and answer.
- Prioritize completing every single question and its unspoilered answer key and explanation. Keep explanations concise, technically rigorous, and complete.
- Include all required sections and the full Part 2 Complete Answer Key & Explanations. Do not omit questions or answers.
"""


def format_p2_user_prompt(
    lecture_text: Optional[str] = None,
    analysis_text: Optional[str] = None,
    num_questions: int = 10,
) -> str:
    """
    Formats the P2 user prompt using structured lecture analysis (P1) as the primary ground truth.
    Accepts lecture_text for backward-compatible call signatures, but does not inject raw
    lecture text into the prompt when analysis_text is provided to prevent token duplication.
    """
    target_analysis = analysis_text
    if target_analysis is None and lecture_text is not None:
        target_analysis = lecture_text

    if not target_analysis or not str(target_analysis).strip():
        raise MissingAnalysisError(
            "Structured lecture analysis (P1) is missing or empty. "
            "Questions cannot be generated without verified lecture analysis."
        )

    safe_count = max(1, min(int(num_questions), 30))

    return P2_USER_PROMPT_TEMPLATE.format(
        analysis_text=str(target_analysis).strip(),
        num_questions=safe_count,
    )


def generate_questions(
    lecture_text: Optional[str] = None,
    analysis_text: Optional[str] = None,
    num_questions: int = 10,
    model: Optional[str] = None,
    temperature: float = 0.3,
    timeout: float = 120.0,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Executes Prompt 2 (P2): Generates revision questions across difficulty tiers
    and cognitive levels with answers and explanations based on P1 structured analysis.

    Args:
        lecture_text: Optional/legacy lecture text preserved for backward-compatible call signatures.
        analysis_text: The structured notes generated by Prompt 1 (primary ground truth).
        num_questions: Total number of practice questions desired (default 10).
        model: Optional model override.
        temperature: Temperature setting (default 0.3 for balanced creativity & precision).
        timeout: Request timeout in seconds.
        max_tokens: Maximum tokens in response completion (defaults dynamically: 5->1200, 10->2048, 15->2800).

    Returns:
        Structured Markdown text containing practice questions and answer key.
    """
    target_analysis = analysis_text
    if target_analysis is None and lecture_text is not None and not analysis_text:
        target_analysis = lecture_text

    if not target_analysis or not str(target_analysis).strip():
        raise MissingAnalysisError(
            "Structured lecture analysis (P1) is missing or empty. "
            "Questions cannot be generated without verified lecture analysis."
        )

    # Determine dynamic token budget if not explicitly overridden
    effective_max_tokens = (
        max_tokens if (max_tokens is not None and max_tokens > 0)
        else calculate_p2_max_tokens(num_questions)
    )

    user_prompt = format_p2_user_prompt(
        lecture_text=lecture_text,
        analysis_text=target_analysis,
        num_questions=num_questions,
    )

    response = generate_response(
        system_prompt=P2_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=model,
        temperature=temperature,
        max_tokens=effective_max_tokens,
        timeout=timeout,
    )

    # Validate that the answer key was not omitted or cut off
    if "## Part 2" not in response and "Answer Key" not in response:
        raise IncompleteQuestionSetError(
            "Generated output is missing the required Complete Answer Key & Explanations (Part 2). "
            "The generation was incomplete. Please try generating with a smaller question volume."
        )

    return response
