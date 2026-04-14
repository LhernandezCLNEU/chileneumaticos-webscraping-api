#!/usr/bin/env python3
"""Run the ExampleComScraper from the command line.

Usage:
  ./scripts/run_example_scraper.py --url https://example.com/ [--dry-run] [--skip-ssl]

Options:
  --url       URL to scrape (default: https://example.com/)
  --dry-run   Don't persist to DB (runs FETCH/PARSE/EXTRACT only)
  --skip-ssl  Temporarily skip SSL verification for this run

"""
from __future__ import annotations

import argparse
import asyncio
import json

from app.core.config import settings
from app.scrappers.example_com import ExampleComScraper
from app.scrappers.base import ScraperStep
import httpx


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://example.com/", help="URL to scrape")
    parser.add_argument("--dry-run", action="store_true", help="Do not save results to DB")
    parser.add_argument("--force-selenium", action="store_true", help="Force use of Selenium even if detection fails")
    parser.add_argument("--skip-ssl", action="store_true", help="Temporarily skip SSL verification for this run")
    args = parser.parse_args()

    # allow temporary override
    if args.skip_ssl:
        settings.SKIP_SSL_VERIFY = True

    verify = not getattr(settings, "SKIP_SSL_VERIFY", False)
    async with httpx.AsyncClient(timeout=20, verify=verify) as client:
      scraper = ExampleComScraper(args.url, client=client)
      if args.force_selenium:
        scraper.force_selenium = True
        if args.dry_run:
          # run steps manually to avoid calling save()
          await scraper.fetch()
          await scraper.parse()
          await scraper.extract()
          out = {"url": args.url, "result": scraper.result, "logs": scraper.logs}
          print(json.dumps(out, ensure_ascii=False, indent=2))
        else:
          saved = await scraper.run()
          out = {"url": args.url, "save_result": saved, "logs": scraper.logs}
          print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
