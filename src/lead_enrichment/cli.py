from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import Settings
from .pipeline import EnrichmentPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich company domains from public web content")
    parser.add_argument("domains", nargs="+", help="Company domains, for example postman.com")
    parser.add_argument("--output", default="output.json", help="JSON output path")
    parser.add_argument("--offline", action="store_true", help="Skip network and produce valid fallback records")
    parser.add_argument("--max-pages", type=int, default=None)
    args = parser.parse_args()
    settings = Settings(max_pages_per_domain=args.max_pages or Settings().max_pages_per_domain)
    results = EnrichmentPipeline(settings, offline=args.offline).enrich_many(args.domains)
    output = [result.model_dump(mode="json") for result in results]
    Path(args.output).write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()