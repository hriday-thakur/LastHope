"""
LastHope Export Helper Module
Provides utilities for compiling comprehensive study packs, sanitizing export
filenames, and validating download payload integrity across Markdown and TXT formats.
"""

from datetime import datetime
from pathlib import Path
import re
from typing import Optional


def sanitize_filename(
    name: Optional[str],
    fallback: str = "lecture",
    max_len: int = 50,
) -> str:
    """
    Sanitizes a document name or filename for safe cross-platform file downloads.
    - Strips path components and directory traversal attempts.
    - Replaces invalid Windows/POSIX filename characters (\\/*?:"<>|) and whitespace with '_'.
    - Preserves only alphanumeric characters, underscores, and hyphens.
    - Collapses consecutive underscores and strips boundary underscores/dots/hyphens.
    - Truncates to max_len characters to avoid filesystem path limit issues.
    - Falls back to `fallback` if the result is empty or invalid.
    """
    if not name or not str(name).strip():
        return fallback

    # Extract stem if a full path or file with extension was provided
    raw_str = str(name).strip()
    stem = Path(raw_str).stem

    # Replace invalid filename characters and whitespace
    clean = re.sub(r"[^A-Za-z0-9_\-]", "_", stem)
    # Collapse multiple consecutive underscores
    clean = re.sub(r"_+", "_", clean).strip("._-")

    if not clean:
        return fallback

    # Truncate and strip trailing boundary punctuation
    return clean[:max_len].rstrip("._-") or fallback


def build_study_pack(
    doc_name: str,
    file_name: Optional[str] = None,
    model_name: Optional[str] = None,
    p1_analysis: Optional[str] = None,
    p2_questions: Optional[str] = None,
    p3_verification: Optional[str] = None,
    timestamp_str: Optional[str] = None,
) -> str:
    """
    Compiles a comprehensive study pack containing all generated revision materials.

    Structure:
    - Metadata Header (Title, timestamp, source filename, model engine)
    - PART I: Lecture Revision Notes (P1) if generated and non-empty
    - PART II: Practice Questions & Answer Key (P2) if generated and non-empty
    - PART III: Content Verification & Audit Report (P3) if generated and non-empty

    Args:
        doc_name: Document display title or stem.
        file_name: Original uploaded source filename.
        model_name: Groq model engine identifier.
        p1_analysis: Generated P1 revision notes text.
        p2_questions: Generated P2 practice questions and answer key text.
        p3_verification: Generated P3 content verification audit report text.
        timestamp_str: Optional explicit timestamp string for reproducible tests.

    Returns:
        Structured Markdown text string of the study pack, or empty string if
        no exportable revision content is available.
    """
    has_p1 = bool(p1_analysis and p1_analysis.strip())
    has_p2 = bool(p2_questions and p2_questions.strip())
    has_p3 = bool(p3_verification and p3_verification.strip())

    if not (has_p1 or has_p2 or has_p3):
        return ""

    ts = timestamp_str or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_file = str(file_name).strip() if (file_name is not None and str(file_name).strip()) else "Unspecified"
    engine = str(model_name).strip() if (model_name is not None and str(model_name).strip()) else "Unknown"
    title_doc = str(doc_name).strip() if (doc_name is not None and str(doc_name).strip()) else "Lecture"

    pack_lines = [
        f"# LastHope Study Pack: {title_doc}",
        f"- Generated On: {ts}",
        f"- Source File: {src_file}",
        f"- Model Engine: {engine}",
        "\n---\n",
    ]

    if has_p1:
        pack_lines.append("## PART I: LECTURE REVISION NOTES (P1)\n")
        pack_lines.append(p1_analysis.strip())
        pack_lines.append("\n---\n")

    if has_p2:
        pack_lines.append("## PART II: REVISION QUESTIONS & ANSWER KEY (P2)\n")
        pack_lines.append(p2_questions.strip())
        pack_lines.append("\n---\n")

    if has_p3:
        pack_lines.append("## PART III: CONTENT VERIFICATION & AUDIT REPORT (P3)\n")
        pack_lines.append(p3_verification.strip())
        pack_lines.append("\n---\n")

    return "\n".join(pack_lines).strip()
