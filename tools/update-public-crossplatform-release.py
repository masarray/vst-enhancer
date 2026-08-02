#!/usr/bin/env python3
"""Update the public binary/landing repository after Windows and macOS gates pass."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def patch_release_javascript(path: Path) -> None:
    """Add macOS asset routing only when an older public controller is encountered."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    old_github_assets = """      vst3Url: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('vst3'))?.url || null,
      standaloneUrl: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('standalone'))?.url || null,
      checksumsUrl: chooseAsset(assets, (name) => name === 'sha256sums.txt' || name.includes('sha256'))?.url || null,"""
    new_github_assets = """      vst3Url: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('windows') && name.includes('vst3'))?.url || null,
      standaloneUrl: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('windows') && name.includes('standalone'))?.url || null,
      macDmgUrl: chooseAsset(assets, (name) => name.endsWith('.dmg') && name.includes('macos'))?.url || null,
      macVst3Url: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('macos') && name.includes('vst3'))?.url || null,
      macStandaloneUrl: chooseAsset(assets, (name) => name.endsWith('.zip') && name.includes('macos') && name.includes('standalone'))?.url || null,
      checksumsUrl: chooseAsset(assets, (name) => name === 'sha256sums.txt')?.url || null,"""
    if old_github_assets in text:
        text = text.replace(old_github_assets, new_github_assets, 1)

    old_manifest_assets = """          vst3Url: officialReleaseUrl(release.vst3Url, true),
          standaloneUrl: officialReleaseUrl(release.standaloneUrl, true),
          checksumsUrl: officialReleaseUrl(release.checksumsUrl, true),
          highlights"""
    new_manifest_assets = """          vst3Url: officialReleaseUrl(release.vst3Url, true),
          standaloneUrl: officialReleaseUrl(release.standaloneUrl, true),
          macDmgUrl: officialReleaseUrl(release.macDmgUrl, true),
          macVst3Url: officialReleaseUrl(release.macVst3Url, true),
          macStandaloneUrl: officialReleaseUrl(release.macStandaloneUrl, true),
          checksumsUrl: officialReleaseUrl(release.checksumsUrl, true),
          highlights"""
    if old_manifest_assets in text:
        text = text.replace(old_manifest_assets, new_manifest_assets, 1)

    marker = "  const renderRelease = (release) => {"
    if "const ensureMacDownloadOption" not in text and marker in text:
        block = r"""  const ensureMacDownloadOption = (release) => {
    if (!release?.macDmgUrl) return;
    const grid = document.querySelector('#download .download-grid');
    if (!grid) return;

    let option = document.getElementById('mac-download-option');
    if (!option) {
      option = document.createElement('article');
      option.id = 'mac-download-option';
      option.className = 'download-option';
      const isId = language === 'id';
      option.innerHTML = `
        <span class="download-tag">macOS Universal</span>
        <h3>${isId ? 'Paket Mac' : 'Mac package'}</h3>
        <p>${isId
          ? 'Universal untuk Apple Silicon dan Intel. Ad-hoc signed, tanpa Developer ID dan tanpa notarization.'
          : 'Universal for Apple Silicon and Intel. Ad-hoc signed, without Developer ID signing or notarization.'}</p>
        <div class="mac-download-actions">
          <a class="button secondary" id="mac-dmg-link" href="${RELEASE_FALLBACK}">${isId ? 'Unduh DMG Mac' : 'Download Mac DMG'}</a>
          <a class="text-link" id="mac-vst3-link" href="${RELEASE_FALLBACK}">VST3 ZIP</a>
          <a class="text-link" id="mac-standalone-link" href="${RELEASE_FALLBACK}">Standalone ZIP</a>
        </div>`;
      grid.appendChild(option);
    }

    setLink(document.getElementById('mac-dmg-link'), release.macDmgUrl, true);
    setLink(document.getElementById('mac-vst3-link'), release.macVst3Url || release.releaseUrl, Boolean(release.macVst3Url));
    setLink(document.getElementById('mac-standalone-link'), release.macStandaloneUrl || release.releaseUrl, Boolean(release.macStandaloneUrl));
  };

