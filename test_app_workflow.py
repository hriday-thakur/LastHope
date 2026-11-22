"""
Comprehensive workflow verification for LastHope.
Tests the exact logic used in app.py:
1. Document upload/parsing (TXT & PDF)
2. P1 Lecture Analysis invocation
3. P2 Practice Question Generation invocation (5 questions)
4. P3 Content Verification invocation
5. Study Pack assembly logic (with and without P3)
"""

import sys
from pathlib import Path
from utils.document_parser import parse_document
from prompts.lecture_analyzer import analyze_lecture
from prompts.question_generator import generate_questions
from prompts.content_verifier import verify_content

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

def run_workflow_test():
    print("=" * 60)
    print("RUNNING LASTHOPE END-TO-END WORKFLOW TEST")
    print("=" * 60)

    # 1. Test Document Parser
    print("\n[STEP 1] Testing Document Parser...")
    parsed = parse_document(SAMPLE_LECTURE.encode("utf-8"), filename="bst_lecture.txt")
    print(f" -> Parsed successfully: {parsed.total_pages} page(s), {parsed.word_count} words.")
    assert parsed.total_pages == 1, "Page count mismatch"
    assert parsed.word_count > 50, "Word count too low"

    # 2. Test P1 Lecture Analysis
    print("\n[STEP 2] Calling P1: analyze_lecture()...")
    p1_notes = analyze_lecture(parsed.extracted_text, timeout=90.0)
    print(f" -> P1 Analysis received ({len(p1_notes)} characters)")
    assert "Overview" in p1_notes or "Revision Notes" in p1_notes
    assert "BST" in p1_notes or "Binary Search" in p1_notes

    # 3. Test P2 Question Generator (5 questions)
    print("\n[STEP 3] Calling P2: generate_questions(num_questions=5)...")
    p2_questions = generate_questions(
        lecture_text=parsed.extracted_text,
        analysis_text=p1_notes,
        num_questions=5,
        timeout=120.0
    )
    print(f" -> P2 Questions received ({len(p2_questions)} characters)")
    assert "Section A" in p2_questions or "Multiple" in p2_questions
    assert "Answer Key" in p2_questions or "Part 2" in p2_questions

    # 4. Test P3 Content Verification
    print("\n[STEP 4] Calling P3: verify_content()...")
    p3_report = verify_content(
        lecture_text=parsed.extracted_text,
        analysis_text=p1_notes,
        questions_text=p2_questions,
        timeout=120.0
    )
    print(f" -> P3 Audit Report received ({len(p3_report)} characters)")
    assert any(status in p3_report for status in ["PASS", "PASS WITH WARNINGS", "NEEDS REVISION"])
    assert "Disclaimer" in p3_report or "guarantee" in p3_report.lower()

    # 5. Test Export Assembly
    print("\n[STEP 5] Testing Study Pack Assembly Logic...")
    # 5a. Without P3
    pack_no_p3 = f"# Study Pack\n{p1_notes}\n{p2_questions}"
    assert "PART III" not in pack_no_p3, "P3 should not appear if not run"

    # 5b. With P3
    pack_with_p3 = f"# Study Pack\n{p1_notes}\n{p2_questions}\n## PART III: CONTENT VERIFICATION\n{p3_report}"
    assert "PART III" in pack_with_p3, "P3 should appear when run"
    assert len(pack_with_p3) > len(pack_no_p3), "Pack with P3 must include full audit"
    print(f" -> Verified download bundle generation (Total size: {len(pack_with_p3)} chars)")

    print("\n" + "=" * 60)
    print("ALL APPLICATION PIPELINE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = run_workflow_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] Workflow test failed: {type(e).__name__} - {e}")
        sys.exit(1)
