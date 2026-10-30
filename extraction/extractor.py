import re
from urllib.parse import urlparse
from extraction.schema import ScholarshipRecord
from crawler.source_classifier import classify_source, source_type

FUNDING_WORDS = re.compile(r"scholarship|fellowship|stipend|financial assistance|education grant", re.I)
DATE_PATTERNS = [
    re.compile(r"(?:last date|closing date|application deadline|apply by|last date to apply)[^\d]{0,30}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", re.I),
    re.compile(r"(?:last date|closing date|application deadline|apply by)[^\d]{0,30}(\d{1,2}\s+[A-Za-z]+\s+20\d{2})", re.I),
]
AMOUNT_RE = re.compile(r"(?:₹|Rs\.?|INR)\s?[\d,]+(?:\s?(?:per annum|/year|per year))?", re.I)

def _snippet(text, pattern, window=220):
    m = pattern.search(text)
    if not m: return None
    start, end = max(0, m.start()-window//2), min(len(text), m.end()+window//2)
    return text[start:end].strip()

def extract_record(url, title, text, provider_hint=""):
    if not FUNDING_WORDS.search(title + " " + text[:5000]):
        return None
    # Avoid treating generic portal pages as a single scholarship if no named scheme can be inferred.
    name = title.strip() or ""
    if not name or len(name) < 5:
        return None
    evidence = [{"field": "name", "value": name, "source_url": url,
                 "snippet": title[:300], "method": "HTML/PDF document title"}]
    amount = "Not specified"
    am = AMOUNT_RE.search(text)
    if am:
        amount = am.group(0)
        evidence.append({"field":"amount","value":amount,"source_url":url,
                         "snippet":_snippet(text, AMOUNT_RE),"method":"regex"})
    deadline = None
    for pat in DATE_PATTERNS:
        found = pat.search(text)
        if found:
            deadline = found.group(1)
            evidence.append({"field":"closing_date","value":deadline,"source_url":url,
                             "snippet":_snippet(text, pat),"method":"regex"})
            break
    eligibility = "Not specified"
    elig_pattern = re.compile(r"(eligibility criteria|eligible candidates|eligibility)[\s:.-]{0,20}", re.I)
    snippet = _snippet(text, elig_pattern, 500)
    if snippet:
        eligibility = snippet[:500]
        evidence.append({"field":"eligibility","value":eligibility,"source_url":url,
                         "snippet":snippet,"method":"keyword context"})
    app_url = None
    # A link to an application form is accepted only when its anchor explicitly indicates application.
    # Link resolution is handled in crawler_engine using the page soup.
    return ScholarshipRecord(
        name=name, provider=provider_hint or urlparse(url).hostname or "Not specified",
        official_source_url=url, source_type=source_type(url), amount=amount,
        eligibility=eligibility, closing_date=deadline,
        confidence=0, current_status="REVIEW_REQUIRED",
        confidence_reason="Awaiting evidence-based verification.", evidence=evidence
    )

def find_application_url(soup, page_url):
    from urllib.parse import urljoin
    for a in soup.select("a[href]"):
        label = " ".join(a.get_text(" ", strip=True).split()).lower()
        href = a.get("href", "")
        if any(x in label for x in ("apply now", "apply online", "application form", "register now")):
            return urljoin(page_url, href)
    return None


def extract_records_from_page(url, title, text, soup, provider_hint=""):
    """Extract multiple named opportunities from listing pages using scholarship-related headings."""
    from extraction.schema import ScholarshipRecord
    from urllib.parse import urlparse
    found = []
    seen = set()
    for node in soup.select("h1, h2, h3, h4, h5, strong"):
        name = " ".join(node.get_text(" ", strip=True).split())
        if not name or len(name) < 8 or not FUNDING_WORDS.search(name):
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        container = node.parent
        block = " ".join(container.get_text(" ", strip=True).split())[:1800] if container else name
        evidence = [{"field":"name","value":name,"source_url":url,
                     "snippet":block[:500],"method":"listing heading + parent text"}]
        amount = "Not specified"
        am = AMOUNT_RE.search(block)
        if am:
            amount = am.group(0)
            evidence.append({"field":"amount","value":amount,"source_url":url,
                             "snippet":block[:500],"method":"regex"})
        deadline = None
        for pat in DATE_PATTERNS:
            m = pat.search(block)
            if m:
                deadline = m.group(1)
                evidence.append({"field":"closing_date","value":deadline,"source_url":url,
                                 "snippet":block[:500],"method":"regex"})
                break
        elig = "Not specified"
        if re.search(r"eligib|income|marks|percentage|category|domicile",block,re.I):
            elig = block[:500]
            evidence.append({"field":"eligibility","value":elig,"source_url":url,
                             "snippet":block[:500],"method":"listing context"})
        rec = ScholarshipRecord(
            name=name, provider=provider_hint or urlparse(url).hostname or "Not specified",
            official_source_url=url, source_type=source_type(url), amount=amount,
            eligibility=elig, closing_date=deadline, current_status="REVIEW_REQUIRED",
            confidence=0, confidence_reason="Awaiting evidence-based verification.", evidence=evidence
        )
        found.append(rec)
    return found
