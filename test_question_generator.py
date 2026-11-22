"""
Integration test script for Prompt 2 (P2): Revision Question Generator.
Uses real lecture text and the P1 analysis from test_p1_output.md to generate
a balanced set of practice questions and answer key via Groq API.
Saves actual output to test_p2_output.md.
"""

import sys
from pathlib import Path
from prompts.question_generator import generate_questions

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
    print("RUNNING P2 QUESTION GENERATOR INTEGRATION TEST")
    print("=" * 60)

    # Load P1 analysis from test_p1_output.md if available
    p1_file = Path("test_p1_output.md")
    if p1_file.exists():
        analysis_text = p1_file.read_text(encoding="utf-8")
        print(f"[INPUT] Loaded P1 analysis from {p1_file.name} ({len(analysis_text)} chars)")
    else:
        analysis_text = "Summary: Memory Hierarchy covers SRAM (caches) vs DRAM (main memory), Locality (temporal/spatial), AMAT formula, and 3 C's of misses."
        print("[INPUT] Using fallback sample P1 analysis")

    print("\nSending request to Groq API (openai/gpt-oss-120b)...")

    try:
        questions_markdown = generate_questions(
            lecture_text=SAMPLE_LECTURE_TEXT,
            analysis_text=analysis_text,
            num_questions=8,
            temperature=0.3
        )

        print("\n[SUCCESS] Response received from Groq API!")
        print("-" * 60)
        print("Generated Questions Preview (First 500 characters):")
        print("-" * 60)
        print(questions_markdown[:500] + "...\n")

        # Save actual output to test_p2_output.md
        output_file = Path("test_p2_output.md")
        output_file.write_text(questions_markdown, encoding="utf-8")
        print(f"[EVIDENCE SAVED] Full output written to: {output_file.name}")

        # Validate structural criteria
        checks = [
            ("Multiple-Choice section present", "Multiple-Choice" in questions_markdown or "Section A" in questions_markdown),
            ("Short-Answer section present", "Short-Answer" in questions_markdown or "Section B" in questions_markdown),
            ("Conceptual/Application section present", "Conceptual" in questions_markdown or "Application" in questions_markdown or "Section C" in questions_markdown),
            ("Answer Key section present", "Answer Key" in questions_markdown or "Part 2" in questions_markdown),
            ("Difficulty tags present", any(tag in questions_markdown for tag in ["[Easy]", "[Medium]", "[Hard]", "Easy", "Medium", "Hard"])),
            ("Page references present", "[Page" in questions_markdown),
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
