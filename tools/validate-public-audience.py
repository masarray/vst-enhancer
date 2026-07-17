#!/usr/bin/env python3
"""Validate public readability and audience coverage for the ArSonKuPik landing page."""

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
        if "id" in data:
            self.ids.append(data["id"])
        if "data-en" in data or "data-id" in data:
            assert data.get("data-en"), f"Missing data-en on <{tag}>"
            assert data.get("data-id"), f"Missing data-id on <{tag}>"
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
    page = root / "site" / "index.html"
    css_path = root / "site" / "trial.css"

    require(page.is_file(), "Missing site/index.html")
    require(css_path.is_file(), "Missing site/trial.css")

    html = page.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")

    parser = LandingParser()
    parser.feed(html)

    duplicates = [value for value, count in Counter(parser.ids).items() if count > 1]
    require(not duplicates, f"Duplicate HTML ids: {duplicates}")

    required_sections = {
        "main",
        "for-you",
        "listen",
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
    require(not missing, f"Missing public-reading sections: {missing}")

    require(parser.translated >= 200, f"Only {parser.translated} bilingual elements found")
    require(parser.details >= 14, f"Only {parser.details} FAQ entries found")

    required_audiences = (
        "First-time user",
        "Musician & creator",
        "Producer",
        "Audio engineer",
        "Pengguna awam",
        "Musisi & kreator",
        "Produser",
    )
    for phrase in required_audiences:
        require(phrase in html, f"Missing audience coverage: {phrase}")

    required_plain_language = (
        "What is the difference between VST3 and Standalone?",
        "Apa perbedaan VST3 dan Standalone?",
        "Use inside a compatible DAW",
        "Use as a standalone application",
        "Install in four steps",
        "Instalasi dalam empat langkah",
    )
    for phrase in required_plain_language:
        require(phrase in html, f"Missing plain-language guidance: {phrase}")

    required_trust = (
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
        "Local audio processing",
        "Official download",
    )
    for phrase in required_trust:
        require(phrase in html, f"Missing trust statement: {phrase}")

    require("USD 25" not in html, "Price must remain outside the public trial landing")
    require("activation/" in parser.links, "Landing must retain a low-emphasis activation link")
    require("data-installer-cta" in html, "Missing release-driven installer CTAs")
    require("SHA256SUMS.txt" in html, "Missing checksum guidance")

    required_styles = (
        ".audience-grid",
        ".test-flow",
        ".workflow-rail",
        ".format-grid",
        ".spec-list",
        ".install-guide",
        ".verification-disclosure",
    )
    for selector in required_styles:
        require(selector in css, f"Missing presentation style: {selector}")

    require(css.count("{") == css.count("}"), "Unbalanced CSS braces")

    print(
        "Audience/readability validation passed: "
        f"{parser.translated} bilingual elements, "
        f"{parser.details} FAQ entries, "
        "four audience paths, plain-language formats and installation guidance."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
