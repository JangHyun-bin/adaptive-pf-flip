# S246 Water Body Thickness Acceptance

## Goal

Fold the S244/S245 water-body thickness/refraction settings into the accepted
`dam_break_water_mesh_smoothing` preset and verify parity against S245.

## Scope

- Promote water material depth/alpha/transmission tuning.
- Promote water volume scatter material tuning.
- Promote the bounded 20-layer volume scattering pass.
- Keep volume occlusion disabled.
- Keep accepted foam, ripple, glint, reflection, and direct secondary behavior
  unchanged.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- S245 parity max changed ratio: `0`.
- S245 parity max strong changed ratio: `0`.
- S245 parity max mean abs luma: `0.00019097222222222223`.
- S245 parity mean luminance delta: `+2.034505200754211e-06`.
- S245 parity bright/highlight/contrast/nonblank/luma percentile deltas: `0`.
- S245 pass deltas: scatter layers `0`, scatter alpha `0`, contact foam mean
  `0`, impact ripple mean `0`, secondary streak mean `0`.
- S242 baseline delta: mean luminance `+0.3763206651475599`, minimum contrast
  `+1.0`, bright ratio `+5.018446180555557e-05`, highlight ratio
  `+2.8754340277777787e-05`, `luma_p95 +0.5`, `luma_p99 +0.09375`,
  `luma_p99.5 0.0`, nonblank `0.0`.

## Artifacts

- Acceptance report:
  `docs/reports/cinematic_water_body_thickness_acceptance_s246.md`
- Baseline delta report:
  `docs/reports/cinematic_water_body_thickness_acceptance_baseline_delta_s246.md`
- Gallery report:
  `docs/reports/cinematic_water_body_thickness_acceptance_gallery_s246.md`
- Gallery:
  `build/shots/s246_water_body_thickness_acceptance/gallery/index.html`
- GIF:
  `build/shots/s246_water_body_thickness_acceptance/shot.gif`

## Decision

Accept S246 as the new cinematic water baseline. The accepted preset now carries
foam/readability plus water-body thickness/refraction tuning, and S245 parity
holds within render noise.

## Next

Move to the next visual pass from S246. Recommended next candidates are
secondary mist readability/lifecycle or the render-export schema needed for
external cinematic review.
