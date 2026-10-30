import sqlite3
from config.settings import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            provider TEXT,
            official_source_url TEXT NOT NULL,
            application_url TEXT,
            source_type TEXT,
            amount TEXT DEFAULT 'Not specified',
            eligibility TEXT DEFAULT 'Not specified',
            academic_requirements TEXT DEFAULT 'Not specified',
            course_level TEXT DEFAULT 'Not specified',
            income_criteria TEXT DEFAULT 'Not specified',
            age_criteria TEXT DEFAULT 'Not specified',
            gender_criteria TEXT DEFAULT 'Not specified',
            category_criteria TEXT DEFAULT 'Not specified',
            domicile TEXT DEFAULT 'Not specified',
            institution_requirements TEXT DEFAULT 'Not specified',
            opening_date TEXT,
            closing_date TEXT,
            documents_required TEXT DEFAULT 'Not specified',
            selection_process TEXT DEFAULT 'Not specified',
            renewal_requirements TEXT DEFAULT 'Not specified',
            current_status TEXT DEFAULT 'REVIEW_REQUIRED',
            confidence REAL DEFAULT 0,
            confidence_reason TEXT,
            evidence_json TEXT DEFAULT '[]',
            source_last_seen TEXT,
            last_verified TEXT,
            content_hash TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS change_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            detected_at TEXT NOT NULL,
            source_url TEXT,
            evidence TEXT,
            FOREIGN KEY(scholarship_id) REFERENCES scholarships(id)
        );
        CREATE TABLE IF NOT EXISTS crawl_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            pages_visited INTEGER DEFAULT 0,
            candidates_found INTEGER DEFAULT 0,
            records_added INTEGER DEFAULT 0,
            records_updated INTEGER DEFAULT 0,
            errors TEXT DEFAULT ''
        );
        """)
