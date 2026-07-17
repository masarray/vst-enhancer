#!/usr/bin/env python3
"""Validate the public ArSonKuPik site, release manifest and owner-controlled workflow."""

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
from typing import Iterable
from urllib.parse import urlparse
from xml.etree import ElementTree

REPOSITORY = "masarray/vst-enhancer"
SITE_URL = "https://masarray.github.io/vst-enhancer/"
RELEASE_PREFIX = f"https://github.com/{REPOSITORY}/releases"
ASSET_PREFIX = f"{RELEASE_PREFIX}/download/"
VERSION_PATTERN = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
FORBIDDEN_TOKENS = (
    "private-key",
    "private_key",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "ArSonKuPikKeyActivator",
)
CHECKOUT_FIELDS = {
    "purchaseUrl",
    "purchaseAllowedHosts",
    "sellerName",
    "purchaseProvider",
    "priceCurrency",
    "taxSummaryEn",
    "taxSummaryId",
    "refundSummaryEn",
    "refundSummaryId",
    "purchasePageIndexable",
}


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.translated = 0
        self.details = 0
        self.meta: list[dict[str, str]] = []
        self.link_tags: list[dict[str, str]] = []
        self.scripts: dict[str, str] = {}
        self._script_id: str | None = None
        self._script_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if "data-en" in data or "data-id" in data:
            require(bool(data.get("data-en") and data.get("data-id")), f"Missing bilingual value on <{tag}>")
            self.translated += 1
        if tag == "details":
            self.details += 1
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])
        if tag == "meta":
            self.meta.append(data)
        if tag == "link":
            self.link_tags.append(data)
        if tag == "script" and data.get("id"):
            self._script_id = data["id"]
            self._script_chunks = []

    def handle_data(self, data: str) -> None:
        if self._script_id:
            self._script_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script_id:
            self.scripts[self._script_id] = "".join(self._script_chunks)
            self._script_id = None
            self._script_chunks = []


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    text = path.read_text(encoding="utf-8")
    require(bool(text.strip()), f"Empty file: {path.as_posix()}")
    return text


def validate_official_url(value: object, *, asset: bool = False) -> str:
    require(isinstance(value, str) and value, "Expected a non-empty URL string")
    prefix = ASSET_PREFIX if asset else RELEASE_PREFIX
    require(value.startswith(prefix), f"URL is outside the official release path: {value}")
    require("\\" not in value and " " not in value, f"Unsafe URL characters: {value}")
    return value


def validate_checkout_manifest(release: dict[str, object]) -> None:
    if release["purchaseCheckoutAvailable"] is not True:
        require(
            release.get("purchaseStatus") in {"not-configured", "paused", "unavailable"},
            "Disabled checkout requires a clear purchaseStatus",
        )
        require("purchaseUrl" not in release, "Disabled checkout must not publish purchaseUrl")
        return

    missing = sorted(field for field in CHECKOUT_FIELDS if field not in release)
    require(not missing, f"Enabled checkout is missing fields: {missing}")
    require(release.get("purchasePageIndexable") is True, "Enabled checkout requires purchasePageIndexable=true")
    allowed = release.get("purchaseAllowedHosts")
    require(isinstance(allowed, list) and allowed, "Enabled checkout requires purchaseAllowedHosts")

    parsed = urlparse(str(release["purchaseUrl"]))
    require(parsed.scheme == "https" and bool(parsed.hostname), "Enabled checkout requires a valid HTTPS purchaseUrl")
    require(not parsed.username and not parsed.password, "Checkout URL must not contain credentials")
    require(parsed.port in {None, 443}, "Checkout URL must use the standard HTTPS port")
    require(parsed.hostname.lower() in {str(host).lower() for host in allowed}, "Checkout hostname is not allowlisted")


