from urllib.parse import urlparse

OFFICIAL_SUFFIXES = (
    ".gov.in", ".nic.in", ".ac.in", ".edu.in", ".ugc.gov.in",
    ".aicte-india.org", ".gov", ".edu"
)
KNOWN_OFFICIAL_HOSTS = {
    "scholarships.gov.in", "www.ugc.gov.in", "ugc.gov.in",
    "socialjustice.gov.in", "www.reliancefoundation.org",
    "reliancefoundation.org", "scholarships.reliancefoundation.org",
}

def classify_source(url: str):
    host = (urlparse(url).hostname or "").lower()
    if host in KNOWN_OFFICIAL_HOSTS or any(host.endswith(s) for s in OFFICIAL_SUFFIXES):
        return "PRIMARY_CANDIDATE"
    return "DISCOVERY_ONLY"

def source_type(url: str):
    host = (urlparse(url).hostname or "").lower()
    if host.endswith(".gov.in") or host.endswith(".nic.in"):
        return "Government"
    if "ugc.gov.in" in host or "aicte" in host:
        return "Government / regulator"
    if "reliancefoundation" in host:
        return "Corporate foundation"
    if host.endswith(".ac.in") or host.endswith(".edu.in"):
        return "University / institution"
    return "Other / unclassified"
