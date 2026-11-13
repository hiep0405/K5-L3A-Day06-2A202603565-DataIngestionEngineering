import urllib.request
import ssl
import os

ctx = ssl._create_unverified_context()
pdf_url = "https://ncthanh.khanhhoa.edu.vn/upload/38624/20230222/45_2019_QH14_392289_75c18.pdf"
out_dir = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "bo_luat_lao_dong_2019.pdf")

print("Downloading from:", pdf_url)
req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
    data = resp.read()
    print("Downloaded size:", len(data), "bytes")
    with open(out_path, "wb") as f:
        f.write(data)
    print("Saved to:", out_path)
