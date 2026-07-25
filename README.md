# ArSonKuPik VST — Musical Audio Enhancement for Windows

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Latest release](https://img.shields.io/github/v/release/masarray/vst-enhancer?label=Latest%20release)](https://github.com/masarray/vst-enhancer/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Product licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a focused, musical Windows VST3 and standalone audio enhancer for fuller, clearer and more dimensional sound without building a complex processing chain.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer Windows VST3 dan standalone yang fokus dan musikal untuk menghasilkan suara lebih berisi, jernih, dan berdimensi tanpa membangun rangkaian processing yang rumit.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing the Mas Ari Signature preset, musical enhancement controls, A/B comparison and level meters">
  </a>
</p>

## Product direction / Arah produk

ArSonKuPik follows one principle: **shape the musical result, not the complexity**.

ArSonKuPik menggunakan satu prinsip: **bentuk hasil suaranya, bukan kerumitannya**.

The interface combines six focused controls:

- Enhance
- Smart Bass
- Smart Treble
- Vocal
- Stereo
- Smart Protect

The flagship **Mas Ari Signature** preset is tuned to make familiar music feel more alive, reveal fine detail and create a convincing live-music impression while retaining a grounded centre.

Preset flagship **Mas Ari Signature** dituning agar musik familiar terasa lebih hidup, menampilkan detail halus, dan menciptakan kesan live music yang meyakinkan dengan centre yang tetap kokoh.

## 41 curated presets / 41 preset terkurasi

- **Signature — 1:** Mas Ari Signature
- **Master — 8:** Clean, Modern, Warm, Open 3D, Low-End Control, Vocal Focus, Streaming Safe, Dynamic
- **Mix Bus — 6:** Glue, Punch, Depth, Air, Warmth, Clean-Up
- **Track — 6:** Vocal Polish, Drum Punch, Bass Tight, Guitar / Synth Width, Acoustic Natural, Podcast
- **Creative — 20:** Max Enhancer, SonKu Deep Chest, Movie Sub, Night Listening, Open Air, Dangdut Koplo, EDM Festival, Reggae Dub, Rock Arena, Pop Radio, Jazz Club, Hip-Hop Punch, R&B Silk, Metal Impact, Acoustic Live, Lo-Fi Warm, K-Pop Gloss, Campursari, Radio Mas Ari, Blues Club

## Official links / Tautan resmi

- **[Product website / Website produk](https://masarray.github.io/vst-enhancer/)**
- **[Latest supported release / Rilis terbaru](https://github.com/masarray/vst-enhancer/releases/latest)**
- **[Optional activation / Aktivasi opsional](https://masarray.github.io/vst-enhancer/activation/)**
- **[Report a reproducible public bug / Laporkan bug publik](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[Private security reporting / Pelaporan keamanan privat](SECURITY.md)**
- **[Support guide / Panduan dukungan](SUPPORT.md)**
- **[Public changelog / Catatan perubahan](CHANGELOG.md)**

> **Distribution safety / Keamanan distribusi:** Download only from the official website or this repository's GitHub Releases. Avoid mirrors and re-uploaded packages. Verify `SHA256SUMS.txt` from the same release before running a file.
>
> Unduh hanya melalui website resmi atau GitHub Releases repository ini. Hindari mirror dan paket yang diunggah ulang. Verifikasi `SHA256SUMS.txt` dari rilis yang sama sebelum menjalankan file.

## Release and download behaviour

The website resolves the latest published full GitHub Release and validates that release and asset URLs belong to `masarray/vst-enhancer` over HTTPS. It selects the official Windows installer while rejecting portable executables, activation utilities and key tools, then updates installer, VST3, Standalone, checksum and release-detail links.

When the GitHub API is temporarily unavailable, the website uses the reviewed bilingual release manifest. The reviewed manifest must describe a real published release and official repository assets; it must never point to private DSP source, signing material or activation utilities.

Website mengambil full release terbaru dari GitHub dan memvalidasi bahwa URL rilis maupun asset berasal dari `masarray/vst-enhancer` melalui HTTPS. Ketika API GitHub sementara tidak tersedia, website menggunakan manifest bilingual yang telah direview.

## Evaluation and optional activation / Evaluasi dan aktivasi opsional

Every preset and editing control is available for **365 days** from first launch on each computer. No account, payment card, subscription, automatic renewal or automatic charge is required.

Seluruh preset dan kontrol editing tersedia selama **365 hari** sejak pertama kali dijalankan pada setiap komputer. Tidak memerlukan akun, kartu pembayaran, langganan, perpanjangan otomatis, atau tagihan otomatis.

After full editing ends, existing projects, saved values, meters, automation playback and audio processing are designed to continue in project-safe read-only mode. Optional activation is relevant only for continued editing, subject to the EULA and technical compatibility.

Setelah full editing berakhir, project lama, nilai tersimpan, meter, playback automation, dan processing audio dirancang tetap berjalan dalam mode project-safe read-only. Aktivasi opsional hanya diperlukan untuk melanjutkan editing, tunduk pada EULA dan kompatibilitas teknis.

The current standard v0.5-generation activation offer is:

- **IDR 399,000** one-time perpetual editing activation;
- no subscription, automatic renewal or automatic charge;
- one active customer-owned or customer-controlled computer at a time;
- purchase initiated from the ArSonKuPik activation card through the authorised hosted Midtrans QRIS checkout;
- automatic signed activation after verified payment, with manual activation fallback;
- reasonable reinstall or replacement-computer recovery after purchase verification and abuse review.

Penawaran aktivasi standar generasi v0.5 saat ini:

- **Rp399.000** untuk aktivasi editing perpetual satu kali;
- tanpa langganan, perpanjangan otomatis, atau tagihan otomatis;
- satu komputer aktif milik atau di bawah kendali pelanggan pada satu waktu;
- pembelian dimulai dari card aktivasi ArSonKuPik melalui checkout Midtrans QRIS resmi;
- aktivasi bertanda tangan diterapkan otomatis setelah pembayaran terverifikasi, dengan fallback aktivasi manual;
- pemulihan instalasi atau komputer pengganti secara wajar setelah verifikasi pembelian dan pemeriksaan penyalahgunaan.

There is no obligation to buy. A completed payment purchases concrete licence rights; it is not a donation. See `EULA.txt` and `PURCHASE_TERMS.txt` for the controlling terms.

## Compatibility

- Windows 10/11, 64-bit
- VST3 plug-in for use inside a compatible DAW
- Standalone application for supported audio-device workflows
- macOS, Linux, VST2, AAX and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer, device and security policy
- Evaluate in the actual target workflow before critical delivery or broadcast

## Install and verify / Instalasi dan verifikasi

1. Use the website installer button or open the [latest official release](https://github.com/masarray/vst-enhancer/releases/latest).
2. Download the Windows x64 setup `.exe` selected from the latest release.
3. Download `SHA256SUMS.txt` from the same release.
4. Verify the exact downloaded filename:

```powershell
Get-FileHash .\<downloaded-installer-name>.exe -Algorithm SHA256
```

5. Compare the result with `SHA256SUMS.txt`. Do not continue if the values differ.
6. Keep normal Windows security and antivirus protection enabled.
7. In a DAW, open the plug-in manager and rescan VST3 plug-ins when required.

### Unsigned Windows package

Current public packages may be distributed without a commercial Windows code-signing certificate. Windows SmartScreen may therefore show an unknown-publisher or reputation warning. A matching SHA-256 value verifies file identity against the value published in the same release, but it does not replace antivirus scanning, endpoint protection, backups or compatibility testing.

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally and does not intentionally transmit audio, DAW projects, presets, parameter values, licence codes, crash analytics, advertising identifiers or usage analytics during normal operation.

- A bounded update check may run after the application has been open for about 30 seconds and no more than once per 24 hours; the user can also request a manual check.
- Update requests read only small public release metadata and do not include audio, project, preset, licence or analytics data.
- The website stores only the selected EN/ID language value in browser local storage.
- Purchase and activation network activity occurs only when the user deliberately starts or resumes the authorised activation flow.
- Hosted checkout and payment processing are handled by the disclosed provider under its own terms and privacy notice.
- Public GitHub Issues must not contain activation codes, Computer Request IDs, customer audio, private projects, order documents or personal data.

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

The website and README provide plain-language explanations. The controlling EULA, purchase terms, authorised checkout, receipt terms, third-party notices and mandatory applicable law govern actual use and completed transactions.

## Repository scope

This repository is public for product information, website source, release metadata, checksums, supported downloads, feedback and public legal notices.

The proprietary DSP implementation, preset recipes, application source, private signing material, Key Activator and customer activation records are not included.

The separately published MIT-licensed ArSonKuPik project remains governed by its original MIT terms. Its publication does not make this proprietary VST product open source.

## Local and self-hosted validation

Run locally on Windows:

```powershell
.\tools\validate-public-release.ps1
```

Optionally validate public release URLs from a connected machine:

```powershell
.\tools\validate-public-release.ps1 --check-remote
```

The validation checks repository/release consistency, product-first bilingual landing content, latest-download routing, public-audience readability, legal/commercial alignment and private-material exclusions.

## Safe feedback

Include the ArSonKuPik version, package type, DAW and version, Windows version, audio interface and driver, sample rate, buffer size, preset, checksum, expected behaviour, actual behaviour and exact reproduction steps.

Never publish activation codes, Computer Request IDs, customer audio, private projects, personal data, order records or security exploit details. Use [SECURITY.md](SECURITY.md) for private vulnerability reporting.

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
