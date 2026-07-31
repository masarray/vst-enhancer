# Public Distribution Changelog

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

## Unreleased

### Cross-platform product copy and release integrity

- Aligned README and public release documentation with the shipped Windows x64 and macOS Universal packages.
- Corrected the v0.5.20 provenance description: Windows was built and audited locally, while macOS Universal was built and audited by the approved manual workflow in the public binary repository using the exact private source tag.
- Added an explicit public provenance document and validation gate for platform, signing and source-disclosure consistency.
- Normalised legacy changelog punctuation and moved unreleased work above published versions.

### Latest-release direct downloads

- Changed every public installer CTA to resolve the latest published GitHub Release dynamically.
- Selects the official Windows installer `.exe` from the latest release assets instead of relying on a version-pinned `release.json` URL.
- Updates the visible version, installer checksum command, package links, release links and structured download metadata from the resolved release.
- Applies the same latest-installer behaviour to the main landing, mobile sticky CTA, final CTA, download card, navigation CTA and optional-activation page.
- Rejects portable executables, activation utilities, key tools, non-HTTPS URLs and assets outside this repository's official release-download path.
- Locks installer `href` values so a late response from older local metadata cannot overwrite the latest installer.
- Falls back only to the repository's `/releases/latest` page when the API cannot be resolved; it does not fall back to an older version-specific installer.
- Added regression checks for the latest-release endpoint, official `browser_download_url` use, direct `.exe` selection, stale-link protection, safe fallback behaviour and activation-page coverage.

### Trial-first public landing

- Reduced the public landing to ten major sections with a compact four-audience strip, one three-minute evaluation flow, a combined controls-and-presets section and a merged technical download and installation journey.
- Reduced the FAQ to eight essential questions and moved legal documents into one optional disclosure.
- Added a viewport-aware mobile sticky download CTA that appears after the hero action leaves view.
- Kept Inter as the primary font and formalised a 10 px, 11 px and 12 px compact typography scale.
- Kept price and payment details outside the free-evaluation journey.
- Standardised development-support wording to “may help sustain” so it does not imply that individual payments are earmarked for a vendor or expense.
- Added future checkout safeguards requiring HTTPS, an exact hostname allowlist, seller and provider identity, currency, tax and refund disclosures and explicit page-indexing readiness before a payment link can appear.
- Kept paid checkout disabled and the activation page `noindex,follow` until those requirements are met.
- Kept the product on one deterministic canonical URL and removed query-language URLs from the sitemap.
- Added validation for mobile CTA behaviour, the Inter 10/11/12 px scale, consistent funding language, trusted checkout fields, URL allowlisting and owner-controlled local validation.

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
