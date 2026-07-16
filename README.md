# ArSonKuPik VST — Public Download, Documentation, and Legal Repository

[![Website](https://img.shields.io/badge/Website-ArSonKuPik-9b68ff)](https://masarray.github.io/vst-enhancer/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-5b8def)](#compatibility)
[![Formats](https://img.shields.io/badge/Formats-VST3%20%2B%20Standalone-c5a0ff)](#compatibility)
[![Evaluation](https://img.shields.io/badge/Evaluation-365%20days-5bd49a)](#evaluation--evaluasi)
[![Licence](https://img.shields.io/badge/Product-Proprietary-ef7c8f)](EULA.txt)

**English:** ArSonKuPik is a smart audio enhancer for mastering, mix bus, tracks, vocals, podcasts, and creative processing. This public repository contains the bilingual landing page, release metadata, public legal documents, checksums, and supported Windows downloads when distribution is enabled.

**Bahasa Indonesia:** ArSonKuPik adalah audio enhancer cerdas untuk mastering, mix bus, track, vokal, podcast, dan pemrosesan kreatif. Repository publik ini berisi landing page dwibahasa, metadata rilis, dokumen legal publik, checksum, serta unduhan Windows yang didukung ketika distribusi sudah diaktifkan.

> **Distribution safety / Keamanan distribusi:** Download only when the [official landing page](https://masarray.github.io/vst-enhancer/) reports that distribution is enabled. Unduh hanya ketika landing page resmi menyatakan distribusi aktif. Do not use mirrors or re-uploaded packages. Verify `SHA256SUMS.txt` from the same GitHub Release.

<p align="center">
  <a href="https://masarray.github.io/vst-enhancer/">
    <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing the Mas Ari Signature preset and smart enhancement controls">
  </a>
</p>

## Quick links / Tautan cepat

- **[Open the bilingual product website / Buka website produk dwibahasa](https://masarray.github.io/vst-enhancer/)**
- **[Official releases / Rilis resmi](https://github.com/masarray/vst-enhancer/releases)**
- **[Report a reproducible issue / Laporkan masalah](https://github.com/masarray/vst-enhancer/issues/new/choose)**
- **[EULA](EULA.txt)** · **[Purchase terms](PURCHASE_TERMS.txt)** · **[Privacy](PRIVACY.txt)** · **[Third-party notices](THIRD_PARTY_NOTICES.txt)**

## Evaluation / Evaluasi

| English | Bahasa Indonesia |
|---|---|
| 365 days of full preset and control editing from first launch on each computer. | 365 hari akses penuh ke preset dan kontrol sejak pertama kali dijalankan pada tiap komputer. |
| No payment card, account, subscription, automatic charge, or audio watermark is required to begin. | Tidak memerlukan kartu pembayaran, akun, langganan, tagihan otomatis, atau watermark audio untuk memulai. |
| Personal and commercial audio-production use is permitted during evaluation, subject to the EULA. | Penggunaan produksi audio personal dan komersial diizinkan selama evaluasi, tunduk pada EULA. |
| After evaluation, projects and saved processing are designed to continue in project-safe read-only mode. | Setelah evaluasi, project dan pemrosesan tersimpan dirancang tetap berjalan dalam mode project-safe read-only. |
| Buying an activation is optional. | Pembelian aktivasi bersifat opsional. |

The published standard offer for the v0.5 evaluation cohort is a **USD 25 perpetual editing activation**, before applicable tax, with no subscription or automatic renewal. One purchase may be used on up to two active customer-owned or customer-controlled computers. Final seller, currency, tax, payment, and refund information will be shown before payment.

Penawaran standar yang dipublikasikan untuk pengguna evaluasi v0.5 adalah **aktivasi editing perpetual USD 25**, sebelum pajak yang berlaku, tanpa langganan atau perpanjangan otomatis. Satu pembelian dapat digunakan pada maksimal dua komputer aktif milik atau di bawah kendali pelanggan. Informasi penjual, mata uang, pajak, pembayaran, dan refund final akan ditampilkan sebelum pembayaran.

## Compatibility

- Windows 10/11, 64-bit
- VST3 plug-in
- Standalone application
- macOS, Linux, VST2, AAX, and Audio Unit are not currently distributed
- Compatibility varies by DAW, driver, device, sample rate, and buffer configuration; evaluate before critical use

## Beginner installation / Instalasi untuk pemula

1. Open the [official release page](https://github.com/masarray/vst-enhancer/releases).
2. Download only after the landing page reports that distribution is enabled.
3. Verify the file against `SHA256SUMS.txt` from the same release:

```powershell
Get-FileHash .\ArSonKuPik-Setup.exe -Algorithm SHA256
```

4. Run the installer. The current build is unsigned, so Windows SmartScreen may show a reputation warning.
5. In your DAW, open the plug-in manager and rescan VST3 plug-ins.
6. Keep backups and verify final renders before delivery or broadcast.

Panduan lengkap dalam Bahasa Indonesia dan English tersedia pada [landing page](https://masarray.github.io/vst-enhancer/#getting-started).

## Privacy summary / Ringkasan privasi

ArSonKuPik processes audio locally. It does not intentionally transmit audio, DAW projects, preset selections, licence codes, crash analytics, or usage analytics. No permanent connection is required for normal processing or offline activation. A network request occurs only when the user manually requests an update check. See [PRIVACY.txt](PRIVACY.txt).

ArSonKuPik memproses audio secara lokal. Software tidak secara sengaja mengirim audio, project DAW, pilihan preset, kode lisensi, crash analytics, atau usage analytics. Tidak diperlukan koneksi permanen untuk pemrosesan normal maupun aktivasi offline. Permintaan jaringan hanya terjadi saat pengguna melakukan update check secara manual. Lihat [PRIVACY.txt](PRIVACY.txt).

## Public repository scope

This repository is public for product information, distribution, release metadata, checksums, feedback, and required legal notices. The proprietary DSP implementation, preset recipes, application source, private RSA signing key, Key Activator, and customer activation records are not included.

Repository ini bersifat publik untuk informasi produk, distribusi, metadata rilis, checksum, feedback, dan pemberitahuan legal wajib. Implementasi DSP proprietary, recipe preset, source aplikasi, private RSA signing key, Key Activator, dan catatan aktivasi pelanggan tidak disertakan.

## Legal documents

- [End User Licence Agreement](EULA.txt)
- [Commercial Activation Terms](PURCHASE_TERMS.txt)
- [Privacy Notice](PRIVACY.txt)
- [Third-Party Notices](THIRD_PARTY_NOTICES.txt)
- [Original ArSonKuPik MIT Notice](ArSonKuPik-MIT.txt)
- [Steinberg VST3 SDK MIT Notice](Steinberg-VST3-SDK-MIT.txt)
- [Plus Jakarta Sans OFL 1.1](Plus-Jakarta-Sans-OFL-1.1.txt)
- [Public Repository Notice](LICENSE.txt)

The bilingual website and this README provide plain-language explanations. The controlling EULA, purchase terms, checkout terms, receipt terms, and mandatory applicable consumer law govern actual use and transactions.

Konten dwibahasa pada website dan README ini adalah penjelasan dengan bahasa sederhana. Penggunaan dan transaksi sebenarnya diatur oleh EULA, ketentuan pembelian, ketentuan checkout, ketentuan receipt, dan hukum perlindungan konsumen wajib yang berlaku.

## Safe feedback / Feedback yang aman

Include DAW and version, Windows version, audio interface, sample rate, buffer size, preset, plug-in format, and reproduction steps. **Never post activation codes, Computer Request IDs, private projects, customer audio, or personal information in a public issue.**

Sertakan DAW dan versinya, versi Windows, audio interface, sample rate, buffer size, preset, format plug-in, dan langkah reproduksi. **Jangan memposting kode aktivasi, Computer Request ID, project privat, audio pelanggan, atau informasi pribadi pada issue publik.**

Copyright (C) 2026 Tutorial Mas Ari / MasArray. All rights reserved. ArSonKuPik VST is proprietary software licensed under `EULA.txt`; third-party components remain governed by their own licence terms.
