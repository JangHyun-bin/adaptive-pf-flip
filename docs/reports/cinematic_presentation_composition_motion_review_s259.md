# S259 Presentation Composition Motion Review

## Status

Passed as a 32-frame camera motion review. Promote to S260 accepted-camera
parity.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s259_presentation_composition_motion_review\comparison_s255\comparison_sheet.png`

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

S259 validates the S258 camera-only wider and slightly lifted composition over the 32-frame accepted motion window.

The camera path keeps the water body primary while adding more top-flow context.
The full-window gate passed with `normal_rough: 3`, `stable: 29`, stable ratio
`0.90625`, and blocked labels `0`. Secondary framing remains inside QA with
mean inside ratio `0.9373630705958788` and min inside ratio
`0.7239057239057239`.

Against S255 accepted, S259 preserves nonblank coverage, raises minimum
contrast by `5.0`, raises mean frame contrast by `7.34375`, and reduces bright,
highlight, near-highlight, and specular ratios. The upper luma tail drops
slightly while `luma_p95` rises, which is consistent with the wider framing
adding structure without increasing hard highlights.

## Next

Run S260 accepted-camera parity by folding this camera motion into
`dam_break_water_mesh_smoothing` and comparing the accepted preset against S259.
