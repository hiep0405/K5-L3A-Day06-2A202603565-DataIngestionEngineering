import json
from pathlib import Path
from starter.src.ingestion import load_pdf
from starter.src.chunking import fixed_size, by_paragraph

pdf_path = Path("data/bo_luat_lao_dong_2019_clean.pdf")
pages = load_pdf(pdf_path, "bo-luat-lao-dong-2019", "pdf")

sample_page_nums = [3, 11, 14, 17, 27, 59, 65, 76, 85, 91]

coherence_records = []

for p_num in sample_page_nums:
    p = next(x for x in pages if x.page == p_num)
    ca = fixed_size(p, 500, 50)[0]
    cb = by_paragraph(p, 600)[0]
    
    # Assess Strategy A
    # Fixed size chunk often cuts mid-sentence or mid-clause
    score_a = 1  # partially understandable, cuts context at 500 boundary
    # If ends with period or complete clause
    if ca.text.endswith((".", "!", "?")):
        score_a = 2
    elif ca.text.endswith((",", ";", ":", "-")) or len(ca.text) == 500:
        score_a = 1
        
    # Strategy B groups by paragraph/provision
    score_b = 2  # preserves complete legal paragraph/article
    if not cb.text.endswith((".", "!", "?")):
        score_b = 1
    else:
        score_b = 2

    coherence_records.append({
        "page": p_num,
        "text_a_preview": ca.text[:120].replace("\n", " "),
        "text_a_end": ca.text[-60:].replace("\n", " "),
        "score_a": score_a,
        "text_b_preview": cb.text[:120].replace("\n", " "),
        "text_b_end": cb.text[-60:].replace("\n", " "),
        "score_b": score_b
    })

print(f"Total samples: {len(coherence_records)}")
avg_a = sum(r["score_a"] for r in coherence_records) / len(coherence_records)
avg_b = sum(r["score_b"] for r in coherence_records) / len(coherence_records)
print(f"Average Coherence Score Strategy A: {avg_a:.2f}/2")
print(f"Average Coherence Score Strategy B: {avg_b:.2f}/2")

for idx, r in enumerate(coherence_records, 1):
    print(f"\nPosition {idx} (Page {r['page']}):")
    print(f"  Strat A [Score {r['score_a']}]: ...{r['text_a_end']}")
    print(f"  Strat B [Score {r['score_b']}]: ...{r['text_b_end']}")
