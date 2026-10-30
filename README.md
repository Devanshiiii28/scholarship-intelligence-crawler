# Scholarship Intelligence Crawler

A Python prototype for discovering scholarship pages, crawling official/primary candidate sources,
extracting structured fields with source evidence, computing deterministic confidence scores,
persisting records in SQLite, detecting field changes and displaying results in Streamlit.

## Important honesty / verification note

This is a working prototype, not a claim that 20+ scholarships have already been independently
verified. The crawler discovers pages at runtime and extracts what it can prove from fetched HTML.
It deliberately leaves missing values as `Not specified` and records below 95% as `REVIEW_REQUIRED`.
A primary-looking domain is not sufficient by itself to mark a record verified. Some portals are
JavaScript-rendered or expose details in PDFs; those require source-specific adapters and manual
validation before submission as verified records.

## Stack

- Python, Requests, BeautifulSoup, lxml
- SQLite (standard library)
- Streamlit, Pandas
- Deterministic evidence-based confidence scoring

## Setup (Windows PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Run the crawler

```powershell
python main.py --crawl
```

Check expiry:
```powershell
python main.py --check-expiry
```

Launch dashboard:
```powershell
streamlit run app.py
```

## Database

SQLite database is created automatically at `data/scholarships.db`.
Tables:
- `scholarships`: normalized records, source URLs, evidence JSON, status and confidence
- `change_history`: old/new field values and detection time
- `crawl_runs`: crawl execution metrics and errors

## Architecture

1. `crawler/discovery.py`: seed sources + same-domain anchor discovery
2. `crawler/scraper.py`: fetch and clean HTML
3. `extraction/extractor.py`: title, amount, eligibility and deadline extraction with evidence snippets
4. `verification/`: official-domain heuristic, evidence validation and deterministic scoring
5. `database/`: SQLite persistence and upsert/change history
6. `monitoring/`: expiry classification
7. `app.py`: searchable dashboard and record inspection

## Confidence methodology

Maximum 100 points:
- Primary-domain heuristic: 20
- Successful page fetch: 15
- Name evidence: 10
- At least 2 evidence-backed fields: +5
- At least 3 evidence-backed fields: +5
- At least 4 evidence-backed fields: +5
- Application link on source page: 10
- Deadline evidence: 10
- Amount or eligibility evidence: 10
- Extraction consistency: 10

A hard guard caps non-primary sources or records without name evidence at 74. `VERIFIED` requires
95 or above. Scores are a prototype heuristic and require manual audit before production use.

## Discovery and source seeds

Starting points are configured in `config/settings.py`:
- National Scholarship Portal: https://scholarships.gov.in/All-Scholarships
- UGC Student Corner: https://www.ugc.gov.in/Home/student_Corner
- Department of Social Justice and Empowerment: https://socialjustice.gov.in/schemes
- Reliance Foundation: https://www.reliancefoundation.org/

The crawler follows same-domain links whose anchor text refers to scholarships/fellowships/financial
assistance. It is not a general-purpose search engine; add a free search adapter or more seed domains
to broaden discovery.

## Change detection

The upsert routine compares tracked fields and writes old/new values to `change_history` rather than
silently overwriting them. A repeated crawl against the same unchanged pages should not create changes.
The `expiry_checker` derives `ACTIVE`, `EXPIRING_SOON`, or `EXPIRED` from extracted deadlines. Missing
deadlines remain unclassified / review required.

## Limitations and next engineering steps

- Add source-specific parsers for JS portals and PDF notices.
- Validate provider identity and application links against provider pages.
- Normalize dates to ISO format before comparing deadlines.
- Add `NO_LONGER_VERIFIABLE` only after repeated failed checks, not a single network error.
- Add robots.txt and crawl-delay handling for larger-scale crawling.
- Add scheduled execution through APScheduler / OS Task Scheduler.
- Expand tests with recorded HTML fixtures and manual field-level audits.

## Demo checklist

1. Run `python main.py --crawl`.
2. Show the run metrics in terminal.
3. Run `streamlit run app.py`.
4. Open a record and inspect its official URL, confidence explanation and evidence.
5. Run crawler again and inspect Crawl Runs / Change history.
6. Demonstrate expiry logic with a controlled test fixture (do not falsify a real scholarship deadline).

## License

Educational assignment prototype. Respect website terms, robots.txt and rate limits.

### PDF source handling

The crawler accepts HTML pages and PDF documents. PDF text is extracted with `pypdf` and passed through the same evidence-aware extraction pipeline. Scanned/image-only PDFs with no selectable text are explicitly flagged for manual/OCR review; they are not treated as verified records.
