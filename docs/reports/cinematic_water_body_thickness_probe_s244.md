# S244 Water Body Thickness Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s244_water_body_thickness_probe\comparison_s242_16f\comparison_sheet.png`
- Gallery: `build\shots\s244_water_body_thickness_probe\gallery\index.html`
- GIF: `build\shots\s244_water_body_thickness_probe\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
- Blocked labels: `0`

## Pass Deltas

- Water volume scatter layers: `18 -> 20`
- Water volume scatter alpha scale: `0.324 -> 0.3456`
- Water volume occlusion enabled: `false -> false`
- Contact foam mean delta: `0`
- Impact ripple mean delta: `0`
- Secondary streak mean delta: `0`

## Metric Deltas

- Mean luminance: left `72.04312038845487`, right `72.43925130208333`, delta `0.3961309136284683`
- Minimum contrast: left `96.0`, right `95.0`, delta `-1.0`
- Mean bright ratio: left `0.00021402994791666668`, right `0.0002446831597222222`, delta `3.065321180555552e-05`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00013726128472222224`, delta `1.6818576388888902e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.0`, right `92.5625`, delta `0.5625`
- Mean luma p99: left `110.0`, right `110.125`, delta `0.125`
- Mean luma p99.5: left `116.75`, right `116.625`, delta `-0.125`
- Mean upper-mid ratio: left `9.684244791666667e-05`, right `0.00010986328125`, delta `1.3020833333333336e-05`
- Mean near-highlight ratio: left `5.018446180555556e-05`, right `6.157769097222223e-05`, delta `1.1393229166666665e-05`
- Mean specular ratio: left `2.5227864583333333e-05`, right `3.0653211805555556e-05`, delta `5.425347222222223e-06`
- Mean frame contrast: left `197.5`, right `196.5625`, delta `-0.9375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S244 tests a bounded water-body thickness/refraction preset against the accepted S242 baseline.

The tuned probe adds a subtle water-body depth cue without changing accepted
foam/ripple/streak counts or nonblank coverage. Compared with the first
occlusion-heavy attempt, the committed probe disables volume occlusion and keeps
the change to material depth plus a small scattering-layer increase.

The remaining risk is small but real: minimum contrast drops by `1.0` and
`luma_p99.5` drops by `0.125`, so the probe should move to motion review before
any accepted-preset promotion.

## Next

Run S245 as a 32-frame motion review for
`dam_break_water_body_thickness_probe` against S242 accepted.
