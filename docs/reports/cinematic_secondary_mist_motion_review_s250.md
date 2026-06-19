# S250 Secondary Mist Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s250_secondary_mist_motion_review\comparison_s246\comparison_sheet.png`
- Gallery: `build\shots\s250_secondary_mist_motion_review\gallery\index.html`
- GIF: `build\shots\s250_secondary_mist_motion_review\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Pass Deltas

- Soft mist spray channel: `3.55 -> 3.64`
- Soft mist foam channel: `3.05 -> 3.14`
- Soft mist alpha scale: `0.37 -> 0.386`
- Soft mist max radius: `1.38 -> 1.42`
- Streak spray channel: `1.18 -> 1.22`
- Streak foam channel: `0.5 -> 0.53`
- Contact mist curtain layers: `11 -> 12`
- Contact mist curtain alpha scale: `0.108 -> 0.114`
- Contact foam mean delta: `0`
- Impact ripple mean delta: `0`
- Secondary streak mean delta: `0`

## Metric Deltas

- Mean luminance: left `72.49517388237847`, right `72.93137546115452`, delta `0.4362015787760498`
- Minimum contrast: left `101.0`, right `98.0`, delta `-3.0`
- Mean bright ratio: left `0.00026502821180555557`, right `0.0002643500434027778`, delta `-6.781684027777754e-07`
- Mean highlight ratio: left `0.00015068901909722222`, right `0.00014946831597222222`, delta `-1.220703125000001e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.4375`, right `92.78125`, delta `0.34375`
- Mean luma p99: left `110.0`, right `110.1875`, delta `0.1875`
- Mean luma p99.5: left `116.40625`, right `116.5`, delta `0.09375`
- Mean upper-mid ratio: left `0.00011773003472222222`, right `0.00011759440104166667`, delta `-1.3563368055554965e-07`
- Mean near-highlight ratio: left `6.212022569444444e-05`, right `6.184895833333334e-05`, delta `-2.712673611110993e-07`
- Mean specular ratio: left `3.1602647569444445e-05`, right `3.173828125e-05`, delta `1.3563368055555643e-07`
- Mean frame contrast: left `199.90625`, right `198.125`, delta `-1.78125`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S250 validates the S249 secondary mist readability probe over the 32-frame accepted motion window.

The result is not an acceptance candidate as-is. The probe raises upper
luminance percentiles and keeps coverage, but it drops minimum contrast by
`3.0` and mean frame contrast by `1.78125`, indicating too much broad haze in
the full motion window.

## Next

Run S251 with a softer mist-only probe: reduce or remove the contact mist curtain
increase, keep a smaller soft/streak lift, and require non-negative minimum
contrast before promotion.
