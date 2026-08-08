#!/usr/bin/env python3
"""Validate the Global Discovery P2 evidence and browser-tool contract."""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree

ROOT = "https://arsonkupik.pages.dev/"
SOCIAL = ROOT + "assets/arsonkupik-guide-social-1200x630.png"
KVR = "https://www.kvraudio.com/product/arsonkupik-by-sonkupik/details"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

PAGES = [
    ("site/evidence/index.html", "en", ROOT + "evidence/", ROOT + "evidence/", ROOT + "id/evidence/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("site/id/evidence/index.html", "id", ROOT + "id/evidence/", ROOT + "evidence/", ROOT + "id/evidence/", {"TechArticle", "WebPage", "BreadcrumbList"}),
    ("site/audio-test-signals/index.html", "en", ROOT + "audio-test-signals/", ROOT + "audio-test-signals/", ROOT + "id/audio-test-signals/", {"WebApplication", "WebPage", "BreadcrumbList"}),
    ("site/id/audio-test-signals/index.html", "id", ROOT + "id/audio-test-signals/", ROOT + "audio-test-signals/", ROOT + "id/audio-test-signals/", {"WebApplication", "WebPage", "BreadcrumbList"}),
]

EXPECTED_SITEMAP = {
    ROOT + "evidence/",
    ROOT + "id/evidence/",
    ROOT + "audio-test-signals/",
    ROOT + "id/audio-test-signals/",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def read(path: Path) -> str:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM is forbidden: {path}")
    return raw.decode("utf-8")


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.title = ""
        self.h1 = 0
        self.meta: dict[str, list[str]] = defaultdict(list)
        self.props: dict[str, list[str]] = defaultdict(list)
        self.canonical: list[str] = []
        self.hreflang: dict[str, str] = {}
        self.stylesheets: list[str] = []
        self.scripts: list[str] = []
        self.links: list[str] = []
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
            if data.get("name"):
                self.meta[data["name"].lower()].append(data.get("content", ""))
            if data.get("property"):
                self.props[data["property"].lower()].append(data.get("content", ""))
        elif tag == "link":
            rel = set(data.get("rel", "").lower().split())
            if "canonical" in rel:
                self.canonical.append(data.get("href", ""))
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"].lower()] = data.get("href", "")
            if "stylesheet" in rel:
                self.stylesheets.append(data.get("href", ""))
        elif tag == "script":
            if data.get("type", "").lower() == "application/ld+json":
                self._json = True
                self._chunks = []
            elif data.get("src"):
                self.scripts.append(data["src"])
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"])

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


def schema_types(page: Page) -> set[str]:
    result: set[str] = set()
    for payload in page.json_ld:
        for node in walk_json(payload):
            value = node.get("@type")
            if isinstance(value, str):
                result.add(value)
            elif isinstance(value, list):
                result.update(item for item in value if isinstance(item, str))
    return result


def parse(path: Path) -> Page:
    page = Page()
    page.feed(read(path))
    return page


def validate_pages(root: Path) -> None:
    titles: list[str] = []
    descriptions: list[str] = []
    forbidden = {"FAQPage", "Review", "AggregateRating", "VideoObject"}
    for filename, lang, canonical, en_url, id_url, required_types in PAGES:
        path = root / filename
        require(path.is_file(), f"Missing P2 page: {filename}")
        page = parse(path)
        titles.append(page.title.strip())
        desc = page.meta.get("description", [""])[0].strip()
        descriptions.append(desc)
        require(page.lang == lang, f"Wrong lang on {filename}: {page.lang}")
        require(page.h1 == 1, f"Expected one H1 on {filename}")
        require(35 <= len(page.title.strip()) <= 90, f"Title length is weak on {filename}")
        require(110 <= len(desc) <= 190, f"Meta description length is weak on {filename}")
        robots = " ".join(page.meta.get("robots", [])).lower()
        require("index" in robots and "follow" in robots, f"Page is not indexable: {filename}")
        require(page.canonical == [canonical], f"Canonical mismatch: {filename}")
        require(page.hreflang.get("en") == en_url, f"EN hreflang mismatch: {filename}")
        require(page.hreflang.get("id") == id_url, f"ID hreflang mismatch: {filename}")
        require(page.hreflang.get("x-default") == en_url, f"x-default mismatch: {filename}")
        require(page.props.get("og:url") == [canonical], f"og:url mismatch: {filename}")
        require(page.props.get("og:image") == [SOCIAL], f"og:image mismatch: {filename}")
        require(page.meta.get("twitter:card") == ["summary_large_image"], f"Twitter card mismatch: {filename}")
        require(page.meta.get("twitter:image") == [SOCIAL], f"Twitter image mismatch: {filename}")
        types = schema_types(page)
        require(required_types <= types, f"Missing schema types on {filename}: {required_types - types}")
        require(not (types & forbidden), f"Unsupported schema on {filename}: {types & forbidden}")
        require("evidence-p2.css" in " ".join(page.stylesheets), f"P2 stylesheet missing: {filename}")

    require(len(titles) == len(set(titles)), "P2 titles are not unique")
    require(len(descriptions) == len(set(descriptions)), "P2 descriptions are not unique")


def validate_evidence_pages(root: Path) -> None:
    en = read(root / "site/evidence/index.html")
    id_text = read(root / "site/id/evidence/index.html")
    for text, label in ((en, "EN evidence"), (id_text, "ID evidence")):
        lowered = text.lower()
        for needle in ("measurements/", "audio-comparisons/", "audio-test-signals/", "measurement-log-template.csv", "ab-listening-log-template.csv", "test-signal-manifest.json"):
            require(needle in text, f"{label} lacks evidence link: {needle}")
        require(KVR in text, f"{label} lacks external KVR directory corroboration")
        require("videoobject" in lowered, f"{label} must explicitly explain why VideoObject is not emitted yet")
        require("not an endorsement" in lowered or "bukan endorsement" in lowered, f"{label} must bound KVR directory meaning")


def validate_generator(root: Path) -> None:
    js = read(root / "site/test-signals.js")
    forbidden_network = ("fetch(", "xmlhttprequest", "sendbeacon", "websocket")
    lowered = js.lower()
    for needle in forbidden_network:
        require(needle not in lowered, f"Generator must stay network-free: found {needle}")
    for needle in ("new Blob", "audio/wav", "RIFF", "WAVE", "sine1k", "sweep", "pink", "channels", "phase", "0x61850"):
        require(needle in js, f"Generator contract missing: {needle}")
    require("-24" in js, "Generator must preserve conservative -24 dBFS default semantics")
    for filename in ("site/audio-test-signals/index.html", "site/id/audio-test-signals/index.html"):
        text = read(root / filename).lower()
        require("value=\"-24\"" in text, f"Default -24 dBFS input missing: {filename}")
        require("not a hearing test" in text or "bukan hearing test" in text, f"Listening-safety boundary missing: {filename}")
        require("autoplay" not in text, f"Test signal page must never autoplay: {filename}")
        require("test-signals.js" in text, f"Generator script missing: {filename}")


def validate_material(root: Path) -> None:
    manifest_path = root / "site/test-material/test-signal-manifest.json"
    manifest = json.loads(read(manifest_path))
    require(manifest.get("generatedLocally") is True, "Manifest must declare local generation")
    require(manifest.get("defaultPeakCeilingDbfs") == -24, "Manifest default peak ceiling changed")
    require(manifest.get("maximumAllowedPeakCeilingDbfs") == -6, "Manifest maximum peak ceiling changed")
    require(set(manifest.get("signals", {})) == {"sine1k", "sweep", "pink", "channels", "phase"}, "Manifest signal set mismatch")

    measurement = root / "site/test-material/measurement-log-template.csv"
    ab = root / "site/test-material/ab-listening-log-template.csv"
    for path in (measurement, ab):
        require(path.is_file(), f"Missing CSV template: {path}")
        rows = list(csv.reader(read(path).splitlines()))
        require(len(rows) == 1 and len(rows[0]) >= 15, f"Template must contain headers only with useful fields: {path}")
    require("software_version" in read(measurement), "Measurement log lacks software version")
    require("gain_match" in read(measurement), "Measurement log lacks Gain Match state")
    require("preferred_state" in read(ab), "A/B log lacks preference field")
    require("confidence_1_to_5" in read(ab), "A/B log lacks confidence field")


def validate_discovery(root: Path) -> None:
    xml_path = root / "site/sitemap-evidence.xml"
    txt_path = root / "site/sitemap-evidence.txt"
    require(xml_path.is_file() and txt_path.is_file(), "P2 evidence sitemap pair is missing")
    tree = ElementTree.fromstring(read(xml_path))
    xml_urls = {node.text.strip() for node in tree.findall(f"{{{NS}}}url/{{{NS}}}loc") if node.text}
    txt_urls = {line.strip() for line in read(txt_path).splitlines() if line.strip()}
    require(xml_urls == EXPECTED_SITEMAP, f"Evidence XML sitemap mismatch: {xml_urls ^ EXPECTED_SITEMAP}")
    require(txt_urls == EXPECTED_SITEMAP, f"Evidence TXT sitemap mismatch: {txt_urls ^ EXPECTED_SITEMAP}")

    robots = read(root / "site/robots.txt")
    for name in ("sitemap-evidence.xml", "sitemap-evidence.txt"):
        require(f"Sitemap: {ROOT}{name}" in robots, f"robots lacks P2 sitemap: {name}")

    headers = read(root / "site/_headers")
    for url in sorted(EXPECTED_SITEMAP):
        require(url in headers and f"Link: <{url}>; rel=\"canonical\"" in headers, f"HTTP canonical missing for {url}")


def validate_hubs_and_workflow(root: Path) -> None:
    require("../evidence/" in read(root / "site/about/index.html"), "EN About page does not link P2 Evidence Lab")
    require("../../id/evidence/" in read(root / "site/id/about/index.html"), "ID About page does not link P2 Evidence Lab")
    workflow = read(root / ".github/workflows/pages.yml")
    require("tools/validate-global-discovery-p2.py" in workflow, "Pages workflow does not run P2 validator")
    renderer = read(root / "tools/render-deployment-seo.py")
    require("EVIDENCE_SITEMAPS" in renderer, "Canonical renderer is not P2 evidence-sitemap aware")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate_pages(root)
    validate_evidence_pages(root)
    validate_generator(root)
    validate_material(root)
    validate_discovery(root)
    validate_hubs_and_workflow(root)
    print("[PASS] Global Discovery P2 validates evidence pages, browser WAV generator, reproducibility kit, KVR boundary, evidence sitemaps and CI integration.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
