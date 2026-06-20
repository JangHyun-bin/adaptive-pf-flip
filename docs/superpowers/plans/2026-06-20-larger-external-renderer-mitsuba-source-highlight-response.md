# S374 Larger External Renderer Mitsuba Source Highlight Response

## Goal

Use the S373 mask diagnosis to tune the target-free highlight response. S373
showed that source luminance around `120` explains target highlights much better
than the previous `135` threshold, while dark-secondary masks remain too broad.

## Inputs

- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- S372 best target-free source response:
  `build/shots/s372_mitsuba_source_region_response_sr6_candidate_gap/renderer_target_gap_summary.json`
- S371 RR5 diagnostic ceiling:
  `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json`

## Work

- Generate SR9-SR19 using `tools/apply_mitsuba_source_region_response.py`.
- Keep dark-secondary strength disabled.
- Focus on `source_highlight_120`, then constrain highlight response to
  nonsecondary pixels with `--highlight-alpha-max 3`.
- Compare every candidate with the target-gap harness.
- Build a visual review gallery for SV1-cache, SR6, SR19, and RR5.

## Results

- Best target-free candidate: `SR19`.
- SR19 max target MAD: `23.651716820987655`.
- SV1-cache max target MAD: `23.72217142489712`.
- S372 SR6 max target MAD: `23.703670267489713`.
- S371 RR5 target-fit diagnostic max target MAD: `23.459497813786008`.
- SR19 reduces target-highlight MAD from SR6's `76.064585` to `35.361356`.
- SR19 leaves target-dark-secondary unchanged at MAD `51.263450`, confirming
  that highlight tuning is no longer the main missing piece.

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_highlight_response_sweep_summary_s374.md`
- SR19 region report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_highlight_response_sr19_regions_s374.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_highlight_response_review_s374.md`
- Public quick-tunnel review:
  `https://trail-leasing-participated-keyboard.trycloudflare.com/index.html`

## Next

Use SR19 as the current target-free highlight baseline. The next work should add
a selective dark-secondary evidence mask instead of further highlight tuning.
