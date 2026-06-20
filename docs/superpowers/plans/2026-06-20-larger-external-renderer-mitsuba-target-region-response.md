# S371 Larger External Renderer Mitsuba Target Region Response

## Goal

Test a bounded target-region response pass after the best SV1-cache secondary
composite. This is a diagnostic target-fit bridge, not the final renderer-native
solution: it should tell us whether the S369 region diagnosis is actionable
before porting the masks into water/material/secondary rendering.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Best current secondary composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active target-gap baseline:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json`

## Work

- Add `tools/apply_mitsuba_target_region_response.py`.
- Apply three bounded response families:
  - RR1/RR2/RR3: broad nonsecondary lift probes.
  - RR4: local highlight and dark-secondary response.
  - RR5: full local target-region response.
  - RR6: RR4 with a tiny nonsecondary lift.
- Extend review/region tools to accept `lsfs_mitsuba_composite_grade` summaries.
- Publish a side-by-side review gallery through a Cloudflare quick tunnel.

## Results

- Best candidate: `RR5`.
- RR5 max target MAD: `23.459497813786008`.
- Previous best `SV1-cache` max target MAD: `23.72217142489712`.
- RR5 aggregate MAD: `18.30976916152263`.
- RR5 fixes the S369 target-highlight and target-dark-secondary regions in the
  diagnostic pass while preserving the hard max gate.
- Broad nonsecondary lift remains rejected: RR6 worsens the hard max gate to
  `24.22597222222222`, while RR1/RR2/RR3 are worse.

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_region_response_sweep_summary_s371.md`
- RR5 region report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_region_response_rr5_regions_s371.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_region_response_review_s371.md`
- Public quick-tunnel review:
  `https://contacting-touched-veterinary-expensive.trycloudflare.com/index.html`

## Next

Port the successful bounded response away from target pixels and into
renderer-native evidence: water crest/highlight masks, secondary darkening masks,
and eventually surface-normal/material reconstruction. Do not continue broad
global lift or key-light sweeps for this shot.
