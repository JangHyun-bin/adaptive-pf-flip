# S232 Highlight Energy Recovery Strong Probe

## Goal

Test whether a stronger overlay-only glint/reflection pass can recover bright
energy after S230 without changing water volume, secondary direct thinning, or
mesh smoothing.

## Scope

- Add `dam_break_highlight_energy_recovery_strong_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Adjust only `water_surface_glint_pass` and `water_reflection_pass`.
- Compare against the S230-equivalent 16-frame accepted foreground-volume
  baseline.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `16` frames.
- Mean luminance delta: `+0.6406933593749926`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+7.324218749999979e-06`.
- Highlight ratio delta: `0.0`.

## Decision

S232 is a partial recovery probe. It preserves the accepted baseline gates and
recovers a small amount of bright ratio, but the aggregate highlight ratio is
still unchanged. Keep it opt-in until a longer motion review confirms that the
extra overlay energy does not shimmer or flatten the water sheet.

## Next

Run S233 as a 32-frame motion review for S232 only if visual inspection of the
gallery supports the stronger glint density. Promotion should still require
preserved coverage, contrast, direct secondary count parity, and no negative
bright/highlight deltas over the motion window.
