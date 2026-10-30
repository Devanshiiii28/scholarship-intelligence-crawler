
import json
import pandas as pd
import streamlit as st

from database.db import init_db, connect
from database.repository import all_records, get_history
from crawler.crawler_engine import run_crawl
from monitoring.expiry_checker import refresh_expiry_status

st.set_page_config(
    page_title="Scholarship Intelligence",
    page_icon="🎓",
    layout="wide"
)

init_db()

st.title("🎓 Scholarship Intelligence Crawler")
st.caption("Discover • Crawl • Extract • Verify • Score • Store • Monitor")

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("Crawler controls")

    if st.button("▶ Run crawler", use_container_width=True):
        with st.spinner("Discovering and crawling official sources..."):
            result = run_crawl()

        st.success(
            f"Run complete. {result['records_added']} added, "
            f"{result['records_updated']} updated."
        )

        if result["errors"]:
            st.warning(
                f"{len(result['errors'])} fetch errors. See Crawl Runs."
            )

    if st.button("Refresh expiry statuses", use_container_width=True):
        st.info(f"Updated {refresh_expiry_status()} records.")

    st.divider()
    st.write("Seed sources")
    st.write("- National Scholarship Portal")
    st.write("- UGC Student Corner")
    st.write("- Social Justice Ministry")
    st.write("- Reliance Foundation")


# ---------------- LOAD DATABASE ----------------

records = all_records()
df = pd.DataFrame(records)

if df.empty:
    st.info(
        "No records yet. Click Run crawler in the sidebar "
        "or run python main.py --crawl."
    )

    df = pd.DataFrame(
        columns=["name", "provider", "current_status", "confidence"]
    )

total = len(df)

verified = (
    int((df["current_status"] == "VERIFIED").sum())
    if total else 0
)

review = (
    int((df["current_status"] == "REVIEW_REQUIRED").sum())
    if total else 0
)

active = (
    int((df["current_status"] == "ACTIVE").sum())
    if total else 0
)

expired = (
    int((df["current_status"] == "EXPIRED").sum())
    if total else 0
)

avg = (
    float(df["confidence"].fillna(0).mean())
    if total else 0
)


# ---------------- DASHBOARD METRICS ----------------

cols = st.columns(5)

for col, label, value in zip(
    cols,
    ["Discovered", "Verified", "Review required", "Expired",
     "Avg confidence"],
    [total, verified, review, expired, f"{avg:.1f}%"]
):
    col.metric(label, value)

st.divider()


# ---------------- TABS ----------------

tab1, tab2, tab3 = st.tabs(
    ["Scholarships", "Crawl runs", "Methodology"]
)


# ---------------- SCHOLARSHIPS TAB ----------------

with tab1:

    st.subheader("Scholarship Records")

    query = st.text_input(
        "Search by scholarship, provider or eligibility"
    )

    status_filter = st.multiselect(
        "Status",
        sorted(df["current_status"].dropna().unique())
        if total else []
    )

    view = df.copy()

    if query and total:
        mask = view.astype(str).apply(
            lambda c: c.str.contains(
                query, case=False, na=False
            )
        ).any(axis=1)

        view = view[mask]

    if status_filter and total:
        view = view[
            view["current_status"].isin(status_filter)
        ]

    display_cols = [
        c for c in [
            "name",
            "provider",
            "amount",
            "closing_date",
            "current_status",
            "confidence",
            "official_source_url"
        ]
        if c in view.columns
    ]

    st.dataframe(
        view[display_cols] if total else view,
        use_container_width=True,
        hide_index=True
    )

    # ---------------- CSV DOWNLOAD SECTION ----------------

    st.divider()
    st.subheader("📥 Download Scholarship Dataset")

    st.write(
        "Download the scholarship records for offline inspection "
        "and analysis."
    )

    if total:

        download_col1, download_col2 = st.columns(2)

        # Complete database export
        all_csv = df.to_csv(
            index=False
        ).encode("utf-8-sig")

        with download_col1:
            st.download_button(
                label="⬇ Download All Scholarships",
                data=all_csv,
                file_name="all_scholarship_records.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Filtered records export
        filtered_csv = view.to_csv(
            index=False
        ).encode("utf-8-sig")

        with download_col2:
            st.download_button(
                label="⬇ Download Filtered Results",
                data=filtered_csv,
                file_name="filtered_scholarship_records.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.caption(
            f"{total} total records | "
            f"{len(view)} records in current search/filter"
        )

    else:
        st.warning("No scholarship records available for download.")

    # ---------------- SCHOLARSHIP DETAILS ----------------

    if total:

        names = {
            f'{r["name"]} — #{r["id"]}': r["id"]
            for r in records
        }

        selected = st.selectbox(
            "Inspect a scholarship",
            list(names)
        )

        r = next(
            x for x in records
            if x["id"] == names[selected]
        )

        st.subheader(r["name"])

        a, b, c = st.columns(3)

        a.metric("Confidence", f'{r["confidence"]:.1f}%')
        b.metric("Status", r["current_status"])
        c.metric(
            "Provider",
            r["provider"] or "Not specified"
        )

        for key, label in [
            ("amount", "Amount / benefit"),
            ("eligibility", "Eligibility"),
            ("closing_date", "Closing date"),
            ("application_url", "Application URL"),
            ("official_source_url", "Official source"),
            ("confidence_reason", "Why this score"),
            ("last_verified", "Last verified")
        ]:

            st.markdown(
                f"**{label}:** {r.get(key) or 'Not specified'}"
            )

        with st.expander("Source evidence"):

            try:
                st.json(
                    json.loads(r.get("evidence_json") or "[]")
                )
            except Exception:
                st.write(r.get("evidence_json"))

        with st.expander("Change history"):

            st.dataframe(
                pd.DataFrame(get_history(r["id"])),
                use_container_width=True
            )


# ---------------- CRAWL RUNS TAB ----------------

with tab2:

    with connect() as conn:

        runs = pd.read_sql_query(
            "SELECT * FROM crawl_runs ORDER BY id DESC",
            conn
        )

    st.dataframe(
        runs,
        use_container_width=True,
        hide_index=True
    )

    if not runs.empty:

        runs_csv = runs.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇ Download Crawl History",
            data=runs_csv,
            file_name="crawler_execution_history.csv",
            mime="text/csv"
        )




with tab3:

    st.markdown("""
     Verification Policy

    The score is computed from deterministic evidence checks,
    not generated by an LLM.

    A record is labelled `VERIFIED` only at 95 or above.
    A government-looking hostname alone cannot make a
    record verified.

    Every extracted field should carry a source URL and
    a supporting snippet.

    Important Limitation

    This prototype uses HTML title, keyword and regex extraction.
    Government portals may render content dynamically or expose
    scheme details through PDFs/API calls.

    Such records must remain `REVIEW_REQUIRED` until the parser
    captures field-level evidence.

    `Not specified` means the source text did not provide a value
    detectable by this parser; it is not a claim that the provider
    has no such criterion.
    """)
