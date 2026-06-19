# S249 Secondary Mist Readability Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s249_secondary_mist_readability_probe\comparison_s246_16f\comparison_sheet.png`
- Gallery: `build\shots\s249_secondary_mist_readability_probe\gallery\index.html`
- GIF: `build\shots\s249_secondary_mist_readability_probe\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
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

- Mean luminance: left `72.43924858940971`, right `72.87313910590278`, delta `0.4338905164930651`
- Minimum contrast: left `95.0`, right `95.0`, delta `0.0`
- Mean bright ratio: left `0.0002446831597222222`, right `0.0002444118923611111`, delta `-2.712673611110993e-07`
- Mean highlight ratio: left `0.00013726128472222224`, right `0.00013590494791666666`, delta `-1.3563368055555778e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.5625`, right `92.8125`, delta `0.25`
- Mean luma p99: left `110.125`, right `110.1875`, delta `0.0625`
- Mean luma p99.5: left `116.625`, right `116.75`, delta `0.125`
- Mean upper-mid ratio: left `0.00010986328125`, right `0.00010850694444444445`, delta `-1.3563368055555507e-06`
- Mean near-highlight ratio: left `6.157769097222223e-05`, right `6.130642361111111e-05`, delta `-2.7126736111111286e-07`
- Mean specular ratio: left `3.0653211805555556e-05`, right `3.0381944444444444e-05`, delta `-2.7126736111111286e-07`
- Mean frame contrast: left `196.5625`, right `195.4375`, delta `-1.125`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S249 tests a bounded secondary mist readability preset against the accepted S246 baseline without changing direct secondary particles.

The tuned probe is intentionally weaker than the first trial in this step. The
first trial added too much broad haze and dropped minimum contrast by `2.0`.
The committed probe preserves minimum contrast and nonblank coverage while
raising `luma_p95`, `luma_p99`, and `luma_p99.5`. The tiny negative bright and
highlight deltas are near comparison noise and need a 32-frame check before
promotion.

## Next

Run S250 as a 32-frame motion review for
`dam_break_secondary_mist_readability_probe` against S246 accepted.
