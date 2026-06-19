# S246 Water Body Thickness Acceptance

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s246_water_body_thickness_acceptance\comparison_s245\comparison_sheet.png`
- Baseline delta sheet:
  `build\shots\s246_water_body_thickness_acceptance\comparison_s242\comparison_sheet.png`
- Gallery: `build\shots\s246_water_body_thickness_acceptance\gallery\index.html`
- GIF: `build\shots\s246_water_body_thickness_acceptance\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## S245 Parity Result

- Max changed ratio: `0`
- Max strong changed ratio: `0`
- Max mean abs luma: `0.00019097222222222223`
- Water volume scatter layer delta: `0`
- Water volume scatter alpha delta: `0`
- Contact foam mean delta: `0`
- Impact ripple mean delta: `0`
- Secondary streak mean delta: `0`

## Metric Deltas

- Mean luminance: left `72.49517184787327`, right `72.49517388237847`, delta `2.034505200754211e-06`
- Minimum contrast: left `101.0`, right `101.0`, delta `0.0`
- Mean bright ratio: left `0.00026502821180555557`, right `0.00026502821180555557`, delta `0.0`
- Mean highlight ratio: left `0.00015068901909722222`, right `0.00015068901909722222`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.4375`, right `92.4375`, delta `0.0`
- Mean luma p99: left `110.0`, right `110.0`, delta `0.0`
- Mean luma p99.5: left `116.40625`, right `116.40625`, delta `0.0`
- Mean upper-mid ratio: left `0.00011773003472222222`, right `0.00011773003472222222`, delta `0.0`
- Mean near-highlight ratio: left `6.212022569444444e-05`, right `6.212022569444444e-05`, delta `0.0`
- Mean specular ratio: left `3.1602647569444445e-05`, right `3.1602647569444445e-05`, delta `0.0`
- Mean frame contrast: left `199.90625`, right `199.90625`, delta `0.0`

## S242 Baseline Delta

- Mean luminance delta: `+0.3763206651475599`
- Minimum contrast delta: `+1.0`
- Bright ratio delta: `+5.018446180555557e-05`
- Highlight ratio delta: `+2.8754340277777787e-05`
- Nonblank ratio delta: `0.0`
- Calibration `luma_p95` delta: `+0.5`
- Calibration `luma_p99` delta: `+0.09375`
- Calibration `luma_p99.5` delta: `0.0`
- Upper-mid ratio delta: `+1.46484375e-05`
- Specular ratio delta: `+5.425347222222223e-06`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S246 folds the S244/S245 water-body thickness settings into the accepted water mesh smoothing preset and checks parity against S245.

The acceptance render is stable against S245 within render noise. Against S242,
it keeps the accepted foam/readability baseline and adds a subtle water-volume
depth lift with positive contrast and upper-tail deltas.

## Next

Use S246 as the new accepted cinematic water baseline before starting the next
secondary mist or render-export pass.