def validate_release(root: Path) -> dict[str, object]:
    release = json.loads(read_text(root / "site" / "release.json"))
    required = {
        "schemaVersion",
        "version",
        "distributionEnabled",
        "distributionStatus",
        "evaluationDays",
        "purchaseCheckoutAvailable",
        "releaseUrl",
        "unsigned",
        "signatureStatus",
    }
    missing = sorted(required.difference(release))
    require(not missing, f"release.json missing fields: {missing}")
    require(isinstance(release["schemaVersion"], int) and release["schemaVersion"] >= 2, "Unsupported schemaVersion")
    require(isinstance(release["distributionEnabled"], bool), "distributionEnabled must be boolean")
    require(isinstance(release["purchaseCheckoutAvailable"], bool), "purchaseCheckoutAvailable must be boolean")
    require(VERSION_PATTERN.match(str(release["version"])) is not None, f"Invalid version: {release['version']}")
    require(release["evaluationDays"] == 365, "evaluationDays must remain 365")
    require(release.get("automaticCharge") is False, "automaticCharge must remain false")
    require(release.get("subscription") is False, "subscription must remain false")
    require(release.get("purchaseObligation") is False, "purchaseObligation must remain false")
    require(release.get("noPaymentCardRequired") is True, "noPaymentCardRequired must remain true")
    require(release.get("keyActivatorDistributedPublicly") is False, "Key Activator must not be public")

    version = str(release["version"])
    release_url = validate_official_url(release["releaseUrl"])
    require(release_url.endswith(f"/tag/{version}"), "releaseUrl tag does not match version")

    if release["distributionEnabled"]:
        expected_assets = {
            "installerUrl": f"ArSonKuPik-{version}-Windows-x64-Setup.exe",
            "vst3Url": f"ArSonKuPik-{version}-Windows-x64-VST3.zip",
            "standaloneUrl": f"ArSonKuPik-{version}-Windows-x64-Standalone.zip",
            "checksumsUrl": "SHA256SUMS.txt",
        }
        for field, filename in expected_assets.items():
            url = validate_official_url(release.get(field), asset=True)
            require(f"/download/{version}/" in url, f"{field} release tag does not match version")
            require(url.endswith(f"/{filename}"), f"{field} filename mismatch: {url}")
    else:
        require(bool(release["distributionStatus"]), "Disabled distribution requires a status reason")

    validate_checkout_manifest(release)

    if release["unsigned"]:
        require(release["signatureStatus"] == "unsigned", "Unsigned release must declare signatureStatus=unsigned")

    return release


