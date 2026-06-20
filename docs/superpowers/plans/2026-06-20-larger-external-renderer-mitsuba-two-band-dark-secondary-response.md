# S376 Larger External Renderer Mitsuba Two-Band Dark Secondary Response

## Goal

Test whether a second, softer source-luma band can improve DS6's dark-secondary
recall without hurting the hard target-gap gate.

## Inputs

- DS6 baseline:
  `build/shots/s375_mitsuba_selective_dark_secondary_response_ds6_candidate_gap/renderer_target_gap_summary.json`
- Active SV1-cache baseline:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json`
- RR5 diagnostic ceiling:
  `build/shots/s371_mitsuba_target_region_response_rr5_candidate_gap/renderer_target_gap_summary.json`

## Work

- Extend `tools/apply_mitsuba_source_region_response.py` with an optional
  non-overlapping soft dark-secondary band.
- Generate TB1-TB4:
  - TB1/TB2: soft `75-85` band.
  - TB3/TB4: wider soft `75-95` band.
- Compare against DS6, SV1-cache, and RR5 using the target-gap harness.
- Build a visual review with DS6, TB1, TB3, and RR5.

## Results

- DS6 remains the best target-free candidate at max target MAD
  `23.56051440329218`.
- Best two-band candidate TB1 worsens the hard gate to `23.576880787037037`.
- TB2 worsens to `23.5941595936214`.
- TB3/TB4 are rejected strongly at `23.827061471193417` and
  `24.032675540123456`.
- TB1 reduces target-dark-secondary signed luma from DS6's `+22.254368` to
  `+19.288754`, but the broader side effects outweigh the regional gain.

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_two_band_dark_secondary_response_sweep_summary_s376.md`
- TB1 region report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_two_band_dark_secondary_response_tb1_regions_s376.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_two_band_dark_secondary_response_review_s376.md`
- Public quick-tunnel review:
  `https://flow-mel-min-mostly.trycloudflare.com/index.html`

## Next

Reject the second screen-space source-luma band for now. Keep DS6 as the
target-free baseline and move to geometry/depth-native mask evidence.
