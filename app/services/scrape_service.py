from __future__ import annotations

import asyncio
import uuid
from typing import Any, Dict, List, Optional

import httpx
from urllib.parse import urlparse

from app.core.config import settings
from app.scrappers.sdn import SDNScraper
from app.scrappers.example_com import ExampleComScraper
from app.scrappers.base import ScraperStep


class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeService:
    def __init__(self) -> None:
        # task_id -> metadata
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def launch(self, urls: List[str], callback_url: Optional[str] = None) -> str:
        task_id = uuid.uuid4().hex
        self.tasks[task_id] = {"status": TaskStatus.PENDING, "result": None, "urls": urls, "callback": callback_url}
        asyncio.create_task(self._run_task(task_id, urls, callback_url))
        return task_id

    async def _run_task(self, task_id: str, urls: List[str], callback_url: Optional[str]) -> None:
        self.tasks[task_id]["status"] = TaskStatus.RUNNING
        results = []
        try:
            # allow skipping SSL verification when configured (dev convenience)
            verify = not settings.SKIP_SSL_VERIFY
            async with httpx.AsyncClient(timeout=30, verify=verify) as client:
                for url in urls:
                    # choose scraper implementation by domain
                    domain = urlparse(url).netloc.lower()
                    if domain.endswith("example.com"):
                        scraper_cls = ExampleComScraper
                    else:
                        # no matching scraper for this domain
                        scraper_cls = None

                    if scraper_cls is None:
                        results.append({"url": url, "error": "no_scraper_for_domain", "logs": []})
                        continue

                    scraper = scraper_cls(url, client=client)  # reuse client
                    try:
                        # run full flow
                        await scraper.run([ScraperStep.FETCH, ScraperStep.PARSE, ScraperStep.EXTRACT, ScraperStep.SAVE])
                        results.append({"url": url, "result": scraper.result, "logs": scraper.logs})
                    except Exception as e:  # capture per-site errors
                        results.append({"url": url, "error": str(e), "logs": scraper.logs})

            self.tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task_id]["result"] = results

            if callback_url:
                # fire-and-forget notification
                try:
                    async with httpx.AsyncClient(timeout=10) as notify_client:
                        await notify_client.post(callback_url, json={"task_id": task_id, "result": results})
                except Exception:
                    # ignore notification errors
                    pass

        except Exception as e:
            self.tasks[task_id]["status"] = TaskStatus.FAILED
            self.tasks[task_id]["result"] = {"error": str(e)}

    def status(self, task_id: str) -> Dict[str, Any]:
        return self.tasks.get(task_id, {"status": "not_found"})


# module-level singleton
service = ScrapeService()

__all__ = ["service", "ScrapeService", "TaskStatus"]
