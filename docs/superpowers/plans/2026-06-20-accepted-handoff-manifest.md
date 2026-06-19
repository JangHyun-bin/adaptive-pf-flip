# S271 Accepted Bridge Handoff Manifest

## Goal

Create a machine-readable handoff manifest for the current accepted S269
bridge-render baseline so external renderer work, larger-shot reruns, and
large-scale benchmark gates can reproduce the exact visual target.

## Scope

- Add `tools/build_bridge_handoff_manifest.py`.
- Consume the accepted review package from S270.
- Optionally attach the active gallery publish manifest.
- Fingerprint the render-data summary, converted sequence, and preset config.
- Record git commit/branch/status, accepted preset name, public review URL,
  key comparison deltas, artifact fingerprints, and source fingerprints.
- Emit a JSON manifest under `build/` and a checked-in Markdown report.

## Validation

- Script compile:
  `python -m py_compile tools/build_bridge_handoff_manifest.py`
- Generated manifest:
  `build/shots/s271_accepted_handoff/handoff_manifest.json`
- Generated report:
  `docs/reports/cinematic_accepted_handoff_manifest_s271.md`
- JSON validation:
  `python -m json.tool build/shots/s271_accepted_handoff/handoff_manifest.json`

## Result

The S271 manifest records:

- Schema: `lsfs_bridge_cinematic_handoff_manifest`
- Version: `1`
- Accepted preset: `dam_break_water_mesh_smoothing`
- Git commit: `b53576c548a45406757f6b3f2740bc528f8278ef`
- Public URL: `https://rfc-empirical-match-outstanding.trycloudflare.com`
- Publish status: `running`
- Render frames: `32`
- Artifact count: `12`
- Summary count: `4`
- Source fingerprint count: `5`

## Decision

Use S271 as the current accepted bridge-render handoff pointer. It does not
replace the human review package; it complements it with stable hashes and
compact baseline metadata for downstream automation.

## Next

Use the S271 handoff manifest as input for external renderer schema work,
larger-shot reruns, or large-scale benchmark gates.
