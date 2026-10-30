REQUIRED_EVIDENCE_FIELDS = {"name"}

def validate_evidence(record):
    evidence = record.get("evidence") or []
    supported = {e.get("field") for e in evidence if e.get("source_url") == record.get("official_source_url") and e.get("snippet")}
    missing = sorted(REQUIRED_EVIDENCE_FIELDS - supported)
    return {"valid": not missing, "missing_fields": missing,
            "supported_fields": sorted(supported)}
