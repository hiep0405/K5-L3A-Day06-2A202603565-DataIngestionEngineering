import pypdf
import json

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(pdf_path)

def get_page_text(p_num):
    return reader.pages[p_num - 1].extract_text() or ""

# Let's inspect pages: 3, 7, 11, 14, 17, 18, 27, 59, 61, 65, 68, 69, 70, 76, 78, 85, 91, 144
pages_to_check = [3, 7, 11, 14, 17, 18, 27, 59, 61, 65, 68, 69, 70, 76, 78, 85, 91, 144]
for p in pages_to_check:
    txt = get_page_text(p)
    print(f"=== PAGE {p} ===")
    for l in txt.split("\n")[:12]:
        if l.strip():
            print(" ", l.strip()[:100])

