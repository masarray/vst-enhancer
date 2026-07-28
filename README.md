# ArSonKuPik VST — Musical Audio Enhancement for Windows and macOS

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Latest release](https://img.shields.io/github/v/release/masarray/vst-enhancer?label=Latest%20release)](https://github.com/masarray/vst-enhancer/releases/latest)
[![Platforms](https://img.shields.io/badge/Platforms-Windows%20x64%20%7C%20macOS%20Universal-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Product licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a focused, musical VST3 and standalone audio enhancer for Windows and macOS. It helps creators achieve fuller, clearer and more dimensional sound without building a complex processing chain.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer VST3 dan standalone untuk Windows dan macOS yang fokus dan musikal. Produk ini membantu kreator menghasilkan suara yang lebih berisi, jernih, dan berdimensi tanpa membangun rangkaian processing yang rumit.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing the Mas Ari Signature engine, professional preset selector, musical enhancement controls, A/B comparison and level meters">
  </a>
</p>

## Product direction / Arah produk

ArSonKuPik is designed around one principle: **shape the musical result, not the complexity**.

ArSonKuPik dirancang berdasarkan satu prinsip: **bentuk hasil suaranya, bukan kerumitannya**.

The interface combines six focused controls:

- Enhance
- Smart Bass
- Smart Treble
- Vocal
- Stereo
- Smart Protect

The **Mas Ari Signature Engine** is the single sonic foundation behind every factory preset. It is tuned to make familiar music feel more alive, reveal fine detail and create a more convincing live-music impression while retaining a grounded centre.

**Mas Ari Signature Engine** adalah satu-satunya pondasi suara di balik seluruh preset factory. Engine ini dituning agar musik familiar terasa lebih hidup, menampilkan detail halus, dan menciptakan kesan live music yang lebih meyakinkan dengan centre yang tetap kokoh.

## 13 professional starting points / 13 titik awal profesional

Every factory preset is a curated starting point over the same engine. Preset selection never swaps DSP topology, and users can save, load, rename and delete their own `.askpreset` files.

- **Signature — 1:** Signature Balanced
- **Mastering — 3:** Transparent Polish, Open & Detailed, Warm Glue
- **Problem Solving — 3:** Dense Mix Clarity, Dark Mix Lift, Bright Mix Safe
- **Mix Bus — 1:** Punch & Separation
- **Tracks — 5:** Vocal Forward & Silky, Guitar Definition & Body, Bass Authority, Drums Punch & Skin, Acoustic Natural Air

Semua preset factory adalah titik awal terkurasi di atas engine yang sama. Pemilihan preset tidak pernah mengganti topologi DSP, dan pengguna dapat menyimpan, membuka, mengganti nama, serta menghapus file `.askpreset` miliknya sendiri.

## Current public release / Rilis publik saat ini

The reviewed public manifest records **v0.5.20** for Windows x64 and macOS Universal. The website resolves the latest published full release and routes downloads only to official assets in this repository.

Manifest publik yang telah direview mencatat **v0.5.20** untuk Windows x64 dan macOS Universal. Website mengambil rilis penuh terbaru yang telah dipublikasikan dan hanya mengarahkan unduhan ke aset resmi repository ini.

### Windows

- Windows 10/11 x64 installer
- Manual VST3 ZIP
- Standalone ZIP
- Packages are not commercially code-signed and may trigger SmartScreen

### macOS

- macOS 11 or later
- Universal Apple Silicon `arm64` + Intel `x86_64`
- VST3 ZIP, Standalone ZIP and DMG
- Ad-hoc signed only; not Developer ID signed and not notarized
- Gatekeeper may require Control-click → Open or **Open Anyway**

## Sound and comparison behaviour

Gain Match defaults to OFF. In normal listening mode, safe creative lift stays audible instead of being attenuated toward an internal loudness target. Gain Match ON is the explicit level-equal comparison mode; independent `-1 dBFS` peak safety remains active in both modes.

Gain Match secara default berada pada posisi OFF. Dalam mode dengar normal, creative lift yang aman tetap terdengar dan tidak ditahan menuju target loudness internal. Gain Match ON adalah mode perbandingan level yang setara; proteksi peak independen `-1 dBFS` tetap aktif pada kedua mode.

## Evaluation and optional activation / Evaluasi dan aktivasi opsional

Every preset and editing control is available for 365 days from first launch on each computer. No account, payment card, subscription, automatic renewal or automatic charge is required.

Seluruh preset dan kontrol editing tersedia selama 365 hari sejak pertama kali dijalankan pada tiap komputer. Tidak memerlukan akun, kartu pembayaran, langganan, perpanjangan otomatis, atau tagihan otomatis.

After full editing ends, existing projects, saved values, meters, automation playback and audio processing are designed to continue in project-safe read-only mode. Optional activation is relevant only for continued editing, subject to the EULA and technical compatibility.

Setelah full editing berakhir, project lama, nilai tersimpan, meter, playback automation, dan processing audio dirancang tetap berjalan dalam mode project-safe read-only. Aktivasi opsional hanya relevan untuk melanjutkan editing, tunduk pada EULA dan kompatibilitas teknis.

There is no obligation to buy. Optional perpetual activation for one active computer is **Rp399.000**. A purchase provides concrete licence rights; it is not a donation.

Tidak ada kewajiban membeli. Aktivasi perpetual opsional untuk satu komputer aktif adalah **Rp399.000**. Pembelian memberikan hak lisensi yang nyata; pembayaran tersebut bukan donasi.

## Install and verify / Instalasi dan verifikasi

1. Open the [latest official release](https://github.com/masarray/vst-enhancer/releases/latest).
2. Download the package for your operating system.
3. Download `SHA256SUMS.txt` from the same release.
4. Verify the exact downloaded filename before installation.

Windows PowerShell:

```powershell
Get-FileHash .\<downloaded-file-name> -Algorithm SHA256
```

macOS Terminal:

```bash
shasum -a 256 <downloaded-file-name>
```

Do not continue when the calculated value differs from `SHA256SUMS.txt`. A matching SHA-256 verifies file identity against the official release value, but it does not replace antivirus, endpoint protection, backups, Gatekeeper or compatibility testing.

## Release integrity and provenance

- Windows packages are built and audited locally on Windows.
- macOS Universal packages are built and audited by the single approved manual workflow in this public repository using an exact tag from the private proprietary source repository.
- Public packages are binary-only and exclude proprietary source, private signing material, Key Activator and customer activation records.
- See [RELEASE-PROVENANCE.md](RELEASE-PROVENANCE.md) for the reviewed v0.5.20 release path and disclosure boundaries.

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally and does not intentionally transmit audio, DAW projects, presets, parameter values, licence codes, crash analytics, advertising identifiers or usage analytics during normal operation.

- The application may make one quiet latest-release metadata check after at least 30 seconds, no more than once per 24 hours per computer; a manual check may bypass that cooldown.
- The website stores only the selected EN/ID language value in browser local storage.
- Activation uses a locally generated Computer Request ID shared only when the user creates or checks an order, requests recovery, or explicitly requests manual activation.
- Public GitHub Issues must not contain activation codes, Computer Request IDs, customer audio, private projects, order documents or personal data.

See [PRIVACY.txt](PRIVACY.txt).

## Official links / Tautan resmi

- **[Product website / Website produk](https://masarray.github.io/vst-enhancer/)**
- **[Latest supported release / Rilis terbaru](https://github.com/masarray/vst-enhancer/releases/latest)**
- **[Optional support and activation / Dukungan dan aktivasi opsional](https://masarray.github.io/vst-enhancer/activation/)**
- **[Report a reproducible public bug / Laporkan bug publik](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[Private security reporting / Pelaporan keamanan privat](SECURITY.md)**
- **[Public changelog / Catatan perubahan](CHANGELOG.md)**

> Download only from the official website or this repository's GitHub Releases. Avoid mirrors and re-uploaded packages. Verify `SHA256SUMS.txt` from the same release before opening a package.
>
> Unduh hanya melalui website resmi atau GitHub Releases repository ini. Hindari mirror dan paket yang diunggah ulang. Verifikasi `SHA256SUMS.txt` dari rilis yang sama sebelum membuka paket.

## Compatibility

- Windows 10/11, 64-bit
- macOS 11 or later, Universal `arm64` + `x86_64`
- VST3 plug-in for use inside a compatible DAW
- Standalone application for supported audio-device workflows
- Linux, VST2, AAX and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer, device and security policy
- Evaluate in your own workflow before critical delivery or broadcast

## Repository scope

This repository contains public product information, website source, release metadata, checksums, supported downloads, feedback surfaces and public legal notices.

The proprietary DSP implementation, preset recipes, application source, private signing material, Key Activator and customer activation records are not included.

The separately published MIT-licensed ArSonKuPik project remains governed by its original MIT terms. Its publication does not make this proprietary VST product open source.

## Local validation

Run on Windows:

```powershell
.\tools\validate-public-release.ps1
```

Optionally validate public release URLs from a connected machine:

```powershell
.\tools\validate-public-release.ps1 --check-remote
```

## Safe feedback

Include the ArSonKuPik version, package type, DAW and version, operating-system version, audio interface and driver, sample rate, buffer size, preset, checksum, expected behaviour, actual behaviour and exact reproduction steps.

Never publish activation codes, Computer Request IDs, customer audio, private projects, personal data, order records or security exploit details. Use [SECURITY.md](SECURITY.md) for private vulnerability reporting.

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
