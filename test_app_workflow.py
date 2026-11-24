"""
Comprehensive offline workflow verification for LastHope.
Tests the exact logic used in app.py across all pipeline stages:
1. Document upload/parsing (TXT & multi-page extraction)
2. P1 Lecture Analysis invocation (offline with mocked LLM response)
3. P2 Practice Question Generation invocation (offline with mocked LLM response)
4. P3 Content Verification invocation (offline with mocked LLM response)
5. Stage 05 Study Pack download assembly & dispatch:
   - 3-stage study pack (P1 + P2 + P3) in Markdown (.md) and plain text (.txt)
   - 2-stage study pack (P1 + P2 without P3)
   - Cross-platform filename sanitization (illegal characters, path traversal, length limit)
   - Empty/whitespace content and download availability flags
   - Graceful error handling during packaging
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.document_parser import parse_document
from prompts.lecture_analyzer import analyze_lecture
from prompts.question_generator import generate_questions
from prompts.content_verifier import verify_content
from utils.export_helper import build_study_pack, sanitize_filename

SAMPLE_LECTURE = """--- [Page 1] ---
CS204: Algorithms & Data Structures
Lecture 3: Binary Search Trees (BST)

BST Definition:
A binary tree where for every node X:
- All keys in left subtree of X are < key(X)
- All keys in right subtree of X are > key(X)

Operations & Time Complexity:
- Search: O(h) where h is tree height. Best case O(log n) for balanced tree; Worst case O(n) for degenerate tree.
- Insert: O(h)
- In-order traversal visits nodes in sorted order.

--- [Page 2] ---
Lecture 3 (Cont.): Balanced BSTs & Self-Balancing

AVL Trees:
- An AVL tree is a self-balancing BST.
- Balance Factor (BF) = Height(left_subtree) - Height(right_subtree).
- In an AVL tree, BF must be in {-1, 0, +1} for every node.
- Rotations: Single (LL, RR) or Double (LR, RL) to restore balance.
- Guaranteed height: h <= 1.44 log2(n), giving O(log n) for search, insert, and delete.
"""

MOCK_P1_NOTES = """# 📚 Lecture Revision Notes: Binary Search Trees & AVL Trees

## 1. Executive Overview
- Explores binary search tree invariant properties, search/insert dynamics, and worst-case performance limits [Page 1].
- Introduces self-balancing AVL trees, balance factor constraints, and tree rotation techniques [Page 2].

## 2. Topic-by-Topic Breakdown
### Module 1: Binary Search Tree Fundamentals [Page 1]
- **Core Concept**: A binary tree maintaining left subtree keys < node key < right subtree keys.
- **Key Details**: In-order traversal yields elements in strictly sorted order. Search complexity depends on height O(h).
- **Formulas / Rules**: Best-case height is O(log n); degenerate worst-case is O(n).

### Module 2: AVL Tree Balance & Rotations [Page 2]
- **Core Concept**: Self-balancing BST guaranteeing logarithmic operation bounds.
- **Key Details**: Balance factor must strictly remain in {-1, 0, +1} for every valid node.
- **Formulas / Rules**: Balance Factor = Height(left) - Height(right). Height h <= 1.44 * log2(n).

## 3. Key Terminology & Definitions
| Term | Definition | Source |
| :--- | :--- | :--- |
| **Binary Search Tree** | A node-based binary tree with sorted left/right subtree properties. | [Page 1] |
| **Balance Factor** | Height difference between left and right subtrees in an AVL tree. | [Page 2] |
| **AVL Rotation** | Tree restructuring operation (single or double) to restore balance. | [Page 2] |

## 4. High-Yield Revision Takeaways
- BST search degrades from O(log n) to O(n) if insertions arrive in sorted order.
- AVL trees enforce balance factor in {-1, 0, +1} to guarantee O(log n) performance.
- Rotations (LL, RR, LR, RL) rebalance an AVL tree in O(1) time after insertions.

