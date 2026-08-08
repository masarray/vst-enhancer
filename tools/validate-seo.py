#!/usr/bin/env python3
"""Validate the complete ArSonKuPik on-site SEO and release-safety contract."""
from __future__ import annotations

import json
import re
import struct
from collections import Counter, defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://arsonkupik.pages.dev/"
SOCIAL = ROOT + "assets/arsonkupik-guide-social-1200x630.png"
WEBSITE_ID = ROOT + "#website"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

PAGES = [
    (ROOT, "site/index.html", "en", ROOT, ROOT + "id/", {"WebSite", "WebPage", "SoftwareApplication"}),
    (ROOT + "id/", "site/id/index.html", "id", ROOT, ROOT + "id/", {"WebPage", "SoftwareApplication"}),
    (ROOT + "guide/", "site/guide/index.html", "en", ROOT + "guide/", ROOT + "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/guide/", "site/id/guide/index.html", "id", ROOT + "guide/", ROOT + "id/guide/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "activation/", "site/activation/index.html", "en", ROOT + "activation/", ROOT + "id/activation/", {"WebPage"}),
    (ROOT + "id/activation/", "site/id/activation/index.html", "id", ROOT + "activation/", ROOT + "id/activation/", {"WebPage"}),
    (ROOT + "about/", "site/about/index.html", "en", ROOT + "about/", ROOT + "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/about/", "site/id/about/index.html", "id", ROOT + "about/", ROOT + "id/about/", {"AboutPage", "WebPage", "BreadcrumbList"}),
    (ROOT + "measurements/", "site/measurements/index.html", "en", ROOT + "measurements/", ROOT + "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/measurements/", "site/id/measurements/index.html", "id", ROOT + "measurements/", ROOT + "id/measurements/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "audio-comparisons/", "site/audio-comparisons/index.html", "en", ROOT + "audio-comparisons/", ROOT + "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/audio-comparisons/", "site/id/audio-comparisons/index.html", "id", ROOT + "audio-comparisons/", ROOT + "id/audio-comparisons/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "use-cases/windows-system-audio/", "site/use-cases/windows-system-audio/index.html", "en", ROOT + "use-cases/windows-system-audio/", ROOT + "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    (ROOT + "id/use-cases/windows-system-audio/", "site/id/use-cases/windows-system-audio/index.html", "id", ROOT + "use-cases/windows-system-audio/", ROOT + "id/use-cases/windows-system-audio/", {"TechArticle", "WebPage", "BreadcrumbList"}),
]


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
        self.refresh = False
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.props: dict[str, list[str]] = defaultdict(list)
        self.canonical: list[str] = []
        self.sitemap: list[str] = []
        self.stylesheets: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.json_ld: list[object] = []
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
            if data.get("http-equiv", "").lower() == "refresh":
                self.refresh = True
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
            if "stylesheet" in rel:
                self.stylesheets.append(data.get("href", ""))
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
    found: list[dict] = []
    for payload in payloads:
        for node in walk_json(payload):
            value = node.get("@type")
            values = {value} if isinstance(value, str) else set(value or [])
            if target in values:
                found.append(node)
    return found


def one(values: list[str], label: str, url: str) -> str:
    require(len(values) == 1, f"{label} count is {len(values)}: {url}")
    return values[0].strip()


def validate_page(root: Path, spec, global_types: Counter[str]) -> None:
    url, relative, language, en_url, id_url, required_types = spec
    parser = Page()
    parser.feed(read(root / relative))

    require(parser.lang == language, f"lang mismatch: {url}")
    require(30 <= len(parser.title.strip()) <= 78, f"title problem: {url}")
    description = one(parser.meta.get("description", []), "description meta", url)
    require(70 <= len(description) <= 230, f"description problem: {url}")
    require(parser.h1 == 1 and not parser.refresh, f"H1/refresh problem: {url}")

    robots = one(parser.meta.get("robots", []) + parser.meta.get("googlebot", []), "robots meta", url)
    directives = {part.strip().lower() for part in robots.split(",") if part.strip()}
    require({"index", "follow"}.issubset(directives), f"not indexable: {url}")
    require("noindex" not in directives and "nofollow" not in directives, f"blocked: {url}")

    require(parser.canonical == [url], f"canonical mismatch: {url}")
    require(parser.sitemap == [ROOT + "sitemap.xml"], f"sitemap link mismatch: {url}")
    require(
        parser.hreflang == {"en": en_url, "id": id_url, "x-default": en_url},
        f"hreflang mismatch: {url}",
    )

    expected_props = {
        "og:url": url,
        "og:image": SOCIAL,
        "og:image:width": "1200",
        "og:image:height": "630",
    }
    for key, expected in expected_props.items():
        require(one(parser.props.get(key, []), key, url) == expected, f"{key} mismatch: {url}")
    for key in ("og:title", "og:description", "og:image:alt", "og:site_name", "og:locale"):
        require(bool(one(parser.props.get(key, []), key, url)), f"empty {key}: {url}")

    expected_meta = {
        "twitter:card": "summary_large_image",
        "twitter:image": SOCIAL,
    }
    for key, expected in expected_meta.items():
        require(one(parser.meta.get(key, []), key, url) == expected, f"{key} mismatch: {url}")
    for key in ("twitter:title", "twitter:description", "twitter:image:alt"):
        require(bool(one(parser.meta.get(key, []), key, url)), f"empty {key}: {url}")

    types = node_types(parser.json_ld)
    global_types.update(types)
    require(required_types.issubset(types), f"schema {sorted(required_types)} missing at {url}; got {sorted(types)}")

    for node in nodes_of_type(parser.json_ld, "WebPage"):
        is_part_of = node.get("isPartOf")
        require(
            isinstance(is_part_of, dict) and is_part_of.get("@id") == WEBSITE_ID,
            f"WebPage isPartOf mismatch: {url}",
        )


def validate_sitemaps(root: Path) -> None:
    raw = read(root / "site/sitemap.xml")
    require(re.match(r"^<\?xml\s+version=['\"]1\.0['\"]\s+encoding=['\"]utf-8['\"]\?>", raw, re.I) is not None, "bad XML declaration")
    tree = ElementTree.fromstring(raw)
    require(tree.tag == f"{{{NS}}}urlset", "bad sitemap root")
    items = tree.findall(f"{{{NS}}}url")
    locs = [item.findtext(f"{{{NS}}}loc", "").strip() for item in items]
    expected = [spec[0] for spec in PAGES]
    require(locs == expected and len(locs) == len(set(locs)), "sitemap.xml URL mismatch")
    for item in items:
        value = item.findtext(f"{{{NS}}}lastmod", "").strip()
        require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None, f"bad lastmod: {value}")
        date.fromisoformat(value)

    text_urls = [line.strip() for line in read(root / "site/sitemap.txt").splitlines() if line.strip()]
    require(text_urls == expected, "sitemap.txt URL mismatch")

    robots = read(root / "site/robots.txt")
    require("User-agent: *" in robots and "Allow: /" in robots and "Disallow: /" not in robots, "robots.txt blocks crawling")
    require(f"Sitemap: {ROOT}sitemap.xml" in robots, "robots.txt lacks sitemap.xml")
    require(f"Sitemap: {ROOT}sitemap.txt" in robots, "robots.txt lacks sitemap.txt")


def validate_png(root: Path) -> None:
    path = root / "site/assets/arsonkupik-guide-social-1200x630.png"
    raw = path.read_bytes()
    require(len(raw) > 10_000, "social PNG is unexpectedly small")
    require(raw[:8] == b"\x89PNG\r\n\x1a\n", "social image is not PNG")
    require(raw[12:16] == b"IHDR", "social PNG lacks IHDR")
    width, height, bit_depth, colour_type = struct.unpack(">IIBB", raw[16:26])
    require((width, height) == (1200, 630), f"social PNG dimensions are {width}x{height}")
    require(bit_depth == 8 and colour_type in {2, 6}, "social PNG must be 8-bit RGB/RGBA")


def validate_activation_styles(root: Path) -> None:
    css = read(root / "site/seo-authority.css")
    for selector in (
        ".activation-page .language-switch a",
        ".activation-page .language-switch a[aria-current=\"page\"]",
    ):
        require(selector in css, f"activation language-switch styling missing: {selector}")


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


def validate_release(root: Path) -> None:
    payload = json.loads(read(root / "site/release.json"))
    version = payload.get("version")
    require(isinstance(version, str) and re.fullmatch(r"v\d+\.\d+\.\d+", version) is not None, "invalid release version")
    require(payload.get("schemaVersion", 0) >= 3, "release schemaVersion is too old")
    require(payload.get("distributionEnabled") is True, "public distribution is disabled")
    platforms = set(payload.get("platforms") or [])
    require({"windows-x64", "macos-universal"}.issubset(platforms), "release manifest is not cross-platform")
    release_url = payload.get("releaseUrl", "")
    require(release_url == f"https://github.com/masarray/vst-enhancer/releases/tag/{version}", "releaseUrl/version mismatch")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    global_types: Counter[str] = Counter()
    try:
        for spec in PAGES:
            validate_page(root, spec, global_types)
        require(global_types["WebSite"] == 1, f"expected one WebSite entity, got {global_types['WebSite']}")
        validate_sitemaps(root)
        validate_png(root)
        validate_activation_styles(root)
        validate_runtime_safety(root)
        validate_release(root)
    except (AssertionError, UnicodeDecodeError, ElementTree.ParseError, json.JSONDecodeError, ValueError, struct.error) as exc:
        print(f"[FAIL] SEO validation: {exc}")
        return 1

    print(
        "[PASS] 14 canonical pages satisfy P0 indexing/runtime guards and P1/P2 "
        "metadata, schema, social-image, sitemap and release contracts."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
