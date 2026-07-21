#!/usr/bin/env python3
"""Validate the V5 readable typography and V4 professional audio-product experience."""

from __future__ import annotations

from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(path: Path) -> str:
    require(path.is_file(), f"Missing file: {path.as_posix()}")
    value = path.read_text(encoding="utf-8")
    require(bool(value.strip()), f"Empty file: {path.as_posix()}")
    return value


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    landing = read(root / "site" / "index.html")
    localized = read(root / "site" / "id" / "index.html")
    trial_js = read(root / "site" / "trial-page.js")
    experience_js = read(root / "site" / "experience-v4.js")
    experience_css = read(root / "site" / "experience-v4.css")
    typography_css = read(root / "site" / "typography-v5.css")
    landing_css = read(root / "site" / "landing-v2.css")

    require('href="landing-v2.css"' in landing, "Core V2 layout must remain statically loaded")
    require("experience-v4.js" in trial_js, "Landing must load the V4 audio experience")
    require("v4-audio-motion" in trial_js, "V4 experience version marker is missing")
    require("typography-v5.css" in trial_js, "Landing must load the V5 readable typography layer")
    require("v5-readable" in trial_js, "V5 typography marker is missing")
    require("premium-polish.css" not in trial_js, "Legacy visual CSS must not return")

    for phrase in (
        "Musical VST3 audio enhancer for Windows",
        "Fuller, clearer and more dimensional sound",
        "Mas Ari Signature brings the music closer.",
        "Shape the result, not the complexity.",
        "40 curated starting points",
        "Premium sound. Focused workflow. Zero pressure.",
    ):
        require(phrase in landing, f"Missing product-first story: {phrase}")

    require("Suara lebih berisi, jernih, dan berdimensi" in localized, "Indonesian product story is missing")
    require("Mas Ari Signature" in localized and "40 preset" in localized, "Indonesian flagship/preset story is incomplete")

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
        require(token in experience_js, f"V4 experience is missing {token}")

    for selector in (
        ".preset-universe.preset-explorer-ready",
        ".preset-browser",
        ".preset-toolbar",
        ".preset-filter",
        ".preset-chip",
        ".motion-ready [data-reveal]",
        ".landing-nav.is-scrolled",
        ".signal-accent",
        ".product-preview-dialog",
    ):
        require(selector in experience_css, f"V4 experience style is missing {selector}")

    require(
        "grid-template-columns: minmax(280px, .68fr) minmax(0, 1.32fr);" in experience_css,
        "Preset explorer must preserve the two-column desktop layout",
    )
    require("browser.append(toolbar, groupsContainer)" in experience_js, "Toolbar and preset groups must share one browser column")
    require("groupsContainer.before(browser)" in experience_js, "Preset browser must be inserted as the second grid child")

    for token in (
        "--landing-copy: 16px",
        "--type-card: 14.5px",
        "--type-lead: clamp(16.5px",
        'font-family: "Segoe UI Variable Text"',
        "text-wrap: pretty",
        ".faq-grid p",
        "font-size: 15px",
        "--type-card: 15px",
    ):
        require(token in typography_css, f"V5 readable typography is missing {token}")

    require("font-weight: 610" in landing_css, "Refined headline weight must remain")
    require("@media (max-width: 740px)" in experience_css, "V4 mobile treatment is missing")
    require("@media (max-width: 740px)" in typography_css, "V5 mobile typography treatment is missing")
    require("@media (prefers-reduced-motion: reduce)" in experience_css, "Reduced-motion safety is missing")
    require(experience_css.count("{") == experience_css.count("}"), "V4 stylesheet has unbalanced braces")
    require(typography_css.count("{") == typography_css.count("}"), "V5 typography stylesheet has unbalanced braces")
    require(experience_js.count("{") == experience_js.count("}"), "V4 script has unbalanced braces")

    require("window.location.assign" in trial_js, "Language controls must navigate to stable locale URLs")
    require("stopImmediatePropagation" in trial_js, "Legacy in-page language handlers must be neutralised")
    require("askp:release-ready" in trial_js, "Canonical page language must be restored after release rendering")
    require("IntersectionObserver" in trial_js, "Mobile download CTA must remain viewport-aware")

    public_text = "\n".join((landing, localized, trial_js, experience_js, experience_css, typography_css))
    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited token: {token}")

    print(
        "V5 premium validation passed: readable 16 px body typography, 14.5-15 px content paragraphs, "
        "stable preset browser, restrained audio motion, accessible preview and reduced-motion support."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
