import pypdf
import re

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(pdf_path)

chapters = []
for p_idx, page in enumerate(reader.pages):
    p_num = p_idx + 1
    text = page.extract_text() or ""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r'^(Chương\s+[IVXLCDM]+)\s*$', line.strip(), re.I)
        if m:
            title = lines[i+1].strip() if i+1 < len(lines) else ""
            chapters.append({"chapter": m.group(1).upper(), "title": title, "page": p_num})

print(f"Total chapters: {len(chapters)}")
for c in chapters:
    print(f"{c['chapter']} (Page {c['page']}): {c['title']}")

