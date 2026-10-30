from database.db import connect
from datetime import datetime, timezone

def record_change(scholarship_id, field_name, old_value, new_value, source_url, evidence=""):
    with connect() as c:
        c.execute("""INSERT INTO change_history
        (scholarship_id,field_name,old_value,new_value,detected_at,source_url,evidence)
        VALUES (?,?,?,?,?,?,?)""",
        (scholarship_id,field_name,str(old_value),str(new_value),
         datetime.now(timezone.utc).isoformat(timespec="seconds"),source_url,evidence))
