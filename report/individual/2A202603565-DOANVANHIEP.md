# Báo cáo cá nhân — Day 6: Data Ingestion Engineering

- **Họ và tên:** Đoàn Văn Hiệp
- **MSSV:** 2A202603565
- **Lớp:** L3A

---

## Dữ liệu và pipeline

### 1. Chủ đề, nguồn/quyền, số trang và quy tắc tính trang
- **Chủ đề:** Bộ luật Lao động Việt Nam năm 2019 (Luật số 45/2019/QH14, ban hành ngày 20/11/2019, có hiệu lực từ ngày 01/01/2021).
- **Nguồn & quyền sở hữu:** Văn bản quy phạm pháp luật của nước Cộng hòa Xã hội Chủ nghĩa Việt Nam, thuộc phạm vi công cộng (Public Domain) theo Điều 19 Luật Sở hữu trí tuệ 2005 (sửa đổi, bổ sung 2022) — không áp dụng quyền tác giả đối với văn bản quy phạm pháp luật, văn bản hành chính và bản dịch chính thức. Văn bản định dạng `.docx` chuẩn được tải từ Cổng thông tin Giáo dục Phòng GD&ĐT Bình Thạnh (`pgdbinhthanh.hcm.edu.vn`), đối chiếu nội dung với Cổng Cơ sở dữ liệu Quốc gia về Văn bản Pháp luật (`vbpl.vn`).
- **Số trang và quy tắc tính trang:**
  - File PDF clean (`data/bo_luat_lao_dong_2019_clean.pdf`) gồm **145 trang** nội dung số hóa hoàn chỉnh, gồm 17 Chương và 220 Điều.
  - Tổng số ký tự trích xuất sau khi chuẩn hóa là **190.098 ký tự**, trung bình **1.311 ký tự/trang**.
  - Quy tắc tính trang: Tính tất cả các trang chứa điều khoản luật (Trang 1 đến Trang 145), mỗi trang đều chứa quy phạm pháp luật thực chất và có số ký tự dao động từ 400 đến 1.800 ký tự (không có trang trắng, trang phụ lục rỗng hay mục lục trang riêng biệt).

### 2. Chuẩn hóa, lỗi và giới hạn
- **Quy trình tiền xử lý & chuẩn hóa:**
  - Chuẩn hóa chuỗi ký tự Unicode tiếng Việt về chuẩn **NFC** (`unicodedata.normalize('NFC', text)`).
  - Chuẩn hóa khoảng trắng (`re.sub(r'[ \t]+', ' ', line)`), loại bỏ các ký tự xuống dòng dư thừa hoặc ngắt dòng bất thường giữa câu do dàn trang văn bản (`\r\n` -> `\n`, loại bỏ khoảng trắng đầu/cuối dòng).
  - Trích xuất metadata chương tự động bằng biểu thức chính quy (`CHƯƠNG [IVXLCDM]+`) gán ngữ cảnh chương hiện hành cho từng trang.
- **Lỗi phát hiện và cách xử lý:**
  - Ban đầu, file scan PDF từ cơ quan quản lý (`data/bo_luat_lao_dong_2019.pdf`) là dạng ảnh scan con dấu (bitmap), khi trích xuất text thuần bằng `pypdf` trả về **0 ký tự** trên 77 trang scan.
  - Giải pháp xử lý: Thu thập bản `.docx` chính thức đồng bộ toàn văn của văn bản 45/2019/QH14, kiểm tra tính toàn vẹn đủ 17 Chương và 220 Điều, sau đó xuất sang PDF chuẩn kỹ thuật số (`bo_luat_lao_dong_2019_clean.pdf`). Tỷ lệ lỗi trích xuất OCR sau chuyển đổi: **0%** trên toàn bộ 145 trang.
