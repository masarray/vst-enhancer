#!/usr/bin/env python3
"""Validate the Global Discovery P1 search-intent cluster without weakening P0 SEO gates."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://arsonkupik.pages.dev/"
SOCIAL = ROOT + "assets/arsonkupik-guide-social-1200x630.png"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

PAGES = [
    ("stereo-enhancer-vst3/", "site/stereo-enhancer-vst3/index.html", "en", "stereo-enhancer-vst3/", "id/stereo-enhancer-vst3/"),
    ("id/stereo-enhancer-vst3/", "site/id/stereo-enhancer-vst3/index.html", "id", "stereo-enhancer-vst3/", "id/stereo-enhancer-vst3/"),
    ("vocal-enhancer-vst3/", "site/vocal-enhancer-vst3/index.html", "en", "vocal-enhancer-vst3/", "id/vocal-enhancer-vst3/"),
    ("id/vocal-enhancer-vst3/", "site/id/vocal-enhancer-vst3/index.html", "id", "vocal-enhancer-vst3/", "id/vocal-enhancer-vst3/"),
    ("mix-bus-enhancer/", "site/mix-bus-enhancer/index.html", "en", "mix-bus-enhancer/", "id/mix-bus-enhancer/"),
    ("id/mix-bus-enhancer/", "site/id/mix-bus-enhancer/index.html", "id", "mix-bus-enhancer/", "id/mix-bus-enhancer/"),
    ("mastering-audio-enhancer/", "site/mastering-audio-enhancer/index.html", "en", "mastering-audio-enhancer/", "id/mastering-audio-enhancer/"),
    ("id/mastering-audio-enhancer/", "site/id/mastering-audio-enhancer/index.html", "id", "mastering-audio-enhancer/", "id/mastering-audio-enhancer/"),
]

DISCOVERY_URLS = [ROOT + spec[0] for spec in PAGES]
EN_ROUTES = [spec[0] for spec in PAGES if spec[2] == "en"]
ID_ROUTES = [spec[0] for spec in PAGES if spec[2] == "id"]


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
        self.h1 = 0
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.props: dict[str, list[str]] = defaultdict(list)
        self.canonical: list[str] = []
        self.sitemaps: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.json_ld: list[object] = []
        self.hrefs: list[str] = []
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
        elif tag == "a" and data.get("href"):
            self.hrefs.append(data["href"])
        elif tag == "meta":
            if data.get("name"):
                self.meta[data["name"].lower()].append(data.get("content", ""))
            if data.get("property"):
                self.props[data["property"].lower()].append(data.get("content", ""))
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
            if "sitemap" in rel:
                self.sitemaps.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json = True
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._title:
            self.title += data
        if self._json:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._title = False
        elif tag == "script" and self._json:
            raw = "".join(self._chunks).strip()
            self._json = False
            self._chunks = []
            if raw:
                self.json_ld.append(json.loads(raw))


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def schema_types(payloads: list[object]) -> Counter[str]:
    result: Counter[str] = Counter()
    for payload in payloads:
        for node in walk_json(payload):
            value = node.get("@type")
            if isinstance(value, str):
                result[value] += 1
            elif isinstance(value, list):
                result.update(v for v in value if isinstance(v, str))
    return result


def one(values: list[str], label: str, url: str) -> str:
    require(len(values) == 1, f"{label} count is {len(values)}: {url}")
    return values[0].strip()


def validate_page(root: Path, spec, titles: set[str]) -> None:
    route, relative, language, en_route, id_route = spec
    url = ROOT + route
    text = read(root / relative)
    require(len(text) >= 4500, f"Discovery page is too thin: {url}")

    page = Page()
    page.feed(text)
    require(page.lang == language, f"lang mismatch: {url}")
    require(page.h1 == 1, f"H1 count is {page.h1}: {url}")

    title = page.title.strip()
    require(30 <= len(title) <= 78, f"title length problem ({len(title)}): {url}")
    require(title not in titles, f"duplicate title: {title}")
    titles.add(title)

    description = one(page.meta.get("description", []), "description", url)
    require(70 <= len(description) <= 230, f"description length problem ({len(description)}): {url}")
    robots = one(page.meta.get("robots", []), "robots", url).lower()
    require("index" in robots and "follow" in robots and "noindex" not in robots, f"indexability problem: {url}")

    require(page.canonical == [url], f"canonical mismatch: {url} {page.canonical}")
    require(page.sitemaps == [ROOT + "sitemap.xml"], f"site sitemap link mismatch: {url}")
    require(page.hreflang == {
        "en": ROOT + en_route,
        "id": ROOT + id_route,
        "x-default": ROOT + en_route,
    }, f"hreflang mismatch: {url} {page.hreflang}")

    require(one(page.props.get("og:url", []), "og:url", url) == url, f"og:url mismatch: {url}")
    require(one(page.props.get("og:image", []), "og:image", url) == SOCIAL, f"og:image mismatch: {url}")
    require(one(page.meta.get("twitter:image", []), "twitter:image", url) == SOCIAL, f"twitter:image mismatch: {url}")

    types = schema_types(page.json_ld)
    require({"TechArticle", "WebPage", "BreadcrumbList"}.issubset(types), f"required schema missing: {url} {sorted(types)}")
    require("FAQPage" not in types, f"unsupported FAQ rich-result markup added: {url}")
    require("aggregateRating" not in text and '"review"' not in text.lower(), f"unearned review/rating schema added: {url}")

    official_downloads = [href for href in page.hrefs if href.startswith("https://github.com/masarray/vst-enhancer/releases")]
    require(official_downloads, f"official download CTA missing: {url}")
    require(any("audio-comparisons" in href or "measurements" in href for href in page.hrefs), f"evidence link missing: {url}")

    sibling_hits = 0
    sibling_routes = ID_ROUTES if language == "id" else EN_ROUTES
    for sibling in sibling_routes:
        if sibling == route:
            continue
        leaf = sibling.removeprefix("id/")
        if any(leaf in href for href in page.hrefs):
            sibling_hits += 1
    require(sibling_hits >= 2, f"discovery cluster is weakly linked ({sibling_hits} siblings): {url}")

    lower = re.sub(r"\s+", " ", text.lower())
    for forbidden in ("#1 vst", "number one vst", "guaranteed professional", "guaranteed mastering"):
        require(forbidden not in lower, f"unsupported hype claim returned ({forbidden}): {url}")


def validate_discovery_sitemaps(root: Path) -> None:
    xml = read(root / "site/sitemap-discovery.xml")
    tree = ElementTree.fromstring(xml)
    require(tree.tag == f"{{{NS}}}urlset", "bad discovery sitemap root")
    items = tree.findall(f"{{{NS}}}url")
    locs = [item.findtext(f"{{{NS}}}loc", "").strip() for item in items]
    require(locs == DISCOVERY_URLS and len(locs) == len(set(locs)), "discovery sitemap URL mismatch")
    for item in items:
        value = item.findtext(f"{{{NS}}}lastmod", "").strip()
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None, f"bad discovery lastmod: {value}")
        date.fromisoformat(value)

    txt = [line.strip() for line in read(root / "site/sitemap-discovery.txt").splitlines() if line.strip()]
    require(txt == DISCOVERY_URLS, "discovery text sitemap URL mismatch")

    robots = read(root / "site/robots.txt")
    require(f"Sitemap: {ROOT}sitemap-discovery.xml" in robots, "robots lacks discovery XML sitemap")
    require(f"Sitemap: {ROOT}sitemap-discovery.txt" in robots, "robots lacks discovery text sitemap")


def validate_headers(root: Path) -> None:
    headers = read(root / "site/_headers")
    for url in DISCOVERY_URLS:
        require(url in headers, f"_headers lacks discovery URL: {url}")
        require(f'Link: <{url}>; rel="canonical"' in headers, f"_headers lacks canonical Link for {url}")
    require("X-Robots-Tag: index" not in headers, "_headers must not override Cloudflare preview noindex")


def validate_hubs(root: Path) -> None:
    en = read(root / "site/about/index.html")
    id_text = read(root / "site/id/about/index.html")
    for route in EN_ROUTES:
        require(f'../{route}' in en, f"EN About hub lacks {route}")
    for route in ID_ROUTES:
        local = route.removeprefix("id/")
        require(f'../{local}' in id_text, f"ID About hub lacks {route}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    titles: set[str] = set()
    for spec in PAGES:
        validate_page(root, spec, titles)
    validate_discovery_sitemaps(root)
    validate_headers(root)
    validate_hubs(root)
    print(f"[PASS] Global Discovery P1 validates {len(PAGES)} intent pages, bilingual hreflang pairs, discovery sitemaps, canonical headers, evidence links and About hubs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
