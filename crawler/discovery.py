import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config.settings import SEED_SOURCES, USER_AGENT, REQUEST_TIMEOUT
from crawler.scraper import fetch_page

SCHOLARSHIP_TERMS = re.compile(r"scholarship|fellowship|stipend|financial assistance|education grant", re.I)

def discover_from_seeds():
    """Fetch seed pages and discover same-domain links whose anchor text looks funding-related."""
    queue, seen, discovered = [], set(), []
    for item in SEED_SOURCES:
        queue.append({**item, "depth": 0})
    while queue and len(seen) < 30:
        item = queue.pop(0)
        url = item["url"]
        if url in seen:
            continue
        seen.add(url)
        try:
            html, final_url = fetch_page(url)
            discovered.append({**item, "url": final_url, "discovery_method": "seed"})
            soup = BeautifulSoup(html, "lxml")
            base_host = urlparse(final_url).hostname
            for a in soup.select("a[href]"):
                label = " ".join(a.get_text(" ", strip=True).split())
                href = urljoin(final_url, a.get("href", ""))
                parsed = urlparse(href)
                if parsed.scheme not in ("http", "https") or parsed.hostname != base_host:
                    continue
                if SCHOLARSHIP_TERMS.search(label) and href not in seen:
                    discovered.append({
                        "url": href, "type": item.get("type", "Discovered official page"),
                        "provider": item.get("provider", base_host),
                        "discovery_method": "same-domain link discovery"
                    })
                    if len(discovered) < 60:
                        queue.append({"url": href, "type": item.get("type", "Discovered page"),
                                      "provider": item.get("provider", base_host), "depth": 1})
        except Exception:
            # A failed seed is recorded by the crawler run; other sources continue.
            continue
    # De-duplicate by canonical URL
    out, used = [], set()
    for x in discovered:
        key = x["url"].split("#")[0].rstrip("/")
        if key not in used:
            used.add(key); out.append(x)
    return out
