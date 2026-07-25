#!/usr/bin/env python3
"""Validate ArSonKuPik release integrity and the V6 static public shell."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

ROOT_URL = "https://masarray.github.io/vst-enhancer/"
ID_URL = ROOT_URL + "id/"
RELEASE_ROOT = "https://github.com/masarray/vst-enhancer/releases"
ASSET_ROOT = RELEASE_ROOT + "/download/"
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    require(bool(text.strip()), f"Empty file: {path.as_posix()}")
    return text


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.hreflang: dict[str, str] = {}
        self.ids: list[str] = []
        self.h1 = ""
        self.structured = ""
        self.styles: list[str] = []
        self.scripts: list[str] = []
        self._title = False
        self._h1 = False
        self._structured = False
        self._chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        data = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = data.get("lang", "")
        if tag == "title":
            self._title = True
        if tag == "h1":
            self._h1 = True
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "meta" and data.get("name") == "description":
            self.description = data.get("content", "")
        if tag == "link":
            rel = data.get("rel", "").split()
            if "canonical" in rel:
                self.canonical = data.get("href", "")
            if "alternate" in rel and data.get("hreflang"):
                self.hreflang[data["hreflang"]] = data.get("href", "")
            if data.get("rel") == "stylesheet":
                self.styles.append(data.get("href", ""))
        if tag == "script" and data.get("id") == "software-structured-data":
            self._structured = True
            self._chunks = []
        if tag == "script" and data.get("src"):
            self.scripts.append(data.get("src", ""))

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._h1:
            self.h1 += data
        if self._structured:
            self._chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False
        if tag == "h1":
            self._h1 = False
        if tag == "script" and self._structured:
            self.structured = "".join(self._chunks)
            self._structured = False
            self._chunks = []


def page(text: str) -> Page:
    result = Page()
    result.feed(text)
    duplicates = [name for name, count in Counter(result.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")
    return result


def validate_release(root: Path) -> dict:
    release = json.loads(read(root / "site/release.json"))
    localized = json.loads(read(root / "site/id/release.json"))
    require(release == localized, "Localized release manifest drift")

    required = {
        "schemaVersion", "version", "distributionEnabled", "evaluationDays",
        "purchaseCheckoutAvailable", "inAppCheckoutAvailable", "purchaseStatus",
        "activationPriceAmount", "activationPriceFormatted", "priceCurrency",
        "maxActiveComputers", "activeComputerPolicy", "checkoutProvider",
        "checkoutMethod", "purchasePageIndexable", "releaseUrl", "installerUrl",
        "vst3Url", "standaloneUrl", "checksumsUrl", "unsigned", "signatureStatus"
    }
    require(not required.difference(release), f"release.json missing {sorted(required.difference(release))}")
    require(VERSION_RE.fullmatch(str(release["version"])) is not None, "Invalid version")
    require(release["schemaVersion"] >= 3 and release["distributionEnabled"] is True, "Release schema/status invalid")
    require(release["automaticCharge"] is False and release["subscription"] is False and release["purchaseObligation"] is False, "No-pressure licence flags changed")

    # Public web checkout remains intentionally disabled. Purchase is initiated in
    # the application through the reviewed hosted Midtrans QRIS flow.
    require(release["purchaseCheckoutAvailable"] is False and "purchaseUrl" not in release, "Direct web checkout must stay disabled")
    require(release["inAppCheckoutAvailable"] is True, "In-application checkout availability drift")
    require(release["purchaseStatus"] == "available-in-app", "Purchase status must identify the in-app flow")
    require(release["activationPriceAmount"] == 399000, "Activation amount drift")
    require(release["activationPriceFormatted"] == "Rp399.000", "Activation display price drift")
    require(release["priceCurrency"] == "IDR", "Activation currency drift")
    require(release["maxActiveComputers"] == 1, "Active-computer limit drift")
    require(release["activeComputerPolicy"] == "one-active-at-a-time", "Active-computer policy drift")
    require(release["checkoutProvider"] == "Midtrans" and release["checkoutMethod"] == "QRIS", "Checkout provider/method drift")
    require(release["purchasePageIndexable"] is False, "Activation information page must remain noindex without direct web checkout")

    version = str(release["version"])
    require(str(release["releaseUrl"]).startswith(RELEASE_ROOT) and str(release["releaseUrl"]).endswith("/tag/" + version), "Release URL mismatch")
    endings = {
        "installerUrl": f"ArSonKuPik-{version}-Windows-x64-Setup.exe",
        "vst3Url": f"ArSonKuPik-{version}-Windows-x64-VST3.zip",
        "standaloneUrl": f"ArSonKuPik-{version}-Windows-x64-Standalone.zip",
        "checksumsUrl": "SHA256SUMS.txt",
    }
    for key, ending in endings.items():
        value = str(release[key])
        parsed = urlparse(value)
        require(value.startswith(ASSET_ROOT) and parsed.scheme == "https" and parsed.hostname == "github.com" and value.endswith("/" + ending), f"{key} invalid")
    return release


def validate_page(text: str, language: str, canonical: str, version: str, prefix: str) -> None:
    parsed = page(text)
    require(parsed.lang == language, f"{canonical} lang mismatch")
    require(parsed.canonical == canonical, f"{canonical} canonical mismatch")
    require(parsed.hreflang == {"en": ROOT_URL, "id": ID_URL, "x-default": ROOT_URL}, f"{canonical} hreflang mismatch")
    require("ArSonKuPik" in parsed.title and "VST3" in parsed.title and "365" not in parsed.title, f"{canonical} title is not product-first")
    require(80 <= len(parsed.description) <= 180 and "365" not in parsed.description, f"{canonical} description is not product-first")
    require(("Suara lebih berisi" in parsed.h1) if language == "id" else ("Fuller, clearer" in parsed.h1), f"{canonical} H1 not localized")
    require(parsed.structured, f"{canonical} missing JSON-LD")
    graph = json.loads(parsed.structured)["@graph"]
    software = next(item for item in graph if item.get("@type") == "SoftwareApplication")
    require(software.get("softwareVersion") == version.lstrip("v"), f"{canonical} structured version mismatch")
    require(software.get("url") == canonical and software.get("inLanguage") == language, f"{canonical} structured locale mismatch")
    require(any("41" in str(item) and "preset" in str(item).lower() for item in software.get("featureList", [])), f"{canonical} structured preset count drift")

    for item in ("main", "workflow", "features", "presets", "download", "faq"):
        require(item in parsed.ids, f"{canonical} missing #{item}")
    require("for-you" in parsed.ids or "sound" in parsed.ids, f"{canonical} missing flagship sound section")
    expected_styles = {f"{prefix}landing-v2.css", f"{prefix}experience-v4.css", f"{prefix}typography-v5.css", f"{prefix}hardening-v6.css"}
    require(expected_styles.issubset(set(parsed.styles)), f"{canonical} static styles incomplete")
    require(f"{prefix}site-v6.js" in parsed.scripts and f"{prefix}experience-v4.js" in parsed.scripts, f"{canonical} V6 scripts incomplete")

    expected_count = "41 titik awal terkurasi" if language == "id" else "41 curated starting points"
    require(expected_count in text, f"{canonical} visible preset count drift")
    require("<strong>Creative</strong><span>20</span>" in text, f"{canonical} creative preset count drift")
    require("Blues Club" in text, f"{canonical} Blues Club missing")
    require("40 curated" not in text and "40 preset" not in text and "40 titik" not in text, f"{canonical} stale 40-preset copy remains")


def validate_sitemap(root: Path) -> None:
    tree = ElementTree.fromstring(read(root / "site/sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
    urls = tree.findall("s:url", ns)
    require([item.findtext("s:loc", default="", namespaces=ns) for item in urls] == [ROOT_URL, ID_URL], "Sitemap localized URLs mismatch")
    expected = {"en": ROOT_URL, "id": ID_URL, "x-default": ROOT_URL}
    for item in urls:
        require({link.attrib.get("hreflang"): link.attrib.get("href") for link in item.findall("x:link", ns)} == expected, "Sitemap hreflang mismatch")


def validate_runtime(root: Path) -> None:
    site_js = read(root / "site/site-v6.js")
    experience = read(root / "site/experience-v4.js")
    activation = read(root / "site/activation/activation.js")
    styles = read(root / "site/experience-v4.css")
    typography = read(root / "site/typography-v5.css")
    hardening = read(root / "site/hardening-v6.css")

    for token in ("siteBase", "officialReleaseUrl", "data-installer-cta", "data-release-status", "IntersectionObserver", "release.json"):
        require(token in site_js, f"V6 release runtime missing {token}")
    require("latest-release.js" not in site_js, "Second resolver must not return")
    require("createElement('link')" not in site_js, "Release runtime must not inject CSS")

    for token in ("setupProductPreview", "setupPresetExplorer", "preset-explorer-ready", "preset-browser", "setupScrollReveals", "setupNavigationState", "setupPointerDepth", "prefers-reduced-motion"):
        require(token in experience, f"Audio runtime missing {token}")
    require("document.createElement('link')" not in experience, "Audio runtime must not inject CSS")

    for token in ("inAppCheckoutAvailable", "activationPriceFormatted", "Midtrans", "QRIS", "one active"):
        require(token in activation, f"Activation runtime missing {token}")

    for selector in (".product-preview-dialog", ".preset-universe.preset-explorer-ready", ".preset-browser", ".preset-toolbar", ".motion-ready [data-reveal]", ".landing-nav.is-scrolled"):
        require(selector in styles, f"Audio styles missing {selector}")
    for token in ("--landing-copy: 16px", "--type-card: 14.5px", ".faq-grid p", "--type-card: 15px"):
        require(token in typography, f"Typography contract missing {token}")
    for token in (".language-switch a", ".mobile-nav", ".mobile-nav-panel"):
        require(token in hardening, f"Global shell style missing {token}")
    require("browser.append(toolbar, groupsContainer)" in experience, "Preset browser DOM contract missing")
    require("minmax(0, 1.32fr)" in styles, "Preset browser desktop grid contract missing")
    require("@media (prefers-reduced-motion: reduce)" in styles, "Reduced-motion safety missing")
    for name, content in (("experience", styles), ("typography", typography), ("hardening", hardening)):
        require(content.count("{") == content.count("}"), f"{name} stylesheet has unbalanced braces")


def validate_public_terms(root: Path) -> None:
    combined = "\n".join(read(root / name) for name in ("README.md", "EULA.txt", "PURCHASE_TERMS.txt", "PRIVACY.txt"))
    for token in ("IDR 399,000", "one active", "Midtrans", "QRIS"):
        require(token.lower() in combined.lower(), f"Public terms missing {token}")
    require("USD 25" not in combined, "Stale USD 25 public offer remains")
    require("up to two active computers" not in combined.lower(), "Stale two-computer public offer remains")


def remote_check(urls: list[str]) -> None:
    for url in urls:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ArSonKuPik-validator/6.1"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                require(200 <= response.status < 400, f"Remote status {response.status}: {url}")
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            raise AssertionError(f"Remote URL failed: {url} ({exc})") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-remote", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        release = validate_release(root)
        validate_page(read(root / "site/index.html"), "en", ROOT_URL, str(release["version"]), "")
        validate_page(read(root / "site/id/index.html"), "id", ID_URL, str(release["version"]), "../")
        validate_sitemap(root)
        validate_runtime(root)
        validate_public_terms(root)
        if args.check_remote:
            remote_check([str(release[key]) for key in ("releaseUrl", "installerUrl", "vst3Url", "standaloneUrl", "checksumsUrl")])
    except (AssertionError, json.JSONDecodeError, ElementTree.ParseError, StopIteration, ValueError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"Validation passed: bilingual 41-preset shell, IDR in-app activation policy, audio UX and release {release['version']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
