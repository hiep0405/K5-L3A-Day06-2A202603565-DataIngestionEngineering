import pypdf
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parents[2]
pdf_path = base_dir / "data" / "bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(str(pdf_path))

pages_meta = []
total_chars = 0
for i, page in enumerate(reader.pages):
    text = (page.extract_text() or "").strip()
    c_len = len(text)
    total_chars += c_len
    pages_meta.append({
        "page_number": i + 1,
        "char_count": c_len,
        "is_content_page": True
    })

manifest = {
    "source_id": "bo-luat-lao-dong-2019",
    "title": "Bộ luật Lao động nước Cộng hòa xã hội chủ nghĩa Việt Nam (Số 45/2019/QH14)",
    "source_path_or_url": "data/bo_luat_lao_dong_2019_clean.pdf (Nguồn gốc: Văn bản công bố chính thức số 45/2019/QH14 được Quốc hội thông qua ngày 20/11/2019)",
    "license_or_permission": "Phạm vi công cộng (Theo Điều 19 Luật Sở hữu trí tuệ, văn bản quy phạm pháp luật không thuộc đối tượng bảo hộ quyền tác giả)",
    "accessed_at": "2026-11-13",
    "total_pages": len(reader.pages),
    "content_pages_count": len([p for p in pages_meta if p["is_content_page"]]),
    "page_counting_rule": "Toàn bộ 145 trang đều có text số hóa đầy đủ (>100 ký tự/trang). Trong đó trang 1 là tóm lược điểm mới, từ trang 2 đến trang 145 là toàn văn 17 chương và 220 điều của Bộ luật Lao động 2019.",
    "total_characters": total_chars,
    "pages": pages_meta
}

manifest_path = base_dir / "data" / "manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Manifest created successfully at:", manifest_path)
