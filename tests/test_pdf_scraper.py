from crawler.scraper import _pdf_to_html, extract_page_text


class FakeMetadata:
    title = "National Fellowship Scheme"


class FakePage:
    def extract_text(self):
        return "Eligibility criteria: Indian students\nFellowship amount Rs. 25,000 per month"


class FakeReader:
    metadata = FakeMetadata()
    pages = [FakePage()]


def test_pdf_text_is_wrapped_for_existing_extractor(monkeypatch):
    import crawler.scraper as scraper
    monkeypatch.setattr(scraper, "PdfReader", lambda _: FakeReader())
    html = scraper._pdf_to_html(b"fake-pdf", "https://example.gov.in/scheme.pdf")
    title, text, soup = extract_page_text(html)
    assert title == "National Fellowship Scheme"
    assert "Eligibility criteria" in text
    assert "Rs. 25,000" in text


def test_scanned_pdf_is_flagged_for_review(monkeypatch):
    import crawler.scraper as scraper

    class EmptyPage:
        def extract_text(self):
            return ""

    class EmptyReader:
        metadata = None
        pages = [EmptyPage()]

    monkeypatch.setattr(scraper, "PdfReader", lambda _: EmptyReader())
    html = scraper._pdf_to_html(b"fake-pdf", "https://example.gov.in/scanned.pdf")
    _, text, _ = extract_page_text(html)
    assert "scanned PDF" in text
