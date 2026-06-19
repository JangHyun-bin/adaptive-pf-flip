# S241 Foam Readability Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s241_foam_readability_motion_review\comparison_s238\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.95684000651042`, right `72.11885470920139`, delta `0.16201470269096774`
- Minimum contrast: left `100.0`, right `100.0`, delta `0.0`
- Mean bright ratio: left `0.00021253797743055555`, right `0.00021484375`, delta `2.3057725694444525e-06`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.4375`, right `91.9375`, delta `0.5`
- Mean luma p99: left `109.71875`, right `109.90625`, delta `0.1875`
- Mean luma p99.5: left `116.375`, right `116.40625`, delta `0.03125`
- Mean upper-mid ratio: left `0.00010321723090277779`, right `0.00010308159722222222`, delta `-1.356336805555632e-07`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `5.655924479166667e-05`, delta `0.0`
- Mean specular ratio: left `2.6312934027777778e-05`, right `2.617730034722222e-05`, delta `-1.3563368055555643e-07`
- Mean frame contrast: left `199.1875`, right `199.1875`, delta `0.0`

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

## Overlay Count Check

- Contact foam mean count: `43.1875 -> 54.5625`
- Contact foam max count: `50 -> 61`
- Impact ripple mean count: `62.0 -> 73.0`
- Impact ripple max count: `62 -> 73`
- Secondary streak mean count: `220.75 -> 220.75`

## Secondary Count Check

Direct secondary counts match the S238 accepted baseline on all `32` motion frames.

## Visual Finding

S241 validates the S240 contact foam and ripple readability probe over the 32-frame accepted motion window.

## Decision

Promote S240 into the accepted preset. S241 improves contact foam and ripple readability while preserving nonblank coverage, minimum contrast, direct secondary count parity, and hard highlight ratio. The tiny negative upper-mid/specular calibration deltas are below the practical gate threshold for this foam-focused pass.

## Next

Run S242 to fold the S240 foam/readability settings into `dam_break_water_mesh_smoothing`, then compare accepted output against S241 for parity.
