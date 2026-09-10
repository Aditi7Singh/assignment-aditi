from __future__ import annotations

import re
from typing import List, Optional

from .crawler import Page
from .models import CompanyIntelligence

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[A-Za-z]{2,})+")
PHONE_RE = re.compile(r"(?:\+?\d[\d ()-]{7,}\d)")


def local_extract(domain: str, pages: List[Page], error: Optional[str] = None) -> CompanyIntelligence:
    valid_pages = [page for page in pages if page.text]
    source_urls = [page.url for page in valid_pages]
    combined = " ".join(page.text for page in valid_pages)
    title = next((page.title for page in pages if page.title), "")
    emails = sorted(set(EMAIL_RE.findall(combined)))
    phones = sorted({" ".join(match.split()) for match in PHONE_RE.findall(combined)})
    social = []
    for match in re.findall(r"https?://[^\s)]+", combined):
        if any(host in match for host in ("linkedin.com", "twitter.com", "x.com", "github.com")):
            social.append(match.rstrip(".,"))
    name = title.split("|")[0].split("-")[0].strip() or domain.split(".")[0].title()
    description = next((page.text[:400] for page in valid_pages if page.text), None)
    status = "success" if valid_pages else "failed"
    return CompanyIntelligence(
        company_name=name,
        domain=domain,
        description=description,
        contact_emails=emails[:20],
        contact_phones=phones[:20],
        social_links=list(dict.fromkeys(social))[:20],
        source_urls=source_urls,
        crawl_status=status,
        error=error or next((page.error for page in pages if page.error), None),
        extraction_method="local",
    )