from __future__ import annotations

import re
from typing import Any, Dict

from app.scrappers.base import BaseScraper, ScraperStep


class SDNScraper(BaseScraper):
	"""Example scraper implementation for a generic site (SDN).

	This demonstrates how to subclass `BaseScraper` and implement parse/extract.
	"""

	async def parse(self) -> None:
		# Very small, dependency-free parsing: extract title and meta description
		html = self.html or ""
		title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
		desc_match = re.search(r"<meta\s+name=[\'\"]description[\'\"]\s+content=[\'\"](.*?)[\'\"]\s*/?>", html, re.IGNORECASE | re.DOTALL)
		self.parsed = {
			"title": (title_match.group(1).strip() if title_match else None),
			"description": (desc_match.group(1).strip() if desc_match else None),
		}

	async def extract(self) -> None:
		parsed = self.parsed or {}
		# Example extracted structure
		self.result = {
			"url": self.url,
			"title": parsed.get("title"),
			"description": parsed.get("description"),
		}


async def run_example(url: str) -> Dict[str, Any]:
	s = SDNScraper(url)
	# run full flow
	await s.run([ScraperStep.FETCH, ScraperStep.PARSE, ScraperStep.EXTRACT, ScraperStep.SAVE])
	return {"result": s.result, "logs": s.logs}


__all__ = ["SDNScraper", "run_example"]
