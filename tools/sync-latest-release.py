#!/usr/bin/env python3
"""Synchronize the public landing metadata with the latest GitHub Release."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

REPOSITORY = "masarray/vst-enhancer"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
RELEASES_ROOT = f"https://github.com/{REPOSITORY}/releases"
DOWNLOAD_PREFIX = f"{RELEASES_ROOT}/download/"
RELEASE_PATH = f"/{REPOSITORY}/releases"
DOWNLOAD_PATH = f"{RELEASE_PATH}/download/"
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


def fail(message: str) -> None:
    raise RuntimeError(message)


def official_release_url(value: Any, *, asset: bool = False) -> str | None:
    if not isinstance(value, str) or len(value) > 800:
        return None
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname != "github.com" or parsed.params or parsed.query or parsed.fragment:
        return None
    valid_path = parsed.path.startswith(DOWNLOAD_PATH) if asset else (
        parsed.path == RELEASE_PATH or parsed.path.startswith(RELEASE_PATH + "/")
    )
    return value if valid_path else None


def score_installer(name: str) -> int:
    lower = name.lower()
    if not lower.endswith(".exe"):
        return -1
    score = 0
    if "arsonkupik" in lower:
        score += 20
    if "windows" in lower:
        score += 10
    if "x64" in lower or "win64" in lower:
        score += 8
    if "setup" in lower:
        score += 12
    if "installer" in lower:
        score += 10
    if "portable" in lower:
        score -= 30
    if "activator" in lower or "key" in lower:
        score -= 100
    return score


def clean_markdown(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", value)
    value = re.sub(r"[`*_~>#]", "", value)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def extract_highlights(body: Any, maximum: int = 6) -> list[str]:
    if not isinstance(body, str):
        return []
    ignored = re.compile(r"^(full changelog|contributors?|new contributors?|assets?|checksums?|sha-?256)\b", re.I)
    seen: set[str] = set()
    result: list[str] = []

    def add(value: str) -> None:
        cleaned = clean_markdown(value)
        cleaned = re.sub(r"^[-+*]\s+", "", cleaned)
        cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned)
        key = cleaned.casefold()
        if len(cleaned) < 8 or ignored.match(cleaned) or key in seen:
            return
        seen.add(key)
        result.append(cleaned[:217].rstrip() + "…" if len(cleaned) > 220 else cleaned)

    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^[-+*]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            add(stripped)

    if not result:
        for paragraph in re.split(r"\r?\n\s*\r?\n", body):
            stripped = paragraph.strip()
            if stripped and not stripped.startswith("#"):
                add(stripped)

    return result[:maximum]


def choose_asset(assets: list[dict[str, str]], predicate, scorer=lambda _: 0) -> dict[str, str] | None:
    matches = [asset for asset in assets if predicate(asset["name"].lower())]
    return max(matches, key=lambda asset: scorer(asset["name"]), default=None)


def normalize_release(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("draft") is True or payload.get("prerelease") is True:
        fail("Latest GitHub release is a draft or prerelease")
    version = payload.get("tag_name")
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        fail(f"Invalid latest release tag: {version!r}")
    release_url = official_release_url(payload.get("html_url"))
    if not release_url:
        fail("Latest release URL is outside the official repository")

    assets: list[dict[str, str]] = []
    for raw in payload.get("assets") or []:
        if not isinstance(raw, dict) or raw.get("state") not in (None, "uploaded"):
            continue
        name = raw.get("name")
        url = official_release_url(raw.get("browser_download_url"), asset=True)
        if isinstance(name, str) and url:
            assets.append({"name": name, "url": url})

    installer = choose_asset(assets, lambda name: name.endswith(".exe"), score_installer)
    if not installer or score_installer(installer["name"]) < 20:
        fail("No safe official Windows installer was found in the latest release")

    vst3 = choose_asset(assets, lambda name: name.endswith(".zip") and "vst3" in name)
    standalone = choose_asset(assets, lambda name: name.endswith(".zip") and "standalone" in name)
    checksums = choose_asset(assets, lambda name: name == "sha256sums.txt" or "sha256" in name)
    if not vst3 or not standalone or not checksums:
        fail("Latest release is missing VST3, Standalone, or SHA-256 assets")

    return {
        "version": version,
        "releaseName": clean_markdown(str(payload.get("name") or version)),
        "publishedAt": payload.get("published_at") or payload.get("created_at"),
        "releaseUrl": release_url,
        "installerUrl": installer["url"],
        "installerName": installer["name"],
        "vst3Url": vst3["url"],
        "standaloneUrl": standalone["url"],
        "checksumsUrl": checksums["url"],
        "releaseHighlights": extract_highlights(payload.get("body")),
    }


def load_payload(fixture: Path | None, *, attempts: int = 3, initial_delay: float = 1.5) -> dict[str, Any]:
    if fixture:
        return json.loads(fixture.read_text(encoding="utf-8"))

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ArSonKuPik-pages-sync/1.1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, max(1, attempts) + 1):
        request = urllib.request.Request(API_URL, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < attempts:
                delay = initial_delay * attempt
                print(
                    f"Release API attempt {attempt}/{attempts} failed ({exc}); retrying in {delay:.1f}s.",
                    file=sys.stderr,
                )
                time.sleep(delay)

    fail(f"Could not fetch latest GitHub Release after {attempts} attempts: {last_error}")


def load_reviewed_release(root: Path) -> dict[str, Any]:
    primary_path = root / "site/release.json"
    localized_path = root / "site/id/release.json"
    primary = json.loads(primary_path.read_text(encoding="utf-8"))
    localized = json.loads(localized_path.read_text(encoding="utf-8"))
    if primary != localized:
        fail("Reviewed EN/ID release manifests do not match")
    if primary.get("distributionEnabled") is not True:
        fail("Reviewed release manifest does not enable distribution")

    version = primary.get("version")
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        fail(f"Reviewed release manifest has an invalid version: {version!r}")

    release_url = official_release_url(primary.get("releaseUrl"))
    installer_url = official_release_url(primary.get("installerUrl"), asset=True)
    vst3_url = official_release_url(primary.get("vst3Url"), asset=True)
    standalone_url = official_release_url(primary.get("standaloneUrl"), asset=True)
    checksums_url = official_release_url(primary.get("checksumsUrl"), asset=True)
    if not all((release_url, installer_url, vst3_url, standalone_url, checksums_url)):
        fail("Reviewed release manifest contains an invalid official URL")

    raw_highlights = primary.get("releaseHighlights")
    highlights = [clean_markdown(item) for item in raw_highlights if isinstance(item, str)] if isinstance(raw_highlights, list) else []
    installer_name = unquote(urlparse(installer_url).path.rsplit("/", 1)[-1])
    return {
        "version": version,
        "releaseName": clean_markdown(str(primary.get("releaseName") or version)),
        "publishedAt": primary.get("publishedAt"),
        "releaseUrl": release_url,
        "installerUrl": installer_url,
        "installerName": installer_name,
        "vst3Url": vst3_url,
        "standaloneUrl": standalone_url,
        "checksumsUrl": checksums_url,
        "releaseHighlights": highlights[:6],
    }


def update_manifest(path: Path, release: dict[str, Any]) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest.update({
        "version": release["version"],
        "publishedAt": release["publishedAt"],
        "releaseName": release["releaseName"],
        "releaseUrl": release["releaseUrl"],
        "installerUrl": release["installerUrl"],
        "vst3Url": release["vst3Url"],
        "standaloneUrl": release["standaloneUrl"],
        "checksumsUrl": release["checksumsUrl"],
        "releaseHighlights": release["releaseHighlights"],
    })
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_asset_url(html: str, suffix_pattern: str, replacement: str) -> str:
    pattern = rf"https://github\.com/{re.escape(REPOSITORY)}/releases/download/v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?/{suffix_pattern}"
    return re.sub(pattern, replacement, html)


def update_html(path: Path, release: dict[str, Any]) -> None:
    html = path.read_text(encoding="utf-8")
    version = release["version"]
    plain_version = version.removeprefix("v")

    html = re.sub(r'("softwareVersion"\s*:\s*")[^"]+("\s*[,}])', rf'\g<1>{plain_version}\2', html)
    html = re.sub(
        rf"https://github\.com/{re.escape(REPOSITORY)}/releases/tag/v\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?",
        release["releaseUrl"],
        html,
    )
    html = replace_asset_url(html, r"ArSonKuPik-v[^/\"]+-Windows-x64-Setup\.exe", release["installerUrl"])
    html = replace_asset_url(html, r"ArSonKuPik-v[^/\"]+-Windows-x64-VST3\.zip", release["vst3Url"])
    html = replace_asset_url(html, r"ArSonKuPik-v[^/\"]+-Windows-x64-Standalone\.zip", release["standaloneUrl"])
    html = replace_asset_url(html, r"SHA256SUMS\.txt", release["checksumsUrl"])
    html = re.sub(
        r"(<(?:span|strong)[^>]*data-release-version[^>]*>)[^<]*(</(?:span|strong)>)",
        rf"\g<1>{version}\2",
        html,
    )
    html = re.sub(
        r"Get-FileHash \.\\[^<]+ -Algorithm SHA256",
        lambda _: f"Get-FileHash .\\{release['installerName']} -Algorithm SHA256",
        html,
    )
    path.write_text(html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--fixture", type=Path)
    parser.add_argument(
        "--allow-reviewed-fallback",
        action="store_true",
        help="Use the checked-in EN/ID release manifests when the live release API is unavailable or incomplete.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    source = "github-latest-api"

    try:
        try:
            release = normalize_release(load_payload(args.fixture))
        except RuntimeError as live_error:
            if not args.allow_reviewed_fallback or args.fixture is not None:
                raise
            print(
                f"RELEASE SYNC WARNING: {live_error}. Using the reviewed local manifest so Pages can still deploy.",
                file=sys.stderr,
            )
            release = load_reviewed_release(root)
            source = "reviewed-manifest-fallback"

        manifest_paths = [root / "site/release.json", root / "site/id/release.json"]
        html_paths = [root / "site/index.html", root / "site/id/index.html"]
        for path in [*manifest_paths, *html_paths]:
            if not path.is_file():
                fail(f"Missing required landing file: {path}")
        for path in manifest_paths:
            update_manifest(path, release)
        for path in html_paths:
            update_html(path, release)
    except (RuntimeError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"RELEASE SYNC FAILED: {exc}", file=sys.stderr)
        return 1

    print(
        f"Synced landing metadata from {source} to {release['version']} with "
        f"{len(release['releaseHighlights'])} release highlights."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
