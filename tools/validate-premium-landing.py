#!/usr/bin/env python3
"""Validate the V3 professional product experience and progressive proof layer."""

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
    experience_js = read(root / "site" / "experience-v3.js")
    experience_css = read(root / "site" / "experience-v3.css")
    landing_css = read(root / "site" / "landing-v2.css")

    require('href="landing-v2.css"' in landing, "Core V2 layout must remain statically loaded")
    require("experience-v3.js" in trial_js, "Landing must load the V3 progressive experience")
    require("v3-professional-proof" in trial_js, "V3 experience version marker is missing")
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
        "HTMLDialogElement",
        "aria-haspopup",
        "setupPresetExplorer",
        "data-preset-filter",
        "preset-chip",
        "data-experience-layer",
    ):
        require(token in experience_js, f"V3 experience is missing {token}")

    for selector in (
        ".product-preview-dialog",
        ".product-preview-close",
        ".preset-toolbar",
        ".preset-filter",
        ".preset-result-count",
        ".preset-chip",
    ):
        require(selector in experience_css, f"V3 experience style is missing {selector}")

    require("--landing-copy: 15px" in landing_css, "Readable 15 px landing typography must remain")
    require("font-weight: 610" in landing_css, "Refined headline weight must remain")
    require("@media (max-width: 740px)" in experience_css, "V3 mobile treatment is missing")
    require(experience_css.count("{") == experience_css.count("}"), "V3 stylesheet has unbalanced braces")
    require(experience_js.count("{") == experience_js.count("}"), "V3 script has unbalanced braces")

    require("window.location.assign" in trial_js, "Language controls must navigate to stable locale URLs")
    require("stopImmediatePropagation" in trial_js, "Legacy in-page language handlers must be neutralised")
    require("askp:release-ready" in trial_js, "Canonical page language must be restored after release rendering")
    require("IntersectionObserver" in trial_js, "Mobile download CTA must remain viewport-aware")

    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in "\n".join((landing, localized, trial_js, experience_js, experience_css)), f"Prohibited token: {token}")

    print(
        "V3 premium validation passed: stable locale routing, accessible full-size product preview, "
        "filterable 40-preset explorer, readable typography and responsive progressive enhancement."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
