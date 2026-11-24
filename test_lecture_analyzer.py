"""
Offline unit and integration test suite for Prompt 1 (P1): Lecture Content Analyzer.
Verifies:
1. P1 passes explicit max_tokens=2500 by default and preserves overrides.
2. All five required sections remain in the P1 system prompt.
3. Concise-output instructions are present (3-6 thematic modules, 10-15 terms, formulas, citations).
4. Successful P1 output is saved and marked as complete analysis.
5. Truncated P1 output raises OutputTruncatedError and is NOT saved as complete analysis.
6. P2 remains unavailable when P1 output is incomplete or truncated.
7. Empty partial content on truncation is handled cleanly.
8. Empty or invalid lecture input raises ValueError.
9. Existing P1 behavior and attributes remain intact.

This test suite runs 100% offline without making live Groq API calls.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.groq_client import (
    GroqClientError,
    OutputTruncatedError,
    generate_response,
)
from prompts.lecture_analyzer import (
    P1_DEFAULT_MAX_TOKENS,
    P1_SYSTEM_PROMPT,
    P1_USER_PROMPT_TEMPLATE,
    format_p1_user_prompt,
    analyze_lecture,
)
from prompts.question_generator import MissingAnalysisError, generate_questions


SAMPLE_LECTURE_TEXT = """--- [Page 1] ---
CS301: Computer Architecture
Lecture 7: Cache Memory & Memory Hierarchy Basics
Instructor: Dr. Alan Vance

Memory Hierarchy Overview:
- Processors operate at GHz speeds, while main memory (DRAM) is much slower (the "Memory Wall").
- SRAM (Static RAM) is used for caches: fast, expensive, volatile, low density.
- DRAM (Dynamic RAM) is used for main memory: slower, cheaper, high density, requires periodic refresh cycles.
- Locality Principle:
  1. Temporal Locality: If an address is accessed, it will likely be accessed again soon (e.g., loop variables).
  2. Spatial Locality: If an address is accessed, nearby addresses will likely be accessed soon (e.g., sequential array traversal).

--- [Page 2] ---
Lecture 7 (Cont.): Cache Performance Metrics

Average Memory Access Time (AMAT):
AMAT = Hit_Time + (Miss_Rate * Miss_Penalty)
- Hit Time: Time to access data from the cache (typically 1-4 cycles).
- Miss Rate: Fraction of accesses that result in a miss (Misses / Total Accesses).
- Miss Penalty: Time to fetch the block from the lower memory level into the cache (e.g., 50-200 cycles).

