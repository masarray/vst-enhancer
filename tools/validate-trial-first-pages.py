#!/usr/bin/env python3
"""Validate the trial-first funnel, single release controller, and canonical mode."""

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
        self.details = 0
        self.meta: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if data.get("id"):
            self.ids.append(data["id"])
        if "data-en" in data or "data-id" in data:
            if not data.get("data-en") or not data.get("data-id"):
                raise AssertionError(f"Missing bilingual value on <{tag}>")
            self.translated += 1
        if tag == "details":
            self.details += 1
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


def validate_trial_content(landing: str, activation: str, landing_parser: PageParser, activation_parser: PageParser) -> None:
    require(landing_parser.translated >= 200, "Trial landing needs at least 200 bilingual elements")
    require(landing_parser.details >= 14, "Trial landing needs at least 14 FAQ/disclosure entries")
    require(activation_parser.translated >= 45, "Activation page needs at least 45 bilingual elements")

    landing_description = next(
        (item.get("content", "") for item in landing_parser.meta if item.get("name") == "description"),
        "",
    )
    require("365 days" in landing_description, "Landing description must state the evaluation duration")
    require("obligation to buy" in landing_description, "Landing description must state no purchase obligation")

    for phrase in (
        "All controls for 365 days",
        "No account or card",
        "No automatic charge",
        "No obligation to buy",
        "Your own audio is the most relevant demo",
        "Download free for Windows",
        "First-time user",
        "Musician & creator",
        "Producer",
        "Audio engineer",
    ):
        require(phrase in landing, f"Landing is missing trial-first phrase: {phrase}")

    require("USD 25" not in landing, "Price must not appear on the main trial landing")
    require('href="activation/"' in landing, "Main landing must link the separate activation page")
    require('id="purchase-status" hidden' in landing, "Checkout state must remain non-prominent")
    require(
        landing.find("commercially code-signed") > landing.find('id="download"'),
        "Unsigned disclosure must appear in the download journey, not the hero",
    )
    require("data-installer-cta" in landing, "Trial landing must expose release-driven installer CTAs")
    require("What is the difference between VST3 and Standalone?" in landing, "Landing must explain VST3 versus Standalone")
    require("Install in four steps" in landing, "Landing must include beginner installation guidance")

    robots = next(
        (item.get("content", "") for item in activation_parser.meta if item.get("name") == "robots"),
        "",
    )
    require(robots == "noindex,follow", "Activation page must remain noindex while checkout is unavailable")
    require("USD 25" in activation, "Activation page must contain the published activation price")
    require("not a donation" in activation.lower(), "Activation page must distinguish a licence purchase from a donation")
    require("JUCE" in activation, "Activation page must explain applicable JUCE licensing support")
    require("Windows code signing" in activation, "Activation page must explain trusted Windows distribution support")


def validate_single_release_controller(landing: str, app_js: str, trial_js: str) -> None:
    require(
        app_js.count("fetch('./release.json'") == 1,
        "app.js must be the single release.json requester",
    )
    require("fetch(" not in trial_js and "release.json" not in trial_js, "trial-page.js must not fetch release metadata")
    require(
        "querySelectorAll('[data-installer-cta]')" in app_js,
        "The central controller must manage every installer CTA",
    )
    require(
        "button.dataset[currentLanguage]" in app_js,
        "Enabled installer CTAs must preserve their contextual bilingual labels",
    )
    require("askp:release-ready" in app_js, "The central controller must announce its final release state")
    require("officialReleaseUrl" in app_js, "The central controller must validate official release URLs")

    forbidden_metadata_mutations = (
        "document.title",
        "canonical-link",
        "meta[name=\"description\"]",
        "localizedUrl",
    )
    for token in forbidden_metadata_mutations:
        require(token not in app_js, f"app.js must not mutate canonical SEO metadata: {token}")

    require("CANONICAL_URL" in trial_js, "Canonical guard must define one product URL")
    require("link[rel=\"alternate\"][hreflang]" in trial_js, "Canonical guard must remove legacy rendered hreflang alternates")
    require("history.replaceState" in trial_js, "Canonical guard must remove legacy language query parameters")
    require("data-canonical-mode" in trial_js, "Canonical guard must expose its deterministic mode")

    app_script = landing.find('<script src="app.js"></script>')
    guard_script = landing.find('<script src="trial-page.js"></script>')
    require(app_script >= 0 and guard_script > app_script, "Canonical guard must load after the central release controller")


def validate_manifest_and_public_safety(release: dict[str, object], activation_js: str, public_text: str) -> None:
    require("../release.json" in activation_js, "Activation page must read the shared release manifest")
    require(release.get("purchaseObligation") is False, "release.json must declare purchaseObligation=false")
    require(release.get("purchaseCheckoutAvailable") is False, "Checkout must remain disabled until configured")
    require(
        release.get("activationPageUrl") == "https://masarray.github.io/vst-enhancer/activation/",
        "activationPageUrl mismatch",
    )
    require("purchaseUrl" not in release, "Disabled checkout must not publish a purchaseUrl")

    for token in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "ArSonKuPikKeyActivator"):
        require(token not in public_text, f"Prohibited public token: {token}")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    landing = read(root / "site" / "index.html")
    activation = read(root / "site" / "activation" / "index.html")
    styles_css = read(root / "site" / "styles.css")
    trial_css = read(root / "site" / "trial.css")
    app_js = read(root / "site" / "app.js")
    trial_js = read(root / "site" / "trial-page.js")
    activation_js = read(root / "site" / "activation" / "activation.js")
    release = json.loads(read(root / "site" / "release.json"))

    landing_parser = parse(landing)
    activation_parser = parse(activation)

    validate_trial_content(landing, activation, landing_parser, activation_parser)
    validate_single_release_controller(landing, app_js, trial_js)
    validate_manifest_and_public_safety(
        release,
        activation_js,
        "\n".join((landing, activation, styles_css, trial_css, app_js, trial_js, activation_js)),
    )

    require("font-family: Inter" in styles_css, "Public landing must retain Inter as its primary font")

    print(
        "P1 trial-first validation passed: "
        f"{landing_parser.translated} landing translations, "
        f"{activation_parser.translated} activation translations, "
        f"{landing_parser.details} FAQ/disclosure entries, "
        "one release controller, contextual CTAs, deterministic canonical mode."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