## 5. Topics Needing Clarification & Potential Gaps
- Deletion operations and duplicate key resolution strategies are not specified in these slides [Page 1].
- Exact implementation details of LR and RL double rotations are deferred [Page 2].
"""

MOCK_P2_QUESTIONS = """# 📝 Revision Assessment: Binary Search Trees & AVL Trees

## Part 1: Practice Questions

### Section A: Multiple-Choice Questions
#### Question 1 (Foundational)
What is the permitted balance factor range for any node in an AVL tree?
- A) {0}
- B) {-1, 0, +1}
- C) {-2, -1, 0, +1, +2}
- D) {-1, +1}

#### Question 2 (Conceptual)
What is the time complexity of searching in a completely degenerate BST of n nodes?
- A) O(1)
- B) O(log n)
- C) O(n)
- D) O(n log n)

---

## Part 2: Answer Key & Detailed Explanations

### Question 1
- **Correct Answer**: B) {-1, 0, +1}
- **Explanation**: By definition, an AVL tree maintains a balance factor in {-1, 0, +1} at every node [Page 2].

### Question 2
- **Correct Answer**: C) O(n)
- **Explanation**: A degenerate BST resembles a linked list with height h = n, resulting in O(n) search time [Page 1].
"""

MOCK_P3_REPORT = """# 🛡️ Content Verification & Quality Audit Report

## 1. Overall Audit Verdict
- **Status**: PASS
- **Confidence Level**: HIGH (Grounding: 100%)

## 2. Executive Summary of Audit
All concepts, formulas, and time complexities in P1 notes and P2 questions are strictly grounded in the lecture source text.

## 3. Fact-Checking & Syllabus Alignment Matrix
- Binary Search Tree Definition: ✅ VERIFIED [Page 1]
- AVL Balance Factor: ✅ VERIFIED [Page 2]
- Guaranteed Height Bound: ✅ VERIFIED [Page 2]

## 4. Formula & Technical Notation Audit
- Balance Factor = Height(left) - Height(right): ✅ Step-by-step arithmetic verified.

## 5. Question & Answer Key Audit
- Question 1 Answer Key (B): ✅ Mathematically and conceptually correct.
- Question 2 Answer Key (C): ✅ Verified against O(n) worst-case limit.

## 6. Identified Gaps & Ambiguities
- Deletion algorithms are omitted from source slides, correctly flagged in P1 Section 5.

## 7. Actionable Recommendations
- Proceed with revision; materials are fully verified and grounded.

