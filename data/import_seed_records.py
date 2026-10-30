import csv, json, hashlib, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from database.db import init_db, connect
CSV_PATH = ROOT / "data" / "official_nsp_seed_records.csv"

def main():
    init_db()
    inserted = 0
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as f, connect() as conn:
        for row in csv.DictReader(f):
            fp = hashlib.sha256((row["name"].lower().strip()+"|"+row["official_source_url"].lower().strip()).encode()).hexdigest()
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            cur = conn.execute("""INSERT OR IGNORE INTO scholarships
                (fingerprint,name,provider,official_source_url,application_url,source_type,amount,eligibility,
                 academic_requirements,course_level,income_criteria,age_criteria,gender_criteria,category_criteria,
                 domicile,institution_requirements,opening_date,closing_date,documents_required,selection_process,
                 renewal_requirements,current_status,confidence,confidence_reason,evidence_json,source_last_seen,
                 last_verified,content_hash,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (fp,row["name"],row["provider"],row["official_source_url"],row["application_url"] or None,
                 row["source_type"],row["amount"],row["eligibility"],row["academic_requirements"],row["course_level"],
                 row["income_criteria"],row["age_criteria"],row["gender_criteria"],row["category_criteria"],
                 row["domicile"],row["institution_requirements"],row["opening_date"] or None,row["closing_date"],
                 row["documents_required"],row["selection_process"],row["renewal_requirements"],row["current_status"],
                 float(row["confidence"]),row["confidence_reason"],row["evidence_json"],row["source_last_seen"],
                 None,None,ts,ts))
            inserted += cur.rowcount
    print(f"Seed import complete. New records inserted: {inserted}. Existing records were not overwritten.")
    print("All imported records are REVIEW_REQUIRED until scheme-specific details are verified.")

if __name__ == "__main__":
    main()
