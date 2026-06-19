# S231 Highlight Energy Recovery Probe

## Goal

Recover some bright/highlight energy after the S230 foreground-volume acceptance without changing water volume, secondary direct thinning, or mesh smoothing.

## Scope

- Add `dam_break_highlight_energy_recovery_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Adjust only `water_surface_glint_pass` and `water_reflection_pass`.
- Compare against the S230-equivalent 16-frame accepted foreground-volume baseline.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `16` frames.
- Mean luminance delta: `+0.1705642361111046`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `0.0`.
- Highlight ratio delta: `0.0`.

## Decision

S231 is safe but insufficient. It brightens the shot without hurting aggregate metrics, but it does not recover the bright/highlight ratios that S230 slightly reduced.

## Next

Run S232 as a stronger overlay-only probe. Promotion should require at least preserved coverage and contrast plus a non-negative bright/highlight ratio delta.
