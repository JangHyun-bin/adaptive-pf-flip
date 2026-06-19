# S242 Foam Readability Acceptance

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s242_foam_readability_acceptance\comparison_s241\comparison_sheet.png`
- Gallery: `build\shots\s242_foam_readability_acceptance\gallery\index.html`
- GIF: `build\shots\s242_foam_readability_acceptance\shot.gif`

## Surface-Quality Gate

- Status: `passed`
- Frames: `32`
- Label counts: `normal_rough: 3`, `stable: 29`
- Stable ratio: `0.90625`
- Blocked labels: `0`

## S241 Parity Result

- Max changed ratio: `0`
- Max strong changed ratio: `0`
- Max mean abs luma: `0.00014756944444444445`
- Contact foam mean delta: `0`
- Contact foam max delta: `0`
- Impact ripple mean delta: `0`
- Impact ripple max delta: `0`
- Secondary streak mean delta: `0`
- Secondary streak max delta: `0`

## Metric Deltas

- Mean luminance: left `72.11885470920139`, right `72.1188532172309`, delta `-1.4919704796056976e-06`
- Minimum contrast: left `100.0`, right `100.0`, delta `0.0`
- Mean bright ratio: left `0.00021484375`, right `0.00021484375`, delta `0.0`
- Mean highlight ratio: left `0.00012193467881944444`, right `0.00012193467881944444`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.9375`, right `91.9375`, delta `0.0`
- Mean luma p99: left `109.90625`, right `109.90625`, delta `0.0`
- Mean luma p99.5: left `116.40625`, right `116.40625`, delta `0.0`
- Mean upper-mid ratio: left `0.00010308159722222222`, right `0.00010308159722222222`, delta `0.0`
- Mean near-highlight ratio: left `5.655924479166667e-05`, right `5.655924479166667e-05`, delta `0.0`
- Mean specular ratio: left `2.617730034722222e-05`, right `2.617730034722222e-05`, delta `0.0`
- Mean frame contrast: left `199.1875`, right `199.1875`, delta `0.0`

## S238 Baseline Delta

- Baseline comparison sheet:
  `build\shots\s242_foam_readability_acceptance\comparison_s238\comparison_sheet.png`
- Contact foam mean count: `43.1875 -> 54.5625`
- Contact foam max count: `50 -> 61`
- Impact ripple mean count: `62.0 -> 73.0`
- Impact ripple max count: `62 -> 73`
- Secondary streak mean count: `220.75 -> 220.75`
- Mean luminance delta: `+0.16201321072048813`
- Bright ratio delta: `+2.3057725694444525e-06`
- Minimum contrast delta: `0.0`
- Highlight ratio delta: `0.0`
- Nonblank ratio delta: `0.0`
- Calibration `luma_p95` delta: `+0.5`
- Calibration `luma_p99` delta: `+0.1875`
- Calibration `luma_p99.5` delta: `+0.03125`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S242 folds the S240/S241 foam readability settings into the accepted water mesh smoothing preset and checks parity against S241.

The acceptance render is pixel-stable against S241 within render noise, and the
S238 baseline delta remains localized to contact foam and ripple readability
without broad exposure, coverage, or hard-highlight drift.

## Next

Use S242 as the new accepted visual baseline before starting the next water-body
or secondary-particle pass.
