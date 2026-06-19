# S237 Highlight Material Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s237_highlight_material_motion_review\comparison_s230\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.38486056857639`, right `71.95684502495659`, delta `0.571984456380207`
- Minimum contrast: left `84.0`, right `100.0`, delta `16.0`
- Mean bright ratio: left `0.00018310546875`, right `0.00021253797743055555`, delta `2.943250868055555e-05`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `88.90625`, right `91.4375`, delta `2.53125`
- Mean luma p99: left `100.3125`, right `109.71875`, delta `9.40625`
- Mean luma p99.5: left `104.9375`, right `116.375`, delta `11.4375`
- Mean upper-mid ratio: left `0.00010294596354166667`, right `0.00010321723090277779`, delta `2.7126736111111286e-07`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `5.655924479166667e-05`, delta `0.0`
- Mean specular ratio: left `2.6312934027777778e-05`, right `2.6312934027777778e-05`, delta `0.0`
- Mean frame contrast: left `198.03125`, right `199.1875`, delta `1.15625`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Secondary Count Check

Direct secondary counts match the S230 accepted foreground-volume baseline on all `32` review frames.

## Visual Finding

S237 validates the S236 material/specular highlight response over the 32-frame accepted motion window.

## Decision

Promote S236 into the accepted preset. S237 preserves nonblank coverage, minimum contrast, hard-threshold highlight behavior, and direct secondary count parity while improving mean luminance, bright ratio, and upper-tail calibration metrics over the full motion window.

## Next

Run S238 to fold the S236 material response into `dam_break_water_mesh_smoothing`, then compare the accepted preset against S237 for parity.
