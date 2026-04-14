from __future__ import annotations

import asyncio
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx


class ScraperStep(str, Enum):
    FETCH = "fetch"
    PARSE = "parse"
    EXTRACT = "extract"
    SAVE = "save"


class BaseScraper:
    """Base async scraper with composable steps.

    Subclass and override `parse`, `extract`, `save` as needed. Use `run(steps=...)`
    to execute a subset of steps.
    """

    def __init__(self, url: str, client: Optional[httpx.AsyncClient] = None) -> None:
        self.url = url
        self.client = client
        self.html: Optional[str] = None
        self.parsed: Optional[Any] = None
        self.result: Optional[Dict[str, Any]] = None
        self.logs: List[str] = []

    async def fetch(self) -> None:
        self.add_log(f"fetch:start {self.url}")
        client_provided = self.client is not None
        if not client_provided:
            self.client = httpx.AsyncClient(timeout=10)

        try:
            resp = await self.client.get(self.url)
            resp.raise_for_status()
            self.html = resp.text
            self.add_log(f"fetch:ok {len(self.html or '')} bytes")
        except Exception as e:  # pragma: no cover - network errors
            self.add_log(f"fetch:error {e}")
            raise
        finally:
            if not client_provided and self.client is not None:
                await self.client.aclose()

    async def parse(self) -> None:
        """Parse raw HTML into an intermediate representation.

        Default implementation does nothing — override in subclasses.
        """
        self.add_log("parse:noop")

    async def extract(self) -> None:
        """Extract structured data from parsed result.

        Default implementation stores a minimal result.
        """
        self.result = {"url": self.url}
        self.add_log("extract:noop")

    async def save(self) -> Dict[str, Any]:
        """Persist or return the result. Override to save to DB.

        Returns the result by default.
        """
        self.add_log("save:noop")
        return self.result or {}

    async def run(self, steps: Optional[List[ScraperStep]] = None) -> Dict[str, Any]:
        """Run a list of steps in order. If steps is None, run all steps.

        Steps are members of `ScraperStep`.
        """
        if steps is None:
            steps = [ScraperStep.FETCH, ScraperStep.PARSE, ScraperStep.EXTRACT, ScraperStep.SAVE]

        for step in steps:
            if isinstance(step, ScraperStep):
                name = step.value
            else:
                name = str(step)

            method = getattr(self, name, None)
            if method is None or not asyncio.iscoroutinefunction(method):
                # allow calling synchronous methods too
                if method is None:
                    self.add_log(f"step:missing {name}")
                    continue
                else:
                    method()
                    continue

            self.add_log(f"step:start {name}")
            await method()
            self.add_log(f"step:done {name}")

        return await self.save()

    def add_log(self, message: str) -> None:
        self.logs.append(message)


__all__ = ["BaseScraper", "ScraperStep"]
