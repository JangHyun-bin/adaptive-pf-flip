# S267 Secondary Dewarm Probe

## Status

Passed as a 16-frame secondary de-warm probe. Promote to S268 32-frame motion
review before acceptance.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s267_secondary_dewarm_probe\comparison_s264_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.41484944661458`, right `74.17131673177083`, delta `-0.24353271484375227`
- Minimum contrast: left `177.0`, right `177.0`, delta `0.0`
- Mean bright ratio: left `0.00021728515625`, right `0.0002175564236111111`, delta `2.712673611110993e-07`
- Mean highlight ratio: left `0.000126953125`, right `0.00012749565972222223`, delta `5.425347222222257e-07`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `94.5625`, right `93.75`, delta `-0.8125`
- Mean luma p99: left `107.375`, right `106.25`, delta `-1.125`
- Mean luma p99.5: left `111.9375`, right `110.5625`, delta `-1.375`
- Mean upper-mid ratio: left `9.711371527777778e-05`, right `9.711371527777778e-05`, delta `0.0`
- Mean near-highlight ratio: left `5.154079861111111e-05`, right `5.1812065972222224e-05`, delta `2.7126736111111286e-07`
- Mean specular ratio: left `2.197265625e-05`, right `2.2243923611111112e-05`, delta `2.7126736111111286e-07`
- Mean frame contrast: left `207.3125`, right `207.375`, delta `0.0625`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S267 tests cooler secondary materials plus reduced direct bead retention and softer secondary emission against the accepted S264 look.

The surface-quality gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`. Compared with S264, S267 keeps nonblank
coverage and contrast stable while lowering mean luminance by
`0.24353271484375227` and lowering the upper luma tail. Bright/highlight
increases are only around `1e-7`, so the visual de-warm/de-bead effect is safe
enough for full-window review.

## Next

Run S268 as a 32-frame motion review for `dam_break_secondary_dewarm_probe`.
