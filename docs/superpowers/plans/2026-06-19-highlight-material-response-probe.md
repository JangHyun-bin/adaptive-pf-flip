# S236 Highlight Material Response Probe

## Goal

Test whether material/specular response can recover highlight energy better than
additional overlay strip density.

## Scope

- Add `dam_break_highlight_material_response_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Keep accepted overlay density and adjust only `water_glint`,
  `water_reflection`, and small pass alpha/emission scales.
- Compare against the S230-equivalent 16-frame accepted foreground-volume
  baseline.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `16` frames.
- Mean luminance delta: `+0.5723060438368037`.
- Minimum contrast delta: `+6.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+3.580729166666665e-05`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p99` delta: `+9.4375`.
- Calibration `luma_p995` delta: `+11.5`.

## Decision

S236 is the best highlight recovery candidate in the current group. It improves
bright ratio and upper-tail luminance more cleanly than S232/S234 while keeping
hard-threshold highlight behavior non-negative and preserving all bounded gates.

## Next

Run S237 as a 32-frame motion review against S230 accepted foreground-volume.
Promotion should require preserved coverage, minimum contrast, direct secondary
count parity, non-negative hard-threshold highlight behavior, and positive
upper-tail calibration deltas.
