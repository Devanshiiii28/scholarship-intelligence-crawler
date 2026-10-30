import hashlib, json
from datetime import datetime, timezone
from config.settings import MAX_PAGES_PER_RUN
from crawler.discovery import discover_from_seeds
from crawler.scraper import fetch_page, extract_page_text
from extraction.extractor import extract_record, extract_records_from_page, find_application_url
from verification.confidence_score import calculate_confidence
from verification.official_source import explain_source
from database.db import connect, init_db
from database.repository import upsert_record

def run_crawl():
    init_db()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as c:
        cur = c.execute("INSERT INTO crawl_runs(started_at) VALUES (?)",(started,))
        run_id = cur.lastrowid
    pages = candidates = added = updated = 0
    errors = []
    sources = discover_from_seeds()
    for source in sources[:MAX_PAGES_PER_RUN]:
        try:
            html, final_url = fetch_page(source["url"])
            title, text, soup = extract_page_text(html)
            pages += 1
            extracted = extract_records_from_page(final_url,title,text,soup,source.get("provider",""))
            if not extracted:
                one = extract_record(final_url,title,text,source.get("provider",""))
                extracted = [one] if one else []
            for rec in extracted:
                rec.application_url = find_application_url(soup,final_url)
                d = rec.to_dict()
                d["evidence"] = d.get("evidence", [])
                d["evidence"].append({"field":"source_classification","value":explain_source(final_url),
                                      "source_url":final_url,"snippet":title[:250],"method":"domain heuristic"})
                score,status,reason = calculate_confidence(d, page_present=True,
                    extraction_consistent=True, application_url=d.get("application_url"))
                d["confidence"],d["current_status"],d["confidence_reason"] = score,status,reason
                d["content_hash"] = hashlib.sha256(text.encode("utf-8","ignore")).hexdigest()
                outcome, change_count = upsert_record(d,d["content_hash"])
                candidates += 1
                if outcome == "added": added += 1
                else: updated += 1
        except Exception as exc:
            errors.append(f'{source.get("url")}: {type(exc).__name__}: {exc}')
    finished = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as c:
        c.execute("""UPDATE crawl_runs SET finished_at=?,pages_visited=?,candidates_found=?,
        records_added=?,records_updated=?,errors=? WHERE id=?""",
        (finished,pages,candidates,added,updated,"\n".join(errors[:30]),run_id))
    return {"run_id":run_id,"pages_visited":pages,"candidates_found":candidates,
            "records_added":added,"records_updated":updated,"errors":errors}
