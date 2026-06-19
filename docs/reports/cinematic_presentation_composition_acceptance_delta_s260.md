# S260 Presentation Composition Acceptance Delta

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s260_presentation_composition_acceptance\comparison_s255\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `75.0721979437934`, right `74.99527316623264`, delta `-0.07692477756076244`
- Minimum contrast: left `102.0`, right `107.0`, delta `5.0`
- Mean bright ratio: left `0.00029405381944444444`, right `0.00025526258680555556`, delta `-3.879123263888888e-05`
- Mean highlight ratio: left `0.00015326605902777778`, right `0.00013807508680555556`, delta `-1.5190972222222212e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `95.40625`, right `96.84375`, delta `1.4375`
- Mean luma p99: left `112.53125`, right `112.25`, delta `-0.28125`
- Mean luma p99.5: left `118.9375`, right `118.0`, delta `-0.9375`
- Mean upper-mid ratio: left `0.00011813693576388888`, right `0.00010633680555555556`, delta `-1.1800130208333321e-05`
- Mean near-highlight ratio: left `5.900065104166667e-05`, right `5.5202907986111114e-05`, delta `-3.797743055555553e-06`
- Mean specular ratio: left `2.9296875e-05`, right `2.4820963541666667e-05`, delta `-4.475911458333332e-06`
- Mean frame contrast: left `198.21875`, right `205.5625`, delta `7.34375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S260 records the accepted camera-composition delta against the previous S255 accepted baseline.

The accepted camera path preserves full coverage, raises minimum contrast by
`5.0`, raises mean frame contrast by `7.34375`, and reduces bright, highlight,
near-highlight, and specular ratios. Mean luminance changes by only
`-0.07692477756076244`, so the visual effect is composition/readability rather
than an exposure shift.

## Next

Refresh the accepted review package and publish/gallery artifacts from S260.
