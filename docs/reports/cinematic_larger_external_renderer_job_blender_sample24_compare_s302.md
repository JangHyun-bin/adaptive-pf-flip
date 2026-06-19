# S291 Full32 Sampled vs S302 Larger Job Sample24

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s302_larger_external_renderer_job_blender_sample24\comparison_s291\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.90984652295525`, right `74.98456548996914`, delta `0.07471896701389369`
- Minimum contrast: left `188.0`, right `128.0`, delta `-60.0`
- Mean bright ratio: left `0.00025734230324074076`, right `0.00023823302469135803`, delta `-1.9109278549382734e-05`
- Mean highlight ratio: left `0.0001457007137345679`, right `0.00013623649691358024`, delta `-9.464216820987667e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `96.08333333333333`, right `96.25`, delta `0.1666666666666714`
- Mean luma p99: left `109.75`, right `109.83333333333333`, delta `0.0833333333333286`
- Mean luma p99.5: left `116.0`, right `115.91666666666667`, delta `-0.0833333333333286`
- Mean upper-mid ratio: left `0.00011027520576131686`, right `0.00010657793209876543`, delta `-3.69727366255143e-06`
- Mean near-highlight ratio: left `6.462191358024692e-05`, right `6.108539094650206e-05`, delta `-3.536522633744863e-06`
- Mean specular ratio: left `3.423996913580247e-05`, right `3.102494855967078e-05`, delta `-3.215020576131689e-06`
- Mean frame contrast: left `211.5`, right `211.25`, delta `-0.25`

## Metadata Attenuation

- Status: `missing_sidecar`
- Water alpha multiplier: `{'max': 0.88, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 1.08}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 1.0}`

## Visual Finding

S302 renders a 24-frame Blender sample from the larger 48-frame S295 job path.

## Next

If acceptable, publish/package S302 or scale to a full 48-frame larger-job Blender render.
