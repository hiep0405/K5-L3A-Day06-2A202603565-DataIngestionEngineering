import pypdf
import os

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019.pdf"

reader = pypdf.PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total pages: {total_pages}")

non_empty_pages = 0
char_counts = []
sample_heads = []

for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    text_clean = text.strip()
    char_counts.append(len(text_clean))
    if len(text_clean) > 100:
        non_empty_pages += 1
    if idx < 5:
        sample_heads.append((idx + 1, len(text_clean), text_clean[:150].replace('\n', ' ')))

print(f"Non-empty pages (>100 chars): {non_empty_pages}")
print(f"Average chars per page: {sum(char_counts)/total_pages:.1f}")
print("First 5 pages samples:")
for p, length, sample in sample_heads:
    print(f"  Page {p} ({length} chars): {sample}")

# Let's check chapter count
full_text = "\n".join([p.extract_text() or "" for p in reader.pages])
import re
chapters = re.findall(r'(Chương\s+[IVXLCDM]+[^\n]*)', full_text, re.I)
print(f"Found {len(chapters)} chapter mentions. Sample:")
for c in chapters[:10]:
    print(" ", c)

articles = re.findall(r'(Điều\s+\d+\.[^\n]*)', full_text)
print(f"Found {len(articles)} articles (Điều).")

