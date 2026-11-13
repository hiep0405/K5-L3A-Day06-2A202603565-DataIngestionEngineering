"""Implement fixed-size and structure-aware chunking."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Split text into overlapping windows and retain page metadata (Strategy A)."""
    text = page.text
    if not text:
        return []
    
    chunks: list[Chunk] = []
    start = 0
    step = max(1, size - overlap)
    idx = 0
    
    while start < len(text):
        end = min(start + size, len(text))
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk_id = f"{page.document_id}_p{page.page}_a_{idx}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=chunk_text,
                metadata={**page.metadata, "strategy": "A", "chunk_idx": idx}
            ))
            idx += 1
        if end >= len(text):
            break
        start += step
        
    return chunks


def by_paragraph(page: DocumentPage, max_size: int = 600) -> list[Chunk]:
    """Structure-aware chunking by grouping paragraphs / legal provisions (Strategy B & C)."""
    text = page.text
    if not text:
        return []
    
    # Split text by double newlines or lines starting with Điều / Khoản
    raw_paras = re.split(r'\n{2,}|\n(?=(?:Điều\s+\d+|[0-9]+\.\s+|[a-z]\)\s+))', text)
    paras = [p.strip() for p in raw_paras if p.strip()]
    
    chunks: list[Chunk] = []
    current_group: list[str] = []
    current_len = 0
    idx = 0
    
    def flush_group():
        nonlocal current_group, current_len, idx
        if not current_group:
            return
        combined_text = "\n".join(current_group).strip()
        if combined_text:
            chunk_id = f"{page.document_id}_p{page.page}_b_{idx}"
            chunks.append(Chunk(
                chunk_id=chunk_id,
                document_id=page.document_id,
                source=page.source,
                page=page.page,
                text=combined_text,
                metadata={**page.metadata, "strategy": "B", "chunk_idx": idx}
            ))
            idx += 1
        current_group = []
        current_len = 0
        
    for p in paras:
        # If single paragraph is oversized, split it by sentence
        if len(p) > max_size:
            flush_group()
            sentences = re.split(r'(?<=[.;])\s+', p)
            s_group: list[str] = []
            s_len = 0
            for s in sentences:
                if s_len + len(s) > max_size and s_group:
                    chunk_id = f"{page.document_id}_p{page.page}_b_{idx}"
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=" ".join(s_group).strip(),
                        metadata={**page.metadata, "strategy": "B", "chunk_idx": idx}
                    ))
                    idx += 1
                    s_group = [s]
                    s_len = len(s)
                else:
                    s_group.append(s)
                    s_len += len(s) + 1
            if s_group:
                chunk_id = f"{page.document_id}_p{page.page}_b_{idx}"
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=" ".join(s_group).strip(),
                    metadata={**page.metadata, "strategy": "B", "chunk_idx": idx}
                ))
                idx += 1
        else:
            if current_len + len(p) > max_size and current_group:
                flush_group()
            current_group.append(p)
            current_len += len(p) + 1
            
    flush_group()
    return chunks
