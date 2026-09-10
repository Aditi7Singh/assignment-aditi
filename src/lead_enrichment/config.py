import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "25"))
    max_pages_per_domain: int = int(os.getenv("MAX_PAGES_PER_DOMAIN", "6"))
    max_text_chars_per_page: int = int(os.getenv("MAX_TEXT_CHARS_PER_PAGE", "12000"))
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY") or None