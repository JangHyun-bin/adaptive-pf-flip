# S248 Accepted Review Package

## Goal

Create a compact bridge-render review package schema for the current accepted
cinematic baseline so external review does not depend on scattered gallery,
comparison, gate, and diagnostic files.

## Scope

- Add `tools/build_bridge_review_package.py`.
- Package an accepted bridge shot directory, gallery manifest, bridge summary,
  comparison summaries, gate summaries, and diagnostics.
- Emit `review_package.json` under `build/`.
- Emit a Markdown report under `docs/reports/`.

## Results

- Tool schema: `lsfs_bridge_cinematic_review_package`
- Tool output:
  `build/shots/s248_accepted_review_package/review_package.json`
- Report:
  `docs/reports/cinematic_accepted_review_package_s248.md`
- Packaged accepted baseline: `build/shots/s246_water_body_thickness_acceptance`
- Gallery: `build/shots/s246_water_body_thickness_acceptance/gallery/index.html`
- Artifact count: `12`
- Summary source count: `4`
- Included summaries:
  `s246_parity`, `s246_baseline_delta`, `s246_surface_gate`,
  `s247_water_body_contribution`

## Decision

Use the S248 package format as the current bridge-render review/export schema.
It does not replace future renderer cache formats, but it gives the current
cinematic workflow one inspectable manifest with visual assets, hashes, render
metadata, comparison deltas, surface-quality gate results, and diagnostics.

## Next

Publish the S246 gallery/package for external review when needed, then continue
with secondary mist readability from the S246 accepted baseline.
