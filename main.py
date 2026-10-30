import argparse, json
from crawler.crawler_engine import run_crawl
from database.db import init_db
from monitoring.expiry_checker import refresh_expiry_status

def main():
    parser = argparse.ArgumentParser(description="Scholarship Intelligence Crawler")
    parser.add_argument("--crawl", action="store_true", help="Discover, crawl, extract, verify and store")
    parser.add_argument("--check-expiry", action="store_true", help="Refresh expiry statuses")
    args = parser.parse_args()
    init_db()
    if args.crawl:
        print(json.dumps(run_crawl(),indent=2,ensure_ascii=False))
    if args.check_expiry:
        print(f"Expiry statuses updated: {refresh_expiry_status()}")
    if not args.crawl and not args.check_expiry:
        parser.print_help()

if __name__ == "__main__":
    main()
