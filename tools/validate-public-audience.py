#!/usr/bin/env python3
"""Validate static localized audience coverage and readable information architecture."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.details = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "details":
            self.details += 1
        if tag == "a" and data.get("href"):
            self.links.append(data["href"])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse(text: str, label: str) -> LandingParser:
    result = LandingParser()
    result.feed(text)
    duplicates = [value for value, count in Counter(result.ids).items() if count > 1]
    require(not duplicates, f"{label} duplicate HTML ids: {duplicates}")
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    localized = (root / "site" / "id" / "index.html").read_text(encoding="utf-8")
    css = (root / "site" / "trial.css").read_text(encoding="utf-8")

    parser = parse(html, "English")
    localized_parser = parse(localized, "Indonesian")
    shared_sections = {
        "main",
        "workflow",
        "features",
        "presets",
        "technical",
        "download",
        "evaluation",
        "privacy",
        "faq",
        "legal",
    }
    require(not shared_sections.difference(parser.ids) and "for-you" in parser.ids,
            "English reading paths are incomplete")
    require(not shared_sections.difference(localized_parser.ids) and "sound" in localized_parser.ids,
            "Indonesian reading paths are incomplete")
    require(12 <= parser.details <= 14 and 12 <= localized_parser.details <= 14,
            "Expected 12-14 disclosures on each localized page")
    require(html.count("<section") <= 11 and localized.count("<section") <= 11,
            "Localized landing should not exceed eleven major sections")

    for phrase in (
        "First-time user",
        "Musician &amp; creator",
        "Producer",
        "Audio engineer",
        "VST3 or Standalone?",
        "Installation and verification",
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
        "Local processing",
        "Official download",
        "Official Windows and macOS downloads",
        "Mac package",
        "13 professional starting points",
    ):
        require(phrase in html, f"Missing English public guidance: {phrase}")

    for phrase in (
        "Pengguna awam",
        "Musisi &amp; kreator",
        "Produser",
        "Audio engineer",
        "VST3 atau Standalone?",
        "Instalasi dan verifikasi",
        "Tanpa akun atau kartu",
        "Tanpa tagihan otomatis",
        "Processing lokal",
        "Unduhan resmi Windows dan macOS",
        "Paket Mac",
        "13 titik awal profesional",
    ):
        require(phrase in localized, f"Missing Indonesian public guidance: {phrase}")

    require("USD 25" not in html + localized, "Price must remain outside the trial landing")
    require("activation/" in parser.links, "English landing must retain optional activation link")
    require("../activation/" in localized_parser.links, "Indonesian landing must retain optional activation link")
    require("SHA256SUMS.txt" in html + localized, "Missing checksum guidance")
    require('id="mobile-download-bar"' in html and 'id="mobile-download-bar"' in localized,
            "Missing localized mobile sticky download CTA")

    for selector in (
        ".audience-compact",
        ".test-flow",
        ".preset-strip",
        ".format-inline",
        ".install-disclosure",
        ".evaluation-compact",
        ".privacy-compact",
        ".mobile-download-bar",
    ):
        require(selector in css, f"Missing compact presentation style: {selector}")

    require(css.count("{") == css.count("}"), "Unbalanced CSS braces")
    require("--micro: 10px" in css and "--small: 11px" in css and "--copy: 12px" in css,
            "Typography scale changed")
    require("font-family: Inter" in css, "Inter must remain the primary font")

    print(
        "Audience/readability validation passed: static cross-platform EN/ID routes, "
        f"{parser.details}/{localized_parser.details} compact FAQ/disclosures, four audience paths, "
        "merged technical/download flow and mobile CTA."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
