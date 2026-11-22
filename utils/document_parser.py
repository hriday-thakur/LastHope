"""
Document parser utility for LastHope.
Extracts structured text from PDF (using PyMuPDF) and TXT files.
Preserves page numbers, cleans excessive whitespace, and provides robust error handling.
"""

from dataclasses import dataclass, asdict
import io
import os
from pathlib import Path
import re
from typing import BinaryIO, Dict, List, Optional, Union
import pymupdf  # Official PyMuPDF import


class DocumentParsingError(Exception):
    """Base exception for document parsing failures."""
    pass


class EmptyDocumentError(DocumentParsingError):
    """Raised when a document contains zero extractable text (e.g. scanned image-only PDF or empty file)."""
    pass


class UnsupportedFormatError(DocumentParsingError):
    """Raised when an unsupported file format is provided."""
    pass


@dataclass
class PageData:
    """Stores text and metrics for a single extracted page."""
    page_number: int
    text: str
    char_count: int
    word_count: int


@dataclass
class ParsedDocument:
    """Structured result returned by parse_document."""
    extracted_text: str
    pages: List[PageData]
    page_numbers: List[int]
    total_pages: int
    word_count: int
    char_count: int
    file_type: str

    def to_dict(self) -> Dict:
        """Serializes the parsed document data to a dictionary."""
        return {
            "extracted_text": self.extracted_text,
            "pages": [asdict(p) for p in self.pages],
            "page_numbers": self.page_numbers,
            "total_pages": self.total_pages,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "file_type": self.file_type,
        }


