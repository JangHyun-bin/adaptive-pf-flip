# S214 Mixed-Window Accepted Preset Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s214_mixed_window_accepted_preset\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80924587673611`, right `69.80939507378473`, delta `0.00014919704861426908`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.0001904296875`, right `0.00019097222222222223`, delta `5.425347222222257e-07`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Label Routing

- Mixed dry-run labels: `normal_rough: 1`, `stable: 7`
- Mixed gate: `passed`
- Quality smoothing config: enabled for `normal_rough`, `factor: 0.04`, `iterations: 1`
- Component/topology blocked labels: absent in the mixed window

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S214 compares the accepted water mesh smoothing preset against the same preset with the normal_rough quality smoothing pass disabled.

## Decision

Keep the S213 accepted-preset fold. In the mixed review window the new
`normal_rough` quality smoothing pass changes only one routed frame, preserves
nonblank coverage, preserves minimum contrast, and does not reduce the mean
highlight ratio.

## Next

The next pass can move from mesh-quality gating back to broader cinematic
quality: either publish the S214 gallery for external review or start a focused
water depth/reflection treatment on top of the accepted mixed-window preset.