- **Giới hạn:**
  - Một số bảng biểu hoặc danh mục liệt kê theo điểm a, b, c nhiều cấp nếu phân tách theo ký tự cố định có thể làm đứt gãy quan hệ logic giữa đoạn dẫn và điểm áp dụng.

### 3. Embedding model, Vector store, Lệnh chạy và Chi phí
- **Embedding Model:**
  - Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
  - Nhà cung cấp / Thư viện: Hugging Face / Sentence-Transformers v6.3.0 (chạy local trên PyTorch 2.15.0).
  - Số chiều (Dimension): **384** chiều.
  - Chiến lược xử lý: Document chunks và Query được chuẩn hóa chuỗi và mã hóa trực tiếp bằng `SentenceTransformer.encode(..., normalize_embeddings=True)` (chuẩn hóa L2 để tương thích khoảng cách Cosine).
- **Vector Store:**
  - Công nghệ: **ChromaDB v1.5.9** (Local Persistent Client tại thư mục `./chroma_db`).
  - Metric tính khoảng cách: **Cosine Similarity** (`hnsw:space: cosine`).
  - Khởi tạo & nạp lại: Mỗi chiến lược được tạo collection riêng biệt (`strategy_a_fixed`, `strategy_b_paragraph`, `strategy_c_filtered`). Cơ chế kiểm tra nạp lại: Nếu collection đã tồn tại và đủ số lượng chunk, hệ thống tái sử dụng index mà không nhân bản dữ liệu.
- **Lệnh chạy tái lập pipeline:**
  ```powershell
  cd starter
  .\.venv\Scripts\Activate.ps1
  python -m src.run
  ```
- **Chi phí (Cost):**
  - **0 USD (Hoàn toàn miễn phí)**: Sử dụng mô hình mã nguồn mở chạy on-premise/local trên CPU máy tính cá nhân, không phát sinh chi phí API token thương mại.

### 4. Metadata bắt buộc và trường lọc bổ sung
- **Metadata bắt buộc:**
  - `document_id`: Định danh văn bản (`bo_luat_lao_dong_2019`).
  - `source`: Tên file gốc lưu trữ (`bo_luat_lao_dong_2019_clean.pdf`).
  - `page`: Số trang vật lý chính xác trong file PDF (Trang 1 đến 145), phục vụ truy vết bằng chứng pháp lý (Legal Citation).
- **Trường lọc bổ sung (`chapter`):**
  - Tên trường: `chapter` (ví dụ: `CHƯƠNG_I`, `CHƯƠNG_III`, `CHƯƠNG_VIII`, `CHƯƠNG_IX`, `CHƯƠNG_XII`).
  - Kiểu dữ liệu: `String`.
  - Nguồn giá trị: Trích xuất tự động theo phân cấp cấu trúc chương trong văn bản luật tại thời điểm phân trang/chunking.
  - Lý do chọn: Văn bản luật Việt Nam có cấu trúc chương rất rõ ràng theo từng phân mảng quan hệ lao động (Hợp đồng, Tiền lương, Kỷ luật, Giải quyết tranh chấp, v.v.). Khi người dùng truy vấn một phạm vi pháp lý cụ thể (ví dụ: "theo quy định tại Chương VIII về Thời giờ làm việc, thời giờ nghỉ ngơi"), metadata filter giúp thu hẹp không gian tìm kiếm, loại bỏ hoàn toàn các điều khoản thuộc chương khác có từ khóa tương đồng (ví dụ: các điều khoản chuyển tiếp ở Chương XVII hay giải thích từ ngữ ở Chương I).

---

## Cấu hình và benchmark

### 1. Ba cấu hình thử nghiệm (A / B / C)
- **Cấu hình A (Fixed Size Chunking):**
  - Chunk size: **500 ký tự**.
  - Overlap: **50 ký tự**.
  - Metadata: `document_id`, `source`, `page`, `chapter`.
  - Filter: Không sử dụng filter (`filter = None`).
  - Tổng số chunk sinh ra: **481 chunks** (độ dài trung bình 429,9 ký tự).
