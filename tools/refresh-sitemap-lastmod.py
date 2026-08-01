#!/usr/bin/env python3
"""Refresh sitemap lastmod only for pages changed by a public release update."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://masarray.github.io/vst-enhancer/"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
RELEASE_UPDATED_URLS = {ROOT, ROOT + "id/"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--date",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="UTC date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--sitemap",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "site" / "sitemap.xml",
    )
    args = parser.parse_args()

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date) is None:
        raise SystemExit(f"Invalid sitemap date: {args.date!r}")

    ElementTree.register_namespace("", NS)
    tree = ElementTree.parse(args.sitemap)
    root = tree.getroot()
    if root.tag != f"{{{NS}}}urlset":
        raise SystemExit(f"Unexpected sitemap root: {root.tag}")

    updated: set[str] = set()
    for item in root.findall(f"{{{NS}}}url"):
        loc = item.findtext(f"{{{NS}}}loc", "").strip()
        if loc not in RELEASE_UPDATED_URLS:
            continue
        lastmod = item.find(f"{{{NS}}}lastmod")
        if lastmod is None:
            lastmod = ElementTree.SubElement(item, f"{{{NS}}}lastmod")
        lastmod.text = args.date
        updated.add(loc)

    if updated != RELEASE_UPDATED_URLS:
        missing = sorted(RELEASE_UPDATED_URLS - updated)
        raise SystemExit(f"Sitemap is missing release-updated pages: {missing}")

    ElementTree.indent(tree, space="  ")
    tree.write(args.sitemap, encoding="utf-8", xml_declaration=True, short_empty_elements=True)
    print(f"[PASS] Sitemap lastmod refreshed for {len(updated)} release-updated pages: {args.date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
