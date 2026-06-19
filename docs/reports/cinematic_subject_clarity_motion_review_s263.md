# S263 Subject Clarity Motion Review

## Status

Passed as a 32-frame subject-clarity motion review. Promote to S264
accepted-preset parity.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s263_subject_clarity_motion_review\comparison_s260\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.99527316623264`, right `74.41683525933159`, delta `-0.5784379069010441`
- Minimum contrast: left `107.0`, right `154.0`, delta `47.0`
- Mean bright ratio: left `0.00025526258680555556`, right `0.00023600260416666667`, delta `-1.925998263888889e-05`
- Mean highlight ratio: left `0.00013807508680555556`, right `0.0001462131076388889`, delta `8.138020833333332e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `96.84375`, right `94.375`, delta `-2.46875`
- Mean luma p99: left `112.25`, right `107.53125`, delta `-4.71875`
- Mean luma p99.5: left `118.0`, right `112.125`, delta `-5.875`
- Mean upper-mid ratio: left `0.00010633680555555556`, right `0.00011691623263888888`, delta `1.057942708333332e-05`
- Mean near-highlight ratio: left `5.5202907986111114e-05`, right `6.171332465277778e-05`, delta `6.510416666666661e-06`
- Mean specular ratio: left `2.4820963541666667e-05`, right `2.753363715277778e-05`, delta `2.7126736111111116e-06`
- Mean frame contrast: left `205.5625`, right `208.0`, delta `2.4375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S263 validates the S262 lower glint/reflection clutter and stronger water body volume/detail over the 32-frame accepted motion window.

The full-window gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`. Compared with S260 accepted, S263 preserves
coverage, raises minimum contrast by `47.0`, raises mean frame contrast by
`2.4375`, and reduces mean bright ratio. The luma tail drops, which is expected
from reduced glint/reflection clutter, while highlight/specular increases stay
small enough for acceptance parity.

## Next

Run S264 accepted-preset parity by folding the S262 subject-clarity settings
into `dam_break_water_mesh_smoothing` and comparing the accepted preset against
S263.
