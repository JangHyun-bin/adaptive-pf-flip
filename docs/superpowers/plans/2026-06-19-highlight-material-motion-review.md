# S237 Highlight Material Motion Review

## Goal

Validate the S236 material/specular highlight response over the 32-frame accepted
motion window before accepted-preset promotion.

## Scope

- Reuse the S230 accepted foreground-volume render as baseline.
- Render `dam_break_highlight_material_response_probe` over the same source
  index window `8..55`.
- Keep simulation/cache data unchanged.
- Check surface-quality gate, legacy image metrics, calibration metrics, and
  direct secondary count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match S230 accepted on all `32` frames.
- Mean luminance delta: `+0.571984456380207`.
- Minimum contrast delta: `+16.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+2.943250868055555e-05`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p99` delta: `+9.40625`.
- Calibration `luma_p995` delta: `+11.4375`.

## Decision

Promote S236 into the accepted preset. The 32-frame motion review preserves all
bounded gates and improves both legacy bright ratio and upper-tail calibration
metrics without increasing direct secondary particles.

## Next

Run S238 to fold the S236 material response into `dam_break_water_mesh_smoothing`
and compare the accepted preset against S237 for parity.
