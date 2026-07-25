#!/usr/bin/env python3
"""Synchronize reviewed public product facts into both static landing pages."""
from __future__ import annotations

import json
from pathlib import Path


class CatalogSyncError(RuntimeError):
    pass


def replace_once_or_present(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise CatalogSyncError(f"{label}: expected one stale token, found {count}")
    return text.replace(old, new, 1)


def replace_all_or_present(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new not in text:
            raise CatalogSyncError(f"{label}: neither stale nor synchronized token was found")
        return text
    return text.replace(old, new)


def sync_page(path: Path, *, language: str, version: str) -> None:
    text = path.read_text(encoding="utf-8")

    if language == "en":
        replacements = [
            ("40 curated mastering, mix bus, track and creative presets", "41 curated mastering, mix bus, track and creative presets", "EN structured preset count"),
            ("40 curated presets", "41 curated presets", "EN hero preset count"),
            ("40 curated starting points", "41 curated starting points", "EN catalog heading"),
            ("Update checking happens only when you request it.", "A bounded update check may run after about 30 seconds and no more than once per 24 hours; you can also request a manual check.", "EN updater disclosure"),
        ]
    else:
        replacements = [
            ("40 preset mastering, mix bus, track, dan creative", "41 preset mastering, mix bus, track, dan creative", "ID structured preset count"),
            ("40 preset terkurasi", "41 preset terkurasi", "ID hero preset count"),
            ("40 titik awal terkurasi", "41 titik awal terkurasi", "ID catalog heading"),
            ("Pemeriksaan update hanya terjadi saat Anda memintanya.", "Pemeriksaan update terbatas dapat berjalan setelah sekitar 30 detik dan maksimal satu kali per 24 jam; Anda juga dapat menjalankan pemeriksaan manual.", "ID updater disclosure"),
        ]

    for old, new, label in replacements:
        text = replace_all_or_present(text, old, new, label)

    text = replace_all_or_present(
        text,
        "<strong>Creative</strong><span>19</span>",
        "<strong>Creative</strong><span>20</span>",
        f"{language.upper()} creative count",
    )
    text = replace_all_or_present(
        text,
        " · Radio Mas Ari</p></article>",
        " · Radio Mas Ari · Blues Club</p></article>",
        f"{language.upper()} Blues Club catalog entry",
    )

    # The release synchronizer owns version and official asset URLs. This catalog
    # sync only ensures the reviewed fallback version is present before that step.
    text = replace_all_or_present(
        text,
        '"softwareVersion":"0.5.13"',
        f'"softwareVersion":"{version.removeprefix("v")}"',
        f"{language.upper()} structured version fallback",
    )
    text = replace_all_or_present(
        text,
        ">v0.5.13</span>",
        f">{version}</span>",
        f"{language.upper()} visible version fallback",
    )
    text = replace_all_or_present(
        text,
        "ArSonKuPik-v0.5.13-Windows-x64-Setup.exe",
        f"ArSonKuPik-{version}-Windows-x64-Setup.exe",
        f"{language.upper()} checksum fallback filename",
    )

    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    release = json.loads((root / "site/release.json").read_text(encoding="utf-8"))
    version = str(release.get("version", ""))
    if not version.startswith("v"):
        raise CatalogSyncError(f"Invalid reviewed release version: {version!r}")

    sync_page(root / "site/index.html", language="en", version=version)
    sync_page(root / "site/id/index.html", language="id", version=version)
    print(f"Synchronized 41-preset bilingual public catalog and reviewed {version} fallbacks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
