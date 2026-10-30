from datetime import date, datetime
from database.db import connect

def refresh_expiry_status():
    today = date.today()
    updated = 0
    with connect() as c:
        rows = c.execute("SELECT id,closing_date,current_status FROM scholarships WHERE closing_date IS NOT NULL").fetchall()
        for row in rows:
            # Preserve verification state: expiry classification must not turn an
            # unverified record into ACTIVE/EXPIRING_SOON/EXPIRED.
            if row["current_status"] == "REVIEW_REQUIRED":
                continue
            raw = row["closing_date"]
            parsed = None
            for fmt in ("%d/%m/%Y","%d-%m-%Y","%d %B %Y","%d %b %Y"):
                try: parsed = datetime.strptime(raw,fmt).date(); break
                except ValueError: pass
            if not parsed: continue
            status = "EXPIRED" if parsed < today else ("EXPIRING_SOON" if (parsed-today).days <= 14 else "ACTIVE")
            if status != row["current_status"]:
                c.execute("UPDATE scholarships SET current_status=?,updated_at=? WHERE id=?",
                          (status,datetime.now().isoformat(timespec="seconds"),row["id"]))
                updated += 1
    return updated
