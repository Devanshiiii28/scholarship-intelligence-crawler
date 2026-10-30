from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "scholarships.db"
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
USER_AGENT = os.getenv("CRAWLER_USER_AGENT", "ScholarshipIntelligenceCrawler/1.0 (educational project)")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))
MAX_PAGES_PER_RUN = int(os.getenv("MAX_PAGES_PER_RUN", "40"))

# Official/primary domains used as starting points, not as proof that every page is current.
SEED_SOURCES = [
    {"url": "https://scholarships.gov.in/All-Scholarships", "type": "Government portal", "provider": "National Scholarship Portal"},
    {"url": "https://scholarships.gov.in/Students", "type": "Government portal", "provider": "National Scholarship Portal"},
    {"url": "https://www.ugc.gov.in/Home/student_Corner", "type": "Government / regulator", "provider": "University Grants Commission"},
    {"url": "https://socialjustice.gov.in/schemes", "type": "Government ministry", "provider": "Department of Social Justice and Empowerment"},
    {"url": "https://www.reliancefoundation.org/", "type": "Corporate foundation", "provider": "Reliance Foundation"},
    {"url": "https://scholarships.reliancefoundation.org/UG_Scholarship.aspx", "type": "Corporate foundation", "provider": "Reliance Foundation"},
]
