#!/usr/bin/env python3
"""Validate the V2 product-first premium hierarchy for the public landing."""

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
    trial_js = read(root / "site" / "trial-page.js")
    landing_css = read(root / "site" / "landing-v2.css")

    require('href="landing-v2.css"' in landing, "Landing must load the V2 visual layer statically")
    require("premium-polish.css" not in trial_js, "Visual CSS must not be injected after first paint")
    require("data-visual-polish', 'v2-product-first'" in trial_js, "Landing must expose the V2 polish version")

    for phrase in (
        "Musical VST3 audio enhancer for Windows",
        "Fuller, clearer and more dimensional sound",
        "Mas Ari Signature brings the music closer.",
        "More alive",
        "Detail you can feel",
        "Live-like dimension",
        "Shape the result, not the complexity.",
        "40 curated starting points",
        "Premium sound. Focused workflow. Zero pressure.",
    ):
        require(phrase in landing, f"Missing product-first story: {phrase}")

    for selector in (
        ".landing-hero",
        ".product-stage",
        ".signature-grid",
        ".signature-panel",
        ".signature-pillars",
        ".outcome-grid",
        ".preset-universe",
        ".preset-groups",
        ".freedom-grid",
        ".mobile-download-bar",
    ):
        require(selector in landing_css, f"Missing premium visual rule: {selector}")

    require("--landing-copy: 15px" in landing_css, "Desktop body typography must remain 15 px")
    require("font-size: clamp(2.45rem" in landing_css, "Hero typography scale is missing")
    require("font-weight: 610" in landing_css, "Headline weight must remain refined rather than heavy")
    require("grid-template-columns: repeat(4" in landing_css, "Four sonic outcomes must retain their desktop hierarchy")
    require("@media (max-width: 740px)" in landing_css, "Mobile hierarchy breakpoint is missing")
    require("font-size: 15px" in landing_css, "Mobile body typography must remain readable")
    require(landing_css.count("{") == landing_css.count("}"), "Landing stylesheet has unbalanced braces")

    require('id="distribution-banner"' in landing, "Static release status markup must remain available")
    require("statusBar.hidden = true" in trial_js, "Top release status must stay out of the product introduction")
    require("download-release-status" in trial_js, "Release status must remain near the download decision")
    require("IntersectionObserver" in trial_js, "Mobile download CTA must remain viewport-aware")

    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in "\n".join((landing, trial_js, landing_css)), f"Prohibited token: {token}")

    print(
        "V2 premium landing validation passed: product-category hero, Mas Ari Signature flagship story, "
        "sonic outcomes, 40-preset universe, refined typography, static CSS and responsive download journey."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
