import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Hỏi đáp chính sách Thuế Hộ kinh doanh 2026",
    page_icon="⚖️",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚖️ Thuế Hộ Kinh Doanh 2026")
    st.markdown(
        """
        **Hệ thống RAG tra cứu chính sách thuế:**
        - Bỏ thuế khoán từ 01/01/2026
        - Chuyển sang kê khai doanh thu thực tế
        - Hóa đơn điện tử máy tính tiền
        - Tỷ lệ thuế GTGT & TNCN
        """
    )
    top_k = st.slider("Số lượng trích dẫn (top_k)", 3, 10, 5)
    if st.button("Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()

st.title("Trợ lý Pháp lý & Thuế Hộ Kinh Doanh")
st.caption("Tra cứu quy định thuế GTGT, TNCN, hóa đơn điện tử và hướng dẫn kê khai 2026 có trích dẫn nguồn.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(f"📚 Nguồn trích dẫn ({len(message['sources'])} tài liệu)"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'N/A')}** "
                        f"*(Nguồn: `{meta.get('source', 'N/A')}` | Phương thức: `{src.get('retrieval_method', 'hybrid')}` | Điểm: `{src.get('score', 0):.4f}`)*"
                    )
                    st.text(src.get("content", "")[:300] + ("..." if len(src.get("content", "")) > 300 else ""))

query = st.chat_input("Nhập câu hỏi về thuế hộ kinh doanh...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tổng hợp câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]

            st.markdown(answer)
            if sources:
                with st.expander(f"📚 Nguồn trích dẫn ({len(sources)} tài liệu)"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        st.markdown(
                            f"**[{idx}] {meta.get('title', 'N/A')}** "
                            f"*(Nguồn: `{meta.get('source', 'N/A')}` | Phương thức: `{src.get('retrieval_method', 'hybrid')}` | Điểm: `{src.get('score', 0):.4f}`)*"
                        )
                        st.text(src.get("content", "")[:300] + ("..." if len(src.get("content", "")) > 300 else ""))

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
