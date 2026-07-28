# Contributing to the ArSonKuPik Public Repository

Thank you for helping improve the public ArSonKuPik product surface.

## Repository boundaries

This repository is the public distribution, documentation and support surface for a proprietary audio product. Appropriate contributions include:

- website accessibility, performance and responsive-layout fixes;
- English and Bahasa Indonesia documentation or localization corrections;
- public release metadata and checksum validation improvements;
- reproducible issue forms and support workflow improvements;
- privacy, security and legal-document clarity corrections; and
- validation tools that protect public-release consistency.

Do not submit or request:

- proprietary DSP source or preset recipes;
- activation bypasses, licence generators or reverse-engineered activation logic;
- private signing material, credentials or customer records;
- copyrighted third-party assets without clear redistribution rights; or
- customer audio, private DAW projects, order documents or personal data.

## Before opening an issue

1. Test the latest supported official release.
2. Verify the package SHA-256 against the checksum file from the same release.
3. Read [SUPPORT.md](SUPPORT.md) and [SECURITY.md](SECURITY.md).
4. Search existing issues and pull requests for the same problem.
5. Reduce technical problems to the smallest reproducible case.

Security vulnerabilities must be reported privately through GitHub Security Advisories.

## Pull-request expectations

A focused pull request should:

- solve one coherent problem;
- explain the user-facing impact;
- preserve Windows and macOS parity;
- preserve English and Bahasa Indonesia parity when public copy changes;
- update release metadata only when the corresponding official release exists;
- avoid claims that cannot be verified from public evidence;
- keep confidential and proprietary information out of the diff; and
- include validation evidence relevant to the files changed.

Use clear Conventional Commit-style messages where practical, for example:

```text
docs: clarify macOS installation guidance
fix: synchronize localized release metadata
test: guard canonical and hreflang consistency
chore: improve public issue templates
```

## Local validation

On Windows, run:

```powershell
.\tools\validate-public-release.ps1
```

For changes that affect public links and when network access is available, also run:

```powershell
.\tools\validate-public-release.ps1 --check-remote
```

At minimum, verify that:

- both localized pages remain valid and navigable;
- canonical and `hreflang` URLs remain reciprocal;
- `site/release.json` and `site/id/release.json` remain identical;
- release URLs point only to official assets in this repository;
- public copy does not expose private implementation details; and
- no activation, order, customer or signing secrets are present.

## Review and merge policy

Maintainers may request changes, close stale or superseded pull requests, or decline work outside the public repository scope. Approval does not transfer ownership of the proprietary product or grant access to private source repositories.

By submitting a contribution, you confirm that you have the right to provide it and that it may be incorporated into this repository under the repository's applicable terms.
