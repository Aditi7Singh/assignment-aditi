from __future__ import annotations

from .config import Settings
from .crawler import Page
from .extractor import local_extract
from .models import CompanyIntelligence

SYSTEM_PROMPT = """You extract company intelligence from public website text. Never invent facts.
Return only the requested schema. Use null or [] when evidence is missing. Keep source_urls limited
to URLs present in the input. Founders and leadership should only include people explicitly identified
by the pages, with their role and profile URL when available."""


def llm_extract(domain: str, pages: list[Page], settings: Settings) -> CompanyIntelligence:
    fallback = local_extract(domain, pages)
    if not settings.openai_api_key:
        return fallback
    try:
        from openai import OpenAI

        context = "\n\n".join(f"SOURCE: {page.url}\nTITLE: {page.title}\n{page.text}" for page in pages if page.text)
        response = OpenAI(api_key=settings.openai_api_key).beta.chat.completions.parse(
            model=settings.openai_model,
            temperature=0,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": context}],
            response_format=CompanyIntelligence,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            return fallback
        parsed.domain = domain
        parsed.source_urls = [page.url for page in pages if page.text]
        parsed.extraction_method = "openai"
        return parsed
    except Exception as exc:  # noqa: BLE001 - provider failure must use local fallback
        fallback.error = f"LLM fallback: {type(exc).__name__}: {exc}"
        return fallback