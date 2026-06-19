# S229 Foreground Volume Motion Review

## Goal

Validate the S228 foreground-volume separation probe over the 32-frame accepted motion window before promotion.

## Scope

- Reuse the S227 accepted-motion render as baseline.
- Render `dam_break_foreground_volume_separation_probe` over the same source index window `8..55`.
- Keep simulation/cache data unchanged.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match S227 accepted motion on all `32` frames.
- Mean luminance delta versus S227 accepted: `+0.6768454318576431`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Mean bright ratio delta: `-5.56098090277778e-06`.
- Mean highlight ratio delta: `-2.8483072916666647e-06`.

## Decision

Promote the S228 foreground-volume settings. The longer motion window preserves the bounded metrics and direct secondary thinning, while the foreground water body is easier to read.

## Next

S230 should fold the S228 settings into `dam_break_water_mesh_smoothing` and run accepted-preset parity against S229.
