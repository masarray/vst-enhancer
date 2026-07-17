#!/usr/bin/env python3
"""Validate compact audience coverage and readable information architecture."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class LandingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.translated = 0
        self.details = 0
        self.links: list[str] = []

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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    html = (root / "site" / "index.html").read_text(encoding="utf-8")
    css = (root / "site" / "trial.css").read_text(encoding="utf-8")

    parser = LandingParser()
    parser.feed(html)
    duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")

    required_sections = {
        "main",
        "for-you",
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
    missing = sorted(required_sections.difference(parser.ids))
    require(not missing, f"Missing reading paths: {missing}")
    require(parser.translated >= 120, f"Only {parser.translated} bilingual elements found")
    require(9 <= parser.details <= 11, f"Expected 9-11 disclosures, found {parser.details}")
    require(html.count("<section") <= 10, "Landing should not exceed ten major sections")

    for phrase in (
        "First-time user",
        "Musician & creator",
        "Producer",
        "Audio engineer",
        "Pengguna awam",
        "Musisi & kreator",
        "Produser",
        "VST3 or Standalone?",
        "Installation and verification — four steps",
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
        "Local processing",
        "Official download",
    ):
        require(phrase in html, f"Missing public guidance: {phrase}")

    require("USD 25" not in html, "Price must remain outside the trial landing")
    require("activation/" in parser.links, "Landing must retain optional activation link")
    require("SHA256SUMS.txt" in html, "Missing checksum guidance")
    require('id="mobile-download-bar"' in html, "Missing mobile sticky download CTA")

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
    require("--micro: 10px" in css and "--small: 11px" in css and "--copy: 12px" in css, "Typography scale changed")
    require("font-family: Inter" in css, "Inter must remain the primary font")

    print(
        "Audience/readability validation passed: "
        f"{parser.translated} bilingual elements, "
        f"{parser.details} compact FAQ/disclosures, "
        "four audience paths, merged technical/download flow and mobile CTA."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
