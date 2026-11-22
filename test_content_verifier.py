"""
Integration test script for Prompt 3 (P3): Content Verification Assistant.
Reads the original lecture text, real P1 output (test_p1_output.md), and real
P2 output (test_p2_output.md), calls Groq API to perform an audit, and writes
the unedited verification report to test_p3_output.md.
"""

import sys
from pathlib import Path
from prompts.content_verifier import verify_content

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

def run_test():
    print("=" * 60)
    print("RUNNING P3 CONTENT VERIFIER INTEGRATION TEST")
    print("=" * 60)

    p1_path = Path("test_p1_output.md")
    p2_path = Path("test_p2_output.md")

    if not p1_path.exists():
        print(f"[FAIL] Missing required test input: {p1_path.name}")
        return False
    if not p2_path.exists():
        print(f"[FAIL] Missing required test input: {p2_path.name}")
        return False

    analysis_text = p1_path.read_text(encoding="utf-8")
    questions_text = p2_path.read_text(encoding="utf-8")

    print(f"[INPUT 1] Original lecture text: {len(SAMPLE_LECTURE_TEXT)} characters")
    print(f"[INPUT 2] P1 Analysis: {len(analysis_text)} characters from {p1_path.name}")
    print(f"[INPUT 3] P2 Questions & Answers: {len(questions_text)} characters from {p2_path.name}")

    print("\nSending audit request to Groq API (openai/gpt-oss-120b)...")

    try:
        report_markdown = verify_content(
            lecture_text=SAMPLE_LECTURE_TEXT,
            analysis_text=analysis_text,
            questions_text=questions_text,
            temperature=0.1
        )

        print("\n[SUCCESS] Verification report received from Groq API!")
        print("-" * 60)
        print("Generated Audit Report Preview (First 500 characters):")
        print("-" * 60)
        print(report_markdown[:500] + "...\n")

        # Save actual unedited response
        output_file = Path("test_p3_output.md")
        output_file.write_text(report_markdown, encoding="utf-8")
        print(f"[EVIDENCE SAVED] Full report written to: {output_file.name}")

        # Structural and policy checks
        checks = [
            ("Disclaimer present", "Disclaimer" in report_markdown or "not a guarantee" in report_markdown.lower()),
            ("Summary section present", "Summary" in report_markdown or "Overview" in report_markdown),
            ("Verified claims section present", "Verified" in report_markdown),
            ("Calculation checks present", "Calculation" in report_markdown or "AMAT" in report_markdown),
            ("Status present (PASS/WARNINGS/NEEDS REVISION)", any(s in report_markdown for s in ["PASS", "PASS WITH WARNINGS", "NEEDS REVISION"])),
            ("Page references present", "Page" in report_markdown),
        ]

        print("\nOutput Structure Verification:")
        all_passed = True
        for name, passed in checks:
            status = "[PASS]" if passed else "[WARN]"
            print(f" {status} {name}")
            if not passed:
                all_passed = False

        print("=" * 60)
        return all_passed

    except Exception as e:
        print(f"\n[FAIL] Test encountered an error: {type(e).__name__} - {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
