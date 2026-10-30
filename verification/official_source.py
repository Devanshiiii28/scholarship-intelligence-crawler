from urllib.parse import urlparse
from crawler.source_classifier import classify_source

def is_primary_candidate(url):
    return classify_source(url) == "PRIMARY_CANDIDATE"

def explain_source(url):
    host = (urlparse(url).hostname or "").lower()
    if is_primary_candidate(url):
        return f"Host {host} matches the project's official-domain allowlist / government or institutional suffix heuristic. Human review is still required."
    return f"Host {host} is not in the official-domain allowlist; use for discovery only, not authoritative verification."
