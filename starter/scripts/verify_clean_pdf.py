import pypdf

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"

reader = pypdf.PdfReader(pdf_path)
total = len(reader.pages)
print(f"Total pages: {total}")

non_empty = 0
char_counts = []
for i, page in enumerate(reader.pages):
    text = (page.extract_text() or "").strip()
    char_counts.append(len(text))
    if len(text) > 100:
        non_empty += 1

print(f"Non empty pages (>100 chars): {non_empty}/{total}")
print(f"Total characters: {sum(char_counts)}")
print(f"Average characters/page: {sum(char_counts)/total:.1f}")
print("--- Page 1 snippet ---")
print(reader.pages[0].extract_text()[:300])
print("--- Page 2 snippet ---")
print(reader.pages[1].extract_text()[:300])

