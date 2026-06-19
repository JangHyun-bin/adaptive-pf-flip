# S272 Accepted Bridge Handoff Validation

## Goal

Make the S271 handoff manifest enforceable by validating source fingerprints,
gallery artifact fingerprints, publish status, and current public review URLs.

## Scope

- Add `tools/validate_bridge_handoff_manifest.py`.
- Validate `lsfs_bridge_cinematic_handoff_manifest` schema and version.
- Verify source file SHA-256 fingerprints.
- Verify gallery artifact SHA-256 fingerprints.
- Verify active publish status.
- Optionally check public `index.html` and `assets/shot.gif`.
- Emit a JSON validation result under `build/` and a checked-in Markdown report.

## Validation

- Script compile:
  `python -m py_compile tools/validate_bridge_handoff_manifest.py`
- Public/source validation:
  `python tools/validate_bridge_handoff_manifest.py build/shots/s271_accepted_handoff/handoff_manifest.json --out build/shots/s272_handoff_validation/validation.json --report docs/reports/cinematic_accepted_handoff_validation_s272.md --check-public --timeout-seconds 30`

## Result

- Validation schema: `lsfs_bridge_cinematic_handoff_validation`
- Status: `passed`
- Checks: `23`
- Failures: `0`
- Warnings: `0`
- Source fingerprints checked: `5`
- Gallery artifact fingerprints checked: `12`
- Public `index.html`: HTTP `200`
- Public `assets/shot.gif`: HTTP `200`

## Decision

Use the S271/S272 pair as the current machine-readable accepted baseline gate.
S271 identifies the baseline; S272 proves the local source/artifact hashes and
the public review endpoint still match that baseline.

## Next

Use this gate before external-render experiments, larger-shot reruns, or
large-scale benchmark jobs consume the S269 accepted visual baseline.
