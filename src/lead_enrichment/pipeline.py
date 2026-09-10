from __future__ import annotations

import time
from typing import List, Optional

from .config import Settings
from .crawler import Page, crawl_sync
from .extractor import local_extract
from .llm import llm_extract
from .models import CompanyIntelligence


class EnrichmentPipeline:
    def __init__(self, settings: Optional[Settings] = None, offline: bool = False):
        self.settings = settings or Settings()
        self.offline = offline

    def enrich(self, domain: str) -> CompanyIntelligence:
        started = time.perf_counter()
        try:
            pages: List[Page] = [] if self.offline else crawl_sync(domain, self.settings)
            result = local_extract(domain, pages, "Offline mode" if self.offline else None) if self.offline else llm_extract(domain, pages, self.settings)
            if self.offline:
                result.crawl_status = "offline"
        except Exception as exc:  # noqa: BLE001 - isolate a failed domain
            result = CompanyIntelligence(domain=domain, crawl_status="failed", error=f"{type(exc).__name__}: {exc}")
        result.duration_ms = round((time.perf_counter() - started) * 1000)
        return result

    def enrich_many(self, domains: List[str]) -> List[CompanyIntelligence]:
        return [self.enrich(domain.strip()) for domain in domains if domain.strip()]