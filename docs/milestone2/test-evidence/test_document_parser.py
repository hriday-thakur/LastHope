"""
Unit and edge-case test suite for utils/document_parser.py.
Tests PDF extraction, TXT extraction, whitespace cleaning,
encoding fallbacks, and edge cases (empty, scanned, corrupt, unsupported).
"""

import io
import pymupdf  # Official PyMuPDF import
from utils.document_parser import (
    clean_text,
    parse_pdf,
    parse_txt,
    parse_document,
    DocumentParsingError,
    EmptyDocumentError,
    UnsupportedFormatError,
)

def create_sample_pdf() -> bytes:
    """Creates an in-memory 2-page PDF with lecture content."""
    doc = pymupdf.open()
    
    # Page 1
    page1 = doc.new_page()
    page1.insert_text(
        (50, 72),
        "Lecture 1: Introduction to Machine Learning\n\n"
        "Supervised learning uses labeled training data.\n"
        "Key algorithms include Linear Regression and SVM.\n\n\n\n"
        "End of Page 1."
    )
    
    # Page 2
    page2 = doc.new_page()
    page2.insert_text(
        (50, 72),
        "Lecture 1 (Cont.): Unsupervised Learning\n\n"
        "Clustering finds natural groupings in unlabeled data.\n"
        "Common algorithms: K-Means and PCA."
    )
    
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def create_blank_pdf() -> bytes:
    """Creates a 2-page PDF with blank pages (simulates scanned/image PDF with no text)."""
    doc = pymupdf.open()
    doc.new_page()
    doc.new_page()
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def run_tests():
    print("=" * 60)
    print("RUNNING DOCUMENT PARSER TEST SUITE")
    print("=" * 60)
    passed = 0
    total = 0

    def check(test_name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            print(f"[PASS] {test_name}")
            if details:
                print(f"       -> {details}")
            passed += 1
        else:
            print(f"[FAIL] {test_name}")
            if details:
                print(f"       -> {details}")

    # 1. Clean whitespace test
    dirty_text = "  Line 1   \r\n\r\n\r\n\r\nLine 2    \n\n\nLine 3   "
    cleaned = clean_text(dirty_text)
    expected = "Line 1\n\nLine 2\n\nLine 3"
    check("Whitespace cleaning", cleaned == expected, f"Result: {repr(cleaned)}")

    # 2. Multi-page PDF extraction
    sample_pdf_bytes = create_sample_pdf()
    pdf_res = parse_document(sample_pdf_bytes, filename="lecture.pdf")
    check("PDF multi-page parsing", pdf_res.total_pages == 2, f"Total pages: {pdf_res.total_pages}")
    check("PDF page 1 preservation", "--- [Page 1] ---" in pdf_res.extracted_text and "Linear Regression" in pdf_res.extracted_text)
    check("PDF page 2 preservation", "--- [Page 2] ---" in pdf_res.extracted_text and "K-Means" in pdf_res.extracted_text)
    check("PDF word count metric", pdf_res.word_count > 20, f"Word count: {pdf_res.word_count}")

    # 3. Stream/file-like object handling
    stream = io.BytesIO(sample_pdf_bytes)
    stream_res = parse_document(stream, filename="stream_lecture.pdf")
    check("PDF stream/buffer parsing", stream_res.total_pages == 2, f"Total pages: {stream_res.total_pages}")

    # 4. Standard UTF-8 TXT extraction
    txt_content = "Topic: Operating Systems\n\nProcesses vs Threads.\nA process has its own address space."
    txt_res = parse_document(txt_content.encode("utf-8"), filename="notes.txt")
    check("TXT UTF-8 parsing", txt_res.total_pages == 1 and "Operating Systems" in txt_res.extracted_text)
    check("TXT structured metadata", txt_res.word_count == 13, f"Word count: {txt_res.word_count}")

    # 5. TXT Fallback Encoding (Latin-1 with accented characters)
    latin1_bytes = "Thème: Intelligence Artificielle & Système d'Exploitation. Coût: 100£.".encode("latin-1")
    latin_res = parse_document(latin1_bytes, filename="french_notes.txt")
    check("TXT fallback encoding (Latin-1)", "Intelligence Artificielle" in latin_res.extracted_text, f"Extracted: {latin_res.extracted_text[:40]}...")

    # 6. TXT Fallback Encoding (CP1252 with Euro symbol)
    cp1252_bytes = "Prix total du cours: 50€ TTC.".encode("cp1252")
    cp_res = parse_document(cp1252_bytes, filename="pricing.txt")
    check("TXT fallback encoding (CP1252)", "50€" in cp_res.extracted_text, f"Extracted: {cp_res.extracted_text}")

    # 7. Edge Case: Scanned / Image-only PDF (No text)
    blank_pdf_bytes = create_blank_pdf()
    try:
        parse_document(blank_pdf_bytes, filename="scanned.pdf")
        check("Scanned PDF detection", False, "Should have raised EmptyDocumentError")
    except EmptyDocumentError as e:
        check("Scanned PDF detection", True, f"Caught expected EmptyDocumentError: {e}")

    # 8. Edge Case: Completely empty 0-byte PDF
    try:
        parse_document(b"", filename="empty.pdf")
        check("0-byte PDF handling", False, "Should have raised EmptyDocumentError")
    except EmptyDocumentError as e:
        check("0-byte PDF handling", True, f"Caught expected EmptyDocumentError: {e}")

    # 9. Edge Case: Corrupt PDF
    try:
        parse_document(b"%PDF-1.4 corrupt junk content that cannot be parsed by pymupdf", filename="corrupt.pdf")
        check("Corrupt PDF handling", False, "Should have raised DocumentParsingError")
    except DocumentParsingError as e:
        check("Corrupt PDF handling", True, f"Caught expected DocumentParsingError: {e}")

    # 10. Edge Case: Empty / Whitespace-only TXT
    try:
        parse_document(b"   \n\n\t  \n  ", filename="blank.txt")
        check("Whitespace-only TXT handling", False, "Should have raised EmptyDocumentError")
    except EmptyDocumentError as e:
        check("Whitespace-only TXT handling", True, f"Caught expected EmptyDocumentError: {e}")

    # 11. Edge Case: Unsupported File Format
    try:
        parse_document(b"PK\x03\x04...", filename="document.docx")
        check("Unsupported format rejection", False, "Should have raised UnsupportedFormatError")
    except UnsupportedFormatError as e:
        check("Unsupported format rejection", True, f"Caught expected UnsupportedFormatError: {e}")

    print("=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed.")
    print("=" * 60)
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    import sys
    sys.exit(0 if success else 1)
