from verification.official_source import is_primary_candidate
from verification.evidence_validator import validate_evidence

def calculate_confidence(record, page_present=True, extraction_consistent=True, application_url=None):
    """
    Deterministic score (0-100), not an LLM-generated number.
    Components: primary host 20, page fetched 15, field evidence 25,
    application URL 10, deadline evidence 10, amount/eligibility evidence 10,
    extraction consistency 10.
    """
    score, reasons = 0, []
    if is_primary_candidate(record["official_source_url"]):
        score += 20; reasons.append("Primary-domain heuristic: +20")
    else: reasons.append("Non-primary host: +0")
    if page_present:
        score += 15; reasons.append("Source page fetched successfully: +15")
    ev = record.get("evidence") or []
    fields = {e.get("field") for e in ev if e.get("snippet") and e.get("source_url") == record["official_source_url"]}
    if "name" in fields:
        score += 10; reasons.append("Name backed by source evidence: +10")
    if len(fields) >= 2:
        score += 5; reasons.append("At least two fields have evidence: +5")
    if len(fields) >= 3:
        score += 5; reasons.append("At least three fields have evidence: +5")
    if len(fields) >= 4:
        score += 5; reasons.append("At least four fields have evidence: +5")
    if application_url:
        score += 10; reasons.append("Application link found on source page: +10")
    if "closing_date" in fields:
        score += 10; reasons.append("Deadline backed by source snippet: +10")
    if {"amount", "eligibility"} & fields:
        score += 10; reasons.append("Amount or eligibility has evidence: +10")
    if extraction_consistent:
        score += 10; reasons.append("Extraction completed without parser error: +10")
    score = min(score, 100)
    # Hard guard: domain and evidence are necessary; an official-looking host alone is insufficient.
    if not is_primary_candidate(record["official_source_url"]) or "name" not in fields:
        score = min(score, 74)
    status = "VERIFIED" if score >= 95 else "REVIEW_REQUIRED"
    return round(score, 1), status, "; ".join(reasons)
