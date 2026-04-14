from __future__ import annotations

import asyncio
import re
from typing import Dict, Any, Optional

import httpx
from app.core.config import settings
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False

from app.scrappers.base import BaseScraper, ScraperStep
from app.db import AsyncSessionLocal
from app.models.product import Product
from app.models.parsed_result import ParsedResult


class ExampleComScraper(BaseScraper):
    """Simple scraper for https://example.com/ that extracts the page title
    and meta description (if present).
    """

    async def parse(self) -> None:
        # keep the raw HTML as parsed representation
        self.parsed = self.html or ""
        self.add_log("parse:stored_html")

    async def fetch(self) -> None:
        """Prefer Selenium for fetching (for JS-rendered pages); fall back to httpx.

        Selenium can be forced by setting `self.force_selenium = True` on the instance.
        """
        use_selenium = getattr(self, "force_selenium", False) or SELENIUM_AVAILABLE
        if use_selenium:
            # try importing selenium components at runtime (handles --force-selenium)
            try:
                from selenium import webdriver as _webdriver
                from selenium.webdriver.chrome.options import Options as _Options
                from selenium.webdriver.chrome.service import Service as _Service
                from webdriver_manager.chrome import ChromeDriverManager as _ChromeDriverManager
                from selenium.webdriver.common.by import By as _By
                from selenium.common.exceptions import NoSuchElementException as _NoSuchElementException
            except Exception as ie:
                self.add_log(f"fetch:selenium:import_error {ie}")
                if getattr(self, "force_selenium", False):
                    # user explicitly forced Selenium; raise a clear error
                    raise ImportError("Selenium is not available in the environment. Install selenium and webdriver-manager.")
                # otherwise fall back to httpx
                await super().fetch()
                return

            self.add_log("fetch:selenium:start")

            # run selenium in a thread to avoid blocking the event loop
            def _selenium_get(url: str):
                options = _Options()
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                # if configured to skip SSL verify in dev, allow insecure certs
                if getattr(settings, "SKIP_SSL_VERIFY", False):
                    options.add_argument("--ignore-certificate-errors")
                    options.set_capability("acceptInsecureCerts", True)

                # Support remote webdriver (e.g., selenium standalone container) when configured
                use_remote = getattr(settings, "SELENIUM_REMOTE", False) and getattr(settings, "WEBDRIVER_URL", None)
                driver = None
                try:
                    if use_remote:
                        driver = _webdriver.Remote(command_executor=settings.WEBDRIVER_URL, options=options)
                    else:
                        service = _Service(_ChromeDriverManager().install())
                        driver = _webdriver.Chrome(service=service, options=options)

                    driver.get(url)
                    # try to obtain description via provided selector
                    selenium_desc = None
                    try:
                        el = driver.find_element(_By.CSS_SELECTOR, "body > div > p:nth-child(2)")
                        selenium_desc = el.text.strip() if el and el.text else None
                    except _NoSuchElementException:
                        selenium_desc = None

                    return {"page_source": driver.page_source, "selenium_desc": selenium_desc}
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except Exception:
                            pass

            try:
                res = await asyncio.to_thread(_selenium_get, self.url)
                # res is a dict with page_source and selenium_desc
                page_src = res.get("page_source") if isinstance(res, dict) else res
                self.html = page_src
                self._selenium_desc = res.get("selenium_desc") if isinstance(res, dict) else None
                self.add_log(f"fetch:selenium:ok {len(page_src or '')} bytes")
                return
            except Exception as e:  # pragma: no cover - selenium runtime
                self.add_log(f"fetch:selenium:error {e}")

        # fallback to httpx
        await super().fetch()

    async def extract(self) -> None:
        html = (self.parsed or "")
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # prefer Selenium-extracted selector text when available
        description = None
        if getattr(self, "_selenium_desc", None):
            description = self._selenium_desc
        else:
            desc_match = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']\s*/?>",
                                    html, re.IGNORECASE | re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else None

        
        self.result = {
            "url": self.url,
            "title": title,
            "description": description,
        }

        print(f"Extracted result for {self.url}: {self.result}")
        self.add_log("extract:basic_fields")

    async def save(self) -> Dict[str, Any]:
        """Persist result to DB: create or update a Product and add a ParsedResult."""
        # create a minimal product record and a parsed_result linking to it
        try:
            async with AsyncSessionLocal() as session:
                prod = Product(
                    title_raw=self.result.get("title") or "",
                    title_normalized=None,
                    url=self.url,
                    source="example.com",
                    specs=None,
                )
                session.add(prod)
                await session.flush()  # get prod.id

                parsed = ParsedResult(product_id=prod.id, result=self.result)
                session.add(parsed)
                await session.commit()

                self.add_log(f"save:db product_id={prod.id} parsed_id={parsed.id}")
                return {"product_id": prod.id, "parsed_id": parsed.id}
        except Exception as e:  # pragma: no cover - DB errors
            self.add_log(f"save:error {e}")
            raise


def run_example_sync(url: str = "https://example.com/") -> Dict[str, Any]:
    """Helper to run the scraper synchronously (useful from CLI/tests).

    Creates an AsyncClient and executes the full run sequence.
    """

    async def _run() -> Dict[str, Any]:
        # honor SKIP_SSL_VERIFY from settings
        verify = not getattr(settings, "SKIP_SSL_VERIFY", False)
        async with httpx.AsyncClient(timeout=10, verify=verify) as client:
            s = ExampleComScraper(url, client=client)
            return await s.run()

    return asyncio.run(_run())


__all__ = ["ExampleComScraper", "run_example_sync"]
