# S291 Full32 Sampled vs S299 Larger Job Sample12

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s299_larger_external_renderer_job_blender_sample12\comparison_s291\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.90984652295525`, right `75.1337416409465`, delta `0.22389511799124762`
- Minimum contrast: left `188.0`, right `159.0`, delta `-29.0`
- Mean bright ratio: left `0.00025734230324074076`, right `0.00027600951646090537`, delta `1.8667213220164604e-05`
- Mean highlight ratio: left `0.0001457007137345679`, right `0.00013824588477366257`, delta `-7.454828960905345e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `96.16666666666667`, right `96.08333333333333`, delta `-0.08333333333334281`
- Mean luma p99: left `109.75`, right `109.58333333333333`, delta `-0.1666666666666714`
- Mean luma p99.5: left `116.0`, right `115.66666666666667`, delta `-0.3333333333333286`
- Mean upper-mid ratio: left `0.00010947145061728396`, right `0.00010834619341563784`, delta `-1.1252572016461169e-06`
- Mean near-highlight ratio: left `6.028163580246913e-05`, right `6.188914609053498e-05`, delta `1.6075102880658444e-06`
- Mean specular ratio: left `3.182870370370371e-05`, right `3.070344650205761e-05`, delta `-1.1252572016460965e-06`
- Mean frame contrast: left `210.91666666666666`, right `206.75`, delta `-4.166666666666657`

## Metadata Attenuation

- Status: `missing_sidecar`
- Water alpha multiplier: `{'max': 0.88, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 1.08}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 1.0}`

## Visual Finding

S299 renders a bounded Blender sample from the larger 48-frame S295 job path.

## Next

If acceptable, publish/package S299 or scale to a longer larger-job Blender render.
