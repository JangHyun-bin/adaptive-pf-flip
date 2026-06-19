# S238 Highlight Material Acceptance

## Goal

Fold the S236/S237 material highlight response into the accepted
`dam_break_water_mesh_smoothing` preset and verify parity.

## Scope

- Add accepted `water_glint` and `water_reflection` material values to
  `dam_break_water_mesh_smoothing`.
- Update accepted glint/reflection alpha and emission scales to the S236 values.
- Render the accepted preset over the same 32-frame source window `8..55`.
- Compare S238 accepted against S237 probe for parity.
- Also check S238 accepted against the previous S230 accepted foreground-volume
  baseline.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match S237 on all `32` frames.
- S237 parity mean luminance delta: `-5.018446174176461e-06`.
- S237 parity bright/highlight/nonblank/contrast/calibration deltas: `0.0`.
- S230 comparison mean luminance delta: `+0.5719794379340328`.
- S230 comparison minimum contrast delta: `+16.0`.
- S230 comparison bright ratio delta: `+2.943250868055555e-05`.
- S230 comparison calibration `luma_p99` delta: `+9.40625`.
- S230 comparison calibration `luma_p995` delta: `+11.4375`.

## Decision

S238 accepts the material highlight response into `dam_break_water_mesh_smoothing`.
Parity with S237 holds within render noise, and the accepted preset keeps the
S237 improvement over S230.

## Next

Use S238 as the current accepted cinematic water baseline. The next visual work
should move to either contribution masks/specular diagnostics or a new
photoreal pass that is not just highlight recovery.
