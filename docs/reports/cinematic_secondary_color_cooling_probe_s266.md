# S266 Secondary Color Cooling Probe

## Status

Passed as a safe material-only probe, but do not promote as-is.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s266_secondary_color_cooling_probe\comparison_s264_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.41484944661458`, right `74.36247233072916`, delta `-0.05237711588542027`
- Minimum contrast: left `177.0`, right `177.0`, delta `0.0`
- Mean bright ratio: left `0.00021728515625`, right `0.00021728515625`, delta `0.0`
- Mean highlight ratio: left `0.000126953125`, right `0.000126953125`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `94.5625`, right `94.375`, delta `-0.1875`
- Mean luma p99: left `107.375`, right `107.0`, delta `-0.375`
- Mean luma p99.5: left `111.9375`, right `111.4375`, delta `-0.5`
- Mean upper-mid ratio: left `9.711371527777778e-05`, right `9.711371527777778e-05`, delta `0.0`
- Mean near-highlight ratio: left `5.154079861111111e-05`, right `5.154079861111111e-05`, delta `0.0`
- Mean specular ratio: left `2.197265625e-05`, right `2.197265625e-05`, delta `0.0`
- Mean frame contrast: left `207.3125`, right `207.3125`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S266 tests cooler secondary spray/foam/bubble materials against the accepted S264 look without changing particle counts or overlays.

The surface-quality gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`. The probe keeps all particle counts and
overlay passes unchanged.

The visual delta is intentionally safe but too small: mean luminance shifts by
only `-0.05237711588542027`, contrast/bright/highlight/nonblank metrics are
unchanged, and the comparison still leaves the secondary beads reading warmer
than desired.

## Next

Do not promote S266. Run S267 with stronger secondary bead de-warming that also
reduces direct bead retention/alpha and secondary emission.