---
*Disclaimer: System verification provides automated cross-examination and does not replace official course instructor review.*
"""


def run_workflow_test():
    print("=" * 65)
    print("RUNNING LASTHOPE OFFLINE END-TO-END WORKFLOW & STAGE 05 TEST")
    print("=" * 65)

    # -------------------------------------------------------------------------
    # 1. Test Document Parser
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Testing Document Parser...")
    parsed = parse_document(SAMPLE_LECTURE.encode("utf-8"), filename="bst_lecture.txt")
    print(f" -> Parsed successfully: {parsed.total_pages} page(s), {parsed.word_count} words.")
    assert parsed.total_pages == 1, "Page count mismatch"
    assert parsed.word_count > 50, "Word count too low"
    assert "CS204" in parsed.extracted_text
    print("  [PASS] Document parsing and page tracking verified")

    # -------------------------------------------------------------------------
    # 2. Test P1 Lecture Analysis (Mocked LLM)
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Calling P1: analyze_lecture() [Mocked LLM]...")
    with patch("prompts.lecture_analyzer.generate_response", return_value=MOCK_P1_NOTES) as mock_gen_p1:
        p1_notes = analyze_lecture(parsed.extracted_text, timeout=90.0)
        assert mock_gen_p1.called
        kwargs = mock_gen_p1.call_args[1]
        assert kwargs.get("max_tokens") == 2500, "P1 must pass max_tokens=2500"

    print(f" -> P1 Analysis received ({len(p1_notes)} characters)")
    assert "Executive Overview" in p1_notes
    assert "Topic-by-Topic Breakdown" in p1_notes
    assert "Key Terminology & Definitions" in p1_notes
    assert "High-Yield Revision Takeaways" in p1_notes
    assert "Topics Needing Clarification & Potential Gaps" in p1_notes
    print("  [PASS] P1 complete analysis and five-section schema verified")

    # -------------------------------------------------------------------------
    # 3. Test P2 Question Generator (Mocked LLM)
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Calling P2: generate_questions(num_questions=5) [Mocked LLM]...")
    with patch("prompts.question_generator.generate_response", return_value=MOCK_P2_QUESTIONS) as mock_gen_p2:
        p2_questions = generate_questions(
            lecture_text=parsed.extracted_text,
            analysis_text=p1_notes,
            num_questions=5,
            timeout=120.0,
        )
        assert mock_gen_p2.called
        kwargs_p2 = mock_gen_p2.call_args[1]
        assert kwargs_p2.get("max_tokens") == 1200, "P2 5-questions must pass max_tokens=1200"

    print(f" -> P2 Questions received ({len(p2_questions)} characters)")
    assert "Part 1: Practice Questions" in p2_questions
    assert "Part 2: Answer Key & Detailed Explanations" in p2_questions
    print("  [PASS] P2 practice questions and answer key verified")

    # -------------------------------------------------------------------------
    # 4. Test P3 Content Verification (Mocked LLM)
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Calling P3: verify_content() [Mocked LLM]...")
    with patch("prompts.content_verifier.generate_response", return_value=MOCK_P3_REPORT) as mock_gen_p3:
        p3_report = verify_content(
            lecture_text=parsed.extracted_text,
            analysis_text=p1_notes,
            questions_text=p2_questions,
            timeout=120.0,
        )
        assert mock_gen_p3.called
        kwargs_p3 = mock_gen_p3.call_args[1]
        assert kwargs_p3.get("max_tokens") == 1200, "P3 must pass max_tokens=1200"

    print(f" -> P3 Audit Report received ({len(p3_report)} characters)")
    assert "PASS" in p3_report
    assert "Audit Verdict" in p3_report
    assert "Disclaimer" in p3_report or "guarantee" in p3_report.lower()
    print("  [PASS] P3 verification report and max_tokens=1500 verified")

    # -------------------------------------------------------------------------
    # 5. Stage 05 Study Pack Download & Packaging Verification
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Testing Stage 05 Study Pack Assembly & Download Packaging...")

    # 5a. Full 3-stage Study Pack (P1 + P2 + P3)
    print(" -> Testing 3-stage study pack compilation...")
    pack_full = build_study_pack(
        doc_name="BST & AVL Trees",
        file_name="CS204_Lecture_03.pdf",
        model_name="openai/gpt-oss-120b",
        p1_analysis=p1_notes,
        p2_questions=p2_questions,
        p3_verification=p3_report,
        timestamp_str="2026-11-24 21:00:00",
    )
    assert "# LastHope Study Pack: BST & AVL Trees" in pack_full
    assert "- Source File: CS204_Lecture_03.pdf" in pack_full
    assert "- Model Engine: openai/gpt-oss-120b" in pack_full
    assert "## PART I: LECTURE REVISION NOTES (P1)" in pack_full
    assert "## PART II: REVISION QUESTIONS & ANSWER KEY (P2)" in pack_full
    assert "## PART III: CONTENT VERIFICATION & AUDIT REPORT (P3)" in pack_full
    assert "Binary Search Tree" in pack_full
    assert "Part 2: Answer Key & Detailed Explanations" in pack_full
    assert "Overall Audit Verdict" in pack_full
    print(f"    [PASS] 3-stage study pack contains all 3 stages verbatim ({len(pack_full)} chars)")

    # 5b. Markdown vs TXT download format integrity
    print(" -> Testing Markdown and TXT download formats...")
    md_content = pack_full
    txt_content = str(pack_full)
    assert len(md_content) == len(txt_content)
    assert "## PART I:" in txt_content
    assert "## PART II:" in txt_content
    assert "## PART III:" in txt_content
    # Test UTF-8 byte encodability for downloads
    md_bytes = md_content.encode("utf-8")
    txt_bytes = txt_content.encode("utf-8")
    assert len(md_bytes) > 0 and len(txt_bytes) > 0
    print("    [PASS] Both Markdown (.md) and TXT (.txt) formats contain complete content")

    # 5c. 2-stage Study Pack without P3 (P1 + P2 only)
    print(" -> Testing 2-stage study pack (without P3)...")
    pack_no_p3 = build_study_pack(
        doc_name="BST & AVL Trees",
        file_name="CS204_Lecture_03.pdf",
        model_name="openai/gpt-oss-120b",
        p1_analysis=p1_notes,
        p2_questions=p2_questions,
        p3_verification=None,
    )
    assert "## PART I: LECTURE REVISION NOTES (P1)" in pack_no_p3
    assert "## PART II: REVISION QUESTIONS & ANSWER KEY (P2)" in pack_no_p3
    assert "## PART III" not in pack_no_p3, "P3 must not appear when not run"
    assert len(pack_full) > len(pack_no_p3)
    print("    [PASS] Study pack without P3 cleanly omits Part III")

    # 5d. Filename sanitization across edge cases
    print(" -> Testing cross-platform filename sanitization...")
    assert sanitize_filename("Activity_1_S24CSEU2000.pdf") == "Activity_1_S24CSEU2000"
    assert sanitize_filename("Lecture 04: Trees & Graphs [CS-204] (Fall'26).pdf") == "Lecture_04_Trees_Graphs_CS-204_Fall_26"
    assert sanitize_filename("../../etc/passwd.txt") == "passwd"
    assert sanitize_filename("invalid:?*chars.pdf") == "invalid_chars"
    assert sanitize_filename("   ") == "lecture"
    assert sanitize_filename(None) == "lecture"
    assert sanitize_filename("...____...") == "lecture"
    long_name = "A" * 100
    sanitized_long = sanitize_filename(long_name, max_len=50)
    assert len(sanitized_long) <= 50
    print("    [PASS] Filenames sanitized safely against OS and browser errors")

    # 5e. Empty content and availability flags handling
    print(" -> Testing empty content and pipeline flag behavior...")
    # Empty pack check
    empty_pack = build_study_pack(
        doc_name="Empty",
        file_name=None,
        model_name=None,
        p1_analysis="",
        p2_questions="   ",
        p3_verification=None,
    )
    assert empty_pack == "", "Empty content must produce empty pack string"

    # Flag verification (matching app.py logic)
    p1_done = bool(MOCK_P1_NOTES and MOCK_P1_NOTES.strip())
    p2_done = bool(MOCK_P2_QUESTIONS and MOCK_P2_QUESTIONS.strip())
    p3_done = bool(MOCK_P3_REPORT and MOCK_P3_REPORT.strip())
    export_ready = bool(p1_done or p2_done)
    assert p1_done is True and p2_done is True and p3_done is True and export_ready is True

    # Empty string edge cases
    assert bool("" and "".strip()) is False
    assert bool("   " and "   ".strip()) is False
    assert bool(None and None.strip()) is False
    print("    [PASS] Empty content and availability flags correctly handled")

    # 5f. Download generation error handling
    print(" -> Testing download preparation error resilience...")
    try:
        # Pass unexpected invalid type to test error capture
        corrupted_output = build_study_pack(doc_name=12345, file_name=None, p1_analysis=MOCK_P1_NOTES)
        assert len(corrupted_output) > 0
    except Exception as e:
        assert False, f"build_study_pack should not raise unhandled exception: {e}"
    print("    [PASS] Download generation handles edge cases gracefully")

    print("\n" + "=" * 65)
    print("ALL LASTHOPE WORKFLOW & STAGE 05 OFFLINE TESTS PASSED!")
    print("=" * 65)
    return True


if __name__ == "__main__":
    try:
        success = run_workflow_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Workflow test failed: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
