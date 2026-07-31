#!/usr/bin/env python3
"""Fail fast when public ArSonKuPik pages become non-indexable or SEO signals drift."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://masarray.github.io/vst-enhancer/"
PAGES = {
    ROOT: ("site/index.html", "en", ROOT, ROOT + "id/"),
    ROOT + "id/": ("site/id/index.html", "id", ROOT, ROOT + "id/"),
    ROOT + "guide/": ("site/guide/index.html", "en", ROOT + "guide/", ROOT + "id/guide/"),
    ROOT + "id/guide/": ("site/id/guide/index.html", "id", ROOT + "guide/", ROOT + "id/guide/"),
}
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@dataclass
class SeoPage(HTMLParser):
    lang: str = ""
    title: str = ""
    description: str = ""
    robots: list[str] = field(default_factory=list)
    canonical: list[str] = field(default_factory=list)
    hreflang: dict[str, str] = field(default_factory=dict)
    h1_count: int = 0
    meta_refresh: bool = False
    json_ld: list[str] = field(default_factory=list)
    _in_title: bool = False
    _in_json_ld: bool = False
    _json_chunks: list[str] = field(default_factory=list)

    def handle_starttag(self, tag: str, attrs) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "").lower()
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta":
            name = data.get("name", "").lower()
            http_equiv = data.get("http-equiv", "").lower()
            if name == "description":
                self.description = data.get("content", "").strip()
            elif name in {"robots", "googlebot"}:
                self.robots.append(data.get("content", ""))
            elif http_equiv == "refresh":
                self.meta_refresh = True
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_json_ld:
            self._json_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_json_ld:
            self.json_ld.append("".join(self._json_chunks).strip())
            self._in_json_ld = False
            self._json_chunks = []


def read_utf8(path: Path) -> str:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM is not allowed: {path}")
    text = raw.decode("utf-8")
    require(bool(text.strip()), f"File is empty: {path}")
    return text


def parse_page(path: Path) -> SeoPage:
    parser = SeoPage()
    parser.feed(read_utf8(path))
    return parser


def validate_html(root: Path) -> None:
    for url, (relative_path, language, english_url, indonesian_url) in PAGES.items():
        path = root / relative_path
        require(path.is_file(), f"Missing indexable page: {relative_path}")
        page = parse_page(path)

        require(page.lang == language, f"Wrong html lang on {url}: {page.lang!r}")
        require(page.title.strip(), f"Missing title on {url}")
        require(35 <= len(page.title.strip()) <= 75, f"Title length is weak on {url}: {len(page.title.strip())}")
        require(70 <= len(page.description) <= 220, f"Description length is weak on {url}: {len(page.description)}")
        require(page.h1_count == 1, f"Expected exactly one H1 on {url}, found {page.h1_count}")
        require(not page.meta_refresh, f"Meta refresh is forbidden on indexable page: {url}")

        require(len(page.robots) == 1, f"Expected one robots meta tag on {url}, found {len(page.robots)}")
        directives = {token.strip().lower() for token in page.robots[0].split(",") if token.strip()}
        require("index" in directives and "follow" in directives, f"Missing index,follow on {url}: {sorted(directives)}")
        require("noindex" not in directives and "nofollow" not in directives, f"Blocking robots directive on {url}: {sorted(directives)}")

        require(page.canonical == [url], f"Canonical mismatch on {url}: {page.canonical}")
        require("?" not in url and "#" not in url, f"Canonical URL must be clean: {url}")
        expected_hreflang = {"en": english_url, "id": indonesian_url, "x-default": english_url}
        require(page.hreflang == expected_hreflang, f"hreflang mismatch on {url}: {page.hreflang}")

        for payload in page.json_ld:
            if payload:
                json.loads(payload)


def validate_sitemaps(root: Path) -> None:
    xml_path = root / "site/sitemap.xml"
    xml_text = read_utf8(xml_path)
    require(xml_text.startswith('<?xml version="1.0" encoding="UTF-8"?>'), "sitemap.xml must start with a UTF-8 XML declaration")
    tree = ElementTree.fromstring(xml_text)
    require(tree.tag == f"{{{SITEMAP_NS}}}urlset", f"Unexpected sitemap root: {tree.tag}")

    locs = [item.findtext(f"{{{SITEMAP_NS}}}loc", default="").strip() for item in tree.findall(f"{{{SITEMAP_NS}}}url")]
    expected = list(PAGES)
    require(locs == expected, f"sitemap.xml URLs differ from the canonical page set: {locs}")
    require(len(locs) == len(set(locs)), "sitemap.xml contains duplicate URLs")

    for item in tree.findall(f"{{{SITEMAP_NS}}}url"):
        lastmod = item.findtext(f"{{{SITEMAP_NS}}}lastmod", default="").strip()
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod) is not None, f"Invalid lastmod: {lastmod!r}")

    text_urls = [line.strip() for line in read_utf8(root / "site/sitemap.txt").splitlines() if line.strip()]
    require(text_urls == expected, f"sitemap.txt URLs differ from sitemap.xml: {text_urls}")

    robots = read_utf8(root / "site/robots.txt")
    require(re.search(r"(?im)^User-agent:\s*\*$", robots) is not None, "robots.txt is missing User-agent: *")
    require(re.search(r"(?im)^Allow:\s*/$", robots) is not None, "robots.txt must allow crawling")
    require("Disallow: /" not in robots, "robots.txt blocks the public site")
    require(f"Sitemap: {ROOT}sitemap.xml" in robots, "robots.txt is missing sitemap.xml")
    require(f"Sitemap: {ROOT}sitemap.txt" in robots, "robots.txt is missing sitemap.txt")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        validate_html(root)
        validate_sitemaps(root)
    except (AssertionError, UnicodeDecodeError, ElementTree.ParseError, json.JSONDecodeError) as exc:
        print(f"[FAIL] SEO validation: {exc}")
        return 1
    print("[PASS] Four canonical pages are indexable; robots, canonicals, hreflang and both sitemaps are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
