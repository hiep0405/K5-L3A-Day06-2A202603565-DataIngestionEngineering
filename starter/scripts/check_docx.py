import docx
import re

doc_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019.docx"
doc = docx.Document(doc_path)

total_paragraphs = len(doc.paragraphs)
print(f"Total paragraphs: {total_paragraphs}")

full_text = "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
print(f"Total characters: {len(full_text)}")
print(f"Total words: {len(full_text.split())}")

chapters = re.findall(r'(Chương\s+[IVXLCDM]+[^\n]*)', full_text, re.I)
print(f"Total chapters found: {len(chapters)}")
for c in chapters[:10]:
    print(" ", c)

articles = re.findall(r'(Điều\s+\d+\.[^\n]*)', full_text)
print(f"Total articles (Điều) found: {len(articles)}")
for a in articles[:5]:
    print(" ", a)
print("  ...")
for a in articles[-3:]:
    print(" ", a)

