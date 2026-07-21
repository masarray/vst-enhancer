#!/usr/bin/env python3
"""Validate product-first EN/ID pages, V6 release routing and optional activation separation."""

from __future__ import annotations

import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.details = 0
        self.meta: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.styles: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "details":
            self.details += 1
        if tag == "meta":
            self.meta.append(data)
        if tag == "a":
            self.links.append(data)
        if tag == "link" and data.get("rel") == "stylesheet":
            self.styles.append(data.get("href", ""))
        if tag == "script" and data.get("src"):
            self.scripts.append(data.get("src", ""))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    value = path.read_text(encoding="utf-8")
    require(bool(value.strip()), f"Empty file: {path.as_posix()}")
    return value


def parse(html: str) -> PageParser:
    parser = PageParser()
    parser.feed(html)
    duplicates = [name for name, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")
    return parser


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    landing = read(root / "site" / "index.html")
    localized = read(root / "site" / "id" / "index.html")
    activation = read(root / "site" / "activation" / "index.html")
    landing_css = read(root / "site" / "landing-v2.css")
    experience_css = read(root / "site" / "experience-v4.css")
    typography_css = read(root / "site" / "typography-v5.css")
    hardening_css = read(root / "site" / "hardening-v6.css")
    site_js = read(root / "site" / "site-v6.js")
    experience_js = read(root / "site" / "experience-v4.js")
    activation_js = read(root / "site" / "activation" / "activation.js")
    release = json.loads(read(root / "site" / "release.json"))

    landing_parser = parse(landing)
    localized_parser = parse(localized)
    activation_parser = parse(activation)

    require(landing_parser.details >= 9, "English landing must retain install, FAQ and legal disclosure depth")
    require(localized_parser.details >= 9, "Indonesian landing must retain equivalent disclosure depth")
    require(activation_parser.details >= 1, "Activation page must retain legal disclosure")

    title = next((item.get("content", "") for item in landing_parser.meta if item.get("property") == "og:title"), "")
    description = next((item.get("content", "") for item in landing_parser.meta if item.get("name") == "description"), "")
    require("VST3 Audio Enhancer" in title, "Social title must identify the product category")
    require("fuller, clearer and more dimensional" in description.lower(), "Search description must lead with sonic value")
    require("365 days" not in description.lower(), "Evaluation duration must not dominate search copy")

    for phrase in (
        "Musical VST3 audio enhancer for Windows",
        "Fuller, clearer and more dimensional sound",
        "Mas Ari Signature",
        "40 curated starting points",
        "Your own audio is the real demo",
        "Download free for Windows",
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
    ):
        require(phrase in landing, f"Landing is missing product-first phrase: {phrase}")

    for phrase in (
        "VST3 audio enhancer musikal untuk Windows",
        "Suara lebih berisi, jernih, dan berdimensi",
        "40 titik awal terkurasi",
        "Tanpa tagihan otomatis",
    ):
        require(phrase in localized, f"Localized landing is missing: {phrase}")

    require("USD 25" not in landing, "Price must remain outside the main product landing")
    require('href="activation/"' in landing, "English landing must link optional activation")
    require('href="../activation/"' in localized, "Indonesian landing must link optional activation")
    require('id="mobile-download-bar"' in landing and 'id="mobile-download-bar"' in localized, "Both pages need mobile download CTA")

    for page, prefix in ((landing_parser, ""), (localized_parser, "../")):
        require(f"{prefix}site-v6.js" in page.scripts, "V6 release controller must load statically")
        require(f"{prefix}experience-v4.js" in page.scripts, "Audio experience must load statically")
        for stylesheet in ("landing-v2.css", "experience-v4.css", "typography-v5.css", "hardening-v6.css"):
            require(f"{prefix}{stylesheet}" in page.styles, f"Missing static stylesheet {stylesheet}")

    require("fetch(`${siteBase}/release.json`" in site_js, "Single release manifest request is missing")
    require("officialReleaseUrl" in site_js, "Release URL allowlist is missing")
    require("querySelectorAll('[data-installer-cta]')" in site_js, "Single release controller must manage all installer CTAs")
    require("latest-release.js" not in landing + localized, "Second release resolver must not load")
    require("app.js" not in landing + localized and "trial-page.js" not in landing + localized, "Legacy landing controllers must not load")

    for token in (
        "setupProductPreview",
        "setupPresetExplorer",
        "preset-explorer-ready",
        "preset-browser",
        "setupScrollReveals",
        "setupNavigationState",
        "setupPointerDepth",
        "prefers-reduced-motion",
    ):
        require(token in experience_js, f"Audio experience is missing {token}")

    require("document.createElement('link')" not in experience_js, "Experience must not inject CSS")
    require("createElement('link')" not in site_js, "Release controller must not inject CSS")
    require("browser.append(toolbar, groupsContainer)" in experience_js, "Preset toolbar and groups must remain together")
    require("grid-template-columns: minmax(280px, .68fr) minmax(0, 1.32fr);" in experience_css, "Desktop preset layout contract is missing")

    for token in ("--landing-copy: 16px", "--type-card: 14.5px", ".faq-grid p", "--type-card: 15px"):
        require(token in typography_css, f"Readable typography contract is missing {token}")
    for token in (".language-switch a", ".mobile-nav-panel", "@media (max-width: 860px)"):
        require(token in hardening_css, f"Mobile/global shell contract is missing {token}")

    require("trustedCheckoutUrl" in activation_js, "Activation page must validate checkout URLs")
    require("purchaseAllowedHosts" in activation_js, "Activation page must allowlist checkout hosts")
    require(release.get("purchaseCheckoutAvailable") is False, "Checkout must remain disabled until configured")
    require("purchaseUrl" not in release, "Disabled checkout must not publish a purchase URL")
    require("font-weight: 610" in landing_css, "Refined headline weight must remain")
    require("@media (prefers-reduced-motion: reduce)" in experience_css, "Reduced-motion support is missing")

    for name, content in (("landing", landing_css), ("experience", experience_css), ("typography", typography_css), ("hardening", hardening_css)):
        require(content.count("{") == content.count("}"), f"{name} stylesheet has unbalanced braces")

    public_text = "\n".join((landing, localized, activation, landing_css, experience_css, typography_css, hardening_css, site_js, experience_js, activation_js))
    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited token: {token}")

    print(
        "Product-first V6 validation passed: static EN/ID routes, one release controller, hyperlink locales, "
        "mobile navigation, readable typography, audio motion and optional activation separation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
