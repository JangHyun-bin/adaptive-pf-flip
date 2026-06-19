# S246 Water Body Thickness Acceptance Baseline Delta

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s246_water_body_thickness_acceptance\comparison_s242\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `72.1188532172309`, right `72.49517388237847`, delta `0.3763206651475599`
- Minimum contrast: left `100.0`, right `101.0`, delta `1.0`
- Mean bright ratio: left `0.00021484375`, right `0.00026502821180555557`, delta `5.018446180555557e-05`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00015068901909722222`, delta `2.8754340277777787e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.9375`, right `92.4375`, delta `0.5`
- Mean luma p99: left `109.90625`, right `110.0`, delta `0.09375`
- Mean luma p99.5: left `116.40625`, right `116.40625`, delta `0.0`
- Mean upper-mid ratio: left `0.00010308159722222222`, right `0.00011773003472222222`, delta `1.46484375e-05`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `6.212022569444444e-05`, delta `5.560980902777766e-06`
- Mean specular ratio: left `2.617730034722222e-05`, right `3.1602647569444445e-05`, delta `5.425347222222223e-06`
- Mean frame contrast: left `199.1875`, right `199.90625`, delta `0.71875`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S246 accepted preset keeps S242 foam/readability and adds the S244/S245 water-body thickness response.

## Next

Use S246 as the new accepted visual baseline before starting the next secondary mist or render-export pass.
