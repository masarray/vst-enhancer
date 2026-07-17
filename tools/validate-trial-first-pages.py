#!/usr/bin/env python3
"""Validate the trial-first landing and separated optional-activation page."""

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
        self.meta: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if "data-en" in data or "data-id" in data:
            if not data.get("data-en") or not data.get("data-id"):
                raise AssertionError(f"Missing bilingual value on <{tag}>")
            self.translated += 1
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
    require(value.strip() != "", f"Empty file: {path.as_posix()}")
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
    trial_css = read(root / "site" / "trial.css")
    trial_js = read(root / "site" / "trial-page.js")
    activation_js = read(root / "site" / "activation" / "activation.js")
    release = json.loads(read(root / "site" / "release.json"))

    landing_parser = parse(landing)
    activation_parser = parse(activation)

    require(landing_parser.translated >= 150, "Trial landing needs at least 150 bilingual elements")
    require(activation_parser.translated >= 45, "Activation page needs at least 45 bilingual elements")

    landing_description = next(
        (item.get("content", "") for item in landing_parser.meta if item.get("name") == "description"),
        "",
    )
    require("365 days" in landing_description, "Landing description must state the evaluation duration")
    require("obligation to buy" in landing_description, "Landing description must state no purchase obligation")

    for phrase in (
        "Every control for 365 days",
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
        "Your music is the real demo",
        "Download free for Windows",
    ):
        require(phrase in landing, f"Landing is missing trial-first phrase: {phrase}")

    require("USD 25" not in landing, "Price must not appear on the main trial landing")
    require('href="activation/"' in landing, "Main landing must link the separate activation page")
    require('id="purchase-status" hidden' in landing, "Checkout state must remain non-prominent on the trial landing")
    require(landing.find("commercially code-signed") > landing.find('id="download"'), "Unsigned disclosure must appear in the download/installation journey, not the hero")
    require('data-installer-cta' in landing, "Trial landing must expose release-driven installer CTAs")

    robots = next(
        (item.get("content", "") for item in activation_parser.meta if item.get("name") == "robots"),
        "",
    )
    require(robots == "noindex,follow", "Activation page must remain noindex while checkout is unavailable")
    require("USD 25" in activation, "Activation page must contain the published activation price")
    require("not a donation" in activation.lower(), "Activation page must distinguish a licence purchase from a donation")
    require("JUCE" in activation, "Activation page must explain applicable JUCE licensing support")
    require("Windows code signing" in activation, "Activation page must explain trusted Windows distribution support")
    require("../release.json" in activation_js, "Activation page must read the shared release manifest")
    require("OFFICIAL_ASSET_PREFIX" in trial_js, "Trial CTA script must validate installer asset paths")

    require(release.get("purchaseObligation") is False, "release.json must declare purchaseObligation=false")
    require(release.get("purchaseCheckoutAvailable") is False, "Checkout must remain disabled until configured")
    require(release.get("activationPageUrl") == "https://masarray.github.io/vst-enhancer/activation/", "activationPageUrl mismatch")
    require("purchaseUrl" not in release, "Disabled checkout must not publish a purchaseUrl")

    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in "\n".join((landing, activation, trial_css, trial_js, activation_js)), f"Prohibited public token: {token}")

    print(
        "Trial-first validation passed: "
        f"{landing_parser.translated} landing translations, "
        f"{activation_parser.translated} activation translations, "
        "price separated, checkout disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
