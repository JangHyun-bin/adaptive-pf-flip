# S382 Larger External Renderer Mitsuba Screen Evidence AOV Package

## Goal

Consolidate the useful screen-space evidence from S377-S381 into one visual AOV
review package so the next visual response is driven by inspectable evidence
rather than another broad mask search.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Bridge contact/ripple settings:
  `build/shots/s305_larger_external_renderer_job_blender_full48/bridge_summary.json`

## Work

- Add `tools/build_mitsuba_screen_evidence_aov_package.py`.
- Build a 3x3 AOV grid per selected frame:
  - Target
  - Actual
  - Layer Alpha
  - Source Luma
  - DS6 Mask
  - Target Dark Diagnostic
  - Water Mask
  - Contact Mask
  - Overlay
- Package the grids into an HTML gallery and animated GIF.

## Results

- Frames: `4`
- AOVs per frame: `9`
- GIF bytes: `3582361`
- Grid dimensions: `2880 x 1704`
- Key coverage sample:
  - output `0`: DS6 `0.006265`, target-dark `0.008146`
  - output `13`: DS6 `0.002122`, target-dark `0.002415`
  - output `34`: DS6 `0.000150`, target-dark `0.007041`
  - output `47`: DS6 `0.003582`, target-dark `0.003322`

## Decision

Use this package as the current visual evidence board. It shows that DS6 is the
best available target-free mask, but still misses some target-dark diagnostic
regions, especially output `34`. The next step should be a bounded visual
response that uses DS6 safely, or a renderer AOV export for richer shading state.

## Artifacts

- New tool:
  `tools/build_mitsuba_screen_evidence_aov_package.py`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_screen_evidence_aov_package_sv1_s382.md`
- Main gallery:
  `build/shots/s382_mitsuba_screen_evidence_aov_package_sv1/gallery/index.html`
- Public quick-tunnel review:
  `https://jill-will-open-aids.trycloudflare.com/index.html`

## Next

Build a bounded visual response using DS6 as the mask, then compare it against
the current DS6 candidate and RR5 diagnostic ceiling.
