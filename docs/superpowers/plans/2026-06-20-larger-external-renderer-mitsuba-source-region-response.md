# S372 Larger External Renderer Mitsuba Source Region Response

## Goal

Move the S371 target-region response away from target pixels and into a
target-free source-evidence pass. This is still a screen-space diagnostic, but
the masks use only the current composite luminance and secondary alpha layer.

## Inputs

- Best current secondary composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- S371 diagnostic ceiling:
  `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json`
- Active SV1-cache baseline:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json`

## Work

- Add `tools/apply_mitsuba_source_region_response.py`.
- Generate SR1-SR8 source-evidence candidates.
- Compare every candidate with the existing target-gap harness.
- Analyze SR6 regions and build a visual review gallery against SV1-cache and
  RR5.

## Results

- Best target-free candidate: `SR6`.
- SR6 max target MAD: `23.703670267489713`.
- SV1-cache max target MAD: `23.72217142489712`.
- S371 RR5 diagnostic max target MAD: `23.459497813786008`.
- SR6 improves the baseline slightly without using target pixels, but it does
  not close the RR5 gap.
- Dark-secondary source rules are rejected for now: SR1/SR2/SR3 all worsen the
  hard gate. SR6 is highlight-only.
- SR6 region analysis leaves target highlights too dark by about `-76.279920`
  luma and target-dark secondary pixels too bright by about `51.392797` luma.

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_region_response_sweep_summary_s372.md`
- SR6 region report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_region_response_sr6_regions_s372.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_source_region_response_review_s372.md`
- Public quick-tunnel review:
  `https://met-installations-habits-selections.trycloudflare.com/index.html`

## Next

The remaining RR5 gap requires better renderer-native masks, not stronger
screen-space source luma rules. The next step should derive water crest and
secondary-dark masks from render-cache geometry, projected secondary channel
metadata, or surface-normal/material evidence.
