# S240 Foam Readability Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s240_foam_readability_probe\comparison_s238_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.89021674262153`, right `72.04312445746528`, delta `0.15290771484374943`
- Minimum contrast: left `96.0`, right `96.0`, delta `0.0`
- Mean bright ratio: left `0.00021185980902777777`, right `0.00021402994791666668`, delta `2.170138888888903e-06`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `91.4375`, right `92.0`, delta `0.5625`
- Mean luma p99: left `109.6875`, right `110.0`, delta `0.3125`
- Mean luma p99.5: left `116.5625`, right `116.75`, delta `0.1875`
- Mean upper-mid ratio: left `9.684244791666667e-05`, right `9.684244791666667e-05`, delta `0.0`
- Mean near-highlight ratio: left `5.018446180555556e-05`, right `5.018446180555556e-05`, delta `0.0`
- Mean specular ratio: left `2.5227864583333333e-05`, right `2.5227864583333333e-05`, delta `0.0`
- Mean frame contrast: left `197.5`, right `197.5`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Surface-Quality Gate

- Render frames: `16`
- Label counts: `normal_rough: 2`, `stable: 14`
- Stable ratio: `0.875`
- Blocked labels: `0`
- Component treatment no-op: `true`

## Overlay Count Check

- Contact foam mean count: `42.75 -> 52.4375`
- Contact foam max count: `49 -> 61`
- Impact ripple mean count: `62.0 -> 73.0`
- Impact ripple max count: `62 -> 73`
- Secondary streak mean count: `235.8125 -> 235.8125`

## Secondary Count Check

Direct secondary counts match the S238 accepted 16-frame baseline on all `16` probe frames.

## Visual Finding

S240 tests bounded contact foam sheet and ripple cue readability on top of the accepted S238 water baseline.

## Decision

Promote S240 to a 32-frame motion review. The probe improves contact foam and ripple cue density while preserving nonblank coverage, minimum contrast, direct secondary count parity, and accepted highlight-material behavior.

## Next

Run S241 against the S238 accepted motion baseline before any accepted-preset promotion.
