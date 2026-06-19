# S197 S195 Public Gallery Triage

## Status

S191 remains the accepted baseline. S195 is not promoted.

## Public Gallery

- URL: `https://dicke-automotive-fitness-category.trycloudflare.com`
- Publish report: `docs/reports/cinematic_gallery_publish_s196.md`
- Gallery report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_gallery_s196.md`

## Evidence

- Review sheet:
  `build/shots/s197_s195_public_triage/review_comparison/comparison_sheet.png`
- Review summary:
  `build/shots/s197_s195_public_triage/review_comparison/comparison_summary.json`
- Full comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_comparison_s195.md`

## Metrics

- S191 minimum contrast: `186`
- S195 minimum contrast: `181`
- S186 minimum contrast floor: `181`
- S195 mean nonblank ratio: `1.0`
- S195 mean luminance delta from S191: `-0.020953987027397147`

## Visual Finding

S195 makes the water body slightly smoother, but the change is subtle and does
not clearly improve the shot at gallery scale. The diff concentrates around
water-body edge and highlight details, while the public-facing frames remain
nearly indistinguishable from S191 in overall composition and readability.

Because S195 gives up 5 minimum contrast points against S191 without a clear
visual win, it should stay as a recorded candidate rather than replace the
accepted baseline.

## Decision

Keep S191 as the current accepted water mesh smoothing baseline.

## Next

Move to reconstruction/export smoothing instead of increasing renderer-side mesh
smoothing. The next milestone should target the actual render data surface:
surface export continuity, cache-side normal/gradient cues, or a water volume
representation that can improve body cohesion without lowering frame contrast.
