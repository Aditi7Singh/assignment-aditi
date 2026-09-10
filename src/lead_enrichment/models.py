from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Person(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    role: Optional[str] = None
    profile_url: Optional[HttpUrl] = None


class CompanyIntelligence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    company_name: Optional[str] = None
    domain: str
    description: Optional[str] = None
    industry: Optional[str] = None
    headquarters: Optional[str] = None
    founded_year: Optional[int] = Field(default=None, ge=1800, le=2100)
    products_services: List[str] = Field(default_factory=list)
    founders: List[Person] = Field(default_factory=list)
    leadership: List[Person] = Field(default_factory=list)
    contact_emails: List[str] = Field(default_factory=list)
    contact_phones: List[str] = Field(default_factory=list)
    social_links: List[HttpUrl] = Field(default_factory=list)
    source_urls: List[HttpUrl] = Field(default_factory=list)
    crawl_status: str = "success"
    error: Optional[str] = None
    extraction_method: str = "local"
    duration_ms: int = 0