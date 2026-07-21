#!/usr/bin/env python3
"""Validate the V6 static-first global landing, V5 typography and audio UX."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.styles: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "link" and data.get("rel") == "stylesheet":
            self.styles.append(data.get("href", ""))
        if tag == "a":
            self.links.append(data)
        if tag == "script" and data.get("src"):
            self.scripts.append(data)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    value = path.read_text(encoding="utf-8")
    require(bool(value.strip()), f"Empty file: {path.as_posix()}")
    return value


def parse(html: str) -> Page:
    page = Page()
    page.feed(html)
    duplicates = [name for name, count in Counter(page.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")
    return page


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    landing = read(root / "site" / "index.html")
    localized = read(root / "site" / "id" / "index.html")
    site_js = read(root / "site" / "site-v6.js")
    experience_js = read(root / "site" / "experience-v4.js")
    experience_css = read(root / "site" / "experience-v4.css")
    typography_css = read(root / "site" / "typography-v5.css")
    hardening_css = read(root / "site" / "hardening-v6.css")
    landing_css = read(root / "site" / "landing-v2.css")

    landing_page = parse(landing)
    localized_page = parse(localized)

    for page, prefix in ((landing_page, ""), (localized_page, "../")):
        expected_styles = {
            f"{prefix}landing-v2.css",
            f"{prefix}experience-v4.css",
            f"{prefix}typography-v5.css",
            f"{prefix}hardening-v6.css",
        }
        require(expected_styles.issubset(set(page.styles)), f"Missing static V6 styles for prefix {prefix!r}")
        script_sources = {item.get("src", "") for item in page.scripts}
        require(f"{prefix}site-v6.js" in script_sources, "Single V6 release controller is missing")
        require(f"{prefix}experience-v4.js" in script_sources, "Static audio experience controller is missing")
        require(all(item.get("defer") == "" for item in page.scripts), "Public scripts must use defer")

    for phrase in (
        "Musical VST3 audio enhancer for Windows",
        "Fuller, clearer and more dimensional sound",
        "Mas Ari Signature brings the music closer.",
        "Shape the result, not the complexity.",
        "40 curated starting points",
        "Premium sound. Focused workflow. Zero pressure.",
    ):
        require(phrase in landing, f"Missing English product story: {phrase}")

    for phrase in (
        "VST3 audio enhancer musikal untuk Windows",
        "Suara lebih berisi, jernih, dan berdimensi",
        "Mas Ari Signature membawa musik terasa lebih dekat.",
        "40 titik awal terkurasi",
    ):
        require(phrase in localized, f"Missing Indonesian product story: {phrase}")

    require('hreflang="en"' in landing and 'hreflang="id"' in landing and 'hreflang="x-default"' in landing, "English hreflang must be static")
    require('hreflang="en"' in localized and 'hreflang="id"' in localized and 'hreflang="x-default"' in localized, "Indonesian hreflang must be static")
    require('class="mobile-nav"' in landing and 'class="mobile-nav"' in localized, "Native mobile navigation is missing")
    require('aria-current="page"' in landing and 'aria-current="page"' in localized, "Current language state is missing")

    for token in (
        "setupProductPreview",
        "setupPresetExplorer",
        "preset-explorer-ready",
        "preset-browser",
        "setupScrollReveals",
        "setupNavigationState",
        "setupPointerDepth",
        "setupSignalAccent",
        "prefers-reduced-motion",
        "data-experience-layer",
    ):
        require(token in experience_js, f"Audio experience is missing {token}")

    require("document.createElement('link')" not in experience_js, "Experience script must not inject stylesheets")
    require("createElement('link')" not in site_js, "Release controller must not inject stylesheets")
    require("latest-release.js" not in landing + localized, "Second release resolver must not be loaded")
    require("fetch(`${siteBase}/release.json`" in site_js, "V6 must use one localized-safe manifest request")
    require("officialReleaseUrl" in site_js and "releases/download/" in site_js, "Official release URL validation is missing")
    require("data-release-status" in landing and "data-release-status" in localized, "Release status contract is missing")

    for token in (
        "--landing-copy: 16px",
        "--type-card: 14.5px",
        "--type-lead: clamp(16.5px",
        'font-family: "Segoe UI Variable Text"',
        "text-wrap: pretty",
        ".faq-grid p",
        "--type-card: 15px",
    ):
        require(token in typography_css, f"Readable typography is missing {token}")

    for token in (".language-switch a", ".mobile-nav", ".mobile-nav-panel", "@media (max-width: 860px)"):
        require(token in hardening_css, f"V6 shell style is missing {token}")

    require("font-weight: 610" in landing_css, "Refined headline weight must remain")
    require("browser.append(toolbar, groupsContainer)" in experience_js, "Preset toolbar and groups must share one browser column")
    require("grid-template-columns: minmax(280px, .68fr) minmax(0, 1.32fr);" in experience_css, "Preset explorer desktop grid is missing")
    require("@media (prefers-reduced-motion: reduce)" in experience_css, "Reduced-motion support is missing")

    for name, content in (("experience", experience_css), ("typography", typography_css), ("hardening", hardening_css)):
        require(content.count("{") == content.count("}"), f"{name} stylesheet has unbalanced braces")

    public_text = "\n".join((landing, localized, site_js, experience_js, experience_css, typography_css, hardening_css))
    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited token: {token}")

    print(
        "V6 premium validation passed: static EN/ID SEO, hyperlink language navigation, one release controller, "
        "native mobile menu, readable typography, stable preset browser and restrained audio motion."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
