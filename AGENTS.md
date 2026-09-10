# AGENTS.md — ArSonKuPik VST Public Distribution Contract

These rules apply to every AI/code agent working in this repository. This repository is the public product/distribution surface for ArSonKuPik VST3. It does not contain the proprietary DSP implementation. Public metadata, release provenance, download routing, legal/security text, website behavior, and package identity are production-critical.

## 1. Prime directive

Do not treat this repository as a generic marketing site. A change can affect what users download, trust, install, purchase, or believe is officially supported.

Priority order:
1. release/download identity and integrity;
2. security/privacy/legal truthfulness;
3. provenance and version consistency;
4. regression-safe public compatibility;
5. site reliability and usability;
6. maintainability.

Never invent product capabilities, signing status, compatibility, licence rights, prices, release assets, checksums, or privacy claims.

## 2. Mandatory workflow

For non-trivial changes:

RECONNAISSANCE -> BASELINE -> ROOT CAUSE/REQUIREMENT -> AUTHORITATIVE SOURCE -> IMPACT MAP -> IMPLEMENT -> VALIDATE -> REMOTE/RELEASE CHECK WHEN APPLICABLE

Before editing, identify which artifact is authoritative for the affected fact and every duplicated/public representation that must remain synchronized.

Do not patch one visible page while leaving manifests, README, release metadata, legal text or validation tools inconsistent.

## 3. Authority and boundaries

Keep these concerns distinct:
- product/release metadata;
- website presentation;
- download routing;
- release provenance/checksums;
- legal/privacy/security/support documents;
- validation tooling.

The public website is not allowed to become a second uncontrolled source of release truth. Prefer data-driven rendering from reviewed metadata where the repository already supports it.

Do not add proprietary DSP source, private signing material, activation records, customer information, secret keys, private order data, or unpublished commercial internals to this public repository.

## 4. Release identity invariants

A release/version change must be coherent wherever the repository exposes that identity. Validate as applicable:
- product version;
- asset filenames;
- supported OS/architecture;
- VST3/standalone/package type;
- checksums;
- release notes/changelog;
- download URLs;
- public manifests;
- website labels;
- provenance documentation.

Do not silently route users to an asset whose filename/version/platform does not match the displayed product metadata.

A stale or missing release should fail visibly and safely rather than silently selecting an unrelated asset.

## 5. Download and checksum safety

Official download routing must stay constrained to approved product/repository assets. Do not introduce arbitrary mirrors, user-controlled URLs, broad redirects or unaudited third-party binary hosts.

Checksum generation/validation must be deterministic. Do not reuse a checksum for a rebuilt artifact with the same filename.

Do not weaken checksum/provenance validation to make a release pass.

## 6. Truthful signing and platform claims

Do not describe an artifact as code-signed, notarized, trusted, verified, universal, x64/arm64, installer, portable, DMG, ZIP or VST3 unless the actual reviewed artifact supports that claim.

Preserve explicit warnings about SmartScreen/Gatekeeper/ad-hoc signing when they remain true.

Never convert a limitation into reassuring copy merely for marketing polish.

## 7. Legal, privacy and commercial consistency

Changes touching EULA, purchase terms, privacy, evaluation period, activation, supported computers, refund/support statements, pricing or licensing semantics require cross-document consistency review.

Do not infer legal rights from implementation behavior. Do not change commercial/legal meaning as part of unrelated copy editing.

Privacy claims must match actual public/product behavior. Never add analytics/trackers or remote data collection while leaving local-only/no-analytics claims unchanged.

## 8. Security and secret handling

Never commit credentials, activation codes, Computer Request IDs, customer audio/projects, order records, private signing keys, API secrets or vulnerability details intended for private disclosure.

Treat all external metadata and URLs as untrusted input in validation scripts. Validate schemes/hosts/filenames/expected structure before using them.

Validation or site tooling must not execute downloaded binaries as part of routine metadata verification.

## 9. Failure handling

Expected failures in validation tooling should return explicit status and actionable diagnostics rather than being hidden or silently downgraded.

Examples:
- missing release asset;
- duplicate asset mapping;
- version mismatch;
- checksum mismatch;
- malformed manifest;
- inaccessible remote endpoint;
- unsupported platform declaration;
- stale metadata.

Do not broadly catch and convert failures into success. If an optional remote check is unavailable, distinguish `unverified` from `verified` rather than guessing.

## 10. Website performance and accessibility

Keep the public site lightweight. Avoid unnecessary frameworks, large runtime dependencies, blocking third-party scripts, oversized media, layout instability and decorative effects that degrade usability.

Preserve keyboard access, readable contrast, meaningful alt text, responsive layout and reduced-motion behavior where applicable.

Do not trade download clarity or trust information for visual novelty.

## 11. Deployment discipline

Changes to GitHub Pages/Cloudflare/deployment configuration must preserve the canonical site identity and compatibility mirror semantics documented by the repository.

Do not make DNS, deployment-target or canonical-URL changes incidentally.

Generated output must be reproducible from reviewed source. Do not hand-edit generated release artifacts as the primary fix when the generator/source is wrong.

## 12. Regression prevention

Every release/public-metadata bug fix should add or extend validation where practical. Test the exact failure mode such as stale version, wrong asset selection, missing checksum, broken canonical URL, invalid public path or contradictory metadata.

When one fact is intentionally duplicated for user readability, validation should detect drift between copies whenever practical.

## 13. Performance and dependency discipline

Do not add dependencies without evaluating maintenance, security, supply-chain exposure, bundle/runtime cost and whether existing tooling already solves the problem.

Prefer deterministic standard-library/script solutions for release validation.

## 14. Definition of done

A task is not complete because the page renders.

Validate as applicable:
- repository/public-release validation tooling;
- local site/link checks;
- version/manifest consistency;
- release asset mapping;
- checksum/provenance consistency;
- legal/privacy/security cross-document consistency;
- deployment workflow syntax;
- remote release URL checks when explicitly applicable and available;
- mobile/desktop accessibility smoke check for presentation changes.

Never claim a validation that was not executed.

## 15. Completion report

Report: Changed; Root cause/requirement; Authoritative source used; Public invariants preserved; Regression protection; Validation executed; Any remote check not performed; Remaining genuine limitations.

## Final rule

Think like the maintainer of a public software supply chain. Every displayed version, download button, checksum, security statement and licensing sentence can affect a real installation or purchase. Keep one release truth, make uncertainty explicit, preserve provenance, and never make trust claims without evidence.