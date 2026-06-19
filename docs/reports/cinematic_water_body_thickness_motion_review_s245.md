# S245 Water Body Thickness Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s245_water_body_thickness_motion_review\comparison_s242\comparison_sheet.png`
- Gallery: `build\shots\s245_water_body_thickness_motion_review\gallery\index.html`
- GIF: `build\shots\s245_water_body_thickness_motion_review\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Pass Deltas

- Water volume scatter layers: `18 -> 20`
- Water volume scatter alpha scale: `0.324 -> 0.3456`
- Water volume occlusion enabled: `false -> false`
- Contact foam mean delta: `0`
- Impact ripple mean delta: `0`
- Secondary streak mean delta: `0`

## Metric Deltas

- Mean luminance: left `72.1188532172309`, right `72.49517184787327`, delta `0.37631863064235915`
- Minimum contrast: left `100.0`, right `101.0`, delta `1.0`
- Mean bright ratio: left `0.00021484375`, right `0.00026502821180555557`, delta `5.018446180555557e-05`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00015068901909722222`, delta `2.8754340277777787e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.9375`, right `92.4375`, delta `0.5`
- Mean luma p99: left `109.90625`, right `110.0`, delta `0.09375`
- Mean luma p99.5: left `116.40625`, right `116.40625`, delta `0.0`
- Mean upper-mid ratio: left `0.00010308159722222222`, right `0.00011773003472222222`, delta `1.46484375e-05`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `6.212022569444444e-05`, delta `5.560980902777766e-06`
- Mean specular ratio: left `2.617730034722222e-05`, right `3.1602647569444445e-05`, delta `5.425347222222223e-06`
- Mean frame contrast: left `199.1875`, right `199.90625`, delta `0.71875`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S245 validates the S244 water-body thickness/refraction probe over the 32-frame accepted motion window.

The S244 watch items are cleared in the full motion window: minimum contrast
rises by `1.0`, `luma_p99.5` is unchanged, coverage stays fixed, and direct
readability overlays keep identical counts. The comparison sheet shows a subtle,
scene-wide water-body depth lift rather than a new foam/highlight-only pass.

## Next

Promote `dam_break_water_body_thickness_probe` into
`dam_break_water_mesh_smoothing` in S246 and run accepted-preset parity against
S245.
