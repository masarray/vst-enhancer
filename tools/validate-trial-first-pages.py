#!/usr/bin/env python3
"""Validate the product-first landing, latest-release resolver, mobile CTA and activation readiness."""

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
    activation = read(root / "site" / "activation" / "index.html")
    styles_css = read(root / "site" / "styles.css")
    trial_css = read(root / "site" / "trial.css")
    landing_css = read(root / "site" / "landing-v2.css")
    app_js = read(root / "site" / "app.js")
    trial_js = read(root / "site" / "trial-page.js")
    latest_release_js = read(root / "site" / "latest-release.js")
    activation_js = read(root / "site" / "activation" / "activation.js")
    release = json.loads(read(root / "site" / "release.json"))

    landing_parser = parse(landing)
    activation_parser = parse(activation)

    require(landing_parser.translated >= 150, "Product-first landing needs at least 150 bilingual elements")
    require(9 <= landing_parser.details <= 11, "Landing must keep 9-11 FAQ/disclosure entries")
    require(activation_parser.translated >= 45, "Activation page needs at least 45 bilingual elements")
    require(landing.count("<section") <= 10, "Landing has too many major sections")
    require(len(landing.splitlines()) <= 390, "Landing is no longer compact")

    title = next((item.get("content", "") for item in landing_parser.meta if item.get("property") == "og:title"), "")
    description = next((item.get("content", "") for item in landing_parser.meta if item.get("name") == "description"), "")
    require("VST3 Audio Enhancer" in title, "Social title must identify the product category")
    require("fuller, clearer and more dimensional" in description.lower(), "Landing description must lead with sonic value")
    require("365 days" not in description.lower(), "Evaluation duration must not dominate the search description")

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
        "First-time user",
        "Musician & creator",
        "Producer",
        "Audio engineer",
        "may help sustain independent development",
    ):
        require(phrase in landing, f"Landing is missing product-first phrase: {phrase}")

    require("USD 25" not in landing, "Price must remain outside the main product landing")
    require('href="activation/"' in landing, "Landing must link the separate optional activation page")
    require('id="purchase-status" hidden' in landing, "Checkout state must remain non-prominent")
    require(landing.find("commercially code-signed") > landing.find('id="download"'), "Unsigned disclosure must stay in download flow")
    require('id="mobile-download-bar"' in landing, "Landing must include a mobile sticky download bar")
    require('href="landing-v2.css"' in landing, "Product-first stylesheet must load statically from the document head")

    require(app_js.count("fetch('./release.json'") == 1, "app.js must retain one local manifest request")
    require("fetch(" not in trial_js and "release.json" not in trial_js, "trial-page.js must not fetch release metadata")
    require("querySelectorAll('[data-installer-cta]')" in app_js, "Central controller must manage every installer CTA")
    require("button.dataset[currentLanguage]" in app_js, "CTA labels must remain contextual and bilingual")
    require("IntersectionObserver" in trial_js, "Mobile CTA visibility must respond to hero visibility")
    require("mobile-download-bar" in trial_js, "Mobile CTA controller is missing")
    require("latest-release.js" in trial_js, "Main landing must load the latest-release resolver")
    require("../latest-release.js" in activation_js, "Activation page must load the latest-release resolver")
    require("premium-polish.css" not in trial_js, "Primary visual CSS must not be injected after first paint")
    require("document.title" in trial_js and 'meta[name="description"]' in trial_js, "Language switching must update user-visible metadata")

    require("const REPOSITORY = 'masarray/vst-enhancer';" in latest_release_js, "Resolver repository constant is incorrect")
    require("fetch(LATEST_API" in latest_release_js, "Resolver must request GitHub's latest release endpoint")
    require("browser_download_url" in latest_release_js, "Resolver must use official release asset URLs")
    require("scoreInstaller" in latest_release_js, "Resolver must rank installer assets explicitly")
    require("portable" in latest_release_js, "Resolver must reject portable executables for the installer CTA")
    require("activator" in latest_release_js and "key" in latest_release_js, "Resolver must reject activation tools and key utilities")
    require("OFFICIAL_DOWNLOAD_PREFIX" in latest_release_js, "Resolver must restrict assets to this repository")
    require("expectedInstallerUrl" in latest_release_js, "Resolver must lock CTAs against stale manifest overwrites")
    require("MutationObserver" in latest_release_js, "Resolver must protect direct installer links from late stale writes")
    require("software.downloadUrl = release.installerUrl" in latest_release_js, "Structured data must point to the resolved latest installer")

    require("trustedCheckoutUrl" in activation_js, "Activation page must validate checkout URL")
    require("purchaseAllowedHosts" in activation_js, "Activation page must require allowed checkout hosts")
    require("purchasePageIndexable" in activation_js, "Activation page must require explicit indexing readiness")
    require(release.get("purchaseCheckoutAvailable") is False, "Checkout must remain disabled until configured")
    require("purchaseUrl" not in release, "Disabled checkout must not publish a purchaseUrl")

    require("--landing-copy: 15px" in landing_css, "Landing body typography must remain at least 15 px")
    require("font-size: 15px" in landing_css, "Mobile landing body typography must remain 15 px")
    require("landing-v2.css" not in trial_js, "Landing stylesheet must be static, not injected with JavaScript")
    require("font-family: Inter" in trial_css or "font-family: Inter" in styles_css, "Inter fallback stack must remain available")
    require(landing_css.count("{") == landing_css.count("}"), "Landing stylesheet has unbalanced braces")

    public_text = "\n".join((landing, activation, trial_css, landing_css, app_js, trial_js, latest_release_js, activation_js))
    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited token: {token}")

    print(
        "Product-first landing validation passed: "
        f"{landing_parser.translated} bilingual elements, "
        f"{landing_parser.details} FAQ/disclosures, flagship Mas Ari Signature story, "
        "40-preset library, static premium CSS, 15 px readable typography, latest release routing and mobile CTA."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
