# ArSonKuPik Support Guide

## Use the right channel

### Public reproducible bug

Use the [GitHub bug-report form](https://github.com/masarray/vst-enhancer/issues/new/choose) for reproducible, non-confidential defects in an official ArSonKuPik package.

Include:

- ArSonKuPik version and exact package type;
- package SHA-256;
- operating system and version;
- VST3 or Standalone;
- DAW or host and exact version;
- audio interface, driver or device layer, sample rate and buffer size;
- preset and relevant control positions;
- exact reproduction steps;
- expected and actual behaviour;
- whether bypass removes the problem; and
- a crash log or screenshot only after removing confidential information.

For macOS reports, also include the Mac model, processor architecture (`arm64` or `x86_64`), installation method (DMG or ZIP), and any Gatekeeper message. For Windows reports, include the Windows edition/build, installer or ZIP package, and relevant SmartScreen or endpoint-security message.

### Security vulnerability

Follow [SECURITY.md](SECURITY.md). Do not publish exploit details, activation weaknesses or suspected signing-material exposure in a public issue.

### Activation or purchase information

Do not place any of the following in a public issue:

- activation code;
- Computer Request ID;
- order ID or receipt;
- proof of purchase;
- personal contact information; or
- payment information.

Public checkout is separate from the evaluation download. The current product manifest records optional activation as available in the application; do not assume that a public web checkout exists.

### Compatibility question

Compatibility depends on the DAW or host, operating system, driver or device layer, audio interface, sample rate, buffer size, plug-in scan path and security policy. Test the current evaluation build in the actual target workflow before critical use.

## Before reporting

1. Confirm that the file came from the official GitHub Release or product website.
2. Verify SHA-256 against the checksum file from the same release.
3. Confirm the current version in the plug-in, Standalone About view or release page.
4. Reproduce in a new minimal project when possible.
5. Compare VST3 and Standalone if the issue applies to both.
6. Test with bypass and at matched loudness for audio-quality reports.
7. Check whether the problem follows the project, host, driver, device or computer.
8. Remove confidential customer, project, activation and order information.

## Response scope

Public support prioritizes:

- reproducible defects in the current supported release;
- release integrity and installation problems;
- cross-platform compatibility evidence;
- documentation or localization errors; and
- safe, actionable public-distribution improvements.

Public support does not cover unofficial mirrors, modified packages, cracked builds, activation bypass, redistributed installers, reverse-engineered variants or third-party bundles.
