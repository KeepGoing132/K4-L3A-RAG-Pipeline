# RAG evaluation results

## Run information

| Field                              | Value                                                 |
| ---------------------------------- | ----------------------------------------------------- |
| Evaluation date                    | 2026-09-21                                            |
| Student name                       | Nguyễn Ngọc Bảo                                       |
| Student ID                         | 2A202602951                                           |
| Group                              | KeepGoing132 (L3A)                                    |
| Framework and version              | RAGAS 0.4.3, LangChain 1.4.2                          |
| Evaluator model                    | gpt-4o                                                |
| Generator model                    | gpt-4o-mini                                           |
| Embedding model                    | BAAI/bge-m3                                           |
| Corpus version/commit              | 9c707de                                               |
| Golden dataset size                | 15 Q&A pairs                                          |
| `top_k`                            | 5                                                     |
| Fallback threshold and calibration | Threshold 0.30 (calibrated on in/out-domain queries)   |

## Configurations

- **Config A — dense-only:** Semantic search thuần túy sử dụng ChromaDB vector store và cosine similarity metric.
- **Config B — hybrid + RRF:** Hybrid retrieval kết hợp Semantic Search và BM25 lexical search qua thuật toán Reciprocal Rank Fusion (RRF, k=60).

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.86 |     0.94 |     +0.08 |
| Answer relevance  |     0.84 |     0.92 |     +0.08 |
| Context recall    |     0.80 |     0.93 |     +0.13 |
| Context precision |     0.78 |     0.90 |     +0.12 |
| **Average**       |     0.82 |     0.92 |     +0.10 |

## A/B comparison

- Cấu hình tốt hơn: Config B (Hybrid + RRF).
- Evidence: Điểm trung bình vượt trội hơn Config A (+0.10), đặc biệt là Context Recall (+0.13) và Context Precision (+0.12). BM25 giúp bắt chính xác các từ khóa số liệu (ví dụ: các tỷ lệ thuế cụ thể 1%, 0.5%, 5%, số văn bản pháp luật như 40/2021/TT-BTC, 126/2020/NĐ-CP, 38/2019/QH14) mà mô hình dense embedding đôi khi bị trôi nghĩa.
- Trade-off về latency/cost: Config B có thêm chi phí tính điểm BM25 và xếp hạng RRF, làm tăng độ trễ truy xuất thêm ~15-25ms so với Config A. Tuy nhiên, thời gian này là không đáng kể so với tổng thời gian sinh từ LLM (~1.2s), trong khi độ chính xác của ngữ cảnh tăng đáng kể.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Câu hỏi về trường hợp ấn định thuế khi che giấu doanh thu | Config A | 0.72 | 0.75 | 0.67 | 0.65 | retrieval | Dense search không bắt được thuật ngữ chuyên ngành "ấn định thuế" do khoảng cách ngữ nghĩa rộng hơn ngữ cảnh chung |
|   2 | Tỷ lệ thuế áp dụng cho hoạt động cho thuê tài sản của cá nhân | Config A | 0.80 | 0.81 | 0.70 | 0.72 | retrieval | Thiếu từ khóa chính xác "cho thuê tài sản" dẫn đến việc chunk kết quả bị xếp sau các dịch vụ khác |
|   3 | Quy định xử phạt vi phạm chậm nộp thuế 0.03%/ngày | Config B | 0.88 | 0.85 | 0.82 | 0.80 | generation | LLM giải thích dài dòng kèm các ví dụ không có trong context gốc |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Duy trì Hybrid + RRF làm phương pháp retrieval mặc định | Delta Recall +0.13 và Precision +0.12 trên toàn bộ 15 test cases | Nâng cao độ chính xác và giảm hallucination của câu trả lời | Chạy test suite đánh giá tự động trên golden dataset |
|        2 | Tối ưu hóa kích thước chunking (Chunk Size = 400, Overlap = 80) cho các điều khoản luật | Các điều khoản luật thường ngắn gọn và có cấu trúc điều/khoản/điểm rõ ràng | Tăng context precision và tránh cắt rời các bảng tỷ lệ thuế | So sánh điểm context precision trước và sau khi đổi tham số |
|        3 | Cải thiện System Prompt siết chặt yêu cầu citation và hạn chế suy diễn | Failure case số 3 cho thấy mô hình tự thêm ví dụ ngoài context | Tăng điểm Faithfulness từ 0.94 lên > 0.98 | Đo lường metric Faithfulness bằng RAGAS |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Reorder context (Lost-in-the-middle) | Default order | Faithfulness +0.03 | +0ms / +$0 | Đưa chunk quan trọng ra đầu và cuối giúp LLM chú ý tốt hơn đến bằng chứng chính |
| PageIndex fallback for out-of-domain | No fallback | Answer relevance +0.05 | +120ms khi kích hoạt fallback | Giúp hệ thống không bị crash hoặc trả lời sai khi dense score < 0.30 |
