#!/usr/bin/env python3
"""Validate compact audience coverage and readable bilingual information architecture."""

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


def parse(html: str) -> LandingParser:
    parser = LandingParser()
    parser.feed(html)
    duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")
    return parser


def validate_page(html: str, *, language: str) -> LandingParser:
    parser = parse(html)
    common_sections = {"main", "workflow", "features", "presets", "technical", "download", "evaluation", "privacy", "faq", "legal"}
    required_sections = common_sections | ({"sound"} if language == "id" else {"for-you"})
    missing = sorted(required_sections.difference(parser.ids))
    require(not missing, f"{language.upper()} missing reading paths: {missing}")
    require(9 <= parser.details <= 11, f"{language.upper()} expected 9-11 disclosures, found {parser.details}")
    require(html.count("<section") <= 10, f"{language.upper()} landing should not exceed ten major sections")
    require('id="mobile-download-bar"' in html, f"{language.upper()} missing mobile sticky download CTA")
    return parser


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    english = (root / "site" / "index.html").read_text(encoding="utf-8")
    indonesian = (root / "site" / "id" / "index.html").read_text(encoding="utf-8")
    css = (root / "site" / "trial.css").read_text(encoding="utf-8")

    en = validate_page(english, language="en")
    id_page = validate_page(indonesian, language="id")

    for phrase in (
        "First-time user", "Musician &amp; creator", "Producer", "Audio engineer",
        "VST3 or Standalone?", "Installation and verification — four steps",
        "No account or card", "No automatic charge", "No obligation to buy",
        "Local processing", "Official download", "41 curated starting points", "Blues Club",
    ):
        require(phrase in english, f"Missing English public guidance: {phrase}")

    for phrase in (
        "Pengguna awam", "Musisi &amp; kreator", "Produser", "Audio engineer",
        "VST3 atau Standalone?", "Instalasi dan verifikasi — empat langkah",
        "Tanpa akun atau kartu", "Tanpa tagihan otomatis", "Tanpa kewajiban membeli",
        "Processing lokal", "Unduhan resmi", "41 titik awal terkurasi", "Blues Club",
    ):
        require(phrase in indonesian, f"Missing Indonesian public guidance: {phrase}")

    require("USD 25" not in english + indonesian, "Price must remain outside the evaluation landing")
    require("activation/" in en.links and "../activation/" in id_page.links, "Both landing pages must retain optional activation links")
    require("SHA256SUMS.txt" in english and "SHA256SUMS.txt" in indonesian, "Missing checksum guidance")

    for selector in (
        ".audience-compact", ".test-flow", ".preset-strip", ".format-inline",
        ".install-disclosure", ".evaluation-compact", ".privacy-compact", ".mobile-download-bar",
    ):
        require(selector in css, f"Missing compact presentation style: {selector}")

    require(css.count("{") == css.count("}"), "Unbalanced CSS braces")
    require("--micro: 10px" in css and "--small: 11px" in css and "--copy: 12px" in css, "Typography scale changed")
    require("font-family: Inter" in css, "Inter must remain the primary font")

    print(
        "Audience/readability validation passed: separate EN/ID pages, compact disclosures, "
        "four audience paths, 41 presets, merged technical/download flow and mobile CTA."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
