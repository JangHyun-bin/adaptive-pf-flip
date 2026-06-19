# S241 Foam Readability Motion Review

## Goal

Validate the S240 foam/readability probe over the 32-frame accepted motion
window before accepted-preset promotion.

## Scope

- Reuse S238 accepted highlight-material as the baseline.
- Render `dam_break_foam_readability_probe` over source window `8..55`.
- Check surface-quality gate, image metrics, contact foam/ripple counts, and
  direct secondary count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match on all `32` frames.
- Contact foam mean count: `43.1875 -> 54.5625`.
- Impact ripple mean count: `62.0 -> 73.0`.
- Mean luminance delta: `+0.16201470269096774`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+2.3057725694444525e-06`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p99` delta: `+0.1875`.

## Decision

Promote S240 into the accepted preset. The motion review preserves all primary
gates and improves foam/ripple readability. The tiny negative upper-mid/specular
calibration deltas are below one pixel in aggregate scale and do not affect the
legacy highlight gate.

## Next

Run S242 to fold S240 into `dam_break_water_mesh_smoothing` and compare accepted
output against S241 for parity.
