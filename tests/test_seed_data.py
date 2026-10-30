import csv
from pathlib import Path

def test_seed_dataset_has_20_plus_real_portal_listings():
    p=Path(__file__).resolve().parents[1]/"data"/"official_nsp_seed_records.csv"
    with p.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    assert len(rows)>=20
    assert all(r["official_source_url"]=="https://scholarships.gov.in/All-Scholarships" for r in rows)
    assert all(r["current_status"]=="REVIEW_REQUIRED" for r in rows)
