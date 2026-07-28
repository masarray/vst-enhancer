# Security Policy

## Supported public versions

Security fixes and vulnerability review focus on the current public release listed in [`site/release.json`](site/release.json) and the latest supported GitHub Release.

| Version or package | Security review status |
|---|---|
| Current public `v0.5.x` release | Supported for reports |
| Older public beta packages | Update to the current release before reporting when possible |
| Unofficial mirrors, modified builds or re-uploaded packages | Not supported |

## Report a vulnerability privately

Use GitHub private vulnerability reporting:

**https://github.com/masarray/vst-enhancer/security/advisories/new**

Do not open a public issue for:

- activation bypass or licence-system weaknesses;
- suspected private signing key, signing material or activation-material exposure;
- malicious, replaced or mismatched release assets;
- exploitable installer, DMG, archive, update-check or activation behaviour;
- disclosure of customer, order, activation or support records; or
- a reproducible security issue that could put users at risk before a fix exists.

Include only the information needed to reproduce and assess the issue:

- affected version and exact package filename;
- SHA-256 of the tested file;
- operating system, architecture and host environment;
- impact and realistic attack conditions;
- reproduction steps or a minimal proof of concept;
- whether the issue is already public; and
- a safe way to request further private details if needed.

Do not send customer audio, private DAW projects, identity documents, payment-card data, activation codes, Computer Request IDs or unrelated personal information.

If GitHub does not offer the private reporting form, create a minimal public issue titled **Security contact request** without technical details or sensitive data. A private route can then be arranged.

## Release authenticity

Official packages are linked only from:

- https://masarray.github.io/vst-enhancer/
- https://github.com/masarray/vst-enhancer/releases

The current Windows packages are not commercially code-signed. The current macOS packages are ad-hoc signed but are not Developer ID signed or notarized. Verify every package against the checksum file from the same official release.

A matching SHA-256 confirms identity against the published hash; it is not a malware guarantee. Keep ordinary endpoint protection enabled. On macOS, retain Gatekeeper and use only the documented **Open** or **Open Anyway** path for the verified official package. On Windows, review SmartScreen or enterprise-security warnings before proceeding.

## Coordinated disclosure

Please allow reasonable time to reproduce, assess, correct, validate and publish a security update before public disclosure. No fixed bounty, payment or response-time commitment is offered unless agreed in writing for a specific report.
