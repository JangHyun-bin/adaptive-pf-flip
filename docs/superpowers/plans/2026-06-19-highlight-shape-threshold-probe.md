# S234 Highlight Shape Threshold Probe

## Goal

Test a bounded highlight-shape adjustment after S233 showed broad stronger
overlay energy was motion-safe but still slightly negative on aggregate
highlight ratio.

## Scope

- Add `dam_break_highlight_shape_threshold_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Adjust only `water_surface_glint_pass` and `water_reflection_pass`.
- Reduce broad strip area relative to S232 and use tighter, brighter segmented
  strokes with existing `angle_jitter_degrees`, `length_jitter`, and
  `width_jitter` controls.
- Compare against the S230-equivalent 16-frame accepted foreground-volume
  baseline.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `16` frames.
- Mean luminance delta: `+0.20324544270832234`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+2.441406249999975e-06`.
- Highlight ratio delta: `0.0`.

## Decision

S234 is safe but insufficient. The tighter highlight shape is less aggressive
than S232 and preserves all bounded gates, but it does not recover aggregate
highlight ratio.

## Next

Do not promote S234 to motion review. The next useful step is a render-metric
calibration pass that separates highlight pixels by water/overlay contribution,
or a real material/specular change, because overlay-only strip tuning is now
hitting the current aggregate metric ceiling.
