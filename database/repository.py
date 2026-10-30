import json, hashlib
from datetime import datetime, timezone
from database.db import connect, init_db

TRACKED_FIELDS = ["amount","eligibility","closing_date","application_url","current_status",
                  "income_criteria","course_level","academic_requirements"]

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def fingerprint(name, url):
    return hashlib.sha256((name.lower().strip()+"|"+url.lower().strip()).encode()).hexdigest()

ALL_FIELDS = ["provider","application_url","source_type","amount","eligibility","academic_requirements",
              "course_level","income_criteria","age_criteria","gender_criteria","category_criteria",
              "domicile","institution_requirements","opening_date","closing_date","documents_required",
              "selection_process","renewal_requirements","current_status","confidence","confidence_reason",
              "evidence_json","source_last_seen","last_verified","content_hash","updated_at"]

def upsert_record(record, content_hash=None):
    init_db()
    d = record.copy()
    fp = fingerprint(d["name"], d["official_source_url"])
    ts = now()
    values = {
        "provider":d.get("provider"),"application_url":d.get("application_url"),"source_type":d.get("source_type"),
        "amount":d.get("amount","Not specified"),"eligibility":d.get("eligibility","Not specified"),
        "academic_requirements":d.get("academic_requirements","Not specified"),"course_level":d.get("course_level","Not specified"),
        "income_criteria":d.get("income_criteria","Not specified"),"age_criteria":d.get("age_criteria","Not specified"),
        "gender_criteria":d.get("gender_criteria","Not specified"),"category_criteria":d.get("category_criteria","Not specified"),
        "domicile":d.get("domicile","Not specified"),"institution_requirements":d.get("institution_requirements","Not specified"),
        "opening_date":d.get("opening_date"),"closing_date":d.get("closing_date"),
        "documents_required":d.get("documents_required","Not specified"),"selection_process":d.get("selection_process","Not specified"),
        "renewal_requirements":d.get("renewal_requirements","Not specified"),"current_status":d.get("current_status","REVIEW_REQUIRED"),
        "confidence":d.get("confidence",0),"confidence_reason":d.get("confidence_reason",""),
        "evidence_json":json.dumps(d.get("evidence",[]),ensure_ascii=False),"source_last_seen":ts,
        "last_verified":ts if d.get("current_status") == "VERIFIED" else None,"content_hash":content_hash,"updated_at":ts
    }
    with connect() as c:
        old = c.execute("SELECT * FROM scholarships WHERE fingerprint=?", (fp,)).fetchone()
        if old:
            changes = 0
            for field in TRACKED_FIELDS:
                newv = values.get(field)
                oldv = old[field]
                if newv is not None and str(oldv or "") != str(newv or ""):
                    c.execute("""INSERT INTO change_history
                    (scholarship_id,field_name,old_value,new_value,detected_at,source_url,evidence)
                    VALUES (?,?,?,?,?,?,?)""",
                    (old["id"],field,str(oldv or ""),str(newv or ""),ts,d["official_source_url"],values["evidence_json"]))
                    changes += 1
            assignments = ",".join(f"{f}=?" for f in ALL_FIELDS)
            c.execute(f"UPDATE scholarships SET {assignments} WHERE id=?",
                      tuple(values[f] for f in ALL_FIELDS)+(old["id"],))
            return "updated", changes
        cols = ["fingerprint","name","official_source_url"] + ALL_FIELDS[:-1] + ["created_at","updated_at"]
        vals = [fp,d["name"],d["official_source_url"]] + [values[f] for f in ALL_FIELDS[:-1]] + [ts,ts]
        placeholders = ",".join("?" for _ in cols)
        c.execute(f"INSERT INTO scholarships ({','.join(cols)}) VALUES ({placeholders})",vals)
        return "added", 0

def all_records():
    init_db()
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM scholarships ORDER BY updated_at DESC")]

def get_history(scholarship_id):
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM change_history WHERE scholarship_id=? ORDER BY detected_at DESC",(scholarship_id,))]
