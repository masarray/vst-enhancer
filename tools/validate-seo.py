#!/usr/bin/env python3
"""Validate indexability, localization and sitemap safety for every public SEO page."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://masarray.github.io/vst-enhancer/"
PAGES = {
    ROOT: ("site/index.html", "en", ROOT, ROOT + "id/"),
    ROOT + "id/": ("site/id/index.html", "id", ROOT, ROOT + "id/"),
    ROOT + "guide/": ("site/guide/index.html", "en", ROOT + "guide/", ROOT + "id/guide/"),
    ROOT + "id/guide/": ("site/id/guide/index.html", "id", ROOT + "guide/", ROOT + "id/guide/"),
    ROOT + "activation/": (
        "site/activation/index.html",
        "en",
        ROOT + "activation/",
        ROOT + "id/activation/",
    ),
    ROOT + "id/activation/": (
        "site/id/activation/index.html",
        "id",
        ROOT + "activation/",
        ROOT + "id/activation/",
    ),
}
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def read(path: Path) -> str:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM is forbidden: {path}")
    text = raw.decode("utf-8")
    require(bool(text.strip()), f"Empty file: {path}")
    return text


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.title = ""
        self.description = ""
        self.robots: list[str] = []
        self.canonical: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.h1 = 0
        self.refresh = False
        self.json_ld: list[str] = []
        self._title = False
        self._json = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "").lower()
        elif tag == "title":
            self._title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta":
            name = data.get("name", "").lower()
            if name == "description":
                self.description = data.get("content", "").strip()
            elif name in {"robots", "googlebot"}:
                self.robots.append(data.get("content", ""))
            elif data.get("http-equiv", "").lower() == "refresh":
                self.refresh = True
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json, self._chunks = True, []

    def handle_data(self, data) -> None:
        if self._title:
            self.title += data
        if self._json:
            self._chunks.append(data)

    def handle_endtag(self, tag) -> None:
        if tag == "title":
            self._title = False
        elif tag == "script" and self._json:
            self.json_ld.append("".join(self._chunks).strip())
            self._json, self._chunks = False, []


def validate_page(root: Path, url: str, spec: tuple[str, str, str, str]) -> None:
    relative, language, en_url, id_url = spec
    parser = Page()
    parser.feed(read(root / relative))

    require(parser.lang == language, f"lang mismatch: {url}")
    require(30 <= len(parser.title.strip()) <= 75, f"title problem: {url}")
    require(70 <= len(parser.description) <= 220, f"description problem: {url}")
    require(parser.h1 == 1 and not parser.refresh, f"H1/refresh problem: {url}")
    require(len(parser.robots) == 1, f"robots meta count problem: {url}")

    directives = {part.strip().lower() for part in parser.robots[0].split(",") if part.strip()}
    require({"index", "follow"}.issubset(directives), f"not indexable: {url}")
    require("noindex" not in directives and "nofollow" not in directives, f"blocked: {url}")
    require(parser.canonical == [url], f"canonical mismatch: {url}")
    require(
        parser.hreflang == {"en": en_url, "id": id_url, "x-default": en_url},
        f"hreflang mismatch: {url}",
    )

    for payload in parser.json_ld:
        if payload:
            json.loads(payload)


def validate_sitemaps(root: Path) -> None:
    xml = read(root / "site/sitemap.xml")
    require(xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'), "bad XML declaration")
    tree = ElementTree.fromstring(xml)
    require(tree.tag == f"{{{NS}}}urlset", "bad sitemap root")

    locs = [
        node.findtext(f"{{{NS}}}loc", "").strip()
        for node in tree.findall(f"{{{NS}}}url")
    ]
    expected = list(PAGES)
    require(locs == expected and len(locs) == len(set(locs)), "sitemap.xml URL mismatch")

    for node in tree.findall(f"{{{NS}}}url"):
        lastmod = node.findtext(f"{{{NS}}}lastmod", "").strip()
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", lastmod) is not None, "bad lastmod")

    text_urls = [line.strip() for line in read(root / "site/sitemap.txt").splitlines() if line.strip()]
    require(text_urls == expected, "sitemap.txt URL mismatch")

    robots = read(root / "site/robots.txt")
    require(
        "User-agent: *" in robots
        and "Allow: /" in robots
        and "Disallow: /" not in robots,
        "robots.txt blocks crawling",
    )
    require(
        f"Sitemap: {ROOT}sitemap.xml" in robots
        and f"Sitemap: {ROOT}sitemap.txt" in robots,
        "sitemap discovery missing",
    )


def validate_runtime_safety(root: Path) -> None:
    locale_loader = read(root / "site/site-v6.js")
    activation_runtime = read(root / "site/activation/activation.js")

    for forbidden in (
        "location.replace(",
        "location.assign(",
        "navigator.languages",
        "resolvedOptions().timeZone",
        "detectedIndonesia",
    ):
        require(forbidden not in locale_loader, f"automatic locale redirect returned: {forbidden}")

    for forbidden in (
        'meta[name="robots"]',
        "noindex",
        "setMetadataForCheckout",
        "document.title =",
        "data-lang-button",
    ):
        require(forbidden not in activation_runtime, f"dynamic SEO mutation returned: {forbidden}")

    require("site-v6-core.js" in locale_loader, "locale loader no longer loads site-v6-core.js")
    require("data-site-base" in read(root / "site/activation/index.html"), "EN activation lacks site base")
    require("data-site-base" in read(root / "site/id/activation/index.html"), "ID activation lacks site base")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        for url, spec in PAGES.items():
            validate_page(root, url, spec)
        validate_sitemaps(root)
        validate_runtime_safety(root)
    except (AssertionError, UnicodeDecodeError, ElementTree.ParseError, json.JSONDecodeError) as exc:
        print(f"[FAIL] SEO validation: {exc}")
        return 1

    print(
        "[PASS] Six canonical pages are indexable; localization, runtime behavior, "
        "robots and both sitemap formats are consistent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