def validate_html(root: Path, release: dict[str, object]) -> SiteParser:
    html = read_text(root / "site" / "index.html")
    parser = SiteParser()
    parser.feed(html)

    duplicates = [name for name, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")

    required_ids = {
        "main",
        "for-you",
        "workflow",
        "features",
        "presets",
        "technical",
        "download",
        "evaluation",
        "privacy",
        "faq",
        "legal",
        "distribution-banner",
        "distribution-title",
        "distribution-message",
        "installer-link",
        "installer-link-bottom",
        "installer-link-final",
        "mobile-download-bar",
        "vst3-link",
        "standalone-link",
        "release-version",
        "release-link",
        "checksums-link",
        "purchase-status",
        "checksum-command",
        "software-structured-data",
        "canonical-link",
    }
    missing = sorted(required_ids.difference(parser.ids))
    require(not missing, f"Missing required HTML ids: {missing}")
    require(parser.translated >= 120, f"Only {parser.translated} bilingual elements found")
    require(9 <= parser.details <= 11, f"Expected a compact 9-11 disclosure/FAQ set, found {parser.details}")
    require(html.count("<section") <= 10, "Public landing has regrown beyond ten sections")
    require(len(html.splitlines()) <= 380, "Public landing is no longer compact")

    description = next((m.get("content", "") for m in parser.meta if m.get("name") == "description"), "")
    robots = next((m.get("content", "") for m in parser.meta if m.get("name") == "robots"), "")
    require(80 <= len(description) <= 180, "Meta description should be 80-180 characters")
    require("index" in robots, "Missing indexable robots meta")
    require(any(m.get("property") == "og:image:alt" and m.get("content") for m in parser.meta), "Missing og:image:alt")

    canonical = next((link.get("href") for link in parser.link_tags if link.get("rel") == "canonical"), "")
    hreflangs = [link for link in parser.link_tags if link.get("rel") == "alternate" and link.get("hreflang")]
    require(canonical == SITE_URL, "Canonical must remain the single product root")
    require(not hreflangs, "Single-URL language preference must not publish query-language hreflang alternates")

    legal_files = {
        "EULA.txt",
        "PURCHASE_TERMS.txt",
        "PRIVACY.txt",
        "THIRD_PARTY_NOTICES.txt",
        "LICENSE.txt",
        "SECURITY.md",
        "SUPPORT.md",
        "CHANGELOG.md",
    }
    for filename in legal_files:
        require((root / filename).is_file(), f"Missing public document: {filename}")
        require(any(filename in link for link in parser.links), f"Landing does not link {filename}")

    structured = json.loads(parser.scripts.get("software-structured-data", ""))
    graph = structured.get("@graph", [])
    software = next((entry for entry in graph if entry.get("@type") == "SoftwareApplication"), None)
    require(software is not None, "Missing SoftwareApplication structured data")
    require(software.get("name") == "ArSonKuPik", "Structured-data software name mismatch")
    require(software.get("offers", {}).get("price") == "0", "Evaluation structured-data price must remain zero")
    require(str(release["version"]).lstrip("v") == software.get("softwareVersion"), "Structured-data version mismatch")

    for token in FORBIDDEN_TOKENS:
        require(token not in html, f"Public site contains prohibited token: {token}")

    return parser


def validate_support_files(root: Path, release: dict[str, object]) -> None:
    required_files = [
        "README.md",
        "EULA.txt",
        "PURCHASE_TERMS.txt",
        "PRIVACY.txt",
        "THIRD_PARTY_NOTICES.txt",
        "LICENSE.txt",
        "SECURITY.md",
        "SUPPORT.md",
        "CHANGELOG.md",
        "site/app.js",
        "site/trial-page.js",
        "site/activation/activation.js",
        "site/styles.css",
        "site/trial.css",
        "site/robots.txt",
        "site/sitemap.xml",
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug-report.yml",
        ".github/ISSUE_TEMPLATE/feature-request.yml",
        ".github/workflows/validate-public-site.yml",
        "tools/validate-public-release.py",
        "tools/validate-public-release.ps1",
    ]
    texts = {relative: read_text(root / relative) for relative in required_files}

    version = str(release["version"])
    require(version in texts["README.md"], "README does not mention current release version")
    require("releases/latest" in texts[".github/ISSUE_TEMPLATE/config.yml"], "Issue chooser must use releases/latest")
    stale_tag = "/tag/" + "v0.5.0"
    require(stale_tag not in "\n".join(texts.values()), "Stale v0.5.0 release link found")
    workflow = texts[".github/workflows/validate-public-site.yml"]
    require("pull_request:" not in workflow, "Self-hosted workflow must not run public PR code")
    require("runs-on: self-hosted" in workflow, "Workflow must use the self-hosted runner")
    require("workflow_dispatch:" in workflow, "Workflow must remain manually triggered")
    require("askp-language" in texts["PRIVACY.txt"], "Privacy notice must disclose language preference storage")
    require("officialReleaseUrl" in texts["site/app.js"], "Frontend must validate release URLs")
    require("IntersectionObserver" in texts["site/trial-page.js"], "Mobile sticky CTA must use viewport-aware visibility")
    require("trustedCheckoutUrl" in texts["site/activation/activation.js"], "Activation page must validate checkout URLs")
    require("purchaseAllowedHosts" in texts["site/activation/activation.js"], "Activation checkout must require a host allowlist")
    require("--micro: 10px" in texts["site/trial.css"], "Compact typography must retain 10 px micro text")
    require("--small: 11px" in texts["site/trial.css"], "Compact typography must retain 11 px small text")
    require("--copy: 12px" in texts["site/trial.css"], "Compact typography must retain 12 px body text")
    require('font-family: Inter' in texts["site/trial.css"], "Inter must remain the primary public font")

    sitemap = ElementTree.fromstring(texts["site/sitemap.xml"])
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locations = [entry.text or "" for entry in sitemap.findall("s:url/s:loc", namespace)]
    require(locations == [SITE_URL], f"Sitemap must contain only the canonical product root: {locations}")

    combined = "\n".join(text for name, text in texts.items() if name != "tools/validate-public-release.py")
    for token in FORBIDDEN_TOKENS:
        require(token not in combined, f"Public repository contains prohibited token: {token}")


def check_remote_urls(urls: Iterable[str]) -> None:
    for url in urls:
        request = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "ArSonKuPik-public-release-validator/2.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                require(200 <= response.status < 400, f"Remote URL returned {response.status}: {url}")
        except urllib.error.HTTPError as exc:
            raise AssertionError(f"Remote URL returned {exc.code}: {url}") from exc
        except urllib.error.URLError as exc:
            raise AssertionError(f"Remote URL could not be reached: {url} ({exc.reason})") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-remote", action="store_true", help="Verify official release and asset URLs")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Repository root")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        release = validate_release(root)
        site = validate_html(root, release)
        validate_support_files(root, release)
        if args.check_remote:
            check_remote_urls(
                [
                    str(release["releaseUrl"]),
                    str(release["installerUrl"]),
                    str(release["vst3Url"]),
                    str(release["standaloneUrl"]),
                    str(release["checksumsUrl"]),
                ]
            )
    except (AssertionError, json.JSONDecodeError, ElementTree.ParseError, ValueError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1

    print(
        "Validation passed: "
        f"{site.translated} bilingual elements, "
        f"{site.details} compact FAQ/disclosures, "
        f"release {release['version']}, "
        f"distribution={'enabled' if release['distributionEnabled'] else 'paused'}, "
        f"checkout={'enabled' if release['purchaseCheckoutAvailable'] else 'not enabled'}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
