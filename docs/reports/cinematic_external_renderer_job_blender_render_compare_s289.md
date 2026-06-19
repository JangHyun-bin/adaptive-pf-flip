# S282 Accepted HiRes Sampled vs S289 Job Blender

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s289_external_renderer_job_blender_render\comparison_s282_aligned\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.10551462432484`, right `74.66468798225308`, delta `0.5591733579282447`
- Minimum contrast: left `145.0`, right `207.0`, delta `62.0`
- Mean bright ratio: left `0.00021454234182098766`, right `0.0002630690586419753`, delta `4.852671682098762e-05`
- Mean highlight ratio: left `0.0001238184799382716`, right `0.0001285204475308642`, delta `4.701967592592605e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `93.375`, right `95.25`, delta `1.875`
- Mean luma p99: left `109.125`, right `109.5`, delta `0.375`
- Mean luma p99.5: left `115.25`, right `115.75`, delta `0.5`
- Mean upper-mid ratio: left `9.162808641975308e-05`, right `0.00010320216049382716`, delta `1.1574074074074085e-05`
- Mean near-highlight ratio: left `5.160108024691358e-05`, right `5.9799382716049385e-05`, delta `8.198302469135803e-06`
- Mean specular ratio: left `2.9176311728395064e-05`, right `3.3275462962962965e-05`, delta `4.099151234567901e-06`
- Mean frame contrast: left `212.5`, right `212.375`, delta `-0.125`

## Metadata Attenuation

- Status: `missing_sidecar`
- Water alpha multiplier: `{'max': 0.88, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 1.08}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 1.0}`

## Visual Finding

S289 uses the S285 job path through Blender with the same accepted preset and an aligned 8-frame S282 sample.

## Next

Treat S289 as the first actual Blender render from the external renderer job schema; next publish or package it, then scale the job-path render length.