- **Cấu hình B (Structure-Aware Paragraph Chunking):**
  - Chiến lược: Cắt theo ranh giới đoạn văn bản và điều khoản pháp luật (`\n\n`, các tiêu đề `Điều ...`).
  - Giới hạn độ dài tối đa (`max_chars`): **600 ký tự**.
  - Overlap: **0 ký tự** (giữ nguyên vẹn toàn bộ câu văn/khoản luật).
  - Metadata: `document_id`, `source`, `page`, `chapter`.
  - Filter: Không sử dụng filter (`filter = None`).
  - Tổng số chunk sinh ra: **436 chunks** (độ dài trung bình 435,3 ký tự).
- **Cấu hình C (Structure-Aware + Metadata Filter):**
  - Chiến lược chunking: **Hoàn toàn giống cấu hình B** (cắt theo cấu trúc đoạn/điều khoản, max 600 ký tự, 0 overlap, cùng 436 chunks).
  - Metadata & Filter: Sử dụng **Metadata Filtering** theo trường `chapter` khi câu hỏi có chỉ định điều kiện ngữ cảnh chương (ví dụ: filter `{"chapter": "CHƯƠNG_VIII"}`).
  - **Khác biệt duy nhất giữa B và C:** Chỉ bổ sung cơ chế lọc Metadata (`where={"chapter": ...}`) trên vector store khi thực hiện truy vấn; giữ nguyên embedding model, vector space, và dữ liệu chunking để đánh giá chính xác tác động riêng rẽ của Metadata Filtering.

### 2. Thiết kế Benchmark (≥20 câu hỏi)
- **Quy mô tập Benchmark:**
  - Tổng số câu hỏi: **20 câu** (lưu tại `benchmark/questions.json` và `starter/data/benchmark.json`).
  - Phân chia: **15 câu Dev** (`q01` đến `q15`) và **5 câu Test độc lập** (`q16` đến `q20`).
- **Phân loại câu hỏi:**
  - Câu hỏi trực tiếp (Factoid): Ví dụ `q01` (nguyên tắc áp dụng), `q05` (thử việc), `q18` (tuổi nghỉ hưu).
  - Câu hỏi diễn đạt lại (Paraphrased): Ví dụ `q03` (đơn phương chấm dứt hợp đồng), `q19` (bất đồng ý kiến tập thể).
  - Câu hỏi có điều kiện / ngoại lệ: Ví dụ `q08` (làm thêm giờ và giới hạn giờ làm), `q10` (các trường hợp sa thải).
  - Câu hỏi kiểm tra Metadata Filter (3 câu, gồm 2 câu dev và 1 câu test):
    - `q04` (Dev): Quyền đơn phương chấm dứt của NLĐ không cần báo trước trong **Chương III**.
    - `q09` (Dev): Mức trả lương làm thêm giờ ban đêm trong **Chương VI**.
    - `q16` (Test): Thời gian nghỉ hằng năm của người làm việc điều kiện bình thường theo **Chương VIII**.
- **Kiểm chứng Evidence:**
  - 100% câu hỏi đều được xác minh thủ công trực tiếp từ văn bản gốc, có số trang `gold_page` và đoạn trích bằng chứng `evidence_quote` đối chiếu với nội dung trang sau chuẩn hóa.

### 3. Tiêu chí chọn chiến lược trước khi xem Test
- **Nguyên tắc ưu tiên:**
  1. Ưu tiên 1: Tối đa hóa **Evidence Hit@3** trên tập Dev (đảm bảo văn bản chứa câu trả lời nằm trong top 3 kết quả trả về cho RAG).
  2. Ưu tiên 2: Tối đa hóa **Coherence trung bình** (đảm bảo chunk văn bản không bị xé vụn nửa câu, giữ trọn ý của điều khoản pháp luật).
  3. Ưu tiên 3: Hiệu quả tài nguyên (thời gian truy vấn thấp, không sinh chunk dư thừa).

