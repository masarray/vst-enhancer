#!/usr/bin/env python3
"""Verify the deployed ArSonKuPik GitHub Pages SEO and release contract."""
from __future__ import annotations

import argparse
import json
import re
import struct
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from xml.etree import ElementTree

ROOT = "https://masarray.github.io/vst-enhancer/"
SOCIAL_PAGE = ROOT + "assets/arsonkupik-guide-social-1200x630.png"
SOCIAL_RAW = (
    "https://raw.githubusercontent.com/masarray/vst-enhancer/main/"
    "site/assets/arsonkupik-guide-social-1200x630.png"
)
SOCIAL_ALLOWED = {SOCIAL_PAGE, SOCIAL_RAW}
WEBSITE_ID = ROOT + "#website"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
PAGES = [
    (ROOT, "en", ROOT, ROOT + "id/", {"WebSite", "WebPage", "SoftwareApplication"}),
    (ROOT + "id/", "id", ROOT, ROOT + "id/", {"WebPage", "SoftwareApplication"}),
    (ROOT + "guide/", "en", ROOT + "guide/", ROOT + "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/guide/", "id", ROOT + "guide/", ROOT + "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "activation/", "en", ROOT + "activation/", ROOT + "id/activation/", {"WebPage"}),
    (ROOT + "id/activation/", "id", ROOT + "activation/", ROOT + "id/activation/", {"WebPage"}),
    (ROOT + "about/", "en", ROOT + "about/", ROOT + "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/about/", "id", ROOT + "about/", ROOT + "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    (ROOT + "measurements/", "en", ROOT + "measurements/", ROOT + "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/measurements/", "id", ROOT + "measurements/", ROOT + "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "audio-comparisons/", "en", ROOT + "audio-comparisons/", ROOT + "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/audio-comparisons/", "id", ROOT + "audio-comparisons/", ROOT + "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "use-cases/windows-system-audio/", "en", ROOT + "use-cases/windows-system-audio/", ROOT + "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/use-cases/windows-system-audio/", "id", ROOT + "use-cases/windows-system-audio/", ROOT + "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Unexpected redirect", headers, fp)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.h1 = 0
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.props: dict[str, list[str]] = defaultdict(list)
        self.canonical: list[str] = []
        self.sitemap: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.json_ld: list[object] = []
        self._json = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        data = {key.lower(): value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "").lower()
        elif tag == "h1":
            self.h1 += 1
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
                self.sitemap.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
        elif tag == "script" and data.get("type", "").lower() == "application/ld+json":
            self._json = True
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._json:
            self._chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json:
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


def node_types(payloads: list[object]) -> Counter[str]:
    result: Counter[str] = Counter()
    for payload in payloads:
        for node in walk_json(payload):
            value = node.get("@type")
            if isinstance(value, str):
                result[value] += 1
            elif isinstance(value, list):
                result.update(item for item in value if isinstance(item, str))
    return result


def nodes_of_type(payloads: list[object], target: str) -> list[dict]:
    result: list[dict] = []
    for payload in payloads:
        for node in walk_json(payload):
            value = node.get("@type")
            values = {value} if isinstance(value, str) else set(value or [])
            if target in values:
                result.append(node)
    return result


def one(values: list[str], label: str, url: str) -> str:
    if len(values) != 1:
        raise AssertionError(f"{label} count is {len(values)}: {url}")
    return values[0].strip()


def get(opener, url: str, accept: str = "text/html,*/*;q=0.8") -> tuple[dict[str, str], bytes]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ArSonKuPik-SEO-Release-Gate/3.0",
            "Accept": accept,
            "Cache-Control": "no-cache",
        },
    )
    with opener.open(request, timeout=25) as response:
        if response.status != 200:
            raise AssertionError(f"{url} returned HTTP {response.status}")
        return {key.lower(): value for key, value in response.headers.items()}, response.read()


def verify_pages(opener) -> set[str]:
    global_types: Counter[str] = Counter()
    social_urls: set[str] = set()
    for url, language, en_url, id_url, required_types in PAGES:
        headers, raw = get(opener, url)
        x_robots = headers.get("x-robots-tag", "").lower()
        if "noindex" in x_robots or "nofollow" in x_robots:
            raise AssertionError(f"blocked X-Robots-Tag: {url}")
        page = Page()
        page.feed(raw.decode("utf-8"))
        if page.lang != language:
            raise AssertionError(f"lang mismatch: {url}")
        if page.h1 != 1:
            raise AssertionError(f"{url} has {page.h1} H1 elements")
        robots = one(page.meta.get("robots", []) + page.meta.get("googlebot", []), "robots meta", url)
        directives = {part.strip().lower() for part in robots.split(",") if part.strip()}
        if not {"index", "follow"}.issubset(directives) or {"noindex", "nofollow"} & directives:
            raise AssertionError(f"blocked robots directives: {url} {sorted(directives)}")
        if page.canonical != [url]:
            raise AssertionError(f"canonical mismatch: {url} {page.canonical}")
        if page.sitemap != [ROOT + "sitemap.xml"]:
            raise AssertionError(f"sitemap link mismatch: {url}")
        if page.hreflang != {"en": en_url, "id": id_url, "x-default": en_url}:
            raise AssertionError(f"hreflang mismatch: {url} {page.hreflang}")
        if one(page.props.get("og:url", []), "og:url", url) != url:
            raise AssertionError(f"og:url mismatch: {url}")
        social_image = one(page.props.get("og:image", []), "og:image", url)
        if social_image not in SOCIAL_ALLOWED:
            raise AssertionError(f"og:image mismatch: {url} {social_image}")
        if one(page.props.get("og:image:width", []), "og:image:width", url) != "1200":
            raise AssertionError(f"og:image:width mismatch: {url}")
        if one(page.props.get("og:image:height", []), "og:image:height", url) != "630":
            raise AssertionError(f"og:image:height mismatch: {url}")
        social_urls.add(social_image)
        for key in ("og:title", "og:description", "og:image:alt"):
            if not one(page.props.get(key, []), key, url):
                raise AssertionError(f"empty {key}: {url}")
        if one(page.meta.get("twitter:card", []), "twitter:card", url) != "summary_large_image":
            raise AssertionError(f"twitter:card mismatch: {url}")
        if one(page.meta.get("twitter:image", []), "twitter:image", url) != social_image:
            raise AssertionError(f"twitter:image mismatch: {url}")
        for key in ("twitter:title", "twitter:description", "twitter:image:alt"):
            if not one(page.meta.get(key, []), key, url):
                raise AssertionError(f"empty {key}: {url}")
        types = node_types(page.json_ld)
        global_types.update(types)
        if not required_types.issubset(types):
            raise AssertionError(f"schema missing at {url}: expected {sorted(required_types)}, got {sorted(types)}")
        for node in nodes_of_type(page.json_ld, "WebPage"):
            is_part_of = node.get("isPartOf")
            if not isinstance(is_part_of, dict) or is_part_of.get("@id") != WEBSITE_ID:
                raise AssertionError(f"WebPage isPartOf mismatch: {url}")
    if global_types["WebSite"] != 1:
        raise AssertionError(f"expected one WebSite entity, got {global_types['WebSite']}")
    return social_urls


def verify_discovery(opener) -> None:
    _, robots_raw = get(opener, ROOT + "robots.txt", "text/plain,*/*;q=0.8")
    robots = robots_raw.decode("utf-8")
    if "User-agent: *" not in robots or "Allow: /" not in robots or "Disallow: /" in robots:
        raise AssertionError("robots.txt blocks crawling")
    for sitemap in (ROOT + "sitemap.xml", ROOT + "sitemap.txt"):
        if f"Sitemap: {sitemap}" not in robots:
            raise AssertionError(f"robots.txt does not advertise {sitemap}")

    _, sitemap_raw = get(opener, ROOT + "sitemap.xml", "application/xml,text/xml,*/*;q=0.8")
    tree = ElementTree.fromstring(sitemap_raw.decode("utf-8"))
    if tree.tag != f"{{{NS}}}urlset":
        raise AssertionError(f"Unexpected sitemap root: {tree.tag}")
    items = tree.findall(f"{{{NS}}}url")
    locs = [item.findtext(f"{{{NS}}}loc", "").strip() for item in items]
    expected = [spec[0] for spec in PAGES]
    if locs != expected:
        raise AssertionError(f"Live sitemap URL mismatch: {locs}")
    for item in items:
        value = item.findtext(f"{{{NS}}}lastmod", "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            raise AssertionError(f"Invalid sitemap lastmod: {value}")
        date.fromisoformat(value)

    _, text_raw = get(opener, ROOT + "sitemap.txt", "text/plain,*/*;q=0.8")
    text_urls = [line.strip() for line in text_raw.decode("utf-8").splitlines() if line.strip()]
    if text_urls != expected:
        raise AssertionError(f"Live text sitemap URL mismatch: {text_urls}")


def verify_release(opener, expected_version: str) -> None:
    _, raw = get(opener, ROOT + "release.json", "application/json,*/*;q=0.8")
    payload = json.loads(raw.decode("utf-8"))
    if payload.get("version") != expected_version:
        raise AssertionError(f"Live release version is {payload.get('version')!r}, expected {expected_version!r}")
    if payload.get("schemaVersion", 0) < 3 or payload.get("distributionEnabled") is not True:
        raise AssertionError("Live release manifest is disabled or obsolete")
    platforms = set(payload.get("platforms") or [])
    if not {"windows-x64", "macos-universal"}.issubset(platforms):
        raise AssertionError(f"Live release manifest is not cross-platform: {sorted(platforms)}")
    expected_url = f"https://github.com/masarray/vst-enhancer/releases/tag/{expected_version}"
    if payload.get("releaseUrl") != expected_url:
        raise AssertionError("Live releaseUrl/version mismatch")


def verify_social_image(url: str) -> None:
    opener = urllib.request.build_opener()
    headers, raw = get(opener, url, "image/png,*/*;q=0.8")
    content_type = headers.get("content-type", "").lower()
    if "image/png" not in content_type:
        raise AssertionError(f"Social image content type is {content_type!r}")
    if len(raw) <= 10_000 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise AssertionError("Social image is not a valid PNG")
    width, height, bit_depth, colour_type = struct.unpack(">IIBB", raw[16:26])
    if (width, height) != (1200, 630) or bit_depth != 8 or colour_type not in {2, 6}:
        raise AssertionError(f"Unexpected social PNG format: {width}x{height}, depth={bit_depth}, type={colour_type}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--attempts", type=int, default=18)
    parser.add_argument("--delay-seconds", type=float, default=10.0)
    args = parser.parse_args()

    site_opener = urllib.request.build_opener(NoRedirect())
    last_error: Exception | None = None
    for attempt in range(1, args.attempts + 1):
        try:
            social_urls = verify_pages(site_opener)
            verify_discovery(site_opener)
            verify_release(site_opener, args.expected_version)
            for social_url in sorted(social_urls):
                verify_social_image(social_url)
        except (
            AssertionError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ElementTree.ParseError,
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            struct.error,
        ) as exc:
            last_error = exc
            if attempt == args.attempts:
                break
            print(f"[WAIT] Live SEO verification attempt {attempt}/{args.attempts} did not pass yet: {exc}")
            time.sleep(args.delay_seconds)
            continue
        print(
            "[PASS] Live GitHub Pages serves 14 non-redirecting canonical pages with "
            "P0 runtime/indexing safety and P1/P2 metadata, schema, discovery, social-image "
            "and release-version contracts."
        )
        return 0

    print(f"[FAIL] Live SEO verification did not converge: {last_error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
