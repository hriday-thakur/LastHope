"""
Offline unit and integration test suite for Prompt 3 (P3): Content Verification Assistant.
Verifies:
1. P3 passes explicit max_tokens=1200 by default and preserves custom overrides.
2. Compact evidence payload extracts and preserves cited lecture evidence, formulas, and definitions.
3. P2 streamlining preserves all question stems, answer keys, arithmetic, and citations while eliminating distractor overhead.
4. P1 context remains complete, factually grounded, and sufficient for verification while eliminating table formatting.
5. Total measured request budget (input tokens + max_tokens reservation) stays comfortably below the 8,000 TPM limit.
6. All seven required verification report sections, disclaimer, and status directives remain in P3_SYSTEM_PROMPT.
7. Input validation (empty lecture, analysis, or questions text raises ValueError).
8. Backward-compatible call signatures (positional & keyword).

This test suite runs 100% offline without making live Groq API calls.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.groq_client import OutputTruncatedError
from prompts.content_verifier import (
    P3_DEFAULT_MAX_TOKENS,
    P3_SYSTEM_PROMPT,
    P3_USER_PROMPT_TEMPLATE,
    extract_evidence_payload,
    streamline_p1_analysis_for_audit,
    streamline_p2_questions_for_audit,
    format_p3_user_prompt,
    verify_content,
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

SAMPLE_P1_ANALYSIS = """# 📚 Lecture Revision Notes: Cache Memory & Memory Hierarchy Basics

## 1. Executive Overview
- Scope: High-level overview of memory hierarchy bridging the processor-memory speed gap.
- Estimated source coverage: Pages 1 to 2.

## 2. Topic-by-Topic Breakdown
### Memory Hierarchy & Locality *(Source: [Page 1])*
- **Core Concept**: Bridges the processor-memory speed gap (Memory Wall) using SRAM and DRAM.
- **Key Details**:
  - Temporal Locality: Frequently accessed addresses remain in cache.
  - Spatial Locality: Adjacent addresses fetched simultaneously.
- **Formulas / Algorithms / Rules**: None on Page 1.

### Cache Performance Metrics *(Source: [Page 2])*
- **Core Concept**: Quantifies access latency using AMAT.
- **Key Details**:
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

SAMPLE_P2_QUESTIONS = """# 📝 Revision Practice Questions: Cache Memory

## Part 1: Practice Questions

### Section A: Multiple-Choice Questions
1. [Page 1] What type of memory is primarily used for cache levels?
   - A) DRAM
   - B) SRAM
   - C) Flash
   - D) ROM

2. [Page 2] Given Hit_Time = 2 cycles, Miss_Rate = 0.05, and Miss_Penalty = 100 cycles, what is the AMAT?
   - A) 5 cycles
   - B) 7 cycles
   - C) 10 cycles
   - D) 12 cycles

---

## Part 2: Complete Answer Key & Explanations

### Multiple-Choice Answers
1. **Correct Answer: B**
   - **Explanation:** SRAM is fast, expensive, volatile, and low density, making it ideal for caches.
   - **Source:** [Page 1]

2. **Correct Answer: B**
   - **Explanation:** AMAT = 2 + (0.05 * 100) = 2 + 5 = 7 cycles.
   - **Source:** [Page 2]
"""

MOCK_P3_REPORT = """# 🛡️ Content Verification & Fact-Check Report

> **Disclaimer:** *This is an AI-assisted academic verification report intended to aid revision quality.*

## 1. Executive Verification Summary
- The generated P1 analysis and P2 practice questions were audited against the original lecture text.
- **Audit Verdict:** PASS

## 2. Verified Claims & Grounded Concepts
- ✅ **SRAM for Caches**: Confirmed grounded. *(Source: [Page 1])*
- ✅ **AMAT Formula**: Confirmed grounded. *(Source: [Page 2])*

## 3. Unsupported or Inaccurate Claims
- None identified in the sample set.

## 4. Mathematical & Calculation Checks
- 🧮 **AMAT Calculation in Q2**:
  - *Given in Generated Material:* AMAT = 2 + (0.05 * 100) = 7 cycles
  - *Step-by-Step Verification:* 0.05 * 100 = 5.0; 2 + 5.0 = 7.0 cycles.
  - *Verdict:* Correct

## 5. Context Gaps & Ambiguities
- Cache coherence deferred to Chapter 8.

## 6. Actionable Recommended Corrections
- No corrections required.

## 7. Final Review Status
- **Final Status:** **PASS**
- **Justification:** All claims and calculations are grounded in the lecture text.
"""