---

## Kết quả

### Bảng 1: Hiệu năng Retrieval trên Dev và Test
| Strategy | Split | Hit@1 (n/N) | Evidence Hit@3 (n/N) | Chunk count | Thời gian | Chi phí |
|---|---|---|---|---|---|---|
| **A** (Fixed 500/50) | Dev | 5/15 (33.3%) | 8/15 (53.3%) | 481 | 0.43s | $0.00 |
| **A** (Fixed 500/50) | Test | 3/5 (60.0%) | 3/5 (60.0%) | 481 | 0.43s | $0.00 |
| **B** (Paragraph 600) | Dev | 7/15 (46.7%) | 10/15 (66.7%) | 436 | 0.60s | $0.00 |
| **B** (Paragraph 600) | Test | 3/5 (60.0%) | 3/5 (60.0%) | 436 | 0.60s | $0.00 |
| **C** (Paragraph + Filter) | Dev | 7/15 (46.7%) | 10/15 (66.7%) | 436 | 0.43s | $0.00 |
| **C** (Paragraph + Filter) | Test | 3/5 (60.0%) | 3/5 (60.0%) | 436 | 0.43s | $0.00 |

### Bảng 2: Đánh giá 5 khía cạnh chất lượng
| Strategy | Coherence trung bình /2 (n) | Metadata đủ và đúng (n/N) | Filter tuân thủ (n/N hoặc N/A) | Grounding 0/1/2 (số câu) và trung bình /2 |
|---|---|---|---|---|
| **A** | 1.00 / 2 (n=10) | 15/15 (100%) | N/A | 0 câu mức 0, 2 câu mức 1, 3 câu mức 2 — TB: 1.60 / 2 |
| **B** | 1.70 / 2 (n=10) | 15/15 (100%) | N/A | 0 câu mức 0, 2 câu mức 1, 3 câu mức 2 — TB: 1.60 / 2 |
| **C** | 1.70 / 2 (n=10) | 15/15 (100%) | 1/1 (100%) | 0 câu mức 0, 2 câu mức 1, 3 câu mức 2 — TB: 1.60 / 2 |

### Đường dẫn trace, nhãn thủ công và phương pháp chọn mẫu
- **Đường dẫn lưu trace:**
  - `results/traces_strategy_a.json`
  - `results/traces_strategy_b.json`
  - `results/traces_strategy_c.json`
  - `results/benchmark_summary.json`
- **Phương pháp chọn mẫu Coherence:**
  - Lấy mẫu tại 10 vị trí trang cố định trải dài văn bản: Trang 1, 15, 30, 45, 60, 75, 90, 105, 120, 135.
  - Tiêu chí chấm:
    - `0`: Chunk bị cắt ngang giữa câu hoặc mất chủ ngữ chính, không thể hiểu trọn vẹn ngữ nghĩa điều luật.
    - `1`: Chunk hiểu được một phần nhưng bị cắt cụm điều kiện hoặc phụ lục đi kèm.
    - `2`: Chunk giữ trọn vẹn toàn bộ một điều hoặc một khoản luật hoàn chỉnh, tự giải thích được.
  - Kết quả: Strategy A chỉ đạt **1.00/2** do ngắt cơ học 500 ký tự thường xé đôi một câu luật phức tạp. Strategy B và C đạt **1.70/2** do tôn trọng ranh giới đoạn và khoản luật.
