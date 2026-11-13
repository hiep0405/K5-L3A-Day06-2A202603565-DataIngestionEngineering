"""Evaluate retrieved evidence and preserve per-query traces."""
import re
from typing import Any


def _is_evidence_present(evidence_quote: str, chunk_text: str) -> bool:
    """Check if evidence quote or its substantial sub-clause is contained in the chunk text."""
    eq_norm = " ".join(evidence_quote.lower().split())
    ct_norm = " ".join(chunk_text.lower().split())
    
    # Exact substring
    if eq_norm in ct_norm:
        return True
    
    # Break quote into sentences or clauses (split by ; or . or :)
    clauses = [c.strip() for c in re.split(r'[;.:\n]', eq_norm) if len(c.strip()) > 15]
    if clauses:
        # If at least half the clauses or the primary clause is in chunk text
        matched_clauses = sum(1 for c in clauses if c in ct_norm)
        if matched_clauses >= max(1, len(clauses) // 2):
            return True
            
    # Check keyword overlap (at least 75% of meaningful words)
    words = [w for w in re.findall(r'\w+', eq_norm) if len(w) > 2]
    if words:
        found_words = sum(1 for w in words if w in ct_norm)
        if found_words / len(words) >= 0.75:
            return True
            
    return False


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """Check source/page and gold evidence match; retain Hit@1 and Hit@3 trace."""
    gold_page = question.get("gold_page")
    evidence_quote = question.get("evidence_quote", "")
    
    evaluated_hits = []
    has_hit_1 = False
    has_hit_3 = False
    
    for rank, hit in enumerate(hits, start=1):
        hit_page = hit.get("page")
        chunk_text = hit.get("text", "")
        
        # A hit requires matching gold page AND containing sufficient evidence
        page_match = (hit_page == gold_page)
        evidence_match = _is_evidence_present(evidence_quote, chunk_text)
        is_hit = page_match and evidence_match
        
        if rank == 1 and is_hit:
            has_hit_1 = True
        if rank <= 3 and is_hit:
            has_hit_3 = True
            
        evaluated_hits.append({
            "rank": rank,
            "chunk_id": hit.get("chunk_id"),
            "score": hit.get("score"),
            "page": hit_page,
            "gold_page": gold_page,
            "page_match": page_match,
            "evidence_match": evidence_match,
            "is_hit": is_hit,
            "text": chunk_text,
            "metadata": hit.get("metadata", {})
        })
        
    return {
        "question_id": question.get("id"),
        "split": question.get("split"),
        "type": question.get("type"),
        "question": question.get("question"),
        "expected_answer": question.get("expected_answer"),
        "gold_page": gold_page,
        "evidence_quote": evidence_quote,
        "filter_applied": question.get("filter"),
        "hit_1": has_hit_1,
        "hit_3": has_hit_3,
        "hits": evaluated_hits
    }


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Hit@1 and Evidence Hit@3 by dev/test split."""
    summary: dict[str, Any] = {
        "dev": {"total": 0, "hit1": 0, "hit3": 0, "hit1_rate": 0.0, "hit3_rate": 0.0},
        "test": {"total": 0, "hit1": 0, "hit3": 0, "hit1_rate": 0.0, "hit3_rate": 0.0},
        "overall": {"total": 0, "hit1": 0, "hit3": 0, "hit1_rate": 0.0, "hit3_rate": 0.0}
    }
    
    for t in traces:
        split = t.get("split", "dev")
        if split not in summary:
            summary[split] = {"total": 0, "hit1": 0, "hit3": 0, "hit1_rate": 0.0, "hit3_rate": 0.0}
            
        summary[split]["total"] += 1
        summary["overall"]["total"] += 1
        
        if t.get("hit_1"):
            summary[split]["hit1"] += 1
            summary["overall"]["hit1"] += 1
            
        if t.get("hit_3"):
            summary[split]["hit3"] += 1
            summary["overall"]["hit3"] += 1

    for s in ["dev", "test", "overall"]:
        tot = summary[s]["total"]
        if tot > 0:
            summary[s]["hit1_rate"] = round(summary[s]["hit1"] / tot, 4)
            summary[s]["hit3_rate"] = round(summary[s]["hit3"] / tot, 4)
            
    return summary
