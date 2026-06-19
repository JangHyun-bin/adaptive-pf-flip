# S264 Subject Clarity Acceptance Parity

## Status

Passed. `dam_break_water_mesh_smoothing` now matches the reviewed S263
subject-clarity output within render-summary epsilon.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s264_subject_clarity_acceptance\comparison_s263_parity\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.41683525933159`, right `74.4168339029948`, delta `-1.3563367957658556e-06`
- Minimum contrast: left `154.0`, right `154.0`, delta `0.0`
- Mean bright ratio: left `0.00023600260416666667`, right `0.00023600260416666667`, delta `0.0`
- Mean highlight ratio: left `0.0001462131076388889`, right `0.0001462131076388889`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `94.375`, right `94.375`, delta `0.0`
- Mean luma p99: left `107.53125`, right `107.53125`, delta `0.0`
- Mean luma p99.5: left `112.125`, right `112.125`, delta `0.0`
- Mean upper-mid ratio: left `0.00011691623263888888`, right `0.00011691623263888888`, delta `0.0`
- Mean near-highlight ratio: left `6.171332465277778e-05`, right `6.171332465277778e-05`, delta `0.0`
- Mean specular ratio: left `2.753363715277778e-05`, right `2.753363715277778e-05`, delta `0.0`
- Mean frame contrast: left `208.0`, right `208.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S264 validates that the accepted dam_break_water_mesh_smoothing subject-clarity settings match the S263 motion review output.

Parity is exact for minimum contrast, bright ratio, highlight ratio, nonblank
coverage, luma percentiles, upper-mid ratio, near-highlight ratio, specular
ratio, and frame contrast. Mean luminance differs only by
`-1.3563367957658556e-06`. The accepted preset now carries the subject-clarity
glint/reflection/scatter/detail settings without changing camera, tone,
lighting, secondary, foam, or ripple behavior.

Surface-quality gate:

- `normal_rough`: `3`
- `stable`: `29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Next

Use S264 as the current accepted visual baseline and refresh the review
package/public gallery from this render.
