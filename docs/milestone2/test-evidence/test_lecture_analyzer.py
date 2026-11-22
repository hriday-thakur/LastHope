"""
Integration test script for Prompt 1 (P1): Lecture Content Analyzer.
Sends realistic sample lecture text to Groq API and validates the structured output.
Saves the actual generated revision notes as evidence.
"""

import sys
from pathlib import Path
from prompts.lecture_analyzer import analyze_lecture

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
    print("RUNNING P1 LECTURE ANALYZER INTEGRATION TEST")
    print("=" * 60)
    print("Sending sample lecture text to Groq API...")

    try:
        revision_notes = analyze_lecture(SAMPLE_LECTURE_TEXT)

        print("\n[SUCCESS] Response received from Groq API!")
        print("-" * 60)
        print("Generated Output Preview (First 500 characters):")
        print("-" * 60)
        print(revision_notes[:500] + "...\n")

        # Save actual output as test evidence
        evidence_file = Path("test_p1_output.md")
        evidence_file.write_text(revision_notes, encoding="utf-8")
        print(f"[EVIDENCE SAVED] Full output written to: {evidence_file.name}")

        # Basic structural validations
        checks = [
            ("Overview section present", "Overview" in revision_notes),
            ("Topic breakdown present", "Topic" in revision_notes),
            ("Definitions present", "Terminology" in revision_notes or "Definition" in revision_notes),
            ("Clarifications / Gaps present", "Clarification" in revision_notes or "Gap" in revision_notes),
            ("Page citation present", "[Page" in revision_notes),
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