- **Kiểm tra Metadata và Grounding trên Test Set (5 câu `q16` - `q20`):**
  - Metadata: 15/15 chunk top-3 trên 5 câu test đều chứa chính xác `document_id`, `source`, `page`, và `chapter`.
  - Filter tuân thủ: Câu `q16` có chỉ định filter `chapter="CHƯƠNG_VIII"`, 100% (3/3) chunk trong top-3 của Strategy C đều thuộc đúng Chương VIII (loại bỏ hoàn toàn chunk nhiễu thuộc Trang 1 như ở Strategy B).
  - Grounding Quality:
    - Mức 0: 0 câu.
    - Mức 1: 2 câu (`q16` và `q17`) — Trả về điều khoản liên quan trực tiếp nhưng còn thiếu chi tiết cụ thể để trả lời trọn vẹn câu hỏi.
    - Mức 2: 3 câu (`q18`, `q19`, `q20`) — Trả về đúng và đủ điều khoản luật chính xác làm căn cứ trả lời hoàn chỉnh.
    - Điểm trung bình Grounding: **1.60 / 2**.

---

## Phân tích và kết luận

### 1. So sánh chi tiết A–B và B–C & Phân tích 2 trường hợp sai
- **So sánh A–B (Tác động của Chunking Strategy):**
  - Chuyển từ fixed-size chunking (A) sang structure-aware chunking (B) giúp tăng **Evidence Hit@3 từ 53.3% lên 66.7%** (+13.4%) và Hit@1 từ 33.3% lên 46.7% (+13.4%) trên tập Dev.
  - Điểm Coherence tăng vượt bậc từ **1.00 lên 1.70 / 2**. Việc chia chunk theo cấu trúc điều khoản giúp bảo toàn trọn vẹn ngữ cảnh của từng điều luật thay vì ngắt giữa câu, nhờ đó vector embedding biểu diễn ngữ nghĩa chính xác hơn nhiều.
- **So sánh B–C (Tác động của Metadata Filter):**
  - Trên các câu hỏi chung, kết quả B và C tương đương nhau.
  - Tuy nhiên, trên câu hỏi có chỉ định phạm vi chương (`q04`, `q09`, `q16`), Strategy C đã loại bỏ triệt để các chunk "nhiễu" từ các chương khác.
  - Cụ thể ở `q16`, Strategy B trả về Top-3 có chứa chunk tại Trang 1 (Phần mở đầu liệt kê danh mục chương) do trùng lặp từ khóa; Strategy C áp dụng `chapter="CHƯƠNG_VIII"` đã loại trừ hoàn toàn Trang 1, giữ 100% kết quả nằm trong đúng phạm vi điều chỉnh của Chương VIII.
- **Phân tích 2 ví dụ thất bại trên tập Test:**
  - **Ví dụ 1: Câu `q16` (Test)**
    - *Nội dung câu hỏi:* "Thời gian nghỉ hằng năm của người lao động làm việc trong điều kiện bình thường là bao nhiêu ngày theo Chương VIII?"
    - *Nguồn gold:* Trang 75, Điều 113, Khoản 1 Điểm a (Quy định 12 ngày làm việc).
    - *Kết quả truy xuất của C:* Top-1 là Trang 76, Điều 114 (Thanh toán tiền lương những ngày chưa nghỉ hằng năm, score 0.7712); Top-2 là Trang 75, Điều 113 Khoản 3 (score 0.7634).
    - *Nguyên nhân:* Do Điều 113 dài nên bị ngắt thành 2 chunk. Khoản 1 (chứa mốc "12 ngày") nằm ở chunk đầu nhưng câu truy vấn chứa các từ ngữ chung về "nghỉ hằng năm", khiến mô hình embedding MiniLM tính độ tương đồng ngữ nghĩa cao hơn với Điều 114 và Khoản 3 (thỏa thuận nghỉ hằng năm) thay vì đẩy đúng chunk chứa Khoản 1 lên Top-1.
  - **Ví dụ 2: Câu `q17` (Test)**
    - *Nội dung câu hỏi:* "Lao động chưa thành niên được phân loại thành các nhóm tuổi nào theo Bộ luật Lao động?"
    - *Nguồn gold:* Trang 94, Điều 143 (Quy định các nhóm: chưa đủ 15 tuổi, từ đủ 15 đến dưới 18 tuổi).
    - *Kết quả truy xuất của B & C:* Top-1 là Trang 95, Điều 144 (Nguyên tắc sử dụng LĐ chưa thành niên); Top-2 là Trang 96, Điều 147 (Công việc cấm sử dụng lao động từ đủ 15 đến chưa đủ 18 tuổi).
    - *Nguyên nhân:* Thuật ngữ "phân loại thành các nhóm tuổi" trong câu hỏi mang tính khái quát hóa, trong khi Điều 147 lặp lại cụm từ "lao động từ đủ 15 tuổi đến chưa đủ 18 tuổi" rất nhiều lần với tần suất cao, khiến dense retriever bị thiên lệch về Điều 147.

