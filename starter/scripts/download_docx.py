import urllib.request
import ssl
import os

ctx = ssl._create_unverified_context()
base = "https://pgdbinhthanh.hcm.edu.vn"
rel_url = "/tai/L4_CFyZfKKnskeJ61c0luBJhpw3SvFllVPNJQqQWhMsjcFXUdqOlAr2RVz7d3PT-rnY3hIhhuwCfIP6i2iAjUBUfz5IiiTD6RbdueC_GM64GG2AqzR8qC_eEuRAteSc4apfNjuSRFurzazacFbPZLOl-PfresQLON9y7VUgomwrqHDHl6KmpBxxwC6dBYOdej8j8iBAU/38XlJTTkoRKBGXG8qiEl2mBmo7KyOg/luat-lao-dong-2019.docx"
url = base + rel_url
out_dir = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data"
out_path = os.path.join(out_dir, "bo_luat_lao_dong_2019.docx")

print("Downloading docx from:", url)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
    data = resp.read()
    print("Downloaded bytes:", len(data))
    with open(out_path, "wb") as f:
        f.write(data)
print("Saved to:", out_path)

