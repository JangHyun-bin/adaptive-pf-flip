# S375 Larger External Renderer Mitsuba Selective Dark Secondary Response

## Goal

Close the remaining target-free gap after S374 by making the dark-secondary mask
selective. S373 showed that broad secondary alpha or broad source-luma darkening
hurts the hard gate, so this pass looks for a smaller source-evidence mask.

## Inputs

- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- S374 best target-free highlight candidate:
  `build/shots/s374_mitsuba_source_highlight_response_sr19_candidate_gap/renderer_target_gap_summary.json`
- S371 RR5 diagnostic ceiling:
  `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json`

## Work

- Extend `tools/analyze_mitsuba_region_mask_candidates.py` with narrower
  source-luma dark-secondary candidates.
- Confirm `secondary_source_luma_0_75` as the best target-free dark-secondary
  mask.
- Generate DS1-DS8 by combining the S374 SR19 highlight response with selective
  dark-secondary response.
- Compare each candidate with the target-gap harness.
- Build a visual review gallery against SV1-cache, SR19, DS3, DS6, and RR5.

## Results

- Best dark-secondary mask: `secondary_source_luma_0_75`.
  - Precision: `0.858780`
  - Recall: `0.475602`
  - F1: `0.612175`
- Previous best dark-secondary mask from S373 was `secondary_source_luma_20_105`
  at F1 `0.159599`.
- Best target-free combined candidate: `DS6`.
- DS6 max target MAD: `23.56051440329218`.
- SR19 max target MAD: `23.651716820987655`.
- SV1-cache max target MAD: `23.72217142489712`.
- RR5 target-fit diagnostic max target MAD: `23.459497813786008`.
- DS6 reduces target-dark-secondary signed luma from `+51.392797` to
  `+22.254368`.

## Artifacts

- Mask candidate report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_selective_dark_secondary_mask_candidates_sv1_s375.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_selective_dark_secondary_response_sweep_summary_s375.md`
- DS6 region report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_selective_dark_secondary_response_ds6_regions_s375.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_selective_dark_secondary_response_review_s375.md`
- Public quick-tunnel review:
  `https://studying-elegant-solar-unlike.trycloudflare.com/index.html`

## Next

Use DS6 as the current target-free combined highlight/dark-secondary baseline.
The remaining gap to RR5 is mostly mask recall, so the next pass should try a
two-band dark-secondary response or renderer-native geometry/depth evidence.