"""
        text = text.replace(marker, block + marker, 1)

    old_render_links = """    setLink(document.getElementById('vst3-link'), state.vst3Url || state.releaseUrl, Boolean(state.vst3Url));
    setLink(document.getElementById('standalone-link'), state.standaloneUrl || state.releaseUrl, Boolean(state.standaloneUrl));
    setLink(document.getElementById('checksums-link'), state.checksumsUrl || state.releaseUrl, Boolean(state.checksumsUrl));"""
    if old_render_links in text and "ensureMacDownloadOption(state);" not in text:
        text = text.replace(old_render_links, old_render_links + "\n    ensureMacDownloadOption(state);", 1)

    write_text(path, text)


def patch_crossplatform_html(path: Path) -> None:
    """Keep static EN/ID pages cross-platform and add the Mac card when absent."""
    text = path.read_text(encoding="utf-8")
    is_id = path.parent.name == "id" or 'lang="id"' in text

    replacements = {
        "Musical VST3 audio enhancer for Windows<": "Musical VST3 audio enhancer for Windows and macOS<",
        "VST3 audio enhancer musikal untuk Windows<": "VST3 audio enhancer musikal untuk Windows dan macOS<",
        "Windows VST3 and Standalone": "Windows and macOS VST3 and Standalone",
        "Windows VST3 and standalone": "Windows and macOS VST3 and standalone",
        "Official Windows download": "Official Windows and macOS downloads",
        "Unduhan Windows resmi": "Unduhan resmi Windows dan macOS",
        "Focused audio enhancement for fuller, clearer and more dimensional sound on Windows VST3 and Standalone.":
            "Focused audio enhancement for fuller, clearer and more dimensional sound on Windows and macOS VST3 and Standalone.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    if "mac-download-option" not in text:
        article = (
            '<article class="download-option" id="mac-download-option">'
            '<span class="download-tag">macOS Universal</span>'
            f'<h3>{"Paket Mac" if is_id else "Mac package"}</h3>'
            f'<p>{"Universal untuk Apple Silicon dan Intel. Ad-hoc signed, tanpa Developer ID dan tanpa notarization." if is_id else "Universal for Apple Silicon and Intel. Ad-hoc signed, without Developer ID signing or notarization."}</p>'
            f'<a class="button secondary" id="mac-dmg-link" href="https://github.com/masarray/vst-enhancer/releases/latest">{"Unduh DMG Mac" if is_id else "Download Mac DMG"}</a>'
            '<div class="mac-download-actions">'
            '<a class="text-link" id="mac-vst3-link" href="https://github.com/masarray/vst-enhancer/releases/latest">VST3 ZIP</a>'
            '<a class="text-link" id="mac-standalone-link" href="https://github.com/masarray/vst-enhancer/releases/latest">Standalone ZIP</a>'
            '</div></article>'
        )
        pattern = re.compile(r'(</article>)(</div><details class="install-disclosure">)', re.DOTALL)
        text, count = pattern.subn(r"\1" + article + r"\2", text, count=1)
        if count == 0:
            raise RuntimeError(f"Could not insert macOS download card into {path}")

    text = text.replace(
        '"operatingSystem":"Windows 10 and Windows 11, 64-bit"',
        '"operatingSystem":"Windows 10/11 64-bit; macOS 11 or later Universal"',
    )
    text = text.replace(
        '"operatingSystem":"Windows 10 dan Windows 11, 64-bit"',
        '"operatingSystem":"Windows 10/11 64-bit; macOS 11 atau lebih baru Universal"',
    )
    write_text(path, text)


def build_release(tag: str, source_commit: str, published: str) -> dict[str, object]:
    public_repo = "https://github.com/masarray/vst-enhancer"
    release_root = f"{public_repo}/releases/download/{tag}"
    return {
        "schemaVersion": 3,
        "version": tag,
        "channel": "one-year-evaluation",
        "distributionEnabled": True,
        "distributionStatus": "enabled",
        "platforms": ["windows-x64", "macos-universal"],
        "requiredJuceVersion": "8.0.14",
        "evaluationDays": 365,
        "noPaymentCardRequired": True,
        "purchaseObligation": False,
        "automaticCharge": False,
        "subscription": False,
        "purchaseCheckoutAvailable": False,
        "purchaseStatus": "available-in-app",
        "activationPriceAmount": 399000,
        "priceCurrency": "IDR",
        "activationType": "perpetual",
        "maxActiveComputers": 1,
        "readOnlyAfterEvaluation": True,
        "audioContinuesAfterEvaluation": True,
        "offlineActivation": True,
        "keyActivatorDistributedPublicly": False,
        "activationCodeProvider": "Mas Ari",
        "publishedAt": published,
        "sourceCommit": source_commit,
        "releaseUrl": f"{public_repo}/releases/tag/{tag}",
        "installerUrl": f"{release_root}/ArSonKuPik-{tag}-Windows-x64-Setup.exe",
        "vst3Url": f"{release_root}/ArSonKuPik-{tag}-Windows-x64-VST3.zip",
        "standaloneUrl": f"{release_root}/ArSonKuPik-{tag}-Windows-x64-Standalone.zip",
        "macDmgUrl": f"{release_root}/ArSonKuPik-{tag}-macOS-Universal.dmg",
        "macVst3Url": f"{release_root}/ArSonKuPik-{tag}-macOS-Universal-VST3.zip",
        "macStandaloneUrl": f"{release_root}/ArSonKuPik-{tag}-macOS-Universal-Standalone.zip",
        "checksumsUrl": f"{release_root}/SHA256SUMS.txt",
        "windowsChecksumsUrl": f"{release_root}/SHA256SUMS-Windows.txt",
        "macChecksumsUrl": f"{release_root}/SHA256SUMS-macOS.txt",
        "unsigned": True,
        "windowsUnsigned": True,
        "macDeveloperIdSigned": False,
        "macNotarized": False,
        "macAdHocSigned": True,
        "macArchitectures": ["arm64", "x86_64"],
        "macDeploymentTarget": "11.0",
        "signatureStatus": "unsigned-windows-adhoc-macos",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    number = args.version.removeprefix("v")
    tag = f"v{number}"
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise SystemExit(f"Invalid release version: {args.version}")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise SystemExit("source-commit must be a full lowercase Git SHA.")

    now = datetime.now(timezone.utc).replace(microsecond=0)
    published = now.isoformat().replace("+00:00", "Z")
    release = build_release(tag, args.source_commit, published)
    serialized_release = json.dumps(release, indent=2) + "\n"
    write_text(repo / "site" / "release.json", serialized_release)
    write_text(repo / "site" / "id" / "release.json", serialized_release)

    for html_path in (repo / "site").rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        text = re.sub(r'("softwareVersion"\s*:\s*")\d+\.\d+\.\d+(")', rf"\g<1>{number}\2", text)
        text = re.sub(r"v\d+\.\d+\.\d+", tag, text)
        text = re.sub(r"/releases/tag/v\d+\.\d+\.\d+", f"/releases/tag/{tag}", text)
        text = re.sub(r"ArSonKuPik-v\d+\.\d+\.\d+-Windows-x64-", f"ArSonKuPik-{tag}-Windows-x64-", text)
        text = re.sub(r"ArSonKuPik-v\d+\.\d+\.\d+-macOS-Universal", f"ArSonKuPik-{tag}-macOS-Universal", text)
        write_text(html_path, text)
        if html_path.name == "index.html" and (html_path.parent == repo / "site" or html_path.parent.name == "id"):
            patch_crossplatform_html(html_path)

    patch_release_javascript(repo / "site" / "site-v6.js")

    readme_path = repo / "README.md"
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        readme = re.sub(r"records \*\*v\d+\.\d+\.\d+\*\*", f"records **{tag}**", readme)
        readme = re.sub(r"mencatat \*\*v\d+\.\d+\.\d+\*\*", f"mencatat **{tag}**", readme)
        write_text(readme_path, readme)

    changelog_path = repo / "CHANGELOG.md"
    if changelog_path.exists():
        changelog = changelog_path.read_text(encoding="utf-8")
        if f"## {tag}" not in changelog:
            release_date = now.strftime("%d %B %Y").lstrip("0")
            entry = f"""## {tag} - {release_date}

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `{tag}` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

"""
            header = "# Public Distribution Changelog"
            rest = changelog[len(header):].lstrip() if changelog.startswith(header) else changelog
            changelog = f"{header}\n\n{entry}{rest}"
            write_text(changelog_path, changelog)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
