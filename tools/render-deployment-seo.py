#!/usr/bin/env python3
"""Render the canonical SEO identity for ArSonKuPik static hosting.

ArSonKuPik intentionally keeps two public hosts:

* Cloudflare Pages is the canonical public SEO authority.
* GitHub Pages remains an accessible compatibility mirror.

The migration workflow uses this renderer once to promote the repository's
historical GitHub Pages URLs to the Cloudflare identity. It also remains useful
as an idempotent deployment guard for GitHub Pages and release validation.
Cloudflare itself stays a plain static Pages deployment (`exit 0`) after the
source has been promoted.
"""
from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_ROOT = "https://masarray.github.io/vst-enhancer/"
PRIMARY_ROOT = "https://arsonkupik.pages.dev/"
TEXT_SUFFIXES = {".html", ".xml", ".txt", ".json", ".js", ".css"}
SPECIAL_TEXT_FILES = {"_headers", "_redirects"}
CORE_SITEMAPS = ("sitemap.xml", "sitemap.txt")
DISCOVERY_SITEMAPS = ("sitemap-discovery.xml", "sitemap-discovery.txt")
EVIDENCE_SITEMAPS = ("sitemap-evidence.xml", "sitemap-evidence.txt")
OPTIONAL_SITEMAP_PAIRS = (DISCOVERY_SITEMAPS, EVIDENCE_SITEMAPS)


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


def sitemap_names(site_dir: Path) -> tuple[str, ...]:
    """Return canonical sitemap files that exist and must remain discoverable."""
    for name in CORE_SITEMAPS:
        require((site_dir / name).is_file(), f"Required sitemap is missing: {name}")

    names = list(CORE_SITEMAPS)
    for pair in OPTIONAL_SITEMAP_PAIRS:
        present = [(site_dir / name).is_file() for name in pair]
        require(
            all(present) or not any(present),
            f"Optional sitemap XML/TXT files must be present as a pair: {pair}",
        )
        if all(present):
            names.extend(pair)
    return tuple(names)


def validate_rendered_identity(site_dir: Path, source_root: str, primary_root: str) -> None:
    indexed_pages = sorted(site_dir.rglob("index.html"))
    require(indexed_pages, "No index.html pages were found")

    for path in indexed_pages:
        text = path.read_text(encoding="utf-8")
        require(source_root not in text, f"Legacy host remained in {path}")
        require(primary_root in text, f"Primary host is missing from {path}")

    names = sitemap_names(site_dir)
    robots = (site_dir / "robots.txt").read_text(encoding="utf-8")
    require(source_root not in robots, "Legacy host remained in robots.txt")
    for name in names:
        require(
            f"Sitemap: {primary_root}{name}" in robots,
            f"Primary sitemap is missing from robots.txt: {name}",
        )
        sitemap_text = (site_dir / name).read_text(encoding="utf-8")
        require(source_root not in sitemap_text, f"Legacy host remained in {name}")
        require(primary_root in sitemap_text, f"Primary host is missing from {name}")


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

    # Keep every reviewed sitemap authoritative even if a future source edit
    # changes wording around discovery declarations. P1 discovery and P2
    # evidence sitemap pairs are included automatically when present.
    names = sitemap_names(site_dir)
    robots_lines = [
        "# Cloudflare Pages is the canonical SEO authority; GitHub Pages remains a mirror.",
        "User-agent: *",
        "Allow: /",
        "",
        *(f"Sitemap: {primary_root}{name}" for name in names),
        "",
    ]
    (site_dir / "robots.txt").write_text(
        "\n".join(robots_lines),
        encoding="utf-8",
        newline="\n",
    )

    validate_rendered_identity(site_dir, source_root, primary_root)
    print(
        f"[PASS] Canonical SEO authority {primary_root} verified across the site; "
        f"{files_changed} files changed in this run ({replacements} host references rewritten); "
        f"{len(names)} sitemap files advertised."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
