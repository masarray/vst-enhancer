# ArSonKuPik VST — Official Product and Distribution Repository

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Latest release](https://img.shields.io/github/v/release/masarray/vst-enhancer?label=Latest%20release)](https://github.com/masarray/vst-enhancer/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Evaluation](https://img.shields.io/badge/Free%20evaluation-365%20days-5bd49a)](#free-365-day-evaluation--evaluasi-gratis-365-hari)
[![Product licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a focused Windows VST3 and standalone audio enhancer for musicians, creators, producers, audio engineers, and first-time users. Every preset and control is available free for 365 days with no account, payment card, subscription, automatic charge, or obligation to buy.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer Windows VST3 dan standalone untuk musisi, kreator, produser, audio engineer, dan pengguna awam. Seluruh preset dan kontrol tersedia gratis selama 365 hari tanpa akun, kartu pembayaran, langganan, tagihan otomatis, atau kewajiban membeli.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing smart enhancement controls, presets, A/B comparison and level meters">
  </a>
</p>

## Official links / Tautan resmi

- **[Free product evaluation / Evaluasi produk gratis](https://masarray.github.io/vst-enhancer/)**
- **[Latest supported release / Rilis terbaru](https://github.com/masarray/vst-enhancer/releases/latest)**
- **[Optional activation information / Informasi aktivasi opsional](https://masarray.github.io/vst-enhancer/activation/)**
- **[Report a reproducible public bug / Laporkan bug publik](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[Private security reporting / Pelaporan keamanan privat](SECURITY.md)**
- **[Support guide / Panduan dukungan](SUPPORT.md)**
- **[Public changelog / Catatan perubahan](CHANGELOG.md)**

> Download only from the official website or this repository's GitHub Releases. Avoid mirrors and re-uploaded packages. Verify `SHA256SUMS.txt` from the same release before running a file.
>
> Unduh hanya melalui website resmi atau GitHub Releases repository ini. Hindari mirror dan paket yang diunggah ulang. Verifikasi `SHA256SUMS.txt` dari rilis yang sama sebelum menjalankan file.

## Automatic latest-installer routing

The public website does not pin its download buttons permanently to one release version.

At page load it:

1. Requests GitHub's latest published release metadata.
2. Validates that release and every asset belong to `masarray/vst-enhancer` over HTTPS.
3. Selects the official Windows installer `.exe` while rejecting portable executables, activation utilities, and key tools.
4. Points every installer CTA directly to that latest `.exe` asset.
5. Updates the displayed version, package links, checksum command, and structured download metadata.

The behaviour applies to the navigation button, hero CTA, download card, final CTA, mobile sticky CTA, and the free-download button on `/activation/`.

If GitHub's latest-release API cannot be resolved, the website falls back only to the repository's [`/releases/latest`](https://github.com/masarray/vst-enhancer/releases/latest) page. It does **not** fall back to an older version-specific installer.

`site/release.json` remains reviewed local metadata for distribution state, evaluation terms, checkout separation, and static fallback information. It is not the authoritative selector for the newest installer asset.

## Public landing experience

The bilingual landing keeps the path compact while serving four audience groups:

- **First-time users:** preset-first guidance and plain-language VST3/Standalone explanations.
- **Musicians and creators:** vocals, instruments, demos, podcasts, and creative starting points.
- **Producers:** mastering, mix-bus, track processing, and honest A/B comparison.
- **Audio engineers:** matched gain, translation checks, and final metering reminders.

The current flow combines the three-minute listening test, six controls, preset roles, compatibility, package selection, installation, checksum verification, the free-year terms, privacy, essential FAQ, and legal links without turning the landing into a documentation wall.

## Free 365-day evaluation / Evaluasi gratis 365 hari

| English | Bahasa Indonesia |
|---|---|
| Every preset and editing control is available for 365 days from first launch on each computer. | Seluruh preset dan kontrol editing tersedia selama 365 hari sejak pertama kali dijalankan pada tiap komputer. |
| No account, payment card, subscription, automatic renewal, automatic charge, or audio watermark is required to begin. | Tidak memerlukan akun, kartu pembayaran, langganan, perpanjangan otomatis, tagihan otomatis, atau watermark audio untuk memulai. |
| Personal and commercial audio-production use is permitted during evaluation, subject to the EULA. | Penggunaan produksi audio personal dan komersial diizinkan selama evaluasi, tunduk pada EULA. |
| No purchase obligation exists when the evaluation ends. | Tidak ada kewajiban membeli ketika masa evaluasi berakhir. |
| Existing projects and saved processing are designed to continue in project-safe read-only mode after evaluation. | Project lama dan pemrosesan tersimpan dirancang tetap berjalan dalam mode project-safe read-only setelah evaluasi. |

## Optional activation / Aktivasi opsional

There is no obligation to buy. Users who later decide that ArSonKuPik has earned a lasting place in their workflow may review the separate [Optional Activation page](https://masarray.github.io/vst-enhancer/activation/).

The published standard plan for the v0.5 evaluation cohort is a **USD 25 one-time perpetual editing activation**, before applicable tax, with no subscription or automatic renewal. Paid checkout is not currently enabled.

An activation purchase provides concrete licence rights; it is not a donation. Revenue may help sustain independent development, JUCE licensing when applicable, testing, documentation, user support, and trusted Windows code signing and distribution. This is not a promise that each payment is earmarked for a specific vendor, certificate, or expense.

## Compatibility

- Windows 10/11, 64-bit
- VST3 plug-in for use inside a compatible DAW
- Standalone application for supported audio-device workflows
- macOS, Linux, VST2, AAX, and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer, device, and security policy
- Evaluate in your own workflow before critical delivery or broadcast

## Install and verify / Instalasi dan verifikasi

1. Use the website's installer button or open the [latest official release](https://github.com/masarray/vst-enhancer/releases/latest).
2. Download the Windows x64 setup `.exe` selected from the latest release.
3. Download `SHA256SUMS.txt` from the same release.
4. Verify the exact downloaded filename:

```powershell
Get-FileHash .\<downloaded-installer-name>.exe -Algorithm SHA256
```

5. Compare the result with `SHA256SUMS.txt`. Do not continue if the values differ.
6. Keep normal Windows security and antivirus protection enabled.
7. In a DAW, open the plug-in manager and rescan VST3 plug-ins if required.

### Unsigned Windows package

Current public packages may be distributed without a commercial Windows code-signing certificate. Windows SmartScreen may therefore show an unknown-publisher or reputation warning. A matching SHA-256 value verifies file identity against the value published in the same release; it does not replace antivirus scanning, endpoint protection, backups, or compatibility testing.

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally and does not intentionally transmit audio, DAW projects, presets, parameter values, licence codes, crash analytics, advertising identifiers, or usage analytics during normal operation.

- The application checks for updates only when the user requests it.
- The website stores only the selected EN/ID language value in browser local storage.
- Offline activation uses a locally generated Computer Request ID shared only when the user chooses to request activation.
- The evaluation download has no checkout and does not collect payment-card data.
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

## Repository scope

This repository is public for product information, website source, release metadata, checksums, supported downloads, feedback, and public legal notices.

The proprietary DSP implementation, preset recipes, application source, private signing material, Key Activator, and customer activation records are not included.

## Local and self-hosted validation

Run locally on Windows:

```powershell
.\tools\validate-public-release.ps1
```

Optionally verify the current public URLs:

```powershell
.\tools\validate-public-release.ps1 --check-remote
```

The wrapper runs repository/release, latest-download funnel, and audience/readability validators. The manual GitHub workflow uses a self-hosted runner and `workflow_dispatch` only; it does not execute public pull-request code automatically.

## Safe feedback

Include the ArSonKuPik version, package type, DAW and version, Windows version, audio interface and driver, sample rate, buffer size, preset, checksum, expected behaviour, actual behaviour, and exact reproduction steps.

Never publish activation codes, Computer Request IDs, customer audio, private projects, personal data, order records, or security exploit details. Use [SECURITY.md](SECURITY.md) for private vulnerability reporting.

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
