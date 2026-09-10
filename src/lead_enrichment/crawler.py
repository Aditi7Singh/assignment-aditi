from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .config import Settings

KEYWORDS = ("about", "company", "team", "leadership", "contact", "pricing", "product")


@dataclass
class Page:
    url: str
    title: str
    text: str
    status_code: Optional[int] = None
    error: Optional[str] = None


def clean_html(html: str, max_chars: int) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for element in soup(["script", "style", "svg", "noscript", "nav", "footer", "form"]):
        element.decompose()
    main = soup.find("main") or soup.find("body") or soup
    text = " ".join(main.stripped_strings)
    return title, " ".join(text.split())[:max_chars]


class BrowserCrawler:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def crawl(self, domain: str) -> List[Page]:
        base = domain if domain.startswith("http") else f"https://{domain}"
        parsed = urlparse(base)
        base = f"{parsed.scheme}://{parsed.netloc}"
        pages: list[Page] = []

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return [Page(base, "", "", error="Playwright is not installed")]

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="LeadEnrichmentAgent/0.1 (+public-site-research)"
            )
            try:
                homepage = await self._visit(context, base)
                pages.append(homepage)
                links = await self._discover_links(context, base)
                for url in links[: self.settings.max_pages_per_domain - 1]:
                    pages.append(await self._visit(context, url))
            finally:
                await browser.close()
        return pages

    async def _visit(self, context, url: str) -> Page:
        page = await context.new_page()
        try:
            response = await page.goto(
                url, wait_until="domcontentloaded", timeout=self.settings.request_timeout_seconds * 1000
            )
            await page.wait_for_timeout(500)
            title, text = clean_html(await page.content(), self.settings.max_text_chars_per_page)
            return Page(url, title, text, response.status if response else None)
        except Exception as exc:  # noqa: BLE001 - isolate a failed page
            return Page(url, "", "", error=f"{type(exc).__name__}: {exc}")
        finally:
            await page.close()

    async def _discover_links(self, context, base: str) -> list[str]:
        page = await context.new_page()
        try:
            await page.goto(base, wait_until="domcontentloaded", timeout=self.settings.request_timeout_seconds * 1000)
            hrefs = await page.locator("a[href]").evaluate_all("els => els.map(el => el.href)")
        except Exception:  # noqa: BLE001 - link discovery is best effort
            return []
        finally:
            await page.close()
        candidates = []
        seen = set()
        for href in hrefs:
            absolute = urljoin(base, href).split("#", 1)[0].rstrip("/")
            parsed = urlparse(absolute)
            if parsed.netloc != urlparse(base).netloc or parsed.scheme not in {"http", "https"}:
                continue
            path = parsed.path.lower()
            if any(keyword in path for keyword in KEYWORDS) and absolute not in seen:
                seen.add(absolute)
                candidates.append(absolute)
        return candidates


def crawl_sync(domain: str, settings: Settings) -> list[Page]:
    return asyncio.run(BrowserCrawler(settings).crawl(domain))