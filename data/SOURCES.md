# Seed data provenance

The 31 seed records in `official_nsp_seed_records.csv` are scheme names listed on the Government of India's
National Scholarship Portal, Academic Year 2026-27:

https://scholarships.gov.in/All-Scholarships

The CSV's evidence snippets identify the listing text and approximate line ranges from the captured official
listing. For each row, only the provider/department grouping and the displayed student-application deadline
are populated. Fields not supported by that listing are explicitly `Not specified`.

**These are discovered/listed records, not all fully verified scholarship dossiers.** All rows are marked
`REVIEW_REQUIRED` with a conservative 75 score. The score is not a 95+ verification. Before changing a row
to `VERIFIED`, inspect its scheme-specific guideline and current portal application page, capture evidence
for eligibility, amount, course level, institution and date, and run the full evidence validator.
