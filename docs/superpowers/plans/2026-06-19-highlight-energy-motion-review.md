# S233 Highlight Energy Motion Review

## Goal

Validate the S232 strong overlay-only highlight recovery probe over the 32-frame
accepted motion window before considering promotion.

## Scope

- Reuse the S230 accepted foreground-volume render as baseline.
- Render `dam_break_highlight_energy_recovery_strong_probe` over the same
  source index window `8..55`.
- Keep simulation/cache data unchanged.
- Check surface-quality gate, aggregate image metrics, and direct secondary
  count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match S230 accepted on all `32` frames.
- Mean luminance delta: `+0.656890869140625`.
- Minimum contrast delta: `+9.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+4.475911458333328e-06`.
- Highlight ratio delta: `-4.069010416666625e-07`.

## Decision

S233 is motion-safe as an opt-in probe, but it should not be promoted yet. The
longer window preserves coverage and count parity while improving luminance,
contrast, and bright ratio, but the aggregate highlight ratio still slips
slightly.

## Next

Run S234 as a bounded highlight-shape/threshold pass instead of increasing
glint density again. The next probe should try to recover highlight ratio
without adding more broad overlay energy or visible shimmer.
