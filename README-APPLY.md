# ArSonKuPik SEO P1 + P2 On-site — Ready-to-paste bundle

Bundle ini dibuat sebagai jalur aman karena upload file PNG biner langsung melalui GitHub connector tidak dipaksakan.

## Isi bundle

- `site/assets/arsonkupik-guide-social-1200x630.png`
  - 1200 × 630 px
  - RGB PNG
  - digunakan untuk Open Graph dan Twitter large image
- `apply_seo_p1_p2.py`
  - patch idempotent untuk source repo terbaru
  - menyimpan backup pertama di folder lokal `.seo-backup/`
- `APPLY-SEO-P1-P2.ps1`
  - one-click apply + validation untuk Windows PowerShell

## P1 yang diterapkan

1. Title dan description EN/ID dibuat lebih natural dan search-intent oriented.
2. Seluruh 6 halaman lama memakai social image 1200 × 630.
3. OG dan Twitter metadata dilengkapi dan dibuat konsisten.
4. Guide EN/ID mendapat `TechArticle`, `WebPage`, dan `BreadcrumbList` JSON-LD.
5. Homepage Indonesia tidak lagi mendefinisikan `WebSite` kedua pada subdirectory `/id/`.
6. Root homepage mempertahankan satu `WebSite` entity, ditambah `WebPage` dan `SoftwareApplication` relationship.
7. Validator diperkuat untuk menolak metadata, image, schema, canonical, dan hreflang yang tidak konsisten.

## P2 on-site yang diterapkan

Membuat 8 halaman authority baru:

- `/about/` dan `/id/about/`
- `/measurements/` dan `/id/measurements/`
- `/audio-comparisons/` dan `/id/audio-comparisons/`
- `/use-cases/windows-system-audio/` dan `/id/use-cases/windows-system-audio/`

Konten sengaja tidak membuat hasil pengukuran palsu. Halaman measurement menjelaskan protokol, kondisi uji, interpretasi, dan batas pembuktian.

P2 juga menambahkan:

- internal evidence/resource hub pada landing EN/ID dan guide EN/ID;
- `seo-authority.css`;
- sitemap XML dan text berisi 14 canonical URL;
- structured data dan reciprocal hreflang pada semua halaman baru;
- static validator dan live deployment validator untuk 14 URL.

## Batas scope yang belum dapat diselesaikan oleh bundle

Bundle ini menyelesaikan **implementasi teknis P1** dan **fondasi on-site P2**, tetapi bukan seluruh pekerjaan SEO eksternal. Hal berikut tetap memerlukan pekerjaan nyata setelah deploy:

- custom domain dan DNS/CNAME;
- hasil pengukuran aktual dari audio interface serta file data mentah;
- contoh audio A/B yang legal dan benar-benar direkam;
- backlink, liputan, mention komunitas, dan distribusi eksternal;
- pengiriman sitemap, URL Inspection, dan Validate Fix di Google Search Console;
- pengukuran Core Web Vitals lapangan dan optimasi berbasis data CrUX/Search Console;
- pemantauan posisi keyword dan iterasi konten berdasarkan query nyata.

Jadi bundle ini bukan jaminan peringkat nomor satu dan tidak mengarang bukti pengukuran.

## Cara pakai paling mudah

1. Extract ZIP ini.
2. Copy seluruh isinya ke root repository lokal `vst-enhancer`.
3. Izinkan overwrite folder `site`—bundle hanya menambahkan PNG, bukan mengganti folder secara keseluruhan.
4. Buka PowerShell di root repo.
5. Jalankan:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\APPLY-SEO-P1-P2.ps1
```

Atau manual:

```powershell
python .\apply_seo_p1_p2.py
python .\tools\validate-seo.py
git diff --check
git status --short
```

## Review sebelum push

```powershell
git diff -- site/index.html
git diff -- site/id/index.html
git diff -- site/guide/index.html
git diff -- site/id/guide/index.html
git diff -- site/sitemap.xml
git diff -- tools/validate-seo.py
```

Kemudian:

```powershell
git add site tools apply_seo_p1_p2.py APPLY-SEO-P1-P2.ps1 README-APPLY.md
git commit -m "Complete P1 P2 search authority"
git push
```

## Rollback

Sebelum overwrite pertama, script menyimpan backup di luar folder yang biasa di-stage dan menambahkan `.seo-backup/` ke `.git/info/exclude` lokal agar backup tidak ikut ter-stage:

```text
.seo-backup/site/index.html
.seo-backup/site/guide/index.html
```

Untuk membatalkan seluruh perubahan yang belum di-commit:

```powershell
git restore site tools
```

Hapus halaman/file baru yang belum tracked:

```powershell
git clean -fd site/about site/id/about site/measurements site/id/measurements site/audio-comparisons site/id/audio-comparisons site/use-cases site/id/use-cases site/seo-authority.css .seo-backup
```

## Setelah deploy

Di Search Console:

1. Submit ulang `https://masarray.github.io/vst-enhancer/sitemap.xml`.
2. Inspect halaman utama, guide, measurements, audio comparisons, about, dan use-case.
3. Jalankan `Test Live URL` lalu `Request Indexing` secara bertahap.
4. Jangan request semua 14 URL berulang kali dalam hari yang sama.

## Catatan custom domain

Bundle tidak membuat `CNAME`, karena custom domain memerlukan nama domain yang benar-benar Anda miliki serta konfigurasi DNS. Tidak ada domain yang ditebak atau dipasang otomatis.
