#!/usr/bin/env python3
"""Regression checks for automatic latest-release landing behaviour."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("sync_latest_release", path)
    require(spec is not None and spec.loader is not None, "Could not load release synchronizer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    runtime = (root / "site/site-v6.js").read_text(encoding="utf-8")
    workflow = (root / ".github/workflows/pages.yml").read_text(encoding="utf-8")
    sync_path = root / "tools/sync-latest-release.py"
    sync = sync_path.read_text(encoding="utf-8")

    for token in (
        "api.github.com/repos/${REPOSITORY}/releases/latest",
        "parseGitHubRelease",
        "extractHighlights",
        "data-release-highlights",
        "releaseHighlights",
        "fetchJson(LATEST_API",
        "release.json",
    ):
        require(token in runtime, f"Latest-release runtime missing {token}")

    for token in (
        "release:",
        "types: [published, edited]",
        "python tools/sync-latest-release.py",
        "python tools/validate-public-release.py",
        "python tools/validate-latest-release.py",
    ):
        require(token in workflow, f"Pages workflow missing {token}")

    for token in (
        "GITHUB_TOKEN",
        "releases/latest",
        "releaseHighlights",
        "update_manifest",
        "update_html",
    ):
        require(token in sync, f"Release synchronizer missing {token}")

    module = load_module(sync_path)
    fixture = {
        "tag_name": "v9.8.7",
        "name": "ArSonKuPik v9.8.7",
        "draft": False,
        "prerelease": False,
        "published_at": "2026-07-22T00:00:00Z",
        "html_url": "https://github.com/masarray/vst-enhancer/releases/tag/v9.8.7",
        "body": "## Improvements\n- Faster processing.\n- More stable output level.\n- Clearer release information.",
        "assets": [
            {
                "name": "ArSonKuPik-v9.8.7-Windows-x64-Setup.exe",
                "browser_download_url": "https://github.com/masarray/vst-enhancer/releases/download/v9.8.7/ArSonKuPik-v9.8.7-Windows-x64-Setup.exe",
                "state": "uploaded",
            },
            {
                "name": "ArSonKuPik-v9.8.7-Windows-x64-VST3.zip",
                "browser_download_url": "https://github.com/masarray/vst-enhancer/releases/download/v9.8.7/ArSonKuPik-v9.8.7-Windows-x64-VST3.zip",
                "state": "uploaded",
            },
            {
                "name": "ArSonKuPik-v9.8.7-Windows-x64-Standalone.zip",
                "browser_download_url": "https://github.com/masarray/vst-enhancer/releases/download/v9.8.7/ArSonKuPik-v9.8.7-Windows-x64-Standalone.zip",
                "state": "uploaded",
            },
            {
                "name": "SHA256SUMS.txt",
                "browser_download_url": "https://github.com/masarray/vst-enhancer/releases/download/v9.8.7/SHA256SUMS.txt",
                "state": "uploaded",
            },
        ],
    }
    release = module.normalize_release(fixture)
    require(release["version"] == "v9.8.7", "Synchronizer did not preserve the latest tag")
    require(len(release["releaseHighlights"]) == 3, "Release-note highlights were not extracted")
    require(release["installerName"].endswith("Setup.exe"), "Safe installer selection failed")

    main_manifest = json.loads((root / "site/release.json").read_text(encoding="utf-8"))
    id_manifest = json.loads((root / "site/id/release.json").read_text(encoding="utf-8"))
    require(main_manifest == id_manifest, "Localized release manifests drifted")

    print("Validated automatic latest-release resolution, highlights, asset safety, and Pages triggers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
