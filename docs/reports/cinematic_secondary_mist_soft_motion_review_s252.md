# S252 Secondary Mist Soft Motion Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s252_secondary_mist_soft_motion_review\comparison_s246\comparison_sheet.png`
- Gallery: `build\shots\s252_secondary_mist_soft_motion_review\gallery\index.html`
- GIF: `build\shots\s252_secondary_mist_soft_motion_review\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## Pass Deltas

- Soft mist spray channel: `3.55 -> 3.6`
- Soft mist foam channel: `3.05 -> 3.1`
- Soft mist alpha scale: `0.37 -> 0.378`
- Soft mist max radius: `1.38 -> 1.4`
- Streak spray channel: `1.18 -> 1.2`
- Streak foam channel: `0.5 -> 0.51`
- Contact mist curtain layers: `11 -> 11`
- Contact mist curtain alpha scale: `0.108 -> 0.108`
- Contact foam mean delta: `0`
- Impact ripple mean delta: `0`
- Secondary streak mean delta: `0`

## Metric Deltas

- Mean luminance: left `72.49517388237847`, right `72.51579847547742`, delta `0.020624593098958144`
- Minimum contrast: left `101.0`, right `101.0`, delta `0.0`
- Mean bright ratio: left `0.00026502821180555557`, right `0.000264892578125`, delta `-1.3563368055557676e-07`
- Mean highlight ratio: left `0.00015068901909722222`, right `0.00015068901909722222`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.4375`, right `92.5625`, delta `0.125`
- Mean luma p99: left `110.0`, right `110.03125`, delta `0.03125`
- Mean luma p99.5: left `116.40625`, right `116.375`, delta `-0.03125`
- Mean upper-mid ratio: left `0.00011773003472222222`, right `0.00011773003472222222`, delta `0.0`
- Mean near-highlight ratio: left `6.212022569444444e-05`, right `6.198459201388889e-05`, delta `-1.3563368055554965e-07`
- Mean specular ratio: left `3.1602647569444445e-05`, right `3.1602647569444445e-05`, delta `0.0`
- Mean frame contrast: left `199.90625`, right `199.90625`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S252 validates the S251 softer secondary mist probe over the 32-frame accepted motion window.

The result is stable but too subtle to accept. It preserves minimum contrast,
mean frame contrast, coverage, and highlight ratio, and it nudges `luma_p95` and
`luma_p99` upward. However, the mean luminance delta is only
`+0.020624593098958144`, and `luma_p99.5` has a tiny negative delta. This is not
worth another accepted-preset change.

## Next

Do not promote S251. Move to a more visible presentation or shot-composition
pass from the S246 accepted baseline.
