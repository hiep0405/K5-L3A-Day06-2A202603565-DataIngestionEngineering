import pypdf
import re

pdf_path = r"c:\Users\HIEPHIEP\Downloads\DAY06_VIN_AI\K5-L3-Day06-2A202603565-DataIngestionEngineering\data\bo_luat_lao_dong_2019_clean.pdf"
reader = pypdf.PdfReader(pdf_path)

def find_term(term):
    res = []
    for idx, p in enumerate(reader.pages):
        text = p.extract_text() or ""
        if term.lower() in text.lower():
            # extract surrounding line
            for line in text.split("\n"):
                if term.lower() in line.lower():
                    res.append((idx + 1, line.strip()))
    return res

queries = [
    "Độ tuổi lao động tối thiểu",
    "Thời gian thử việc không quá",
    "Tiền lương của người lao động trong thời gian thử việc",
    "Các loại hợp đồng lao động",
    "Người lao động làm việc không trọn thời gian",
    "Thời giờ làm việc bình thường không quá",
    "Làm thêm giờ vào ngày nghỉ lễ",
    "Người lao động làm việc đủ 12 tháng",
    "Hình thức xử lý kỷ luật lao động",
    "Không được xử lý kỷ luật lao động đối với người lao động",
    "Nghỉ trong giờ làm việc",
    "Tiền lương làm thêm giờ vào ban đêm",
    "Đơn phương chấm dứt hợp đồng lao động",
    "Tạm hoãn thực hiện hợp đồng lao động",
    "Bộ luật này có hiệu lực thi hành từ ngày"
]

for q in queries:
    print(f"=== SEARCH: {q} ===")
    matches = find_term(q)
    for p, l in matches[:3]:
        print(f"  Page {p}: {l}")

