#!/usr/bin/env python3
"""Render the deploy-time SEO identity for ArSonKuPik static hosting.

The repository keeps one reviewed static-site source tree. Production hosting is
split intentionally:

* Cloudflare Pages is the canonical public SEO authority.
* GitHub Pages remains an accessible mirror.

Both deployed copies must advertise the Cloudflare URL as canonical so search
engines consolidate duplicate-host signals instead of making the two hosts
compete. Cloudflare runs this script as its build command. The GitHub Pages
workflow runs the same script in its ephemeral checkout before uploading the
mirror artifact.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_ROOT = "https://masarray.github.io/vst-enhancer/"
PRIMARY_ROOT = "https://arsonkupik.pages.dev/"
TEXT_SUFFIXES = {".html", ".xml", ".txt", ".json", ".js", ".css"}
SPECIAL_TEXT_FILES = {"_headers", "_redirects"}


def normalized_root(value: str) -> str:
    value = value.strip()
    if not value.startswith("https://"):
        raise ValueError("SEO roots must use https://")
    return value.rstrip("/") + "/"


def iter_text_files(site_dir: Path):
    for path in sorted(site_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in SPECIAL_TEXT_FILES:
            yield path


def rewrite_file(path: Path, old: str, new: str) -> int:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"UTF-8 BOM is forbidden: {path}")
    text = raw.decode("utf-8")
    count = text.count(old)
    if count:
        path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")
    return count


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_rendered_identity(site_dir: Path, source_root: str, primary_root: str) -> None:
    indexed_pages = sorted(site_dir.rglob("index.html"))
    require(indexed_pages, "No index.html pages were found")

    for path in indexed_pages:
        text = path.read_text(encoding="utf-8")
        require(source_root not in text, f"Legacy host remained in {path}")
        require(primary_root in text, f"Primary host is missing from {path}")

    robots = (site_dir / "robots.txt").read_text(encoding="utf-8")
    require(source_root not in robots, "Legacy host remained in robots.txt")
    require(f"Sitemap: {primary_root}sitemap.xml" in robots, "Primary XML sitemap is missing from robots.txt")
    require(f"Sitemap: {primary_root}sitemap.txt" in robots, "Primary text sitemap is missing from robots.txt")

    sitemap_xml = (site_dir / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_txt = (site_dir / "sitemap.txt").read_text(encoding="utf-8")
    require(source_root not in sitemap_xml, "Legacy host remained in sitemap.xml")
    require(source_root not in sitemap_txt, "Legacy host remained in sitemap.txt")
    require(primary_root in sitemap_xml and primary_root in sitemap_txt, "Primary host is missing from sitemaps")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", default="site", help="Static site directory to render in place")
    parser.add_argument("--source-root", default=SOURCE_ROOT)
    parser.add_argument("--canonical-root", default=PRIMARY_ROOT)
    args = parser.parse_args()

    site_dir = Path(args.site_dir).resolve()
    source_root = normalized_root(args.source_root)
    primary_root = normalized_root(args.canonical_root)

    require(site_dir.is_dir(), f"Site directory does not exist: {site_dir}")
    require(source_root != primary_root, "Source and canonical roots must differ")

    files_changed = 0
    replacements = 0
    for path in iter_text_files(site_dir):
        count = rewrite_file(path, source_root, primary_root)
        if count:
            files_changed += 1
            replacements += count

    # Keep discovery authoritative even if a future source edit changes wording
    # around the sitemap declarations.
    robots_path = site_dir / "robots.txt"
    robots_path.write_text(
        "# Cloudflare Pages is the canonical SEO authority; GitHub Pages remains a mirror.\n"
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {primary_root}sitemap.xml\n"
        f"Sitemap: {primary_root}sitemap.txt\n",
        encoding="utf-8",
        newline="\n",
    )

    validate_rendered_identity(site_dir, source_root, primary_root)
    print(
        f"[PASS] Rendered SEO authority {primary_root} across {files_changed} files "
        f"({replacements} host references rewritten)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
