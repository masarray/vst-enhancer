# Public Distribution Changelog

This changelog covers the public product website, distribution metadata, legal notices, supported packages and public support surface. Proprietary DSP implementation details remain in the private development repository.

## Unreleased — v0.5.18 P6.1 release candidate

### Signature microdetail and low-energy parity

- Adds the reviewed P6 Signature Microdetail & Ear-Tickle calibration for clearer centre-focused Presence, Air and vocal/instrument texture.
- Keeps generated Side contribution held or slightly reduced, preserving the grounded centre and mono/stereo context safeguards.
- Replaces tonal per-band Gain Match correction with one attenuation-only full-band loudness scalar so the active DSP character is not flattened during A/B listening.
- Raises the normal active loudness identity allowance to +0.70 dB and permits at most 0.30 dB of bounded full-band relief when aligned low-transient analysis detects a deficit.
- Keeps the expected active monitoring lead at or below approximately +1.00 dB while avoiding low-only gain, bass EQ, width changes or phase-altering correction.
- Retunes the uncached Mas Ari Signature Gain Match startup seed to avoid a bass-light first handover.

### Stability and real-time safety

- Retains the reviewed P5.3 preset-aware Gain Match cache, stale-target relearning and smooth first/re-enable engagement.
- Keeps the audio callback free from dynamic allocation, blocking locks and background-network work.
- Reduces creative-coefficient retune scheduling while preserving the approved 41-preset voicing, one-millisecond lookahead and -1 dBFS safety ceiling.
- Keeps cold-start RAW-to-DSP handover, bypass, preset switching and output protection inside the validated click/crackle limits.

### Public distribution preparation

- Aligns the public preset count with the 41-preset production bank, including Blues Club.
- Aligns EULA, purchase terms, privacy notice and activation information with the IDR 399,000 one-computer hosted QRIS flow.
- Aligns the reviewed fallback manifest with the latest actually published release until v0.5.18 binaries are published.
- Strengthens validation against version, commercial-policy and localized-manifest drift.

> This section does not claim that v0.5.18 has been published. The supported public version remains the release identified by GitHub's `releases/latest` endpoint until the v0.5.18 release and assets exist.

## v0.5.17 — 22 July 2026

### Musical body and preset library

- Added a stable 280–820 Hz Upper Body foundation for fuller electric-guitar power chords, bass-note definition, piano and vocal warmth below 1 kHz.
- Added the warm, touch-sensitive Blues Club creative preset.
- Redistributed the Mas Ari Signature low-mid contour for stronger 200–800 Hz continuity while keeping the 315 Hz box region controlled.
- Preserved the approved 41-preset, latency and JUCE 8.0.14 baseline.

### Startup and level behaviour

- Prewarmed both creative engines before first audio use.
- Added a peak-safe RAW-to-DSP startup handover.
- Verified that Gain Match remains monitoring-only and that disabling it restores the normal DSP lift.

### Hosted checkout and activation

- Added hosted Midtrans QRIS checkout initiated from the activation card.
- Moved checkout polling and order verification to a bounded low-priority process-wide worker outside audio and DSP paths.
- Preserved paid orders across restart and QR expiry.
- Added automatic signed ASKP-A1 activation after verified payment with manual fallback.
- Added duplicate-checkout protection and recoverable fulfilment when a service is temporarily unavailable.

## v0.5.16 — 21 July 2026

### Visual and responsiveness work

- Reduced visualizer and editor overhead while preserving the product-first visual presentation.
- Kept audio processing and primary meters independent from decorative visual timing.
- Improved first-open behaviour and reduced heavy editor work during the startup quiet window.

## v0.5.15 — 20 July 2026

### QRIS checkout foundation

- Added the first reviewed in-application QRIS checkout and activation-card workflow.
- Separated public evaluation download availability from commercial activation.
- Kept payment, order and activation work outside the real-time audio callback.

## v0.5.14 — 19 July 2026

### Quiet updater

- Added a low-priority bounded update check after an initial delay.
- Limited automatic release checks to one attempt per 24 hours while retaining manual retry.
- Limited metadata size and connection duration.
- Kept credentials, audio, projects, presets, licence values and analytics data out of update requests.

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
- Separated evaluation-download availability from optional paid activation.

### Website and repository

- Rebuilt the bilingual English/Bahasa Indonesia landing page.
- Added structured software metadata, canonical metadata, social preview metadata, sitemap support and release-driven download links.
- Added unsigned-package and SHA-256 verification guidance.
- Added Security, Support, Privacy, EULA, Purchase Terms and third-party transparency documents.

### Known limitations

- Current Windows packages are unsigned and may trigger Windows SmartScreen or enterprise security-policy warnings.
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer size and Windows configuration.
