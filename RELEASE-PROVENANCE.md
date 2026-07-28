# ArSonKuPik Release Provenance

This document records the reviewed public release path for ArSonKuPik VST. It describes how public binaries are produced without publishing the proprietary DSP source.

## v0.5.20 release identity

- Public release tag: `v0.5.20`
- Proprietary source commit: `2170310044c75dc5525ccb3901a7fecca1a5a64d`
- Public distribution repository: `masarray/vst-enhancer`
- Proprietary source repository: private `masarray/askp-vst`
- Required JUCE version: `8.0.14`
- Public package policy: binary-only

The release manifest and release assets are authoritative for downloadable file names and checksums.

## Windows path

Windows x64 packages were built and audited locally on Windows before the public draft release was considered complete.

Required Windows release assets:

- `ArSonKuPik-v0.5.20-Windows-x64-Setup.exe`
- `ArSonKuPik-v0.5.20-Windows-x64-VST3.zip`
- `ArSonKuPik-v0.5.20-Windows-x64-Standalone.zip`
- `BUILDINFO-Windows.json`
- `SHA256SUMS-Windows.txt`

The Windows packages are not commercially code-signed and may trigger SmartScreen or enterprise reputation warnings.

## macOS path

macOS Universal packages were built and audited by the single approved manual GitHub Actions workflow in this public repository. The workflow:

1. requires a complete Windows draft release;
2. verifies that this repository contains exactly one approved manual release workflow;
3. runs only for repository owner `masarray` in the protected `mac-release` environment;
4. checks out the exact private source tag matching the release tag;
5. verifies the approved hybrid release request;
6. builds Release binaries for Apple Silicon `arm64` and Intel `x86_64` with deployment target macOS 11.0;
7. runs the cross-platform DSP, preset, transition, multirate, stereo, headroom, crackle and binary-load gates;
8. validates both architectures with `lipo`;
9. applies and verifies ad-hoc signatures;
10. packages VST3 ZIP, Standalone ZIP and DMG assets;
11. rejects source, development, private-key and activation material from the public package trees;
12. produces macOS and combined SHA-256 checksum files before publication.

Required macOS release assets:

- `ArSonKuPik-v0.5.20-macOS-Universal.dmg`
- `ArSonKuPik-v0.5.20-macOS-Universal-VST3.zip`
- `ArSonKuPik-v0.5.20-macOS-Universal-Standalone.zip`
- `BUILDINFO-macOS.json`
- `SHA256SUMS-macOS.txt`
- `SHA256SUMS.txt`

The macOS packages are ad-hoc signed only. They are not Developer ID signed and are not notarized. Gatekeeper may require Control-click → Open or **Open Anyway**.

## v0.5.20 runner-local compatibility preparation

The immutable private `v0.5.20` tag remains the source identity recorded by the release. During the macOS job, the runner-local checkout also received bounded compatibility preparation before compilation:

- Xcode-compatible per-source DSP compiler options;
- a Clang-safe JUCE `File` reset form;
- isolation of a Windows-specific realtime timing gate from the macOS crackle audit;
- the canonical public legal bundle staged from the exact public workflow commit.

These operations modified only the temporary runner checkout. They did not rewrite the private tag or the Windows provenance.

For future versions, compatibility changes should be committed to the private source repository before the release tag whenever practical. Future `BUILDINFO-macOS.json` records should also include the public workflow commit, workflow run ID and an explicit runner-patch state.

## Public disclosure boundary

Public release packages and logs must not contain:

- proprietary DSP or application source;
- preset recipes or engineering-only implementation details;
- private signing keys or certificates;
- Key Activator binaries or source;
- activation codes, Computer Request IDs or customer records;
- checkout tokens, order tokens or payment credentials.

The public repository may contain product information, website source, legal notices, release metadata, checksums, build provenance and binary downloads.

## User verification

Download packages only from the official GitHub Release. Calculate SHA-256 for the exact downloaded filename and compare it with `SHA256SUMS.txt` from the same release.

Windows PowerShell:

```powershell
Get-FileHash .\<downloaded-file-name> -Algorithm SHA256
```

macOS Terminal:

```bash
shasum -a 256 <downloaded-file-name>
```

Do not open or install a file when the calculated checksum differs.
