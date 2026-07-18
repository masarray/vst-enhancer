#!/usr/bin/env python3
"""Validate the P1 premium visual hierarchy for the public landing."""

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
    premium_css = read(root / "site" / "premium-polish.css")
    trial_css = read(root / "site" / "trial.css")

    require("premium-polish.css" in trial_js, "Landing must load the P1 premium visual layer")
    require("data-visual-polish" in trial_js, "Landing must expose the active visual-polish version")

    require('id="distribution-banner"' in landing, "Static release status markup must remain available")
    require("statusBar.hidden = true" in trial_js, "Top release status must be hidden from the product journey")
    require(".status-bar" in premium_css and "display: none !important" in premium_css, "Status bar CSS guard is missing")
    require("download-release-status" in trial_js, "Release status must be represented in the download flow")
    require("Latest published release" in trial_js, "Download release summary is missing")

    for selector in (
        ".hero-promises",
        ".hero-trust",
        ".product-stage .stage-label",
        ".product-stage figcaption",
    ):
        require(selector in premium_css, f"Hero simplification rule is missing: {selector}")
        require(selector in trial_js, f"Hero accessibility simplification is missing: {selector}")

    require("trustFacts" in trial_js, "Trust strip must be rewritten around compatibility and trust")
    for phrase in (
        "Windows 10/11 x64",
        "VST3 + Standalone",
        "Local processing",
        "Official releases",
        "Direct installer with SHA-256 verification.",
    ):
        require(phrase in trial_js, f"Compatibility trust fact is missing: {phrase}")

    require(".nav-download" in premium_css, "Download navigation style is missing")
    require("rgba(190, 145, 255" in premium_css, "Primary download CTA must use the violet action family")
    require("rgba(103, 217, 163, .42)" not in premium_css, "Primary CTA must not return to the green status treatment")

    require("@media (max-width: 1060px)" in premium_css, "Tablet hierarchy breakpoint is missing")
    require(".trial-hero .hero-copy" in premium_css and "order: 1" in premium_css, "Hero copy must appear first on tablet/mobile")
    require(".trial-hero .product-stage" in premium_css and "order: 2" in premium_css, "Product screenshot must follow hero copy")

    require(".section" in premium_css and "border-top: 0" in premium_css, "Repeated section separators must be removed")
    require(".audience-compact" in premium_css and "background: transparent" in premium_css, "Audience area must use an open editorial treatment")
    require(".test-flow" in premium_css and "border-radius: 0" in premium_css, "Three-minute test must not remain a boxed dashboard block")
    require(".preset-strip" in premium_css and "display: flex" in premium_css, "Preset roles must use compact chips")
    require(".format-inline" in premium_css and "background: transparent" in premium_css, "Format summary must use an open layout")
    require(".privacy-compact" in premium_css and "border-left: 2px solid" in premium_css, "Privacy note must use a restrained editorial accent")

    require("--micro: 10px" in trial_css, "Desktop micro typography must remain 10 px")
    require("--copy: 12px" in trial_css, "Desktop body typography must remain 12 px")
    require("--micro: 12px" in trial_js and "--copy: 13px" in trial_js, "Mobile typography must remain 12-13 px")
    require(premium_css.count("{") == premium_css.count("}"), "Premium stylesheet has unbalanced braces")

    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in "\n".join((landing, trial_js, premium_css)), f"Prohibited token: {token}")

    print(
        "P1 premium landing validation passed: "
        "status moved to download, simplified hero, violet CTA system, copy-first responsive order, "
        "open editorial surfaces and retained 12-13 px mobile typography."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
