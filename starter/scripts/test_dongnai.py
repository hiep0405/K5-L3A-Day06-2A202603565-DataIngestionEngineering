import urllib.request
import ssl
import os
import pypdf

ctx = ssl._create_unverified_context()
pdf_url = "https://dnieza.dongnai.gov.vn/Lists/VanBan/Attachments/162/bo-luat-lao-dong-2019.pdf"
out_dir = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data"
out_path = os.path.join(out_dir, "bo_luat_lao_dong_2019_dongnai.pdf")

print("Downloading from:", pdf_url)
req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        data = resp.read()
        print("Downloaded size:", len(data), "bytes")
        with open(out_path, "wb") as f:
            f.write(data)
    
    reader = pypdf.PdfReader(out_path)
    print("Total pages:", len(reader.pages))
    non_empty = 0
    total_chars = 0
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        chars = len(text.strip())
        total_chars += chars
        if chars > 50:
            non_empty += 1
    print(f"Non empty pages: {non_empty}/{len(reader.pages)}")
    print(f"Total chars: {total_chars}")
    print("Page 1 snippet:", reader.pages[0].extract_text()[:300].replace('\n', ' '))
except Exception as e:
    print("Error:", e)

