# S242 Foam Readability Acceptance

## Goal

Fold the S240/S241 foam readability settings into the accepted
`dam_break_water_mesh_smoothing` preset and verify parity against the S241
probe render.

## Scope

- Promote bounded contact foam, impact ripple, secondary soft, and secondary
  streak render controls into the accepted preset.
- Keep direct secondary particle controls unchanged.
- Render the accepted preset over the 32-frame source window `8..55`.
- Compare accepted output against S241 for parity and against S238 for baseline
  improvement.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- S241 parity: max changed ratio `0`, max strong changed ratio `0`, max mean
  abs luma `0.00014756944444444445`.
- S241 parity metric deltas: bright ratio `0`, highlight ratio `0`, `luma_p95`
  `0`, `luma_p99` `0`, mean luminance `-1.4919704796056976e-06`.
- S241 overlay count deltas: contact foam mean `0`, impact ripple mean `0`,
  secondary streak mean `0`.
- S238 baseline delta: contact foam mean `43.1875 -> 54.5625`, impact ripple
  mean `62.0 -> 73.0`, mean luminance `+0.16201321072048813`, bright ratio
  `+2.3057725694444525e-06`, `luma_p99` `+0.1875`.

## Artifacts

- Parity report:
  `docs/reports/cinematic_foam_readability_acceptance_s242.md`
- Baseline delta report:
  `docs/reports/cinematic_foam_readability_acceptance_baseline_delta_s242.md`
- Gallery report:
  `docs/reports/cinematic_foam_readability_acceptance_gallery_s242.md`
- Gallery:
  `build/shots/s242_foam_readability_acceptance/gallery/index.html`
- GIF:
  `build/shots/s242_foam_readability_acceptance/shot.gif`

## Decision

Accept S242 as the new cinematic water baseline. The accepted preset now carries
the S240/S241 foam/readability improvement, while S241 parity holds within
render noise and direct secondary behavior remains unchanged.

## Next

Start the next non-highlight visual pass from S242. The strongest candidates are
water-body thickness/refraction, secondary mist lifecycle/readability, or a
targeted contribution-mask renderer for foam and ripple cues.