def clean_text(text: str) -> str:
    """
    Cleans excessive whitespace without destroying meaningful formatting.
    - Normalizes \r\n and \r to \n
    - Strips trailing spaces from individual lines
    - Collapses 3 or more consecutive blank lines down to 2
    - Strips leading and trailing outer whitespace
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip trailing whitespace on each line while preserving indentation
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse 3+ consecutive newlines into 2 (one blank line between paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_pdf(source: Union[str, Path, bytes, BinaryIO]) -> ParsedDocument:
    """
    Extracts text page by page from a PDF using PyMuPDF.
    Preserves page numbers, handles corrupt/empty files, and detects scanned/image-only PDFs.
    """
    doc = None
    try:
        if isinstance(source, (str, Path)):
            file_path = Path(source)
            if not file_path.exists():
                raise DocumentParsingError(f"PDF file does not exist: {file_path}")
            doc = pymupdf.open(str(file_path))
        elif isinstance(source, bytes):
            if not source or len(source.strip()) == 0:
                raise EmptyDocumentError("The PDF file buffer is empty (0 bytes).")
            doc = pymupdf.open(stream=source, filetype="pdf")
        elif hasattr(source, "read"):
            content = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
            if not content or len(content.strip()) == 0:
                raise EmptyDocumentError("The PDF file buffer is empty (0 bytes).")
            doc = pymupdf.open(stream=content, filetype="pdf")
        else:
            raise UnsupportedFormatError(f"Unsupported source object type: {type(source)}")

        total_pages = len(doc)
        if total_pages == 0:
            raise EmptyDocumentError("The PDF document contains 0 pages.")

        pages: List[PageData] = []
        page_texts: List[str] = []

        for idx in range(total_pages):
            page_num = idx + 1
            page = doc[idx]
            raw_text = page.get_text()
            cleaned = clean_text(raw_text)

            word_count = len(cleaned.split()) if cleaned else 0
            char_count = len(cleaned)

            pages.append(
                PageData(
                    page_number=page_num,
                    text=cleaned,
                    char_count=char_count,
                    word_count=word_count,
                )
            )

            if cleaned:
                page_texts.append(f"--- [Page {page_num}] ---\n{cleaned}")

        total_chars = sum(p.char_count for p in pages)
        total_words = sum(p.word_count for p in pages)

        # Detect image-only or scanned PDFs with no OCR layer
        if total_chars == 0 or total_words == 0:
            raise EmptyDocumentError(
                "No extractable text was found in this PDF. "
                "The file appears to be a scanned document or image-only PDF without an embedded text layer."
            )

        combined_text = "\n\n".join(page_texts).strip()

        return ParsedDocument(
            extracted_text=combined_text,
            pages=pages,
            page_numbers=[p.page_number for p in pages],
            total_pages=total_pages,
            word_count=total_words,
            char_count=total_chars,
            file_type="pdf",
        )

    except (EmptyDocumentError, DocumentParsingError, UnsupportedFormatError):
        raise
    except pymupdf.FileDataError as e:
        raise DocumentParsingError(f"Corrupt or invalid PDF file: {e}") from e
    except Exception as e:
        raise DocumentParsingError(f"Error parsing PDF document: {e}") from e
    finally:
        if doc is not None:
            doc.close()


def parse_txt(
    source: Union[str, Path, bytes, BinaryIO],
    filename: Optional[str] = None
) -> ParsedDocument:
    """
    Extracts text from a plain text file, supporting UTF-8 and fallback encodings.
    """
    raw_bytes: bytes

    try:
        if isinstance(source, (str, Path)):
            file_path = Path(source)
            if not file_path.exists():
                raise DocumentParsingError(f"Text file does not exist: {file_path}")
            with open(file_path, "rb") as f:
                raw_bytes = f.read()
        elif isinstance(source, bytes):
            raw_bytes = source
        elif hasattr(source, "read"):
            raw_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(0)
        else:
            raise UnsupportedFormatError(f"Unsupported source object type: {type(source)}")

        if not raw_bytes or len(raw_bytes.strip()) == 0:
            raise EmptyDocumentError("The text file is empty (0 bytes).")

        # Encoding fallback strategy: try UTF-8, then CP1252 (Windows western), then ISO-8859-1 / Latin-1
        encodings = ["utf-8", "utf-8-sig", "cp1252", "iso-8859-1", "latin-1"]
        decoded_text: Optional[str] = None

        for enc in encodings:
            try:
                decoded_text = raw_bytes.decode(enc)
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if decoded_text is None:
            raise DocumentParsingError("Unable to decode text file with UTF-8 or common fallback encodings.")

        cleaned = clean_text(decoded_text)
        if not cleaned:
            raise EmptyDocumentError("The text file contains only blank or whitespace characters.")

        word_count = len(cleaned.split())
        char_count = len(cleaned)

        page = PageData(
            page_number=1,
            text=cleaned,
            char_count=char_count,
            word_count=word_count,
        )

        formatted_text = f"--- [Page 1] ---\n{cleaned}"

        return ParsedDocument(
            extracted_text=formatted_text,
            pages=[page],
            page_numbers=[1],
            total_pages=1,
            word_count=word_count,
            char_count=char_count,
            file_type="txt",
        )

    except (EmptyDocumentError, DocumentParsingError, UnsupportedFormatError):
        raise
    except Exception as e:
        raise DocumentParsingError(f"Error parsing text document: {e}") from e


def parse_document(
    source: Union[str, Path, bytes, BinaryIO],
    filename: Optional[str] = None
) -> ParsedDocument:
    """
    Unified dispatcher to parse either PDF or TXT files.
    Infers file type from filename or path, validates format,
    and returns a structured ParsedDocument.
    """
    ext = ""
    if filename:
        ext = Path(filename).suffix.lower()
    elif isinstance(source, (str, Path)):
        ext = Path(source).suffix.lower()

    if ext == ".pdf":
        return parse_pdf(source)
    elif ext in [".txt", ".text"]:
        return parse_txt(source, filename=filename)
    elif ext:
        raise UnsupportedFormatError(
            f"Unsupported file format '{ext}'. Only PDF (.pdf) and plain text (.txt) files are supported."
        )
    else:
        # If no filename is provided, inspect binary header / magic numbers
        if isinstance(source, bytes) and source.startswith(b"%PDF"):
            return parse_pdf(source)
        elif hasattr(source, "read"):
            prefix = source.read(5)
            if hasattr(source, "seek"):
                source.seek(0)
            if prefix.startswith(b"%PDF"):
                return parse_pdf(source)
            return parse_txt(source, filename=filename)
        else:
            raise UnsupportedFormatError(
                "Unable to determine file type. Please provide a file with a .pdf or .txt extension."
            )
