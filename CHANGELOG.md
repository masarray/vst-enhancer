# Public Distribution Changelog

This changelog covers the public product website, distribution metadata, legal notices, supported packages, and public support surface. Proprietary DSP implementation details are not published in this repository.

## Unreleased — latest-release direct downloads

### Download routing

- Changed every public installer CTA to resolve the latest published GitHub Release dynamically.
- Selects the official Windows installer `.exe` from the latest release assets instead of relying on a version-pinned `release.json` URL.
- Updates the visible version, installer checksum command, package links, release links, and structured download metadata from the resolved release.
- Applies the same latest-installer behaviour to the main landing, mobile sticky CTA, final CTA, download card, navigation CTA, and optional-activation page.
- Rejects portable executables, activation utilities, key tools, non-HTTPS URLs, and assets outside this repository's official release-download path.
- Locks installer href values so a late response from older local metadata cannot overwrite the latest installer.
- Falls back only to the repository's `/releases/latest` page when GitHub's latest-release API cannot be resolved; it does not fall back to an older version-specific installer.

### Validation

- Added regression checks for GitHub's latest-release endpoint, official `browser_download_url` use, direct `.exe` selection, stale-link protection, safe fallback behaviour, and activation-page coverage.

## Unreleased — compact trial-first public landing

### Conversion and information architecture

- Reduced the public landing to ten major sections with a compact four-audience strip, one three-minute evaluation flow, a combined controls-and-presets section, and a merged technical-download-installation journey.
- Reduced the FAQ to eight essential questions and moved legal documents into one optional disclosure.
- Added a viewport-aware mobile sticky download CTA that appears after the hero action leaves view.
- Kept Inter as the primary font and formalised a 10 px, 11 px, and 12 px compact typography scale.

### Trust and optional activation

- Kept price and payment details outside the free-evaluation journey.
- Standardised development-support wording to “may help sustain” so it does not imply that individual payments are earmarked for a vendor or expense.
- Added future checkout safeguards requiring HTTPS, an exact hostname allowlist, seller and provider identity, currency, tax and refund disclosures, and explicit page-indexing readiness before a payment link can appear.
- Kept paid checkout disabled and the activation page `noindex,follow` until those requirements are met.

### SEO and validation

- Kept the product on one deterministic canonical URL and removed query-language URLs from the sitemap.
- Updated validators to prevent the landing from regrowing beyond ten sections or eleven disclosures.
- Added checks for mobile CTA behaviour, the Inter 10/11/12 px scale, consistent funding language, trusted checkout fields, URL allowlisting, and owner-controlled self-hosted validation.

## Unreleased — trial-first public landing

### Evaluation-first product journey

- Repositioned the main landing page around listening, free evaluation, download confidence, privacy, and honest A/B comparison.
- Made the 365-day full-editing evaluation, no-account, no-card, no-subscription, no-automatic-charge, and no-purchase-obligation terms prominent.
- Moved the unsigned Windows package disclosure from the hero into a progressive installation and file-verification section.
- Added a three-minute evaluation workflow using familiar audio and loudness-matched A/B comparison rather than publishing unverified or misleading audio examples.

### Public audience and readability

- Added dedicated entry paths for first-time users, musicians and creators, producers, and audio engineers.
- Added plain-language explanations of VST3, Standalone, Windows requirements, local audio processing, and compatibility testing.
- Expanded the six control descriptions with practical “listen for” guidance.
- Added task-oriented preset explanations, a visual three-step workflow, technical requirement summaries, and a four-step installation guide.
- Expanded the bilingual FAQ with a beginner-friendly VST3 versus Standalone explanation.
- Added responsive presentation rules for desktop, tablet, mobile, keyboard focus, and reduced-motion preferences.

### Optional activation

- Moved price, device limits, activation details, checkout prerequisites, and development-support messaging to a separate `/activation/` page.
- Marked the activation page `noindex,follow` while paid checkout is not configured.
- Clarified that activation is a purchase for concrete licence rights, not a donation.
- Clarified that activation revenue may support independent development, applicable JUCE licensing, testing, documentation, support, security, and trusted Windows distribution without promising that individual payments are earmarked for a particular expense.

### Validation

- Added dependency-free checks for four audience paths, bilingual coverage, plain-language format explanations, installation guidance, price separation, release-driven download links, required visual components, duplicate IDs, and balanced CSS.
- Kept validation local and manually triggered on the self-hosted runner.

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
- Added structured software metadata, deterministic canonical metadata, social preview metadata, sitemap support, and release-driven download links.
- Added clear unsigned-package and SHA-256 verification guidance.
- Added Security, Support, Privacy, EULA, Purchase Terms, and third-party transparency documents.
- Added local and self-hosted release validation without requiring GitHub-hosted runner minutes.

### Known limitations

- Current Windows packages are unsigned and may trigger Windows SmartScreen or enterprise security-policy warnings.
- Compatibility varies by DAW, driver, audio interface, sample rate, buffer size, and Windows configuration.
- Paid checkout is not currently enabled; the public evaluation download is available separately.
