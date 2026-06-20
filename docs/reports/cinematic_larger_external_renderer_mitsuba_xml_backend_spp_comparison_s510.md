# S510 Mitsuba XML Backend SPP Comparison

## Status

Passed.

This comparison uses existing Mitsuba backend preview frame directories and adapter summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s510_mitsuba_xml_backend_spp_comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `None`, right `None`, delta `None`
- Minimum contrast: left `None`, right `None`, delta `None`
- Mean bright ratio: left `None`, right `None`, delta `None`
- Mean highlight ratio: left `None`, right `None`, delta `None`
- Mean nonblank ratio: left `None`, right `None`, delta `None`

## Calibration Deltas

- Mean luma p95: left `87.875`, right `87.25`, delta `-0.625`
- Mean luma p99: left `103.5`, right `101.5`, delta `-2.0`
- Mean luma p99.5: left `109.75`, right `107.5`, delta `-2.25`
- Mean upper-mid ratio: left `1.0609567901234568e-05`, right `2.4112654320987654e-06`, delta `-8.198302469135803e-06`
- Mean near-highlight ratio: left `1.2056327160493827e-06`, right `2.4112654320987655e-07`, delta `-9.645061728395062e-07`
- Mean specular ratio: left `4.822530864197531e-07`, right `0.0`, delta `-4.822530864197531e-07`
- Mean frame contrast: left `201.625`, right `150.75`, delta `-50.875`

## Metadata Attenuation

- Status: `None`
- Water alpha multiplier: `None`
- Water emission multiplier: `None`
- Secondary particle cap scale: `None`

## Visual Finding

S508 raises the real Mitsuba backend command adapter from SPP1 to SPP4 with matching frame count and zero process/render failures; use the diff sheet to judge whether the visible noise reduction is worth the larger EXR output.

## Next

Publish or inspect this comparison, then choose the next scale axis: SPP, frame count, or scene size.
