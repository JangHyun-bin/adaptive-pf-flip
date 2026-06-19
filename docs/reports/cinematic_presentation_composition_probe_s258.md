# S258 Presentation Composition Probe

## Status

Passed as a 16-frame camera-only composition probe. Promote to S259 32-frame
motion review before acceptance.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s258_presentation_composition_probe\comparison_s255_camera_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `75.01341200086806`, right `74.98091688368055`, delta `-0.032495117187508527`
- Minimum contrast: left `96.0`, right `153.0`, delta `57.0`
- Mean bright ratio: left `0.00027018229166666667`, right `0.00025010850694444446`, delta `-2.0073784722222216e-05`
- Mean highlight ratio: left `0.00013834635416666666`, right `0.0001296657986111111`, delta `-8.680555555555557e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `95.5`, right `97.0625`, delta `1.5625`
- Mean luma p99: left `112.6875`, right `112.3125`, delta `-0.375`
- Mean luma p99.5: left `119.125`, right `118.1875`, delta `-0.9375`
- Mean upper-mid ratio: left `0.00010850694444444444`, right `0.00010091145833333333`, delta `-7.595486111111106e-06`
- Mean near-highlight ratio: left `5.805121527777778e-05`, right `5.208333333333334e-05`, delta `-5.967881944444442e-06`
- Mean specular ratio: left `2.604166666666667e-05`, right `2.2243923611111112e-05`, delta `-3.7977430555555563e-06`
- Mean frame contrast: left `195.0625`, right `206.0`, delta `10.9375`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S258 tests a camera-only wider and slightly lifted composition against the accepted S255 look.

The probe keeps the S255 accepted look and changes only camera motion. The
surface-quality gate passed with `normal_rough: 2`, `stable: 14`, stable ratio
`0.875`, and blocked labels `0`. Secondary framing remains safely inside QA:
mean inside ratio is `0.934460364976418` and min inside ratio is
`0.762962962962963`.

Compared with the accepted 16-frame camera reference, S258 preserves nonblank
coverage, raises minimum contrast by `57.0`, raises mean frame contrast by
`10.9375`, and lowers bright/highlight ratios. The visual comparison adds more
top-flow context while keeping the water body as the primary subject.

## Next

Run S259 as a 32-frame motion review for
`dam_break_presentation_composition_probe` before accepting or rejecting the
camera path.