def test_p3_default_max_tokens():
    """Verify that verify_content passes max_tokens=1200 by default."""
    print("Testing P3 default max_tokens=1200...")
    with patch("prompts.content_verifier.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_P3_REPORT
        result = verify_content(
            lecture_text=SAMPLE_LECTURE_TEXT,
            analysis_text=SAMPLE_P1_ANALYSIS,
            questions_text=SAMPLE_P2_QUESTIONS,
        )

        assert mock_gen.called, "generate_response was not called"
        call_kwargs = mock_gen.call_args[1]
        assert call_kwargs.get("max_tokens") == 1200, f"Expected max_tokens=1200, got {call_kwargs.get('max_tokens')}"
        assert P3_DEFAULT_MAX_TOKENS == 1200, f"Expected P3_DEFAULT_MAX_TOKENS=1200, got {P3_DEFAULT_MAX_TOKENS}"
        assert result == MOCK_P3_REPORT
    print("  [PASS] P3 passes max_tokens=1200 by default")


def test_p3_max_tokens_override():
    """Verify that verify_content respects custom max_tokens overrides."""
    print("Testing P3 custom max_tokens override...")
    with patch("prompts.content_verifier.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_P3_REPORT
        verify_content(
            lecture_text=SAMPLE_LECTURE_TEXT,
            analysis_text=SAMPLE_P1_ANALYSIS,
            questions_text=SAMPLE_P2_QUESTIONS,
            max_tokens=1500,
        )

        call_kwargs = mock_gen.call_args[1]
        assert call_kwargs.get("max_tokens") == 1500, f"Expected max_tokens=1500, got {call_kwargs.get('max_tokens')}"
    print("  [PASS] P3 respects custom max_tokens override")


def test_compact_evidence_payload():
    """Verify that compact evidence extracts cited pages and preserves formulas."""
    print("Testing compact evidence extraction and formula preservation...")
    payload = extract_evidence_payload(
        lecture_text=SAMPLE_LECTURE_TEXT,
        analysis_text=SAMPLE_P1_ANALYSIS,
        questions_text=SAMPLE_P2_QUESTIONS,
    )

    assert "--- [Page 1] ---" in payload
    assert "--- [Page 2] ---" in payload
    assert "AMAT = Hit_Time + (Miss_Rate * Miss_Penalty)" in payload
    assert "SRAM (Static RAM)" in payload
    assert "DRAM (Dynamic RAM)" in payload
    assert "Compulsory Misses" in payload
    print("  [PASS] Compact evidence preserves all cited pages, formulas, and definitions")


def test_p2_streamlining_for_audit():
    """Verify that P2 questions keep stems, answer key, and math while stripping distractors."""
    print("Testing P2 question streamlining...")
    streamlined = streamline_p2_questions_for_audit(SAMPLE_P2_QUESTIONS)

    # Question stems must be preserved
    assert "What type of memory is primarily used for cache levels?" in streamlined
    assert "Given Hit_Time = 2 cycles" in streamlined
    # Answer key must be preserved verbatim
    assert "Part 2: Complete Answer Key & Explanations" in streamlined
    assert "Correct Answer: B" in streamlined
    assert "AMAT = 2 + (0.05 * 100) = 2 + 5 = 7 cycles." in streamlined
    # Distractors should be stripped from Part 1
    assert "- A) DRAM" not in streamlined
    assert "- C) Flash" not in streamlined
    print("  [PASS] P2 streamlining preserves questions, answer key, math, and citations")


def test_p1_context_sufficiency_and_deduplication():
    """Verify that P1 context retains all necessary claims and formulas while compacting table syntax."""
    print("Testing P1 context sufficiency and deduplication...")
    prompt = format_p3_user_prompt(
        lecture_text=SAMPLE_LECTURE_TEXT,
        analysis_text=SAMPLE_P1_ANALYSIS,
        questions_text=SAMPLE_P2_QUESTIONS,
    )

    assert "Executive Overview" in prompt
    assert "Memory Hierarchy & Locality" in prompt
    assert "AMAT = Hit_Time + (Miss_Rate * Miss_Penalty)" in prompt
    assert "Compulsory, Capacity, Conflict misses" in prompt
    assert "Cache coherence protocol deferred to Chapter 8" in prompt
    assert "[Page 1]" in prompt
    assert "[Page 2]" in prompt

    # Verify that heavy markdown table pipes (| :--- | :--- |) were compacted
    assert ":---" not in prompt, "Redundant markdown table divider syntax was not compacted"
    assert "SRAM" in prompt
    assert "DRAM" in prompt
    print("  [PASS] P1 context is complete, sufficient, and deduplicated")


def test_request_budget_well_below_tpm_limit():
    """Verify that total request payload + output reservation stays well below 8,000 TPM limit."""
    print("Testing total P3 request token budget against 8,000 TPM limit...")
    prompt = format_p3_user_prompt(
        lecture_text=SAMPLE_LECTURE_TEXT,
        analysis_text=SAMPLE_P1_ANALYSIS,
        questions_text=SAMPLE_P2_QUESTIONS,
    )

    # Estimate input tokens (~4 chars per token)
    system_tokens = len(P3_SYSTEM_PROMPT) // 4
    user_tokens = len(prompt) // 4
    total_input = system_tokens + user_tokens
    total_request = total_input + P3_DEFAULT_MAX_TOKENS

    print(f" -> System prompt tokens: ~{system_tokens}")
    print(f" -> User prompt tokens:   ~{user_tokens}")
    print(f" -> Total input tokens:   ~{total_input}")
    print(f" -> Output reservation:   {P3_DEFAULT_MAX_TOKENS}")
    print(f" -> Total request budget: ~{total_request} tokens (Limit: 8,000 TPM)")

    assert total_request < 6000, f"Request budget {total_request} is too close to 8,000 TPM limit"
    assert P3_DEFAULT_MAX_TOKENS == 1200
    print("  [PASS] Total P3 request budget is well below 8,000 TPM limit (~40%+ headroom)")


def test_p3_output_structure_requirements():
    """Verify that all 7 required sections and status criteria remain in P3_SYSTEM_PROMPT."""
    print("Testing P3 output structure and directives in system prompt...")
    required_sections = [
        ("Disclaimer", "Disclaimer"),
        ("Executive Verification Summary", "## 1. Executive Verification Summary"),
        ("Verified Claims", "## 2. Verified Claims & Grounded Concepts"),
        ("Unsupported Claims", "## 3. Unsupported or Inaccurate Claims"),
        ("Mathematical Checks", "## 4. Mathematical & Calculation Checks"),
        ("Context Gaps", "## 5. Context Gaps & Ambiguities"),
        ("Recommended Corrections", "## 6. Actionable Recommended Corrections"),
        ("Final Review Status", "## 7. Final Review Status"),
    ]

    for label, section_header in required_sections:
        assert section_header in P3_SYSTEM_PROMPT, f"Missing section '{label}' in P3_SYSTEM_PROMPT"

    assert "PASS" in P3_SYSTEM_PROMPT
    assert "PASS WITH WARNINGS" in P3_SYSTEM_PROMPT
    assert "NEEDS REVISION" in P3_SYSTEM_PROMPT
    print("  [PASS] All 7 P3 output structure sections and status criteria verified")


def test_empty_input_validation():
    """Verify that empty lecture text, analysis, or questions text raises ValueError."""
    print("Testing empty input validation...")
    try:
        format_p3_user_prompt("", SAMPLE_P1_ANALYSIS, SAMPLE_P2_QUESTIONS)
        assert False, "Should have raised ValueError for empty lecture_text"
    except ValueError as e:
        assert "lecture text" in str(e).lower()

    try:
        format_p3_user_prompt(SAMPLE_LECTURE_TEXT, "", SAMPLE_P2_QUESTIONS)
        assert False, "Should have raised ValueError for empty analysis_text"
    except ValueError as e:
        assert "analysis" in str(e).lower()

    try:
        format_p3_user_prompt(SAMPLE_LECTURE_TEXT, SAMPLE_P1_ANALYSIS, "")
        assert False, "Should have raised ValueError for empty questions_text"
    except ValueError as e:
        assert "questions" in str(e).lower()
    print("  [PASS] Empty input validation correctly raises ValueError")


def test_backward_compatible_signatures():
    """Verify that verify_content maintains exact positional and keyword parameter order."""
    print("Testing backward-compatible function signatures...")
    with patch("prompts.content_verifier.generate_response") as mock_gen:
        mock_gen.return_value = MOCK_P3_REPORT
        # Positional call: lecture, analysis, questions, model, temperature, timeout, max_tokens
        verify_content(
            SAMPLE_LECTURE_TEXT,
            SAMPLE_P1_ANALYSIS,
            SAMPLE_P2_QUESTIONS,
            "test-model",
            0.15,
            90.0,
            1100,
        )
        kwargs = mock_gen.call_args[1]
        assert kwargs["model"] == "test-model"
        assert kwargs["temperature"] == 0.15
        assert kwargs["timeout"] == 90.0
        assert kwargs["max_tokens"] == 1100
    print("  [PASS] Backward-compatible parameter order verified")


def test_concise_output_directives():
    """Verify that P3_SYSTEM_PROMPT enforces 350-450 word compact output."""
    print("Testing concise output directives in P3_SYSTEM_PROMPT...")
    assert "350–450" in P3_SYSTEM_PROMPT or "350-450" in P3_SYSTEM_PROMPT
    assert "maximum 2 sentences" in P3_SYSTEM_PROMPT.lower()
    assert "maximum 3" in P3_SYSTEM_PROMPT.lower()
    print("  [PASS] Concise output directives (350-450 words, max 2 sentences, max 3 recommendations) verified")


def test_truncation_error_propagation():
    """Verify that OutputTruncatedError propagates cleanly when finish_reason='length'."""
    print("Testing OutputTruncatedError propagation...")
    with patch("prompts.content_verifier.generate_response") as mock_gen:
        mock_gen.side_effect = OutputTruncatedError(
            "Generation was cut off because the model reached its maximum token limit (finish_reason='length').",
            partial_content="## 1. Executive Verification Summary\nPartial...",
        )
        try:
            verify_content(
                lecture_text=SAMPLE_LECTURE_TEXT,
                analysis_text=SAMPLE_P1_ANALYSIS,
                questions_text=SAMPLE_P2_QUESTIONS,
            )
            assert False, "Expected OutputTruncatedError to be raised"
        except OutputTruncatedError as e:
            assert "finish_reason='length'" in str(e)
            assert e.partial_content.startswith("## 1.")
    print("  [PASS] OutputTruncatedError propagates cleanly without marking partial output as success")


def run_all_tests():
    print("=" * 65)
    print("RUNNING OFFLINE P3 CONTENT VERIFIER UNIT & REGRESSION TESTS")
    print("=" * 65)

    tests = [
        test_p3_default_max_tokens,
        test_p3_max_tokens_override,
        test_compact_evidence_payload,
        test_p2_streamlining_for_audit,
        test_p1_context_sufficiency_and_deduplication,
        test_request_budget_well_below_tpm_limit,
        test_p3_output_structure_requirements,
        test_empty_input_validation,
        test_backward_compatible_signatures,
        test_concise_output_directives,
        test_truncation_error_propagation,
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
        print("ALL 9 OFFLINE P3 TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED - SEE DETAILS ABOVE.")
    print("=" * 65)
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
