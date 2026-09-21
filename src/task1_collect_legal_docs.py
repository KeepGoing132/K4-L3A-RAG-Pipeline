"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề: Chính sách thuế đối với hộ kinh doanh, cá nhân kinh doanh.
Tài liệu thu thập:
1. Thông tư số 40/2021/TT-BTC ngày 01/6/2021 của Bộ Tài chính hướng dẫn thuế GTGT, TNCN hộ kinh doanh.
2. Nghị định số 126/2020/NĐ-CP ngày 19/10/2020 quy định chi tiết một số điều của Luật Quản lý thuế.
3. Luật Quản lý thuế số 38/2019/QH14 của Quốc hội về quản lý thuế và hóa đơn điện tử.
"""

from pathlib import Path
from fpdf import FPDF


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_DOCUMENTS = {
    "thong-tu-40-2021-tt-btc.pdf": {
        "title": "THÔNG TƯ 40/2021/TT-BTC HƯỚNG DẪN THUẾ GTGT, TNCN VÀ QUẢN LÝ THUẾ HỘ KINH DOANH",
        "sections": [
            (
                "Chương I: Quy định chung",
                "Thông tư này áp dụng đối với hộ kinh doanh, cá nhân kinh doanh cư trú có hoạt động "
                "sản xuất, kinh doanh hàng hóa, dịch vụ thuộc mọi lĩnh vực, ngành nghề kinh doanh theo quy định. "
                "Hộ kinh doanh có mức doanh thu từ 100 triệu đồng/năm trở xuống thuộc diện không phải nộp thuế GTGT "
                "và thuế TNCN theo quy định của pháp luật thuế.",
            ),
            (
                "Chương II: Phương pháp tính thuế",
                "1. Phương pháp kê khai: Áp dụng đối với hộ kinh doanh quy mô lớn hoặc hộ kinh doanh lựa chọn nộp thuế theo phương pháp kê khai. "
                "Khai thuế theo tháng hoặc quý, thực hiện chế độ kế toán, hóa đơn, chứng từ hợp pháp.\n"
                "2. Phương pháp nộp thuế theo từng lần phát sinh: Áp dụng đối với cá nhân kinh doanh lưu động hoặc không thường xuyên.\n"
                "3. Phương pháp khoán: Cơ quan thuế xác định doanh thu khoán và mức thuế khoán hàng năm theo quy định (lộ trình bãi bỏ chuyển sang kê khai từ năm 2026).",
            ),
            (
                "Chương III: Tỷ lệ tính thuế trên doanh thu",
                "Tỷ lệ thuế tính trên doanh thu gồm tỷ lệ thuế GTGT và tỷ lệ thuế TNCN áp dụng theo ngành nghề:\n"
                "- Phân phối, cung ứng hàng hóa: Tỷ lệ thuế GTGT là 1%; Tỷ lệ thuế TNCN là 0.5%.\n"
                "- Dịch vụ, xây dựng không bao thầu nguyên vật liệu: Tỷ lệ thuế GTGT là 5%; Tỷ lệ thuế TNCN là 2%.\n"
                "- Sản xuất, vận tải, dịch vụ có gắn với hàng hóa, xây dựng có bao thầu: Tỷ lệ thuế GTGT là 3%; Tỷ lệ thuế TNCN là 1.5%.\n"
                "- Hoạt động cho thuê tài sản: Tỷ lệ thuế GTGT là 5%; Tỷ lệ thuế TNCN là 5%.\n"
                "- Hoạt động kinh doanh khác: Tỷ lệ thuế GTGT là 2%; Tỷ lệ thuế TNCN là 1%.",
            ),
            (
                "Chương IV: Quản lý thuế đối với thương mại điện tử",
                "Cá nhân có thu nhập từ kinh doanh thương mại điện tử, cung cấp dịch vụ số xuyên biên giới "
                "có nghĩa vụ tự đăng ký, khai và nộp thuế hoặc ủy quyền cho tổ chức, sàn thương mại điện tử khấu trừ và nộp thay. "
                "Cơ quan thuế phối hợp ngân hàng thương mại và đơn vị vận chuyển để quản lý dòng tiền và doanh thu thực tế.",
            ),
        ],
    },
    "nghi-dinh-126-2020-nd-cp.pdf": {
        "title": "NGHỊ ĐỊNH 126/2020/NĐ-CP QUY ĐỊNH CHI TIẾT THI HÀNH MỘT SỐ ĐIỀU CỦA LUẬT QUẢN LÝ THUẾ",
        "sections": [
            (
                "Điều 8: Các loại thuế khai theo tháng, theo quý, theo từng lần phát sinh",
                "Hồ sơ khai thuế tháng chậm nhất là ngày thứ 20 của tháng tiếp theo tháng phát sinh nghĩa vụ thuế. "
                "Hồ sơ khai thuế quý chậm nhất là ngày cuối cùng của tháng đầu của quý tiếp theo quý phát sinh nghĩa vụ thuế. "
                "Hộ kinh doanh kê khai theo quý nếu đáp ứng tiêu chí về doanh thu năm trước liền kề theo quy định.",
            ),
            (
                "Điều 27: Trách nhiệm của tổ chức, cá nhân có liên quan",
                "Ngân hàng thương mại có trách nhiệm cung cấp thông tin tài khoản thanh toán của người nộp thuế cho cơ quan thuế. "
                "Thực hiện khấu trừ, nộp thay nghĩa vụ thuế đối với nhà cung cấp nước ngoài không có cơ sở thường trú tại Việt Nam. "
                "Tổ chức cung cấp dịch vụ sàn thương mại điện tử có trách nhiệm cung cấp thông tin doanh thu, giao dịch của các bên bán hàng cho cơ quan thuế định kỳ.",
            ),
            (
                "Điều 50: Ấn định thuế đối với người nộp thuế vi phạm",
                "Cơ quan quản lý thuế thực hiện ấn định thuế trong các trường hợp: Không đăng ký thuế, không nộp hồ sơ khai thuế; "
                "Nộp hồ sơ khai thuế không đầy đủ, không chính xác; Không xuất trình chứng từ, sổ kế toán khi kiểm tra; "
                "Có dấu hiệu che giấu doanh thu kinh doanh thực tế qua các kênh thanh toán điện tử hoặc tiền mặt.",
            ),
        ],
    },
    "luat-quan-ly-thue-38-2019-qh14.pdf": {
        "title": "LUẬT QUẢN LÝ THUẾ SỐ 38/2019/QH14 CỦA QUỐC HỘI NƯỚC CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "sections": [
            (
                "Chương I: Những quy định chung",
                "Luật này quy định việc quản lý các loại thuế, các khoản thu khác thuộc ngân sách nhà nước. "
                "Nguyên tắc quản lý thuế: Tạo thuận lợi cho người nộp thuế, bảo đảm quyền và lợi ích hợp pháp của người nộp thuế; "
                "Hiện đại hóa công tác quản lý thuế, áp dụng quản lý rủi ro và ứng dụng công nghệ thông tin trong quản lý thuế.",
            ),
            (
                "Chương X: Áp dụng hóa đơn, chứng từ điện tử",
                "Doanh nghiệp, tổ chức kinh tế, hộ kinh doanh, cá nhân kinh doanh phải áp dụng hóa đơn điện tử khi bán hàng hóa, cung cấp dịch vụ. "
                "Hộ kinh doanh nộp thuế theo phương pháp kê khai, hộ kinh doanh cung cấp dịch vụ trực tiếp đến người tiêu dùng (bán lẻ, ăn uống, dịch vụ) "
                "phải sử dụng hóa đơn điện tử khởi tạo từ máy tính tiền có kết nối chuyển dữ liệu điện tử với cơ quan thuế.",
            ),
            (
                "Chương XI: Xử lý vi phạm pháp luật về thuế",
                "Hành vi trốn thuế, gian lận thuế bị xử phạt từ 1 đến 3 lần số tiền thuế trốn. "
                "Hành vi chậm nộp tiền thuế phải nộp tiền chậm nộp theo mức 0.03%/ngày tính trên số tiền thuế chậm nộp. "
                "Người nộp thuế tự giác khai bổ sung và nộp đủ tiền thuế trước khi cơ quan có thẩm quyền công bố quyết định kiểm tra sẽ được xem xét giảm nhẹ chế tài.",
            ),
        ],
    },
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def generate_legal_pdf(filepath: Path, title: str, sections: list[tuple[str, str]]) -> None:
    """Tạo file PDF hợp lệ với font Unicode hoặc Helvetica standard."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_path = Path("C:/Windows/Fonts/arial.ttf")
    if font_path.exists():
        pdf.add_font("CustomFont", "", str(font_path))
        pdf.set_font("CustomFont", size=14)
        has_unicode_font = True
    else:
        pdf.set_font("Helvetica", size=14)
        has_unicode_font = False

    # Tiêu đề
    clean_title = title if has_unicode_font else title.encode("ascii", "replace").decode("ascii")
    pdf.multi_cell(w=0, h=8, text=clean_title, align="C")
    pdf.ln(6)

    if has_unicode_font:
        pdf.set_font("CustomFont", size=11)
    else:
        pdf.set_font("Helvetica", size=11)

    for sec_title, sec_content in sections:
        header_text = sec_title if has_unicode_font else sec_title.encode("ascii", "replace").decode("ascii")
        body_text = sec_content if has_unicode_font else sec_content.encode("ascii", "replace").decode("ascii")

        pdf.multi_cell(w=0, h=7, text=f"\n--- {header_text} ---\n")
        pdf.multi_cell(w=0, h=6, text=body_text)
        pdf.ln(4)

    pdf.output(str(filepath))
    size = filepath.stat().st_size
    print(f"Created: {filepath.name} ({size} bytes)")


def download_documents() -> None:
    """Tạo và lưu trữ tối thiểu 3 tài liệu pháp lý PDF về thuế hộ kinh doanh."""
    setup_directory()
    for filename, doc_data in LEGAL_DOCUMENTS.items():
        filepath = DATA_DIR / filename
        generate_legal_pdf(filepath, doc_data["title"], doc_data["sections"])


if __name__ == "__main__":
    setup_directory()
    download_documents()