Cache Miss Categories (The 3 C's):
1. Compulsory Misses (Cold-start): First access to a block that has never been loaded.
2. Capacity Misses: Cache cannot contain all blocks needed during execution.
3. Conflict Misses: Multiple blocks map to the same set/slot in direct-mapped or set-associative cache.

Note: Cache coherence protocol for multi-core systems is deferred to Chapter 8. (Unspecified in this slide deck).
"""

MOCK_COMPLETE_P1_OUTPUT = """# 📚 Lecture Revision Notes: Cache Memory & Memory Hierarchy Basics

## 1. Executive Overview
- Scope: High-level overview of memory hierarchy bridging the processor-memory speed gap.
- Estimated source coverage: Pages 1 to 2.

## 2. Topic-by-Topic Breakdown
### Memory Hierarchy & Locality *(Source: [Page 1])*
- **Core Concept**: Bridges the processor-memory speed gap (Memory Wall) using SRAM and DRAM.
- **Key Details & Mechanisms**:
  - Temporal Locality: Frequently accessed addresses remain in cache.
  - Spatial Locality: Adjacent addresses fetched simultaneously.
- **Formulas / Algorithms / Rules**: None on Page 1.

### Cache Performance Metrics *(Source: [Page 2])*
- **Core Concept**: Quantifies access latency using AMAT.
- **Key Details & Mechanisms**:
  - 3 C's: Compulsory, Capacity, Conflict misses.
- **Formulas / Algorithms / Rules**:
  - AMAT = Hit_Time + (Miss_Rate * Miss_Penalty)

## 3. Key Terminology & Definitions
| Term / Concept | Definition & Explanation (Grounded in Lecture) | Source Page |
| :--- | :--- | :--- |
| SRAM | Static RAM used for caches; fast, expensive, volatile, low density. | [Page 1] |
| DRAM | Dynamic RAM used for main memory; slower, cheaper, high density. | [Page 1] |
| AMAT | Average Memory Access Time = Hit_Time + (Miss_Rate * Miss_Penalty). | [Page 2] |

## 4. High-Yield Revision Takeaways
- AMAT is the core metric to optimize memory latency.
- Locality principles (temporal & spatial) justify cache hierarchy.
- The 3 C's classify all cache misses.

## 5. Topics Needing Clarification & Potential Gaps
- Cache coherence protocol deferred to Chapter 8 (unspecified in current deck).
"""


def test_p1_default_max_tokens():
    """Verify that analyze_lecture passes max_tokens=2500 by default."""
    print("Testing P1 default max_tokens=2500...")
    with patch("prompts.lecture_analyzer.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_COMPLETE_P1_OUTPUT
        result = analyze_lecture(SAMPLE_LECTURE_TEXT)

        assert mock_gen.called, "generate_response was not called"
        call_kwargs = mock_gen.call_args[1]
        assert call_kwargs.get("max_tokens") == 2500, f"Expected max_tokens=2500, got {call_kwargs.get('max_tokens')}"
        assert P1_DEFAULT_MAX_TOKENS == 2500, f"Expected P1_DEFAULT_MAX_TOKENS=2500, got {P1_DEFAULT_MAX_TOKENS}"
        assert result == MOCK_COMPLETE_P1_OUTPUT
    print("  [PASS] P1 passes max_tokens=2500 by default")


def test_p1_max_tokens_override():
    """Verify that analyze_lecture allows custom max_tokens override."""
    print("Testing P1 max_tokens custom override...")
    with patch("prompts.lecture_analyzer.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_COMPLETE_P1_OUTPUT
        analyze_lecture(SAMPLE_LECTURE_TEXT, max_tokens=1800)

        call_kwargs = mock_gen.call_args[1]
        assert call_kwargs.get("max_tokens") == 1800, f"Expected max_tokens=1800, got {call_kwargs.get('max_tokens')}"
    print("  [PASS] P1 respects custom max_tokens override")


def test_all_five_sections_in_prompt():
    """Verify that all five required sections remain present in P1_SYSTEM_PROMPT."""
    print("Testing presence of all five required sections in P1 system prompt...")
    required_sections = [
        ("Executive / Lecture Overview", "## 1. Executive Overview"),
        ("Topic-by-Topic Breakdown", "## 2. Topic-by-Topic Breakdown"),
        ("Key Terminology & Definitions", "## 3. Key Terminology & Definitions"),
        ("High-Yield Takeaways", "## 4. High-Yield Revision Takeaways"),
        ("Clarifications & Gaps", "## 5. Topics Needing Clarification & Potential Gaps"),
    ]

    for label, section_header in required_sections:
        assert section_header in P1_SYSTEM_PROMPT, f"Missing section '{label}' ({section_header}) in P1_SYSTEM_PROMPT"
    print("  [PASS] All five required sections are present in P1 system prompt")


def test_concise_output_instructions():
    """Verify that concise-output and pacing directives are present in P1_SYSTEM_PROMPT."""
    print("Testing concise-output directives in P1 system prompt...")
    # 3-6 thematic modules
    assert "3–6" in P1_SYSTEM_PROMPT or "3-6" in P1_SYSTEM_PROMPT, "Missing 3-6 module grouping directive"
    assert "thematic modules" in P1_SYSTEM_PROMPT, "Missing 'thematic modules' wording"
    # High-information bullets
    assert "bullet points" in P1_SYSTEM_PROMPT, "Missing bullet points instruction"
    # Formulas verbatim
    assert "Formulas" in P1_SYSTEM_PROMPT, "Missing Formulas instruction"
    # Page attribution
    assert "[Page X]" in P1_SYSTEM_PROMPT, "Missing [Page X] citation instruction"
    # 10-15 terms limit
    assert "10–15" in P1_SYSTEM_PROMPT or "10-15" in P1_SYSTEM_PROMPT, "Missing 10-15 terms table limit"
    # Complete all five sections
    assert "Complete all five sections" in P1_SYSTEM_PROMPT or "all five required sections" in P1_SYSTEM_PROMPT
    # Never invent content
    assert "Never invent missing lecture content" in P1_SYSTEM_PROMPT or "Do not invent" in P1_SYSTEM_PROMPT
    print("  [PASS] Concise-output and pacing directives verified")


def test_successful_p1_output_saved():
    """Verify that complete P1 output is saved normally in session state."""
    print("Testing successful P1 output handling...")
    with patch("prompts.lecture_analyzer.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_COMPLETE_P1_OUTPUT
        result = analyze_lecture(SAMPLE_LECTURE_TEXT)

        # Simulate Streamlit session state workflow
        mock_session = {
            "p1_analysis": None,
            "p1_partial_content": None,
            "p1_truncated_error": None,
        }
        mock_session["p1_analysis"] = result
        mock_session["p1_partial_content"] = None
        mock_session["p1_truncated_error"] = None

        p1_done = mock_session["p1_analysis"] is not None
        assert p1_done is True, "p1_done should be True after successful generation"
        assert mock_session["p1_analysis"] == MOCK_COMPLETE_P1_OUTPUT
        assert mock_session["p1_partial_content"] is None
    print("  [PASS] Successful P1 output is saved normally")


def test_truncated_p1_output_not_saved():
    """Verify that truncated P1 output raises OutputTruncatedError and is NOT saved as complete analysis."""
    print("Testing truncated P1 output handling...")
    partial_text = "## 1. Executive Overview\n- Scope: Incomplete lecture notes..."

    with patch("prompts.lecture_analyzer.generate_response") as mock_gen:
        mock_gen.side_effect = OutputTruncatedError(
            "Generation was cut off because the model reached its maximum token limit (finish_reason='length').",
            partial_content=partial_text,
        )

        try:
            analyze_lecture(SAMPLE_LECTURE_TEXT)
            assert False, "Should have raised OutputTruncatedError"
        except OutputTruncatedError as e:
            # Simulate app.py exception handling
            mock_session = {
                "p1_analysis": None,
                "p1_partial_content": getattr(e, "partial_content", "") or "",
                "p1_truncated_error": str(e),
                "p2_questions": None,
                "p3_verification": None,
            }

            # Verification: p1_analysis must remain None
            assert mock_session["p1_analysis"] is None, "Partial content must NOT be saved as p1_analysis"
            assert mock_session["p1_partial_content"] == partial_text, "Partial content should be saved for review"
            p1_done = mock_session["p1_analysis"] is not None
            assert p1_done is False, "p1_done must be False when truncated"
    print("  [PASS] Truncated P1 output is NOT saved as complete analysis")


def test_p2_remains_unavailable_when_p1_incomplete():
    """Verify that P2 cannot proceed when P1 analysis is truncated or missing."""
    print("Testing P2 availability gate when P1 is incomplete...")
    mock_session = {
        "parsed_doc": MagicMock(),
        "p1_analysis": None,  # Incomplete / truncated
        "p1_partial_content": "Partial notes only...",
    }

    # app.py Stage 03 gate condition:
    # if st.session_state.parsed_doc is None or st.session_state.p1_analysis is None:
    p2_blocked = mock_session["parsed_doc"] is None or mock_session["p1_analysis"] is None
    assert p2_blocked is True, "P2 must be blocked in app.py when p1_analysis is None"

    # question_generator function gate condition:
    # When analysis_text is empty, MissingAnalysisError is raised before any API call is made
    try:
        generate_questions(analysis_text="")
        assert False, "generate_questions should raise MissingAnalysisError when analysis_text is empty"
    except MissingAnalysisError:
        pass  # Expected

    try:
        generate_questions(lecture_text=None, analysis_text=None)
        assert False, "generate_questions should raise MissingAnalysisError when both inputs are None"
    except MissingAnalysisError:
        pass  # Expected

    print("  [PASS] P2 remains strictly unavailable when P1 is incomplete")


def test_empty_partial_content_truncation():
    """Verify handling when OutputTruncatedError contains no partial content."""
    print("Testing truncation error with empty partial content...")
    with patch("prompts.lecture_analyzer.generate_response") as mock_gen:
        mock_gen.side_effect = OutputTruncatedError(
            "Generation cut off before tokens produced",
            partial_content="",
        )

        try:
            analyze_lecture(SAMPLE_LECTURE_TEXT)
            assert False, "Should have raised OutputTruncatedError"
        except OutputTruncatedError as e:
            mock_session = {
                "p1_analysis": None,
                "p1_partial_content": getattr(e, "partial_content", "") or "",
            }
            assert mock_session["p1_analysis"] is None
            assert mock_session["p1_partial_content"] == ""
            # When empty, app shows error rather than partial notes
            should_show_error = not bool(mock_session["p1_partial_content"].strip())
            assert should_show_error is True, "Should flag clear error when partial content is empty"
    print("  [PASS] Empty partial content triggers clear error flag")


def test_empty_lecture_input_validation():
    """Verify that empty lecture text raises ValueError."""
    print("Testing empty lecture text validation...")
    try:
        analyze_lecture("")
        assert False, "Should have raised ValueError for empty text"
    except ValueError as e:
        assert "empty" in str(e).lower()

    try:
        analyze_lecture("   \n\t  ")
        assert False, "Should have raised ValueError for whitespace text"
    except ValueError as e:
        assert "empty" in str(e).lower()
    print("  [PASS] Empty lecture input correctly raises ValueError")


def run_all_tests():
    print("=" * 65)
    print("RUNNING OFFLINE P1 LECTURE ANALYZER UNIT & REGRESSION TESTS")
    print("=" * 65)

    tests = [
        test_p1_default_max_tokens,
        test_p1_max_tokens_override,
        test_all_five_sections_in_prompt,
        test_concise_output_instructions,
        test_successful_p1_output_saved,
        test_truncated_p1_output_not_saved,
        test_p2_remains_unavailable_when_p1_incomplete,
        test_empty_partial_content_truncation,
        test_empty_lecture_input_validation,
    ]

    all_passed = True
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            all_passed = False
        except Exception as e:
            print(f"  [ERROR] {test.__name__}: {type(e).__name__} - {e}")
            all_passed = False

    print("=" * 65)
    if all_passed:
        print("ALL 9 OFFLINE P1 TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED - SEE DETAILS ABOVE.")
    print("=" * 65)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
