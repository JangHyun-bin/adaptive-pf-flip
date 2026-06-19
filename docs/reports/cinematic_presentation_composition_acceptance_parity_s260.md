# S260 Presentation Composition Acceptance Parity

## Status

Passed. `dam_break_water_mesh_smoothing` now matches the reviewed S259 camera
composition output exactly across the comparison metrics.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s260_presentation_composition_acceptance\comparison_s259_parity\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.99527316623264`, right `74.99527316623264`, delta `0.0`
- Minimum contrast: left `107.0`, right `107.0`, delta `0.0`
- Mean bright ratio: left `0.00025526258680555556`, right `0.00025526258680555556`, delta `0.0`
- Mean highlight ratio: left `0.00013807508680555556`, right `0.00013807508680555556`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `96.84375`, right `96.84375`, delta `0.0`
- Mean luma p99: left `112.25`, right `112.25`, delta `0.0`
- Mean luma p99.5: left `118.0`, right `118.0`, delta `0.0`
- Mean upper-mid ratio: left `0.00010633680555555556`, right `0.00010633680555555556`, delta `0.0`
- Mean near-highlight ratio: left `5.5202907986111114e-05`, right `5.5202907986111114e-05`, delta `0.0`
- Mean specular ratio: left `2.4820963541666667e-05`, right `2.4820963541666667e-05`, delta `0.0`
- Mean frame contrast: left `205.5625`, right `205.5625`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S260 validates that the accepted dam_break_water_mesh_smoothing camera path matches the S259 composition motion review output.

Parity is exact for mean luminance, minimum contrast, bright ratio, highlight
ratio, nonblank coverage, luma percentiles, upper-mid ratio, near-highlight
ratio, specular ratio, and frame contrast. The accepted preset now carries the
S258/S259 camera path without changing material, tone, lighting, or secondary
behavior.

Surface-quality gate:

- `normal_rough`: `3`
- `stable`: `29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Next

Use S260 as the current accepted visual baseline and refresh the review
package/public gallery from this render.