### 2. Chiến lược lựa chọn, Đánh đổi và Điều kiện áp dụng
- **Chiến lược được chọn:** **Cấu hình C (Structure-Aware Paragraph Chunking kết hợp Metadata Filter)**.
- **Đánh đổi (Trade-offs):**
  - Cấu hình C đòi hỏi bước trích xuất metadata chương chính xác ở khâu ingestion và người dùng/hệ thống phải nhận diện được phạm vi chương khi truy vấn.
  - Kích thước chunk theo cấu trúc điều khoản có độ biến thiên lớn hơn (từ 150 đến 600 ký tự) so với fixed-size, nhưng đổi lại bảo đảm trọn vẹn tính chặt chẽ của văn bản pháp luật.
- **Điều kiện áp dụng:**
  - Rất phù hợp cho các kho tài liệu có tính phân cấp cấu trúc cao như: Văn bản quy phạm pháp luật, Quy chế nội bộ doanh nghiệp, Hướng dẫn kỹ thuật và Tiêu chuẩn ISO.

### 3. Hạn chế của Dữ liệu, Nhãn, Benchmark và Đo lường
- **Kích thước tập test (5 câu):** Tập test nhỏ chỉ đóng vai trò kiểm tra tính vững chắc (sanity check) và minh họa, không đủ đại diện thống kê để khẳng định vượt trội tuyệt đối trên mọi loại truy vấn.
- **Embedding đơn thuần (Dense-only):** Mô hình embedding đa ngữ dạng nhỏ (`paraphrase-multilingual-MiniLM-L12-v2`) có xu hướng ưu tiên ngữ nghĩa khái quát, đôi khi bỏ qua các từ khóa định lượng chính xác (ví dụ: số ngày "12 ngày", con số tuổi "15 tuổi").
- **Thời gian và chi phí:** Đo trên CPU máy cá nhân với 436 chunks diễn ra rất nhanh (~0.4s - 0.6s) với chi phí $0, nhưng khi scale lên hàng trăm bộ luật (hàng triệu chunks), chi phí lưu trữ vector và độ trễ tìm kiếm sẽ đòi hỏi cấu hình HNSW tối ưu hơn.

### 4. Đề xuất cải tiến nếu mở rộng hệ thống
1. **Kết hợp Hybrid Search (Dense + BM25):** Tích hợp tìm kiếm từ khóa BM25 song song với vector embedding. Điều này sẽ giải quyết dứt điểm các trường hợp như `q16` và `q17`, nơi các từ khóa chính xác như "12 ngày", "nhóm tuổi", "Điều 113" được gán trọng số cao.
2. **Chunking phân cấp kép (Parent-Child Indexing):** Lưu các đoạn nhỏ (Khoản) làm unit tìm kiếm vector, nhưng khi trả kết quả cho LLM thì truy xuất nguyên cả Điều luật cha (Parent Document/Điều).
3. **Mở rộng Metadata:** Bổ sung metadata về `dieu_so` (số hiệu Điều luật), `chu_the_ap_dung` (Người lao động hay Người sử dụng lao động) để hỗ trợ truy vấn lọc đa chiều chính xác hơn.
