$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.\site\index.html')) {
    throw 'Jalankan script ini dari root repository vst-enhancer.'
}

Write-Host 'Applying ArSonKuPik SEO P1 + P2 on-site...' -ForegroundColor Cyan
python .\apply_seo_p1_p2.py
python .\tools\validate-seo.py

git diff --check
Write-Host ''
Write-Host 'Changed files:' -ForegroundColor Yellow
git status --short
Write-Host ''
Write-Host 'Review selesai. Jika diff sesuai, jalankan:' -ForegroundColor Green
Write-Host '  git add site tools apply_seo_p1_p2.py APPLY-SEO-P1-P2.ps1 README-APPLY.md SHA256SUMS.txt'
Write-Host '  git commit -m "Complete P1 and P2 on-site search authority"'
Write-Host '  git push'
