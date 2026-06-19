# S282 Accepted HiRes vs S291 Job Blender Full32

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s291_external_renderer_job_blender_full32\comparison_s282\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.10551462432484`, right `74.90984652295525`, delta `0.8043318986304087`
- Minimum contrast: left `145.0`, right `188.0`, delta `43.0`
- Mean bright ratio: left `0.00021454234182098766`, right `0.00025734230324074076`, delta `4.27999614197531e-05`
- Mean highlight ratio: left `0.0001238184799382716`, right `0.0001457007137345679`, delta `2.188223379629632e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `93.375`, right `95.375`, delta `2.0`
- Mean luma p99: left `109.125`, right `109.375`, delta `0.25`
- Mean luma p99.5: left `115.25`, right `115.75`, delta `0.5`
- Mean upper-mid ratio: left `9.162808641975308e-05`, right `0.00010440779320987654`, delta `1.2779706790123465e-05`
- Mean near-highlight ratio: left `5.160108024691358e-05`, right `5.9799382716049385e-05`, delta `8.198302469135803e-06`
- Mean specular ratio: left `2.9176311728395064e-05`, right `3.279320987654321e-05`, delta `3.6168981481481466e-06`
- Mean frame contrast: left `212.5`, right `212.625`, delta `0.125`

## Metadata Attenuation

- Status: `missing_sidecar`
- Water alpha multiplier: `{'max': 0.88, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 1.08}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 1.0}`

## Visual Finding

S291 renders the full 32-frame accepted window through the S285 external renderer job schema.

## Next

If this parity is acceptable, publish/package S291 as the current full-length job-path Blender proof.
