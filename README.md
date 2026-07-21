# ArSonKuPik VST — Musical Audio Enhancement for Windows

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Latest release](https://img.shields.io/github/v/release/masarray/vst-enhancer?label=Latest%20release)](https://github.com/masarray/vst-enhancer/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Product licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a focused, musical Windows VST3 and standalone audio enhancer that helps creators achieve fuller, clearer and more dimensional sound without building a complex processing chain.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer Windows VST3 dan standalone yang fokus dan musikal untuk membantu kreator menghasilkan suara yang lebih berisi, jernih, dan berdimensi tanpa membangun rangkaian processing yang rumit.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing the Mas Ari Signature preset, musical enhancement controls, A/B comparison and level meters">
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

The flagship **Mas Ari Signature** preset is tuned to make familiar music feel more alive, reveal fine detail and create a more convincing live-music impression while retaining a grounded centre.

Preset flagship **Mas Ari Signature** dituning agar musik familiar terasa lebih hidup, menampilkan detail halus, dan menciptakan kesan live music yang lebih meyakinkan dengan centre yang tetap kokoh.

## 40 curated presets / 40 preset terkurasi

- **Signature — 1:** Mas Ari Signature
- **Master — 8:** Clean, Modern, Warm, Open 3D, Low-End Control, Vocal Focus, Streaming Safe, Dynamic
- **Mix Bus — 6:** Glue, Punch, Depth, Air, Warmth, Clean-Up
- **Track — 6:** Vocal Polish, Drum Punch, Bass Tight, Guitar / Synth Width, Acoustic Natural, Podcast
- **Creative — 19:** Max Enhancer, SonKu Deep Chest, Movie Sub, Night Listening, Open Air, Dangdut Koplo, EDM Festival, Reggae Dub, Rock Arena, Pop Radio, Jazz Club, Hip-Hop Punch, R&B Silk, Metal Impact, Acoustic Live, Lo-Fi Warm, K-Pop Gloss, Campursari, Radio Mas Ari

## Official links / Tautan resmi

- **[Product website / Website produk](https://masarray.github.io/vst-enhancer/)**
- **[Latest supported release / Rilis terbaru](https://github.com/masarray/vst-enhancer/releases/latest)**
- **[Optional support and activation / Dukungan dan aktivasi opsional](https://masarray.github.io/vst-enhancer/activation/)**
- **[Report a reproducible public bug / Laporkan bug publik](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[Private security reporting / Pelaporan keamanan privat](SECURITY.md)**
- **[Support guide / Panduan dukungan](SUPPORT.md)**
- **[Public changelog / Catatan perubahan](CHANGELOG.md)**

> **Distribution safety / Keamanan distribusi:** Download only from the official website or this repository's GitHub Releases. Avoid mirrors and re-uploaded packages. Verify `SHA256SUMS.txt` from the same release before running a file.
>
> Unduh hanya melalui website resmi atau GitHub Releases repository ini. Hindari mirror dan paket yang diunggah ulang. Verifikasi `SHA256SUMS.txt` dari rilis yang sama sebelum menjalankan file.

## Current public release

The reviewed local release manifest currently records **v0.5.13**. The live website also resolves GitHub's latest published full release and routes installer CTAs to the official Windows setup asset when validation succeeds.

Manifest rilis lokal yang telah direview saat ini mencatat **v0.5.13**. Website live juga mengambil rilis penuh terbaru yang dipublikasikan di GitHub dan mengarahkan CTA installer ke asset setup Windows resmi ketika validasi berhasil.

The release resolver:

1. Requests GitHub's latest published full release metadata.
2. Validates that release and asset URLs belong to `masarray/vst-enhancer` over HTTPS.
3. Selects the official Windows installer while rejecting portable executables, activation utilities and key tools.
4. Updates installer, VST3, Standalone, checksum and release-detail links.
5. Falls back only to the repository's `/releases/latest` page when the API cannot be resolved.

## Product-first public landing

The bilingual landing page now leads with:

- the VST3 audio-enhancer category;
- fuller, clearer and more dimensional sound;
- the Mas Ari Signature flagship preset;
- six focused musical controls;
- the complete 40-preset library;
- an honest matched-loudness three-minute comparison;
- Windows compatibility, privacy and official download verification.

The free evaluation and optional activation remain transparent, but they no longer replace the product itself as the main story.

Landing bilingual sekarang mengutamakan:

- kategori VST3 audio enhancer;
- suara yang lebih berisi, jernih, dan berdimensi;
- preset flagship Mas Ari Signature;
- enam kontrol musikal yang fokus;
- library lengkap 40 preset;
- perbandingan tiga menit dengan loudness seimbang;
- kompatibilitas Windows, privasi, dan verifikasi unduhan resmi.

Evaluasi gratis dan aktivasi opsional tetap dijelaskan secara transparan, tetapi tidak lagi menggantikan produk sebagai cerita utama.

## Evaluation and optional activation / Evaluasi dan aktivasi opsional

Every preset and editing control is available for 365 days from first launch on each computer. No account, payment card, subscription, automatic renewal or automatic charge is required.

Seluruh preset dan kontrol editing tersedia selama 365 hari sejak pertama kali dijalankan pada tiap komputer. Tidak memerlukan akun, kartu pembayaran, langganan, perpanjangan otomatis, atau tagihan otomatis.

After full editing ends, existing projects, saved values, meters, automation playback and audio processing are designed to continue in project-safe read-only mode. Optional activation is relevant only for continued editing, subject to the EULA and technical compatibility.

Setelah full editing berakhir, project lama, nilai tersimpan, meter, playback automation, dan processing audio dirancang tetap berjalan dalam mode project-safe read-only. Aktivasi opsional hanya relevan untuk melanjutkan editing, tunduk pada EULA dan kompatibilitas teknis.

There is no obligation to buy. An activation purchase provides concrete licence rights; it is not a donation. Revenue may help sustain independent development, applicable licensing, testing, documentation, support, security work and trusted Windows distribution.

Tidak ada kewajiban membeli. Pembelian aktivasi memberikan hak lisensi yang nyata; pembayaran tersebut bukan donasi. Pendapatan dapat membantu pengembangan independen, lisensi yang berlaku, testing, dokumentasi, dukungan, pekerjaan keamanan, dan distribusi Windows tepercaya.

## Compatibility

- Windows 10/11, 64-bit
- VST3 plug-in for use inside a compatible DAW
- Standalone application for supported audio-device workflows
- macOS, Linux, VST2, AAX and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer, device and security policy
- Evaluate in your own workflow before critical delivery or broadcast

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
7. In a DAW, open the plug-in manager and rescan VST3 plug-ins if required.

### Unsigned Windows package

Current public packages may be distributed without a commercial Windows code-signing certificate. Windows SmartScreen may therefore show an unknown-publisher or reputation warning. A matching SHA-256 value verifies file identity against the value published in the same release, but it does not replace antivirus scanning, endpoint protection, backups or compatibility testing.

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally and does not intentionally transmit audio, DAW projects, presets, parameter values, licence codes, crash analytics, advertising identifiers or usage analytics during normal operation.

- Update checking occurs only when the user requests it.
- The website stores only the selected EN/ID language value in browser local storage.
- Offline activation uses a locally generated Computer Request ID shared only when the user chooses to request activation.
- The evaluation download has no checkout and does not collect payment-card data.
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

The website and README provide plain-language explanations. The controlling EULA, applicable purchase and checkout terms, receipt terms, third-party notices and mandatory applicable law govern actual use and completed transactions.

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

The PowerShell wrapper validates repository/release consistency, the product-first landing, latest-download routing, public-audience readability and private-material exclusions.

## Safe feedback

Include the ArSonKuPik version, package type, DAW and version, Windows version, audio interface and driver, sample rate, buffer size, preset, checksum, expected behaviour, actual behaviour and exact reproduction steps.

Never publish activation codes, Computer Request IDs, customer audio, private projects, personal data, order records or security exploit details. Use [SECURITY.md](SECURITY.md) for private vulnerability reporting.

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
