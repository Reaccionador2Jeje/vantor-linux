# Upstream source policy

VANTOR builds third-party components from their upstream source releases. A release is not eligible for automated download until its version, canonical upstream URL, SHA-256 digest, and license are recorded in the machine-readable source manifest.

## Required metadata

Each component entry must define:

- `name`: stable component identifier.
- `version`: exact upstream release version (never `latest`).
- `url`: canonical upstream release archive URL.
- `sha256`: verified SHA-256 digest for that exact archive.
- `license`: upstream license identifier or license-file reference.
- `role`: why the component is part of VANTOR.

## Verification rules

1. Prefer release archives published by the upstream project.
2. Verify archive digests against upstream-published checksum files or signatures.
3. Do not silently update a version or digest. Changes require a reviewed commit.
4. Keep each component's own license and notices with its source/build output.
5. Never execute downloaded build scripts before archive integrity has been checked.

The manifest is intentionally not populated with guessed versions or checksums. The first toolchain implementation must pin and verify every input before building.
