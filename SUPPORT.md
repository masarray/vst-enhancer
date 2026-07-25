# ArSonKuPik Support Guide

## Use the right channel

### Public reproducible bug

Use the [GitHub bug-report form](https://github.com/masarray/vst-enhancer/issues/new/choose) for non-confidential defects.

Include:

- ArSonKuPik version and package type;
- package SHA-256;
- Windows version;
- VST3 or Standalone;
- DAW and exact version;
- audio interface, driver, sample rate, and buffer size;
- preset and relevant control positions;
- exact reproduction steps;
- expected and actual behaviour;
- whether bypass removes the problem; and
- a crash log or screenshot only after removing confidential information.

### Security vulnerability

Follow [SECURITY.md](SECURITY.md). Do not publish exploit details or suspected key exposure in a public issue.

### Activation or purchase information

Do not place any of the following in a public issue:

- activation code;
- Computer Request ID;
- order ID, order capability, or receipt;
- proof of purchase;
- personal contact information; or
- payment information.

The 365-day evaluation remains separate from optional paid activation. The current
v0.5 activation is IDR 399,000 for one active computer at a time. Purchase is
initiated deliberately from the activation card inside ArSonKuPik through hosted
Midtrans QRIS; this public repository does not expose a direct payment link.

For a legitimate reinstall, repaired computer, or replacement-computer request,
use a private support route and retain the verified purchase email, receipt or
payment history, order information, and current Computer Request ID. Do not post
those values publicly.

### Compatibility question

Compatibility depends on the DAW, driver, interface, Windows configuration, sample rate, buffer, plug-in scan path, and endpoint-security policy. Test the current evaluation build in the actual target workflow before critical use.

## Before reporting

1. Confirm that the file came from the official release.
2. Verify SHA-256 against `SHA256SUMS.txt`.
3. Confirm the current version in the plug-in or release page.
4. Reproduce in a new minimal project when possible.
5. Compare VST3 and Standalone if the issue applies to both.
6. Test with bypass and at matched loudness for audio-quality reports.
7. Remove confidential customer and project information.

## Unsupported requests

Public support does not cover unofficial mirrors, modified packages, cracked builds, activation bypass, redistributed installers, reverse-engineered variants, or third-party bundles.
