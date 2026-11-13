import urllib.request, ssl, re

ctx = ssl._create_unverified_context()
url = 'https://vbpl.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=139330'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, context=ctx, timeout=15).read().decode('utf-8', errors='ignore')

print("Iframes:", re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.I))
print("Attachments:", re.findall(r'href=["\']([^"\']+\.(?:pdf|doc|docx)[^"\']*)["\']', html, re.I))
for line in html.split('\n'):
    if 'toanvan' in line.lower() or 'vanban' in line.lower() or 'docid' in line.lower() or 'download' in line.lower():
        print("MATCH:", line[:120].strip())

