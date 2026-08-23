# Public Distribution Changelog

## v0.5.25 - 23 August 2026

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.25` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

## Unreleased

No unreleased public distribution changes are currently documented after v0.5.24.

## v0.5.24 - 10 August 2026

### Sound and A/B reliability

- Refined the approved Mas Ari Signature balance with warmer vocal-body support and polished upper-air behaviour while preserving the established musical character.
- Corrected the production Gain Match controller so its level-equal comparison target can remain current while Gain Match is OFF and during the intentional engagement transition, then holds after settling to avoid long-term comparison-level breathing.
- Kept Gain Match **OFF by default** for normal listening; enabling it remains the explicit level-equal A/B comparison mode rather than a hidden loudness correction in the normal creative path.
- Preserved the independent peak-safety path and verified Gain Match enable, settled match, OFF recovery and transition behaviour without widening the approved release thresholds.
- Passed the release stability gate across the reviewed 48/96 kHz and 32/64/128-sample realtime matrices with the high-stress 96 kHz / 32-sample cases retained as diagnostic trend checks.

### Public website and documentation

- Synchronized the English and Bahasa Indonesia landing surfaces with v0.5.24, Windows x64 and macOS Universal distribution, the current evaluation model and the intended Gain Match workflow.
- Kept every public download CTA resolved through the official `masarray/vst-enhancer` GitHub Release surface and kept SHA-256 verification visible.
- Kept Cloudflare Pages at `https://arsonkupik.pages.dev/` as the canonical public/search identity while the GitHub Pages deployment remains a compatibility mirror with Cloudflare canonical URLs.
- Published release metadata for source identity, platform packages, signing status, evaluation behaviour and official download URLs in the bilingual public manifests.
- Updated the public release-provenance document to the exact v0.5.24 source, macOS helper and successful release-workflow identity.

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.24` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

## v0.5.23 - 31 July 2026

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.23` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

## v0.5.22 - 31 July 2026

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.22` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

## v0.5.21 — 28 July 2026

### Cross-platform distribution

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.21` tag and pinned commit from the private proprietary source repository.
- Published Windows installer, VST3 and Standalone packages plus macOS Universal VST3, Standalone and DMG packages.
- macOS packages target macOS 11.0, contain Apple Silicon `arm64` and Intel `x86_64`, are ad-hoc signed, and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- GitHub Actions was used only by the public binary repository for the macOS build; Actions remained disabled in the private source repository.

This changelog covers the public product website, distribution metadata, legal notices, supported packages and public support surface. Proprietary DSP implementation details are not published in this repository.

## v0.5.20 — 27 July 2026

### Vocal balance and listening comfort

- Added content-aware warm vocal-body support for bright/high female vocals while preserving the approved Presence/Tickle character.
- Preserved stable long-term level behaviour, optional strict Gain Match comparison and independent `-1 dBFS` peak safety.

### Cross-platform release

- Built and audited Windows x64 binaries locally on Windows.
- Built and audited macOS Universal binaries through the single approved manual workflow in `masarray/vst-enhancer`, using the exact `v0.5.20` tag from the private proprietary source repository.
- Added unsigned Windows installer, VST3 and Standalone packages.
- Added macOS Universal VST3, Standalone and DMG packages for Apple Silicon `arm64` and Intel `x86_64`.
- Declared macOS 11.0 as the deployment target.
- macOS packages are ad-hoc signed only and are not Developer ID signed or notarized.
- Published binary-only assets with Windows, macOS and combined SHA-256 checksums plus build-provenance metadata.
- Kept proprietary source, private signing material, Key Activator and customer activation records out of the public packages.

## v0.5.19 — 26 July 2026

### Signature engine and workflow

- Promoted Mas Ari Signature from a preset into the one immutable DSP engine.
- Added 13 professional factory starting points over that engine and user preset Save, Save As, Load and Delete.
- Restored the compact novice-friendly preset picker and fixed rounded tooltip corners plus About/Unlock overlay flicker.

### Sound and reliability

- Gain Match OFF now preserves safe creative lift instead of attenuating output toward a hidden loudness target. Gain Match ON remains the explicit strict level-equal comparison mode.
- Added a `+0.90 dB` minimum Active floor, independent `-1 dBFS` peak safety, stronger low-level vitality and bass-retention gates across all profiles.
- Passed local DSP, preset, multirate, snapshot and anti-crackle validation, including zero CPU deadline misses at 48/96 kHz and 32/64/128 samples.

### Distribution

- Published Windows x64 installer, VST3 ZIP, Standalone ZIP and `SHA256SUMS.txt` through the local binary-only release workflow.
- Aligned public product, activation and privacy text with the shipped v0.5.19 implementation.

## v0.5.13 — 18 July 2026

### Performance and UX

- Reduced editor repaint and static-background rendering overhead.
- Reduced creative-parameter retune work during automation and small buffers.
- Skipped inactive colour lanes and fused wrapper buffer passes.
- Added high-accuracy fast nonlinear colour processing with SSE2 stereo acceleration and scalar fallback.

### Smart-liquid visual

- Removed the centre radial overlay that obscured the liquid.
- Kept the upper glass reflection while cleaning the centre of the sphere.
- Blended and removed small bubbles before they reach the clean upper violet liquid area.

### Compatibility

- Windows x64 VST3 and Standalone.
- Reviewed JUCE 8.0.14 dependency baseline.
- Same 365-day evaluation and project-safe read-only behaviour.

## v0.5.12 — 17 July 2026

### Public distribution

- Enabled the reviewed Windows x64 public evaluation release.
- Published separate installer, VST3 ZIP, Standalone ZIP and SHA-256 checksum assets.
- Declared the JUCE 8.0.14 dependency baseline in public release metadata.

### Evaluation and licensing

- Published the 365-day full-editing evaluation model.
- Clarified no-card, no-subscription and no-automatic-charge behaviour.
- Documented project-safe read-only behaviour after evaluation.
- Published the optional USD 25 perpetual-editing offer for the v0.5 generation.
- Separated evaluation-download availability from paid-checkout availability.

### Website and repository

- Rebuilt the bilingual English/Bahasa Indonesia landing page.
- Added structured software metadata, deterministic canonical metadata, social preview metadata, sitemap support and release-driven download links.
- Added clear unsigned-package and SHA-256 verification guidance.
- Added Security, Support, Privacy, EULA, Purchase Terms and third-party transparency documents.
- Added local and self-hosted release validation without requiring GitHub-hosted runner minutes.

### Known limitations

- Current Windows packages are unsigned and may trigger Windows SmartScreen or enterprise security-policy warnings.
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer size and Windows configuration.
- Paid checkout is not currently enabled; the public evaluation download is available separately.
