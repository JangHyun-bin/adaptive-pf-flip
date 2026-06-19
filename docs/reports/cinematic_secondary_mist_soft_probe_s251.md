# S251 Secondary Mist Soft Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s251_secondary_mist_soft_probe\comparison_s246_16f\comparison_sheet.png`
- Gallery: `build\shots\s251_secondary_mist_soft_probe\gallery\index.html`
- GIF: `build\shots\s251_secondary_mist_soft_probe\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
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

- Mean luminance: left `72.43924858940971`, right `72.45891438802083`, delta `0.019665798611114838`
- Minimum contrast: left `95.0`, right `95.0`, delta `0.0`
- Mean bright ratio: left `0.0002446831597222222`, right `0.0002444118923611111`, delta `-2.712673611110993e-07`
- Mean highlight ratio: left `0.00013726128472222224`, right `0.00013726128472222224`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.5625`, right `92.625`, delta `0.0625`
- Mean luma p99: left `110.125`, right `110.1875`, delta `0.0625`
- Mean luma p99.5: left `116.625`, right `116.6875`, delta `0.0625`
- Mean upper-mid ratio: left `0.00010986328125`, right `0.00010986328125`, delta `0.0`
- Mean near-highlight ratio: left `6.157769097222223e-05`, right `6.157769097222223e-05`, delta `0.0`
- Mean specular ratio: left `3.0653211805555556e-05`, right `3.0653211805555556e-05`, delta `0.0`
- Mean frame contrast: left `196.5625`, right `196.5625`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S251 tests a softer secondary mist readability preset against the accepted S246 baseline after S250 rejected the stronger haze.

This is a conservative retry. It removes the contact haze increase that hurt
S250, keeps direct secondary particles unchanged, and preserves minimum
contrast, mean frame contrast, coverage, and highlight ratio while nudging
`luma_p95`, `luma_p99`, and `luma_p99.5` upward.

## Next

Run S252 as a 32-frame motion review for
`dam_break_secondary_mist_readability_soft_probe` against S246 accepted.
