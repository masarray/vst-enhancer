# Public Distribution Changelog

This changelog covers the public product website, distribution metadata, legal notices, supported packages, and public support surface. Proprietary DSP implementation details are not published in this repository.

## v0.5.12 — 17 July 2026

### Public distribution

- Enabled the reviewed Windows x64 public evaluation release.
- Published separate installer, VST3 ZIP, Standalone ZIP, and SHA-256 checksum assets.
- Declared the JUCE 8.0.14 dependency baseline in public release metadata.

### Evaluation and licensing

- Published the 365-day full-editing evaluation model.
- Clarified no-card, no-subscription, and no-automatic-charge behaviour.
- Documented project-safe read-only behaviour after evaluation.
- Published the optional USD 25 perpetual-editing offer for the v0.5 generation.
- Separated evaluation-download availability from paid-checkout availability.

### Website and repository

- Rebuilt the bilingual English/Bahasa Indonesia landing page.
- Added structured software metadata, canonical and language-alternate signals, social preview metadata, sitemap support, and release-driven download links.
- Added clear unsigned-package and SHA-256 verification guidance.
- Added Security, Support, Privacy, EULA, Purchase Terms, and third-party transparency documents.
- Added local and self-hosted release validation without requiring GitHub-hosted runner minutes.

### Known limitations

- Current Windows packages are unsigned and may trigger Windows SmartScreen or enterprise security-policy warnings.
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer size, and Windows configuration.
- Paid checkout is not currently enabled; the public evaluation download is available separately.
