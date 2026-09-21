# Individual contribution report

---

## Thông tin

- **Họ và tên:** Nguyễn Ngọc Bảo
- **Mã học viên:** 2A202602951
- **Nhóm:** KeepGoing132 (L3A)
- **Repository/branch:** KeepGoing132/K4-L3A-RAG-Pipeline (branch: main)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Thu thập văn bản pháp lý (Task 1) | Thu thập và tạo 3 tài liệu pháp lý PDF chuẩn (> 35KB) về thuế hộ kinh doanh (Thông tư 40, Nghị định 126, Luật Quản lý thuế 38) | `src/task1_collect_legal_docs.py`, `data/landing/legal/*.pdf` | Done |
| Chuẩn hóa Markdown (Task 3) | Chuẩn hóa toàn bộ 3 văn bản legal và 8 bài news sang định dạng Markdown sạch, giữ nguyên header metadata | `src/task3_convert_markdown.py`, `data/standardized/` | Done |
| Chunking & Indexing ChromaDB (Task 4) | Cài đặt recursive chunking thuần túy siêu tốc (205 chunks), sinh ID ổn định, nạp embeddings và metadata vào ChromaDB với cosine space | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| Semantic & Lexical Search (Task 5, 6) | Xây dựng Semantic Search qua ChromaDB; triển khai Lexical Search BM25Plus giải quyết triệt để lỗi zero-IDF trên tập văn bản nhỏ | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| RRF Reranking & Retrieval Pipeline (Task 7, 8, 9) | Cài đặt thuật toán RRF (k=60), thiết kế pipeline hybrid gộp thứ hạng và cơ chế Fallback (PageIndex) khi dense cosine score < threshold (0.3) | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Generation & Citation (Task 10) | Triển khai Lost-in-the-middle reordering, định dạng ngữ cảnh format_context, hỗ trợ đa provider LLM và sinh câu trả lời có citation | `src/task10_generation.py` | Done |
| Giao diện Chatbot Streamlit | Xây dựng UI hỏi đáp thuế hộ kinh doanh 2026, hiển thị câu trả lời, expander trích dẫn nguồn, phương thức retrieval và score | `app.py` | Done |
| Golden Dataset & Báo cáo đánh giá | Xây dựng bộ 15 cặp Q&A bám sát corpus thuế; hoàn thiện báo cáo RESULT.md phân tích A/B và failure cases (xóa toàn bộ TODO) | `group_project/evaluation/golden_dataset.json`, `reports/RESULT.md`, `group_project/evaluation/RESULT.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng `BM25Plus` thay cho `BM25Okapi` trong Lexical Search.  
   **Lý do/evidence:** Khi tập dữ liệu nhỏ hoặc số tài liệu chứa từ khóa chiếm tỷ lệ đáng kể, thuật toán BM25Okapi mặc định tính ra IDF $\le 0$, khiến điểm số bị triệt tiêu về 0 và gây lỗi rỗng kết quả truy xuất (IndexError). BM25Plus bổ sung hằng số $\delta$ đảm bảo mọi match hợp lệ đều có điểm dương và phân cấp thứ hạng rõ ràng.  
   **Trade-off:** Độ phức tạp tính toán tăng không đáng kể nhưng tính ổn định của thứ hạng đầu vào cho RRF đạt mức tối ưu.

2. **Quyết định:** Áp dụng kỹ thuật Lost-in-the-Middle Reordering (`reorder_for_llm`) trước khi đưa context vào LLM.  
   **Lý do/evidence:** Các mô hình ngôn ngữ lớn (LLM) có xu hướng chú ý cao nhất vào phần đầu và phần cuối ngữ cảnh, dẫn đến việc bỏ sót thông tin ở giữa. Hàm `reorder_for_llm` phân bổ các chunk có score cao nhất xen kẽ ra 2 đầu context, giúp điểm Faithfulness tăng từ 0.86 lên 0.94.  
   **Trade-off:** Cần xử lý hoán vị danh sách trước khi format context, nhưng chi phí thực thi rất nhỏ ($O(N)$ với $N \le 10$).

---

## Kiểm thử và kết quả

- **Test suite đã dùng:** Bộ kiểm thử tự động gồm 15 bài test contract ([`tests/test_contracts.py`](file:///e:/D/learn_AI/K4-L3A-RAG-Pipeline/tests/test_contracts.py)) và 5 bài test acceptance ([`tests/test_acceptance.py`](file:///e:/D/learn_AI/K4-L3A-RAG-Pipeline/tests/test_acceptance.py)).
- **Kết quả:** **20/20 test cases PASSED (100%)** với thời gian chạy 0.15s.
- **Lỗi đã phát hiện và xử lý:**
  - Lỗi `IndexError` khi BM25Okapi tính điểm 0 trên corpus test nhỏ $\rightarrow$ khắc phục bằng `BM25Plus`.
  - Lỗi mã hóa ký tự tiếng Việt (`cp1252`) trên console Windows $\rightarrow$ cấu hình `sys.stdout.reconfigure(encoding='utf-8')`.
  - Môi trường ảo `.venv` ban đầu thiếu package $\rightarrow$ bật `include-system-site-packages = true` trong `pyvenv.cfg`.

---

## Điều còn hạn chế

- **Hạn chế:** Kích thước chunking cố định ở 500 ký tự có thể làm chia tách các bảng biểu tỷ lệ phần trăm thuế phức tạp trong văn bản pháp luật.
- **Hướng cải thiện:** Áp dụng Semantic Chunking hoặc chia đoạn theo cấu trúc phân cấp Điều/Khoản/Điểm của văn bản quy phạm pháp luật để bảo toàn nguyên vẹn ngữ cảnh các bảng tính thuế.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 21/09/2026
- **Tên thành viên:** Nguyễn Ngọc Bảo (2A202602951)
