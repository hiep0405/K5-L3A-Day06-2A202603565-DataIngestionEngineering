import pypdf
import json

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(pdf_path)

pages_text = []
for p in reader.pages:
    pages_text.append(p.extract_text() or "")

print(f"Cached {len(pages_text)} pages.")

queries = [
    ("Độ tuổi lao động tối thiểu", "Điều 3"),
    ("hành vi bị nghiêm cấm", "Điều 8"),
    ("Các loại hợp đồng lao động", "Điều 20"),
    ("Thời gian thử việc", "Điều 25"),
    ("Tiền lương thử việc", "Điều 26"),
    ("Làm việc không trọn thời gian", "Điều 32"),
    ("Các trường hợp chấm dứt hợp đồng lao động", "Điều 34"),
    ("Thời hạn báo trước khi người lao động đơn phương chấm dứt", "Điều 35"),
    ("Trợ cấp thôi việc", "Điều 46"),
    ("Nguyên tắc trả lương", "Điều 94"),
    ("Tiền lương làm thêm giờ", "Điều 98"),
    ("Thời giờ làm việc bình thường", "Điều 105"),
    ("Nghỉ trong giờ làm việc", "Điều 109"),
    ("Nghỉ hằng năm", "Điều 113"),
    ("Nghỉ lễ, tết", "Điều 112"),
    ("Các hình thức xử lý kỷ luật lao động", "Điều 124"),
    ("Thời hiệu xử lý kỷ luật lao động", "Điều 123"),
    ("Không được xử lý kỷ luật lao động", "Điều 122"),
    ("Lao động nữ mang thai", "Điều 137"),
    ("Thời giờ làm việc của người chưa thành niên", "Điều 146"),
    ("Bộ luật này có hiệu lực", "Điều 220")
]

results = []
for title, art in queries:
    matched = False
    for idx, text in enumerate(pages_text):
        if art.lower() in text.lower():
            p_num = idx + 1
            # find the line
            for line in text.split("\n"):
                if art.lower() in line.lower():
                    results.append({"query": title, "article": art, "page": p_num, "line": line.strip()})
                    matched = True
                    break
        if matched:
            break

for r in results:
    print(f"Page {r['page']}: [{r['article']}] {r['query']} -> {r['line'][:80]}")

