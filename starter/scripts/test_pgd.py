import urllib.request, ssl, re

ctx = ssl._create_unverified_context()
url = "https://pgdbinhthanh.hcm.edu.vn/van-ban-phap-luat/bo-luat-lao-dong/vbctmb/84260/416692"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    print("Page length:", len(html))
    links = re.findall(r'href=["\']([^"\']+\.(?:docx?|pdf)[^"\']*)["\']', html, re.I)
    print("Links found:", links)
except Exception as e:
    print("Error:", e)

