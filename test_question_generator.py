"""
Offline unit and contract test suite for Prompt 2 (P2): Revision Question Generator.
Verifies:
1. Non-duplication of raw lecture text when P1 analysis is provided.
2. P1 structured analysis is passed and formatted correctly.
3. Dynamic token budgets: 5 -> 1200, 10 -> 2048, 15 -> 2800 tokens.
4. Custom max_tokens overrides are preserved.
5. Missing or empty P1 analysis raises MissingAnalysisError (subclass of ValueError).
6. Truncated output (finish_reason='length') raises OutputTruncatedError.
7. Incomplete output (missing Part 2 answer key) raises IncompleteQuestionSetError.
8. Concise-output and completeness instructions are present in P2 system and user prompts.
9. Existing question-generation output requirements and structural criteria remain intact.
10. Backward-compatible function signatures (positional & keyword).

This test suite runs 100% offline without making live Groq API calls.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.groq_client import OutputTruncatedError, generate_response
from prompts.question_generator import (
    P2_SYSTEM_PROMPT,
    P2_USER_PROMPT_TEMPLATE,
    MissingAnalysisError,
    IncompleteQuestionSetError,
    calculate_p2_max_tokens,
    format_p2_user_prompt,
    generate_questions,
)

SAMPLE_LECTURE_TEXT = """--- [Page 1] ---
CS301: Computer Architecture
Lecture 7: Cache Memory & Memory Hierarchy Basics
Instructor: Dr. Alan Vance

Memory Hierarchy Overview:
- Processors operate at GHz speeds, while main memory (DRAM) is much slower (the "Memory Wall").
- SRAM (Static RAM) is used for caches: fast, expensive, volatile, low density.
- DRAM (Dynamic RAM) is used for main memory: slower, cheaper, high density, requires periodic refresh cycles.
- Locality Principle:
  1. Temporal Locality: If an address is accessed, it will likely be accessed again soon.
  2. Spatial Locality: If an address is accessed, nearby addresses will likely be accessed soon.
"""

SAMPLE_P1_ANALYSIS = """# 📚 Lecture Revision Notes: Cache Memory & Memory Hierarchy Basics

## 1. Executive Overview
- Scope: Memory hierarchy fundamentals covering SRAM caches and DRAM main memory. *(Source: [Page 1])*

## 2. Topic-by-Topic Breakdown
### Memory Hierarchy Overview *(Source: [Page 1])*
- **Core Concept**: Bridges the processor-memory speed gap.
- **Key Details**: SRAM is fast and volatile; DRAM is dense and requires refresh cycles.
- **Formulas / Rules**: AMAT = Hit_Time + (Miss_Rate * Miss_Penalty) *(Source: [Page 2])*

## 3. Key Terminology & Definitions
| Term / Concept | Definition & Explanation | Source Page |
| :--- | :--- | :--- |
| Temporal Locality | Re-accessing recently used memory | [Page 1] |
| Spatial Locality | Accessing nearby memory addresses | [Page 1] |

## 4. High-Yield Revision Takeaways
- SRAM vs. DRAM trade-offs determine cache vs. main memory design.
"""

SAMPLE_P2_OUTPUT = """# 📝 Revision Practice Questions: Cache Memory

## Part 1: Questions (Practice Mode)

### Section A: Multiple-Choice Questions
1. **[Easy]** Which type of memory is primarily utilized for CPU cache levels? *(Source: [Page 1])*
   - A) DRAM
   - B) SRAM
   - C) Flash ROM
   - D) Magnetic Disk

### Section B: Short-Answer Questions
2. **[Medium]** Distinguish between temporal and spatial locality in computer memory systems. *(Source: [Page 1])*

### Section C: Conceptual & Application Questions
3. **[Hard]** Calculate the Average Memory Access Time (AMAT) given Hit Time = 2 cycles, Miss Rate = 5%, and Miss Penalty = 80 cycles. *(Source: [Page 2])*

---

## Part 2: Complete Answer Key & Explanations

### Multiple-Choice Answers
1. **Correct Answer: B**
   - **Explanation:** SRAM (Static RAM) is fast and used for caches, whereas DRAM is used for main memory.
   - **Source:** [Page 1]

### Short-Answer Model Answers
2. **Model Answer:** Temporal locality refers to re-accessing recently referenced memory addresses soon. Spatial locality refers to accessing memory locations physically adjacent to recently accessed locations. *(Source: [Page 1])*

