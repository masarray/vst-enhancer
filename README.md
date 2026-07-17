# ArSonKuPik VST — Official Public Product and Distribution Repository

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Latest release](https://img.shields.io/github/v/release/masarray/vst-enhancer?label=Latest%20release)](https://github.com/masarray/vst-enhancer/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Evaluation](https://img.shields.io/badge/Evaluation-365%20days-5bd49a)](#evaluation--evaluasi)
[![Product licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a focused Windows VST3 and standalone audio enhancer for mastering, mix bus, tracks, vocals, podcasts, and creative processing. This public repository hosts the bilingual product website, official release metadata, checksums, public legal documents, support policy, and supported downloads.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer Windows VST3 dan standalone untuk mastering, mix bus, track, vokal, podcast, dan pemrosesan kreatif. Repository publik ini memuat website produk dwibahasa, metadata rilis resmi, checksum, dokumen legal publik, kebijakan dukungan, dan unduhan yang didukung.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing smart enhancement controls, presets, A/B comparison and level meters">
  </a>
</p>

## Official links / Tautan resmi

- **[Product website / Website produk](https://masarray.github.io/vst-enhancer/)**
- **[Latest supported release / Rilis terbaru](https://github.com/masarray/vst-enhancer/releases/latest)**
- **[Report a reproducible public bug / Laporkan bug publik](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[Private security reporting / Pelaporan keamanan privat](SECURITY.md)**
- **[Support guide / Panduan dukungan](SUPPORT.md)**
- **[Public changelog / Catatan perubahan](CHANGELOG.md)**

> **Distribution safety / Keamanan distribusi:** Download only from the official website or this repository's GitHub Releases. Avoid mirrors and re-uploaded packages. Verify `SHA256SUMS.txt` from the same release before running a file.
>
> Unduh hanya melalui website resmi atau GitHub Releases repository ini. Hindari mirror dan paket yang diunggah ulang. Verifikasi `SHA256SUMS.txt` dari rilis yang sama sebelum menjalankan file.

## Current public release

Current metadata points to **v0.5.12**:

- Windows x64 installer
- VST3 ZIP package
- Standalone ZIP package
- SHA-256 checksum list
- JUCE 8.0.14 reviewed dependency baseline

Use the [latest release page](https://github.com/masarray/vst-enhancer/releases/latest) as the source of truth. The landing page reads `site/release.json` and enables direct download buttons only when public distribution is explicitly enabled.

## Evaluation / Evaluasi

| English | Bahasa Indonesia |
|---|---|
| 365 days of full preset and control editing from first launch on each computer. | 365 hari akses penuh ke preset dan kontrol sejak pertama kali dijalankan pada tiap komputer. |
| No card, account, subscription, automatic renewal, automatic charge, or audio watermark is required to begin. | Tidak memerlukan kartu, akun, langganan, perpanjangan otomatis, tagihan otomatis, atau watermark audio untuk memulai. |
| Personal and commercial audio-production use is permitted during evaluation, subject to the EULA. | Penggunaan produksi audio personal dan komersial diizinkan selama evaluasi, tunduk pada EULA. |
| After evaluation, existing projects and saved processing are designed to continue in project-safe read-only mode. | Setelah evaluasi, project lama dan pemrosesan tersimpan dirancang tetap berjalan dalam mode project-safe read-only. |
| Buying an activation is optional. | Pembelian aktivasi bersifat opsional. |

The published standard offer for the v0.5 evaluation cohort is a **USD 25 perpetual editing activation**, before applicable tax, with no subscription or automatic renewal. A published price does not mean checkout is currently available. Any purchase can occur only through an authorised checkout that shows seller identity, final currency, tax, payment, privacy, and refund terms before payment.

Penawaran standar yang dipublikasikan untuk pengguna evaluasi v0.5 adalah **aktivasi editing perpetual USD 25**, sebelum pajak yang berlaku, tanpa langganan atau perpanjangan otomatis. Harga yang dipublikasikan tidak berarti checkout sudah tersedia. Pembelian hanya dapat dilakukan melalui checkout resmi yang menampilkan identitas penjual, mata uang final, pajak, pembayaran, privasi, dan ketentuan refund sebelum pembayaran.

## Compatibility

- Windows 10/11, 64-bit
- VST3 plug-in
- Standalone application
- macOS, Linux, VST2, AAX, and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer, device, and security policy
- Evaluate in your own workflow before critical delivery or broadcast

## Install and verify / Instalasi dan verifikasi

1. Open the [latest official release](https://github.com/masarray/vst-enhancer/releases/latest).
2. Choose the installer, VST3 ZIP, or Standalone ZIP.
3. Download `SHA256SUMS.txt` from the same release.
4. Verify the exact installer name:

```powershell
Get-FileHash .\ArSonKuPik-v0.5.12-Windows-x64-Setup.exe -Algorithm SHA256
```

5. Compare the result with `SHA256SUMS.txt`. Do not continue if the values differ.
6. Keep normal Windows security and antivirus protection enabled.
7. In a DAW, open the plug-in manager and rescan VST3 plug-ins if required.

### Unsigned Windows package

The current package is distributed without a commercial Windows code-signing certificate. Windows SmartScreen may therefore show an unknown-publisher or reputation warning. This status is disclosed openly so evaluators can make an informed decision.

A matching SHA-256 value verifies file identity against the value published in the same release. It does not replace antivirus scanning, endpoint protection, backups, or compatibility testing.

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally and does not intentionally transmit audio, DAW projects, presets, parameter values, licence codes, crash analytics, advertising identifiers, or usage analytics during normal operation.

- The application checks for updates only when the user requests it.
- The website stores only the selected EN/ID language value in browser local storage.
- Offline activation uses a locally generated Computer Request ID shared only when the user chooses to request activation.
- The evaluation download does not collect payment-card data.
- Public GitHub Issues must not contain activation codes, Computer Request IDs, customer audio, private projects, order documents, or personal data.

See [PRIVACY.txt](PRIVACY.txt).

## Legal and policy documents

- [End User Licence Agreement](EULA.txt)
- [Commercial Activation Terms](PURCHASE_TERMS.txt)
- [Privacy Notice](PRIVACY.txt)
- [Security Policy](SECURITY.md)
- [Support Guide](SUPPORT.md)
- [Third-Party Notices](THIRD_PARTY_NOTICES.txt)
- [Public Repository Notice](LICENSE.txt)
- [Original ArSonKuPik MIT Notice](ArSonKuPik-MIT.txt)
- [Steinberg VST3 SDK MIT Notice](Steinberg-VST3-SDK-MIT.txt)
- [Plus Jakarta Sans OFL 1.1](Plus-Jakarta-Sans-OFL-1.1.txt)

The website and README provide plain-language explanations. The controlling EULA, applicable purchase and checkout terms, receipt terms, third-party notices, and mandatory applicable law govern actual use and completed transactions.

## Repository scope

This repository is public for product information, website source, release metadata, checksums, supported downloads, feedback, and public legal notices.

The proprietary DSP implementation, preset recipes, application source, private signing material, Key Activator, and customer activation records are not included.

The separately published MIT-licensed ArSonKuPik project remains governed by its original MIT terms. Its publication does not make this proprietary VST product open source.

## Local and self-hosted validation

Validation does not require GitHub-hosted runner minutes.

Run locally on Windows:

```powershell
.\tools\validate-public-release.ps1
```

Optionally validate the public release URLs from a connected machine:

```powershell
.\tools\validate-public-release.ps1 --check-remote
```

The manual GitHub workflow uses a self-hosted runner and `workflow_dispatch` only. It intentionally does not execute untrusted pull-request code on the local runner.

## Safe feedback

Include the ArSonKuPik version, package type, DAW and version, Windows version, audio interface and driver, sample rate, buffer size, preset, checksum, expected behaviour, actual behaviour, and exact reproduction steps.

Never publish activation codes, Computer Request IDs, customer audio, private projects, personal data, order records, or security exploit details. Use [SECURITY.md](SECURITY.md) for private vulnerability reporting.

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
