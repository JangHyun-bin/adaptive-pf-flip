# S302 Sample24 vs S305 Full48 Sampled

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s305_larger_external_renderer_job_blender_full48\comparison_s302\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.98456548996914`, right `75.00571092142489`, delta `0.021145431455749986`
- Minimum contrast: left `128.0`, right `106.0`, delta `-22.0`
- Mean bright ratio: left `0.00023823302469135803`, right `0.00024775752314814815`, delta `9.524498456790125e-06`
- Mean highlight ratio: left `0.00013623649691358024`, right `0.00014214409722222222`, delta `5.907600308641971e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `95.91666666666667`, right `98.66666666666667`, delta `2.75`
- Mean luma p99: left `109.58333333333333`, right `109.45833333333333`, delta `-0.125`
- Mean luma p99.5: left `115.66666666666667`, right `113.625`, delta `-2.0416666666666714`
- Mean upper-mid ratio: left `0.00010818544238683128`, right `6.06031378600823e-05`, delta `-4.758230452674898e-05`
- Mean near-highlight ratio: left `6.028163580246913e-05`, right `3.59278549382716e-05`, delta `-2.435378086419753e-05`
- Mean specular ratio: left `2.925668724279835e-05`, right `2.129951131687243e-05`, delta `-7.957175925925922e-06`
- Mean frame contrast: left `208.20833333333334`, right `204.08333333333334`, delta `-4.125`

## Metadata Attenuation

- Status: `missing_sidecar`
- Water alpha multiplier: `{'max': 0.88, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 1.08}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 1.0}`

## Visual Finding

S305 keeps the larger-job path nonblank while extending the same source window to all 48 frames.

## Next

Build and publish the S305 full48 gallery, then decide whether to package it or start the non-Blender external renderer adapter.
