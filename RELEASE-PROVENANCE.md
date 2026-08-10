# ArSonKuPik Release Provenance

This document records the reviewed public release path for ArSonKuPik VST. It describes how public binaries are produced without publishing the proprietary DSP source.

## v0.5.24 release identity

- Public release tag: `v0.5.24`
- Proprietary source commit: `2c764f82b0fc99eaff04d918cef4f839db7509e5`
- Public distribution repository: `masarray/vst-enhancer`
- Proprietary source repository: private `masarray/askp-vst`
- Required JUCE version: `8.0.14`
- Public package policy: binary-only
- Public macOS release workflow run: `31344141995`
- Approved macOS release-helper commit: `30fda826fec8aeb00eba07fe0d920e85b42d4596`

The public `v0.5.24` release, its attached `BUILDINFO-*.json` files and checksum inventories are authoritative for downloadable filenames, hashes and platform provenance.

## Windows path

Windows x64 packages were built and audited locally on Windows from the exact approved release source before the public draft release was considered complete.

Required Windows release assets:

- `ArSonKuPik-v0.5.24-Windows-x64-Setup.exe`
- `ArSonKuPik-v0.5.24-Windows-x64-VST3.zip`
- `ArSonKuPik-v0.5.24-Windows-x64-Standalone.zip`
- `BUILDINFO-Windows.json`
- `SHA256SUMS-Windows.txt`

The Windows release gate includes the reviewed source/version checks, generated-production-DSP parity checks, preset and transition audits, multirate/realtime stability checks, crackle tests, Gain Match transition validation, binary packaging checks and checksum generation.

The Windows packages are not commercially code-signed and may trigger SmartScreen or enterprise reputation warnings.

## macOS path

macOS Universal packages were built and audited by the single approved manual GitHub Actions release workflow in the public binary repository. The successful v0.5.24 publication path used workflow run `31344141995`.

The workflow:

1. requires an approved hybrid release request and exact proprietary source tag;
2. keeps private-source GitHub Actions disabled;
3. runs the public build job with read-only public contents permission inside the protected `mac-release` environment;
4. resolves the independently pinned proprietary source commit and release-helper commit;
5. stages the canonical public legal bundle without adding proprietary source to the public repository;
6. builds Release binaries for Apple Silicon `arm64` and Intel `x86_64` with deployment target macOS 11.0;
7. runs the reviewed cross-platform DSP, preset, transition, multirate, stereo, headroom, crackle, Gain Match and binary-load gates;
8. validates both architectures and ad-hoc signatures;
9. packages VST3 ZIP, Standalone ZIP and DMG assets;
10. rejects source, development, private-key and activation material from the publish handoff;
11. verifies macOS build provenance and platform checksum inventory;
12. transfers only the verified source-free handoff into the write-scoped publish job;
13. verifies the staged Windows assets before combining Windows and macOS checksum inventories;
14. updates the bilingual public release metadata and landing-page source;
15. validates and deploys the public website/mirror boundary before publication; and
16. publishes the release only after every required Windows, macOS, metadata and site gate succeeds.

Required macOS release assets:

- `ArSonKuPik-v0.5.24-macOS-Universal.dmg`
- `ArSonKuPik-v0.5.24-macOS-Universal-VST3.zip`
- `ArSonKuPik-v0.5.24-macOS-Universal-Standalone.zip`
- `BUILDINFO-macOS.json`
- `SHA256SUMS-macOS.txt`
- `SHA256SUMS.txt`

The macOS packages are ad-hoc signed only. They are not Developer ID signed and are not notarized. Gatekeeper may require Control-click → **Open** or **Open Anyway**.

## v0.5.24 runner-local compatibility boundary

The immutable private `v0.5.24` tag remains the product-source identity recorded by the release. The macOS build is allowed to apply only the explicitly reviewed runner-local compatibility preparation declared by the private release request and release helper.

For v0.5.24, the reviewed temporary compatibility boundary is limited to:

- `CMakeLists.txt`;
- `src/PluginProcessor.cpp`; and
- `tools/crackle_test_main.cpp`.

These runner-local operations exist only to make the exact tagged product source compile and validate correctly on the approved GitHub-hosted macOS/Xcode environment. They do not rewrite the private tag, change the Windows release provenance or publish proprietary source.

The release helper itself is independently pinned at `30fda826fec8aeb00eba07fe0d920e85b42d4596`, while the product source remains pinned at `2c764f82b0fc99eaff04d918cef4f839db7509e5`.

## Gain Match release boundary

v0.5.24 includes the reviewed Gain Match controller correction used by the production source. Publicly relevant behaviour is:

- Gain Match remains **OFF by default** for normal listening;
- enabling Gain Match provides the explicit level-equal A/B comparison path;
- the comparison controller is allowed to learn while disabled and while its intentional engagement transition settles;
- after settling, the learned target is held to avoid long-term comparison-level breathing; and
- disabling Gain Match returns the comparison correction to unity while the normal creative signal path remains the listening reference.

The release gate verifies this behaviour through transition, matched-level, recovery, peak-safety and realtime stability checks rather than by weakening audit thresholds.

## Public disclosure boundary

Public release packages and logs must not contain:

- proprietary DSP or application source;
- preset recipes or engineering-only implementation details;
- private signing keys or certificates;
- Key Activator binaries or source;
- activation codes, Computer Request IDs or customer records;
- checkout tokens, order tokens or payment credentials.

The public repository may contain product information, website source, legal notices, release metadata, checksums, build provenance and binary downloads.

## Website and distribution identity

The public distribution repository and the canonical product website are expected to describe the same supported release. For v0.5.24 this means:

- current public version `v0.5.24`;
- Windows 10/11 x64 installer, VST3 and Standalone packages;
- macOS 11+ Universal `arm64` + `x86_64` VST3, Standalone and DMG packages;
- one-year full-editing evaluation with no account, card, subscription or automatic charge;
- optional perpetual activation as described by the public release manifest; and
- GitHub Release assets as the authoritative downloadable binaries.

Cloudflare Pages at `https://arsonkupik.pages.dev/` is the canonical product/search identity. The GitHub Pages deployment remains a compatibility mirror and must advertise the same Cloudflare canonical URLs.

## User verification

Download packages only from the official GitHub Release or links resolved by the canonical product website. Calculate SHA-256 for the exact downloaded filename and compare it with `SHA256SUMS.txt` from the same release.

Windows PowerShell:

```powershell
Get-FileHash .\<downloaded-file-name> -Algorithm SHA256
```

macOS Terminal:

```bash
shasum -a 256 <downloaded-file-name>
```

Do not open or install a file when the calculated checksum differs.
