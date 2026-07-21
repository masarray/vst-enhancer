#!/usr/bin/env python3
"""Validate product-first EN/ID pages, release routing and the V4 audio UX layer."""

from __future__ import annotations

import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.translated = 0
        self.details = 0
        self.meta: list[dict[str, str]] = []

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
    app_js = read(root / "site" / "app.js")
    trial_js = read(root / "site" / "trial-page.js")
    experience_js = read(root / "site" / "experience-v4.js")
    latest_release_js = read(root / "site" / "latest-release.js")
    activation_js = read(root / "site" / "activation" / "activation.js")
    release = json.loads(read(root / "site" / "release.json"))

    landing_parser = parse(landing)
    localized_parser = parse(localized)
    activation_parser = parse(activation)

    require(landing_parser.translated >= 150, "English landing needs complete bilingual source values")
    require(localized_parser.translated >= 90, "Indonesian landing needs bilingual fallback values")
    require(9 <= landing_parser.details <= 11, "Landing must keep a compact FAQ/disclosure set")
    require(activation_parser.translated >= 45, "Activation page needs bilingual content")

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

    require("Suara lebih berisi, jernih, dan berdimensi" in localized, "Localized H1 is missing")
    require("USD 25" not in landing, "Price must remain outside the main product landing")
    require('href="activation/"' in landing, "Landing must link the optional activation page")
    require('id="mobile-download-bar"' in landing, "Landing must include a mobile sticky download CTA")
    require('href="landing-v2.css"' in landing, "Core product stylesheet must load statically")

    require(app_js.count("fetch('./release.json'") == 1, "Release controller must retain one local manifest request")
    require("querySelectorAll('[data-installer-cta]')" in app_js, "Central release controller must manage installer CTAs")
    require("latest-release.js" in trial_js, "Landing must retain latest-release fallback resolution")
    require("window.location.assign" in trial_js and "stopImmediatePropagation" in trial_js, "Language controls must use stable locale URLs")
    require("askp:release-ready" in trial_js, "Canonical locale must be restored after release rendering")
    require("experience-v4.js" in trial_js and "v4-audio-motion" in trial_js, "V4 product experience is not loaded")
    require("IntersectionObserver" in trial_js, "Mobile CTA visibility must remain viewport-aware")

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
        require(token in experience_js, f"V4 experience is missing {token}")
    for selector in (
        ".product-preview-dialog",
        ".preset-universe.preset-explorer-ready",
        ".preset-browser",
        ".preset-toolbar",
        ".preset-chip",
        ".motion-ready [data-reveal]",
        ".landing-nav.is-scrolled",
    ):
        require(selector in experience_css, f"V4 experience CSS is missing {selector}")

    require("browser.append(toolbar, groupsContainer)" in experience_js, "Preset toolbar and groups must remain in one browser column")
    require("grid-template-columns: minmax(280px, .68fr) minmax(0, 1.32fr);" in experience_css, "Desktop preset layout contract is missing")

    require("fetch(LATEST_API" in latest_release_js, "Latest resolver must request GitHub release metadata")
    require("browser_download_url" in latest_release_js, "Latest resolver must use official asset URLs")
    require("scoreInstaller" in latest_release_js, "Latest resolver must rank installer assets")
    require("portable" in latest_release_js, "Latest resolver must reject portable executables as installer CTAs")
    require("activator" in latest_release_js and "key" in latest_release_js, "Latest resolver must reject activation utilities")
    require("trustedCheckoutUrl" in activation_js, "Activation page must validate checkout URLs")
    require("purchaseAllowedHosts" in activation_js, "Activation page must allowlist checkout hosts")
    require(release.get("purchaseCheckoutAvailable") is False, "Checkout must remain disabled until configured")
    require("purchaseUrl" not in release, "Disabled checkout must not publish a purchase URL")

    require("--landing-copy: 15px" in landing_css, "Landing body typography must remain readable")
    require("@media (max-width: 740px)" in experience_css, "V4 mobile enhancement is missing")
    require("@media (prefers-reduced-motion: reduce)" in experience_css, "Reduced-motion support is missing")
    require(landing_css.count("{") == landing_css.count("}"), "Landing stylesheet has unbalanced braces")
    require(experience_css.count("{") == experience_css.count("}"), "Experience stylesheet has unbalanced braces")

    public_text = "\n".join((landing, localized, activation, landing_css, experience_css, app_js, trial_js, experience_js, latest_release_js, activation_js))
    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited token: {token}")

    print(
        "Product-first V4 validation passed: stable EN/ID routes, fixed preset browser grid, "
        "restrained audio motion, accessible interface preview, release routing and optional activation separation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
