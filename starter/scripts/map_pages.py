import pypdf
import re
import json

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(pdf_path)

page_articles = {}
for p_idx, page in enumerate(reader.pages):
    p_num = p_idx + 1
    text = page.extract_text() or ""
    # find articles
    arts = re.findall(r'(Điều\s+\d+)\.\s*([^\n\r]+)', text)
    chaps = re.findall(r'(Chương\s+[IVXLCDM]+)[\s\n\r]*([^\n\r]+)', text)
    if arts or chaps:
        page_articles[p_num] = {
            "chaps": chaps,
            "arts": arts[:5]
        }

print("Sample mappings:")
for p in sorted(page_articles.keys())[:25]:
    info = page_articles[p]
    print(f"Page {p}: chaps={info['chaps']}, arts={info['arts']}")

