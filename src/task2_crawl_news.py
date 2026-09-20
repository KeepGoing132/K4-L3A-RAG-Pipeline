"""
Task 2 — Crawl bài viết/thông báo về thuế hộ kinh doanh, cá nhân kinh doanh.

Chủ đề: chính sách thuế đối với hộ kinh doanh, cá nhân kinh doanh
(từ 01/01/2026 bỏ thuế khoán, chuyển sang kê khai theo doanh thu thực tế).

Nguồn (cơ quan nhà nước, robots.txt cho phép crawl — `Allow: /`):
    - baochinhphu.vn                   Báo điện tử Chính phủ
    - xaydungchinhsach.chinhphu.vn     Cổng TTĐT Chính phủ

Hai trang trả HTML render sẵn phía server và dùng chung CMS (thân bài nằm
trong div.detail-content), nên chỉ cần requests + BeautifulSoup, không cần
trình duyệt headless.

Mỗi bài lưu thành một JSON trong data/landing/news/ với:
    url, title, date_crawled, content_markdown   (bắt buộc)
    date_published, source                       (thêm, để trích dẫn nguồn)
"""

import asyncio
import json
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # Báo điện tử Chính phủ
    "https://baochinhphu.vn/nhieu-thay-doi-ve-thue-doi-voi-ca-nhan-va-ho-kinh-doanh-102260106104740091.htm",
    "https://baochinhphu.vn/huong-dan-moi-ve-khai-nop-thue-ho-kinh-doanh-102260306124840648.htm",
    "https://baochinhphu.vn/phuong-phap-tinh-thue-ho-kinh-doanh-co-doanh-thu-duoi-3-ty-102260408162033979.htm",
    "https://baochinhphu.vn/chinh-thuc-nang-nguong-chiu-thue-voi-ho-kinh-doanh-len-01-ty-dong-nam-ap-dung-tu-1-1-2026-102260429185517215.htm",
    # Cổng TTĐT Chính phủ
    "https://xaydungchinhsach.chinhphu.vn/tinh-thue-the-nao-neu-doanh-thu-2026-khac-nhom-nop-thue-voi-doanh-thu-2025-119260319155007399.htm",
    "https://xaydungchinhsach.chinhphu.vn/huong-dan-thuc-hien-nghia-vu-thue-trong-ke-khai-thue-2026-cho-ho-ca-nhan-kinh-doanh-11926031716562593.htm",
    "https://xaydungchinhsach.chinhphu.vn/luu-y-chinh-trong-ky-khai-thue-quy-i-2026-119260312174235595.htm",
    "https://xaydungchinhsach.chinhphu.vn/huong-dan-thu-tuc-khai-thue-doi-voi-ho-kinh-doanh-ca-nhan-kinh-doanh-119260530072620314.htm",
]

SOURCE_NAMES = {
    "baochinhphu.vn": "Báo điện tử Chính phủ",
    "xaydungchinhsach.chinhphu.vn": "Cổng TTĐT Chính phủ",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; K4-RAG-Lab/0.1; educational research)"
}
REQUEST_DELAY_SECONDS = 1.0
FETCH_ATTEMPTS = 3
MIN_CONTENT_CHARS = 500

# Phần tử trong thân bài không phải nội dung: ảnh/video/nhúng và các khối
# "đọc thêm" (.kbwscwl-relatedbox) chèn giữa bài.
NOISE_SELECTORS = (
    "script, style, iframe, svg, img, video, "
    ".kbwscwl-relatedbox, [type='VideoStream']"
)


def fetch_html(url: str) -> str:
    """Tải HTML; thử lại khi lỗi mạng hoặc 5xx, không thử lại với lỗi 4xx."""
    for attempt in range(1, FETCH_ATTEMPTS + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response.text
        except requests.RequestException as error:
            status = getattr(getattr(error, "response", None), "status_code", None)
            if attempt == FETCH_ATTEMPTS or (status is not None and status < 500):
                raise
            time.sleep(2 * attempt)
    raise AssertionError("unreachable")


def _clean(text: str) -> str:
    return " ".join(text.split())


def _meta(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.find("meta", attrs={"property": prop})
    content = tag.get("content") if tag else None
    return content.strip() if content and content.strip() else None


def parse_article(url: str, page: str) -> dict:
    """Trích tiêu đề, ngày đăng và nội dung Markdown từ HTML bài viết."""
    soup = BeautifulSoup(page, "html.parser")

    body = soup.select_one("div.detail-content[data-role='content']")
    if body is None:
        raise ValueError("không tìm thấy thân bài (div.detail-content)")
    for tag in body.select(NOISE_SELECTORS):
        tag.decompose()

    heading = soup.select_one("h1.detail-title, h1.title") or soup.find("h1")
    title = _clean(heading.get_text()) if heading else ""
    if not title:
        raise ValueError("không tìm thấy tiêu đề bài viết")

    # Sapo (tóm tắt đầu bài) nằm ngoài thân bài; bỏ dấu nguồn "(Chinhphu.vn) -".
    sapo_tag = soup.select_one("h2.detail-sapo")
    sapo = _clean(sapo_tag.get_text()) if sapo_tag else ""
    sapo = re.sub(r"^\(Chinhphu\.vn\)\s*-\s*", "", sapo)

    content = markdownify(str(body), heading_style="ATX", strip=["a"])
    content = re.sub(r"[ \t]+\n", "\n", content)
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    if sapo:
        content = f"{sapo}\n\n{content}"
    if len(content) < MIN_CONTENT_CHARS:
        raise ValueError(f"nội dung quá ngắn ({len(content)} ký tự)")

    host = urlparse(url).netloc
    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(timespec="seconds"),
        "content_markdown": content,
        "date_published": _meta(soup, "article:published_time"),
        "source": SOURCE_NAMES.get(host, host),
    }


async def crawl_article(url: str) -> dict:
    page = await asyncio.to_thread(fetch_html, url)
    return parse_article(url, page)


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    saved = 0
    for index, url in enumerate(ARTICLE_URLS, 1):
        if index > 1:
            await asyncio.sleep(REQUEST_DELAY_SECONDS)
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            saved += 1
            print(f"Saved: {output.name} — {article['title']}")
        except Exception as error:
            print(f"Failed: {url} — {error}")
    print(f"Done: {saved}/{len(ARTICLE_URLS)} articles saved to {DATA_DIR}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
