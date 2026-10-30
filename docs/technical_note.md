# Technical Note — Scholarship Intelligence Crawler

## Architecture
The prototype follows a modular pipeline: discovery → fetch → extraction → evidence validation →
confidence scoring → SQLite persistence → change/expiry monitoring → Streamlit presentation.
Seed URLs are configurable. The discovery module fetches each seed and identifies same-domain links
whose anchor text contains scholarship-related terms.

## Technology choices
Python and Requests/BeautifulSoup provide a free, inspectable crawling stack. SQLite avoids external
database services. Streamlit gives a compact dashboard. No paid API is required.

## Discovery and crawling
The system starts from government, regulator, ministry and foundation sources. It classifies hosts
using an allowlist and domain suffix heuristics. It follows same-host scholarship-related links. This
is a bounded prototype, not a comprehensive search engine; a free search provider adapter and more
seed domains are required for broad national coverage.

## Extraction
The extractor uses page titles, regular expressions and nearby text snippets to detect scholarship
names, amounts, eligibility text and deadlines. Every detected field stores the URL and a text snippet.
Absent information remains `Not specified`. Dynamic pages and PDFs need dedicated adapters.

## Verification and confidence
The confidence score is deterministic and explainable. It rewards primary-domain candidates, successful
fetches, field-level evidence, application links and consistent extraction. The system caps records
without name evidence or from non-primary domains below the verification threshold. A score of 95+
is required for `VERIFIED`; otherwise the status is `REVIEW_REQUIRED`. This heuristic does not replace
human source audit.

## Anti-hallucination
No LLM is allowed to invent missing fields. The extraction code only fills a field when a matching
source string is found. Each field-level evidence item records source URL, snippet and extraction
method. Unavailable values remain `Not specified`.

## Change detection and stale data
Records are keyed by a stable hash of scholarship name and source URL. On re-crawl, tracked fields are
compared and old/new values are appended to `change_history`. Expiry status is derived from an extracted
deadline. A missing page is not immediately considered withdrawn; repeated failures and official
confirmation should be implemented before assigning `NO_LONGER_VERIFIABLE`.

## Current limitations
The HTML parser is generic and may not capture all portal content. Before claiming the minimum record
counts, run the crawler, inspect records, manually verify each official source and expand source-specific
parsers. The included code intentionally does not fabricate sample scholarship records or artificial
change examples.
