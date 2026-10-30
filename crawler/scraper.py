"""HTTP fetching and text extraction for HTML pages and PDF documents."""
from html import escape
from io import BytesIO
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from config.settings import USER_AGENT, REQUEST_TIMEOUT


def _pdf_to_html(pdf_bytes: bytes, source_url: str) -> str:
    """Extract selectable text from a PDF and wrap it for the existing pipeline.

    Scanned/image-only PDFs may contain no selectable text; those are returned
    with a clear placeholder rather than being treated as successfully parsed.
    """
    reader = PdfReader(BytesIO(pdf_bytes))
    metadata = reader.metadata or {}
    title = str(getattr(metadata, "title", "") or "").strip()
    page_texts = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()
        if page_text:
            page_texts.append(f"Page {index}\n{page_text}")

    combined = "\n\n".join(page_texts)
    if not title and combined:
        title = next((line.strip() for line in combined.splitlines() if line.strip()), "PDF document")
    if not title:
        title = urlparse(source_url).path.rsplit("/", 1)[-1] or "PDF document"
    if not combined:
        combined = "[No selectable text found. This may be a scanned PDF and requires OCR review.]"

    return (
        "<!doctype html><html><head><title>" + escape(title) +
        "</title></head><body><h1>" + escape(title) +
        "</h1><pre>" + escape(combined) + "</pre></body></html>"
    )


def fetch_page(url):
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    is_pdf = "application/pdf" in content_type or urlparse(response.url).path.lower().endswith(".pdf")

    if is_pdf:
        return _pdf_to_html(response.content, response.url), response.url
    if "html" not in content_type and content_type:
        raise ValueError(f"Unsupported content type: {content_type}; expected HTML or PDF")
    return response.text, response.url


def extract_page_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = " ".join(soup.get_text(" ", strip=True).split())
    return title, text, soup
