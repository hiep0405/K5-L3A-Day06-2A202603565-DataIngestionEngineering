# Day 06 · Data Ingestion Engineering: Bộ Luật Lao Động 2019

- **Học viên:** Đoàn Văn Hiệp
- **MSSV:** 2A202603565
- **Lớp:** L3A
- **Chủ đề:** Hệ thống trích xuất và truy vấn tri thức Bộ luật Lao động Việt Nam năm 2019 (Luật số 45/2019/QH14).

---

## 1. Cấu trúc bài nộp

Tuân thủ đầy đủ cấu trúc tối thiểu theo yêu cầu tại `SUBMISSION.md`:

```text
├── STUDENT.md                              # Thông tin học viên và commit chốt bài
├── README.md                               # Hướng dẫn setup, cách chạy, đường dẫn dữ liệu
├── data/
│   ├── bo_luat_lao_dong_2019_clean.pdf     # File dữ liệu PDF clean (145 trang số hóa)
│   ├── bo_luat_lao_dong_2019.docx          # Văn bản gốc đối chiếu
│   └── manifest.json                       # Bảng kê nguồn, số trang, số ký tự, bản quyền
├── benchmark/
│   └── questions.json                      # 20 câu hỏi (15 dev / 5 test) kèm gold evidence
├── artifacts/
│   └── experiment_log.csv                  # Nhật ký thí nghiệm và giả thuyết A/B/C
├── results/
│   ├── benchmark_summary.json              # Tổng hợp chỉ số Hit@1, Evidence Hit@3, thời gian
│   ├── traces_strategy_a.json              # Trace truy xuất Top-3 của Chiến lược A
│   ├── traces_strategy_b.json              # Trace truy xuất Top-3 của Chiến lược B
│   └── traces_strategy_c.json              # Trace truy xuất Top-3 của Chiến lược C
├── report/
│   └── individual/
│       └── 2A202603565-DOANVANHIEP.md      # Báo cáo cá nhân chi tiết theo mẫu
└── starter/
    ├── requirements.txt                    # Thư viện phụ thuộc
    ├── src/                                # Toàn bộ mã nguồn pipeline
    │   ├── ingestion.py                    # Đọc PDF, chuẩn hóa NFC, trích xuất metadata
    │   ├── chunking.py                     # Fixed chunking (A) & Structure-aware chunking (B, C)
    │   ├── embeddings.py                   # Embedding local sentence-transformers
    │   ├── store.py                        # Quản lý ChromaDB persistent, vector search, filter
    │   ├── evaluation.py                   # Đo Hit@1, Evidence Hit@3, xuất trace
    │   └── run.py                          # Pipeline điều phối chạy A/B/C
    └── scripts/
        ├── create_manifest.py              # Script tái lập manifest
        ├── audit_coherence.py              # Script chấm tính mạch lạc (Coherence)
        └── audit_eval.py                   # Script kiểm tra Metadata và Grounding
```

---

## 2. Dữ liệu và Bản quyền

- **Corpus:** [data/bo_luat_lao_dong_2019_clean.pdf](data/bo_luat_lao_dong_2019_clean.pdf)
- **Quy mô:** **145 trang nội dung**, **190.098 ký tự** (trung bình 1.311 ký tự/trang), gồm toàn bộ 17 Chương và 220 Điều. Tỷ lệ lỗi OCR: **0%**.
- **Bản quyền:** Thuộc phạm vi công cộng (Public Domain) theo Điều 19 Luật Sở hữu trí tuệ Việt Nam.
- **Manifest:** [data/manifest.json](data/manifest.json).

---

## 3. Cài đặt môi trường (Setup)

Yêu cầu Python từ 3.11 đến 3.12 trên Windows / Linux / macOS.

```bash
# 1. Di chuyển vào thư mục starter
cd starter

# 2. Tạo môi trường ảo (nếu chưa tạo)
python -m venv .venv

# 3. Kích hoạt môi trường ảo:
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
# source .venv/bin/activate

# 4. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

---

## 4. Hướng dẫn chạy và Tái lập kết quả (Reproduce)

### Bước 1: Chạy toàn bộ pipeline Ingestion, Chunking và Benchmark

Lệnh này sẽ thực hiện ingestion 145 trang PDF, chia chunk theo 3 cấu hình A/B/C, tạo embedding L2, lưu vào persistent ChromaDB (`./chroma_db`), chạy truy vấn trên 20 câu hỏi và lưu trace vào thư mục `results/`:

```powershell
python -m src.run
```

### Bước 2: Chạy script Audit đánh giá 5 khía cạnh

Chấm tự động và kiểm tra tính mạch lạc (Coherence), tính chính xác của Metadata và chất lượng Grounding:

```powershell
# Đặt PYTHONPATH về thư mục gốc của repo
$env:PYTHONPATH="."

# 1. Chấm Coherence trên 10 vị trí ngẫu nhiên giữa Chiến lược A và B:
python scripts/audit_coherence.py

# 2. Kiểm tra Metadata và Grounding trên tập Test (5 câu hỏi):
python scripts/audit_eval.py
```

---

## 5. Tóm tắt kết quả thực nghiệm

### Hiệu năng Retrieval trên Dev (15 câu) và Test (5 câu)

| Strategy | Mô tả | Dev Hit@1 | Dev Hit@3 | Test Hit@1 | Test Hit@3 | Chunk count | Chi phí |
|---|---|---|---|---|---|---|---|
| **A** | Fixed 500 ký tự, overlap 50 | 5/15 (33.3%) | 8/15 (53.3%) | 3/5 (60.0%) | 3/5 (60.0%) | 481 | $0.00 |
| **B** | Theo điều khoản (max 600) | 7/15 (46.7%) | 10/15 (66.7%) | 3/5 (60.0%) | 3/5 (60.0%) | 436 | $0.00 |
| **C** | Giống B + Metadata Chapter Filter | 7/15 (46.7%) | 10/15 (66.7%) | 3/5 (60.0%) | 3/5 (60.0%) | 436 | $0.00 |

### Đánh giá chất lượng 5 chiều
- **Coherence:** Chiến lược B đạt **1.70 / 2** vượt trội so với Chiến lược A (**1.00 / 2**) nhờ việc bảo toàn trọn vẹn ranh giới điều khoản pháp luật thay vì cắt cơ học.
- **Metadata:** Đạt **15/15 (100%)** bản ghi top-3 chính xác trường `source`, `page`, `chapter`.
- **Filter Compliance:** Đạt **100% (1/1)** trên câu test `q16` có áp dụng filter chương, loại bỏ hoàn toàn các trang nhiễu không liên quan.
- **Grounding Quality:** Đạt điểm trung bình **1.60 / 2** (3 câu mức 2, 2 câu mức 1, 0 câu mức 0).
- **Chi phí & Model:** Sử dụng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` chạy offline trên CPU với chi phí **$0.00**.

Chi tiết xem tại báo cáo cá nhân: [report/individual/2A202603565-DOANVANHIEP.md](report/individual/2A202603565-DOANVANHIEP.md).
