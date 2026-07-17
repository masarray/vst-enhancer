# Security Policy

## Supported public versions

Security fixes and vulnerability review are focused on the current public release listed in [`site/release.json`](site/release.json) and on the latest supported GitHub Release.

| Version | Security review status |
|---|---|
| Current public `v0.5.x` release | Supported for reports |
| Older public beta packages | Update to the current release before reporting when possible |
| Unofficial mirrors, modified builds, or re-uploaded packages | Not supported |

## Report a vulnerability privately

Use GitHub's private vulnerability-reporting channel:

**https://github.com/masarray/vst-enhancer/security/advisories/new**

Do not open a public issue for:

- activation bypass or licence-system weaknesses;
- suspected private signing key, signing-material, or activation-material exposure;
- malicious or replaced release assets;
- exploitable installer or update-check behaviour;
- disclosure of customer, order, activation, or support records; or
- a reproducible security issue that could put users at risk before a fix exists.

Include only the information needed to reproduce and assess the issue:

- affected version and package filename;
- SHA-256 of the tested file;
- Windows and host environment;
- impact and realistic attack conditions;
- reproduction steps or a minimal proof of concept;
- whether the issue is already public; and
- a safe way to request further private details if needed.

Do not send customer audio, private DAW projects, identity documents, payment-card data, activation codes, Computer Request IDs, or unrelated personal information.

If GitHub does not offer the private reporting form, create a minimal public issue titled **Security contact request** without technical details or sensitive data. A private route can then be arranged.

## Release authenticity

Official packages are linked only from:

- https://masarray.github.io/vst-enhancer/
- https://github.com/masarray/vst-enhancer/releases

Current packages may be unsigned. Verify the package against `SHA256SUMS.txt` from the same official release and keep ordinary Windows endpoint protection enabled. A matching checksum confirms identity against the published hash; it is not a malware guarantee.

## Coordinated disclosure

Please allow reasonable time to reproduce, assess, correct, validate, and publish a security update before public disclosure. No fixed bounty, payment, or response-time commitment is offered unless agreed in writing for a specific report.
