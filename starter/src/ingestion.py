"""Read and normalize source data."""
from pathlib import Path
import unicodedata
import re
import pypdf
from .models import DocumentPage


def normalize_text(text: str) -> str:
    """Normalize Unicode (NFC), remove weird control characters, and clean up excessive whitespace
    without destroying paragraph breaks.
    """
    if not text:
        return ""
    # NFC normalization for Vietnamese accents
    text = unicodedata.normalize("NFC", text)
    # Replace non-breaking spaces and tabs
    text = text.replace("\u00a0", " ").replace("\t", " ")
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Clean multiple spaces within lines
    lines = []
    for line in text.split("\n"):
        cleaned_line = re.sub(r"[ ]+", " ", line).strip()
        lines.append(cleaned_line)
    # Rejoin lines, collapse more than 2 consecutive newlines into 2
    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract each physical page; keep its page number, source, and chapter metadata."""
    reader = pypdf.PdfReader(str(path))
    pages: list[DocumentPage] = []
    
    current_chapter = "CHƯƠNG_I"  # Default initial chapter
    
    chapter_map = {
        "I": "CHƯƠNG_I", "II": "CHƯƠNG_II", "III": "CHƯƠNG_III", "IV": "CHƯƠNG_IV",
        "V": "CHƯƠNG_V", "VI": "CHƯƠNG_VI", "VII": "CHƯƠNG_VII", "VIII": "CHƯƠNG_VIII",
        "IX": "CHƯƠNG_IX", "X": "CHƯƠNG_X", "XI": "CHƯƠNG_XI", "XII": "CHƯƠNG_XII",
        "XIII": "CHƯƠNG_XIII", "XIV": "CHƯƠNG_XIV", "XV": "CHƯƠNG_XV", "XVI": "CHƯƠNG_XVI",
        "XVII": "CHƯƠNG_XVII"
    }

    for idx, raw_page in enumerate(reader.pages):
        page_num = idx + 1
        raw_text = raw_page.extract_text() or ""
        clean_text = normalize_text(raw_text)
        
        # Check if page contains chapter announcement
        m = re.search(r'Chương\s+([IVXLCDM]+)', clean_text, re.I)
        if m:
            c_roman = m.group(1).upper()
            if c_roman in chapter_map:
                current_chapter = chapter_map[c_roman]
        
        metadata = {
            "chapter": current_chapter,
            "char_count": len(clean_text),
            "is_empty": len(clean_text) == 0
        }
        
        pages.append(DocumentPage(
            document_id=document_id,
            source=source,
            page=page_num,
            text=clean_text,
            metadata=metadata
        ))
        
    return pages
