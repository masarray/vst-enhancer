# ArSonKuPik VST — One-Year Free Public Beta

**ArSonKuPik v0.5.x** provides 365 days of full editing from first launch on each computer. No account, internet connection, or audio watermark is required.

<p align="center">
  <img src="site/assets/arsonkupik-vst-ui-v050.webp" width="1080" alt="ArSonKuPik VST interface showing the Mas Ari Signature preset, smart enhancement controls, A/B comparison, bypass, protect, and input-output meters">
</p>

ArSonKuPik is a smart audio enhancer for mastering, mix bus, tracks, and creative processing. The DSP and application source remain private in `masarray/askp-vst`; this public repository contains the landing site, documentation, release metadata, and downloadable Windows binaries.

## Public beta licence behaviour

- 365 days of full preset and knob editing from first launch
- No login or online validation
- No audio watermark
- Windows 10/11 x64
- VST3 and Standalone application
- Unsigned build; Windows SmartScreen may show a warning

After 365 days, the plugin enters **read-only mode**:

- Existing projects continue to open and sound normally
- Current processing and saved parameter values remain active
- Input/output meters continue working
- Presets, knobs, A/B, bypass, and editing controls are covered by an activation panel
- The user can copy a Computer Request ID and paste a hardware-bound activation code supplied by Mas Ari
- Activation is offline and does not require a permanent internet connection

The plugin does not mute, inject noise, or force true bypass when the editable beta ends.

## Download

- [Download ArSonKuPik v0.5.0 Public Beta](https://github.com/masarray/vst-enhancer/releases/tag/v0.5.0)
- [Open the product landing page](https://masarray.github.io/vst-enhancer/)

Verify every download against `SHA256SUMS.txt` from the same GitHub Release.

## Send beta feedback

Please include:

- DAW and version
- Windows version
- Audio interface and sample rate
- Preset used
- Whether the issue occurs in VST3, Standalone, or both
- Reproduction steps
- CPU behaviour, clipping, pumping, scan failure, or sound-quality observations

[Report a bug or send public-beta feedback](https://github.com/masarray/vst-enhancer/issues/new/choose)

macOS and VST2 are intentionally not distributed.

© 2026 Tutorial Mas Ari / MasArray. Binary use is governed by the EULA included with the installer.