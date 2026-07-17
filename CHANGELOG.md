# Public Distribution Changelog

This changelog covers the public product website, distribution metadata, legal notices, supported packages, and public support surface. Proprietary DSP implementation details are not published in this repository.

## Unreleased — trial-first landing

### Evaluation-first product journey

- Repositioned the main landing page around listening, free evaluation, download confidence, privacy, and honest A/B comparison.
- Made the 365-day full-editing evaluation, no-account, no-card, no-subscription, no-automatic-charge, and no-purchase-obligation terms prominent.
- Moved the unsigned Windows package disclosure from the hero into the installation and file-verification section.
- Added a “your music is the real demo” workflow rather than publishing unverified or misleading audio examples.

### Optional activation

- Moved price, device limits, activation details, checkout prerequisites, and development-support messaging to a separate `/activation/` page.
- Marked the activation page `noindex,follow` while paid checkout is not configured.
- Clarified that activation is a purchase for concrete licence rights, not a donation.
- Clarified that activation revenue may support independent development, applicable JUCE licensing, testing, documentation, support, security, and trusted Windows distribution without promising that individual payments are earmarked for a particular expense.

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
