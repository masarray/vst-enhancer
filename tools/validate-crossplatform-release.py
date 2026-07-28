#!/usr/bin/env python3
"""Validate public cross-platform release copy and provenance invariants."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"[FAILED] {message}")


def read(path: str) -> str:
    target = ROOT / path
    if not target.is_file():
        fail(f"Required file is missing: {path}")
    return target.read_text(encoding="utf-8")


def require(text: str, marker: str, label: str) -> None:
    if marker not in text:
        fail(f"{label} is missing required marker: {marker}")


def reject(text: str, marker: str, label: str) -> None:
    if marker in text:
        fail(f"{label} contains prohibited or stale text: {marker}")


def main() -> int:
    readme = read("README.md")
    changelog = read("CHANGELOG.md")
    provenance = read("RELEASE-PROVENANCE.md")
    release = json.loads(read("site/release.json"))
    site_en = read("site/index.html")
    site_id = read("site/id/index.html")
    experience = read("site/experience-v4.js")

    require(readme, "Windows and macOS", "README")
    require(readme, "macOS 11 or later", "README")
    require(readme, "RELEASE-PROVENANCE.md", "README")
    require(readme, "Rp399.000", "README")
    reject(readme, "Musical Audio Enhancement for Windows\n", "README title")

    require(changelog, "## Unreleased", "CHANGELOG")
    require(changelog, "Built and audited Windows x64 binaries locally on Windows.", "CHANGELOG v0.5.20")
    require(changelog, "single approved manual workflow", "CHANGELOG v0.5.20")
    reject(changelog, "GitHub Actions was not used", "CHANGELOG")
    for marker in ("â€”", "ï»¿", "ðŸ", "Ã"):
        reject(changelog, marker, "CHANGELOG encoding")
    if changelog.index("## Unreleased") > changelog.index("## v0.5.20"):
        fail("Unreleased changes must appear before published versions.")

    expected_platforms = ["windows-x64", "macos-universal"]
    if release.get("version") != "v0.5.20":
        fail(f"site/release.json version is {release.get('version')!r}, expected 'v0.5.20'.")
    if release.get("platforms") != expected_platforms:
        fail(f"site/release.json platforms are {release.get('platforms')!r}, expected {expected_platforms!r}.")
    if release.get("macArchitectures") != ["arm64", "x86_64"]:
        fail("macOS release architectures must be arm64 + x86_64.")
    if release.get("macDeploymentTarget") != "11.0":
        fail("macOS deployment target must be 11.0.")
    if release.get("macDeveloperIdSigned") is not False:
        fail("macDeveloperIdSigned must remain false until Developer ID signing is implemented.")
    if release.get("macNotarized") is not False:
        fail("macNotarized must remain false until notarization is implemented.")
    if release.get("macAdHocSigned") is not True:
        fail("macAdHocSigned must be true for the current macOS package disclosure.")
    for field in ("macDmgUrl", "macVst3Url", "macStandaloneUrl", "macChecksumsUrl"):
        value = release.get(field)
        if not isinstance(value, str) or "releases/download/v0.5.20/" not in value:
            fail(f"Invalid or stale macOS release URL field: {field}={value!r}")

    for label, html in (("English landing", site_en), ("Indonesian landing", site_id)):
        require(html, "macOS 11", label)
        require(html, 'id="mac-download-option"', label)
        require(html, 'id="mac-dmg-link"', label)
        require(html, "SHA256SUMS.txt", label)
        reject(html, "GitHub Actions was not used", label)

    for marker in (
        "Musical VST3 audio enhancer for Windows and macOS",
        "Official Windows and macOS downloads",
        "Mac package",
        "Download Mac DMG",
        'operatingSystem":"Windows 10/11 64-bit; macOS 11 or later Universal"',
    ):
        require(site_en, marker, "static English cross-platform landing")
    reject(site_en, "<h3>Paket Mac</h3>", "static English cross-platform landing")

    for marker in (
        "VST3 audio enhancer musikal untuk Windows dan macOS",
        "Unduhan resmi Windows dan macOS",
        "Paket Mac",
        "Unduh DMG Mac",
        'operatingSystem":"Windows 10/11 64-bit; macOS 11 atau lebih baru Universal"',
    ):
        require(site_id, marker, "static Indonesian cross-platform landing")

    for marker in (
        "setupCrossPlatformCopy",
        "Musical VST3 Audio Enhancer for Windows and macOS",
        "VST3 audio enhancer musikal untuk Windows dan macOS",
        "Official Windows and macOS downloads",
        "Unduhan resmi Windows dan macOS",
        "Mac package",
        "Download Mac DMG",
        "data-crossplatform-copy",
    ):
        require(experience, marker, "live cross-platform landing normalization")

    require(provenance, "2170310044c75dc5525ccb3901a7fecca1a5a64d", "release provenance")
    require(provenance, "runner-local compatibility preparation", "release provenance")
    require(provenance, "Public disclosure boundary", "release provenance")

    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    workflow_names = [path.name for path in workflows]
    if workflow_names != ["build-macos-and-publish.yml"]:
        fail(f"Expected exactly one approved public workflow, found: {workflow_names}")

    print("[PASS] Static and live cross-platform release copy, metadata and provenance are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