### Conceptual & Application Solutions
3. **Solution:** AMAT = Hit_Time + (Miss_Rate * Miss_Penalty) = 2 + (0.05 * 80) = 2 + 4 = 6 cycles. *(Source: [Page 2])*
"""


def test_non_duplication_of_raw_lecture_text():
    """Verifies raw lecture text is NOT injected into the prompt when P1 analysis is provided."""
    raw_canary = "UNIQUE_RAW_LECTURE_CANARY_TOKEN_998877"
    raw_text = f"{raw_canary}\n{SAMPLE_LECTURE_TEXT}"
    p1_notes = SAMPLE_P1_ANALYSIS

    prompt = format_p2_user_prompt(
        lecture_text=raw_text,
        analysis_text=p1_notes,
        num_questions=10,
    )

    assert p1_notes.strip() in prompt, "P1 analysis must be present in the user prompt."
    assert raw_canary not in prompt, "Raw lecture text must NOT be duplicated into the P2 prompt."
    print(" [PASS] test_non_duplication_of_raw_lecture_text")


def test_p1_analysis_passed_correctly():
    """Verifies P1 analysis is correctly formatted with boundary markers and question count."""
    p1_notes = "Structured analysis notes for testing."
    prompt = format_p2_user_prompt(analysis_text=p1_notes, num_questions=8)

    assert "--- BEGIN STRUCTURED LECTURE ANALYSIS (P1) ---" in prompt
    assert p1_notes in prompt
    assert "--- END STRUCTURED LECTURE ANALYSIS (P1) ---" in prompt
    assert "8 high-yield revision practice questions" in prompt
    print(" [PASS] test_p1_analysis_passed_correctly")


def test_dynamic_token_budgets():
    """Verifies that max_tokens scales dynamically based on question volume (5->1200, 10->2048, 15->2800)."""
    assert calculate_p2_max_tokens(5) == 1200
    assert calculate_p2_max_tokens(10) == 2048
    assert calculate_p2_max_tokens(15) == 2800

    # Test through generate_questions with patch
    with patch("prompts.question_generator.generate_response", return_value=SAMPLE_P2_OUTPUT) as mock_gen:
        # 5 questions -> 1200
        generate_questions(analysis_text=SAMPLE_P1_ANALYSIS, num_questions=5)
        assert mock_gen.call_args[1].get("max_tokens") == 1200

        # 10 questions -> 2048
        generate_questions(analysis_text=SAMPLE_P1_ANALYSIS, num_questions=10)
        assert mock_gen.call_args[1].get("max_tokens") == 2048

        # 15 questions -> 2800
        generate_questions(analysis_text=SAMPLE_P1_ANALYSIS, num_questions=15)
        assert mock_gen.call_args[1].get("max_tokens") == 2800

    print(" [PASS] test_dynamic_token_budgets (5->1200, 10->2048, 15->2800)")


def test_custom_max_tokens_override():
    """Verifies that max_tokens can be customized and overrides dynamic scaling."""
    with patch("prompts.question_generator.generate_response", return_value=SAMPLE_P2_OUTPUT) as mock_gen:
        generate_questions(
            analysis_text=SAMPLE_P1_ANALYSIS,
            num_questions=15,
            max_tokens=1500,
        )
        _, kwargs = mock_gen.call_args
        assert kwargs.get("max_tokens") == 1500, f"Expected max_tokens=1500 override, got {kwargs.get('max_tokens')}"

    print(" [PASS] test_custom_max_tokens_override")


def test_truncation_detection_finish_reason_length():
    """Verifies that finish_reason='length' from Groq raises OutputTruncatedError."""
    mock_choice = MagicMock()
    mock_choice.finish_reason = "length"
    mock_choice.message.content = "Truncated text before Part 2..."

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    with patch("utils.groq_client.get_groq_client") as mock_client_factory:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_client_factory.return_value = mock_client

        try:
            generate_response("System Prompt", "User Prompt", max_tokens=2048)
            assert False, "Should have raised OutputTruncatedError when finish_reason='length'"
        except OutputTruncatedError as e:
            assert "finish_reason='length'" in str(e) or "cut off" in str(e).lower()
            assert e.partial_content == "Truncated text before Part 2..."

    print(" [PASS] test_truncation_detection_finish_reason_length")


def test_incomplete_output_missing_answer_key_detection():
    """Verifies that an output missing the answer key raises IncompleteQuestionSetError."""
    incomplete_output = "# 📝 Revision Practice Questions: Cache Memory\n\n## Part 1: Questions\n1. Question 1"

    with patch("prompts.question_generator.generate_response", return_value=incomplete_output):
        try:
            generate_questions(analysis_text=SAMPLE_P1_ANALYSIS, num_questions=10)
            assert False, "Should have raised IncompleteQuestionSetError for missing answer key"
        except IncompleteQuestionSetError as e:
            assert "missing the required complete answer key" in str(e).lower()

    print(" [PASS] test_incomplete_output_missing_answer_key_detection")


def test_concise_instructions_in_prompts():
    """Verifies that P2 system and user prompts include completeness and conciseness directives."""
    assert "Prioritize completing" in P2_USER_PROMPT_TEMPLATE or "Do not omit" in P2_USER_PROMPT_TEMPLATE
    assert "Completeness & Concise Pacing" in P2_SYSTEM_PROMPT or "concise" in P2_SYSTEM_PROMPT.lower()
    assert "Never omit questions or truncate the answer key" in P2_SYSTEM_PROMPT
    print(" [PASS] test_concise_instructions_in_prompts")


def test_missing_or_empty_analysis_handling():
    """Verifies that missing or whitespace-only P1 analysis raises MissingAnalysisError."""
    try:
        format_p2_user_prompt(analysis_text=None)
        assert False, "Should have raised MissingAnalysisError for None"
    except MissingAnalysisError as e:
        assert "missing or empty" in str(e).lower()

    try:
        format_p2_user_prompt(analysis_text="")
        assert False, "Should have raised MissingAnalysisError for empty string"
    except MissingAnalysisError:
        pass

    try:
        format_p2_user_prompt(analysis_text="   \n\t  ")
        assert False, "Should have raised MissingAnalysisError for whitespace"
    except MissingAnalysisError:
        pass

    try:
        generate_questions(analysis_text="")
        assert False, "generate_questions should have raised MissingAnalysisError"
    except MissingAnalysisError:
        pass

    assert issubclass(MissingAnalysisError, ValueError), "MissingAnalysisError must inherit from ValueError"
    assert issubclass(IncompleteQuestionSetError, ValueError), "IncompleteQuestionSetError must inherit from ValueError"

    print(" [PASS] test_missing_or_empty_analysis_handling")


def test_backward_compatible_signatures():
    """Verifies function signature works with legacy keyword arguments and positional arguments."""
    with patch("prompts.question_generator.generate_response", return_value=SAMPLE_P2_OUTPUT):
        # 1. Full keyword call (used by app.py)
        res1 = generate_questions(
            lecture_text=SAMPLE_LECTURE_TEXT,
            analysis_text=SAMPLE_P1_ANALYSIS,
            num_questions=5,
            timeout=150.0,
        )
        assert res1 == SAMPLE_P2_OUTPUT

        # 2. Positional call
        res2 = generate_questions(SAMPLE_LECTURE_TEXT, SAMPLE_P1_ANALYSIS, 5)
        assert res2 == SAMPLE_P2_OUTPUT

        # 3. Analysis-only call
        res3 = generate_questions(analysis_text=SAMPLE_P1_ANALYSIS, num_questions=5)
        assert res3 == SAMPLE_P2_OUTPUT

    print(" [PASS] test_backward_compatible_signatures")


def test_output_structure_requirements():
    """Verifies structural criteria parsing against realistic question output."""
    output = SAMPLE_P2_OUTPUT

    p2_artifact = Path("test_p2_output.md")
    if p2_artifact.exists():
        real_content = p2_artifact.read_text(encoding="utf-8")
        if len(real_content.strip()) > 100:
            output = real_content

    checks = [
        ("Multiple-Choice section present", "Multiple-Choice" in output or "Section A" in output),
        ("Short-Answer section present", "Short-Answer" in output or "Section B" in output),
        ("Conceptual/Application section present", "Conceptual" in output or "Application" in output or "Section C" in output),
        ("Answer Key section present", "Answer Key" in output or "Part 2" in output),
        ("Difficulty tags present", any(tag in output for tag in ["[Easy]", "[Medium]", "[Hard]", "Easy", "Medium", "Hard"])),
        ("Page references present", "[Page" in output),
    ]

    for name, passed in checks:
        assert passed, f"Structural check failed: {name}"

    print(" [PASS] test_output_structure_requirements")


def run_all_offline_tests() -> bool:
    print("=" * 60)
    print("RUNNING P2 QUESTION GENERATOR OFFLINE TEST SUITE")
    print("=" * 60)

    try:
        test_non_duplication_of_raw_lecture_text()
        test_p1_analysis_passed_correctly()
        test_dynamic_token_budgets()
        test_custom_max_tokens_override()
        test_truncation_detection_finish_reason_length()
        test_incomplete_output_missing_answer_key_detection()
        test_concise_instructions_in_prompts()
        test_missing_or_empty_analysis_handling()
        test_backward_compatible_signatures()
        test_output_structure_requirements()
        print("=" * 60)
        print("ALL P2 OFFLINE TESTS PASSED (0 LIVE API CALLS MADE)")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n[FAIL] Test assertion failed: {e}")
        return False
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {type(e).__name__} - {e}")
        return False


if __name__ == "__main__":
    success = run_all_offline_tests()
    sys.exit(0 if success else 1)
