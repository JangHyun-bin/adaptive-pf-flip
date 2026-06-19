# S253 Presentation Lift Probe

## Status

Passed as a 16-frame presentation probe. Promote to S254 32-frame motion
review before acceptance.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s253_presentation_lift_probe\comparison_s246_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `72.43924858940971`, right `75.01341200086806`, delta `2.5741634114583434`
- Minimum contrast: left `95.0`, right `96.0`, delta `1.0`
- Mean bright ratio: left `0.0002446831597222222`, right `0.00027018229166666667`, delta `2.5499131944444473e-05`
- Mean highlight ratio: left `0.00013726128472222224`, right `0.00013834635416666666`, delta `1.0850694444444243e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `92.5625`, right `95.5`, delta `2.9375`
- Mean luma p99: left `110.125`, right `112.6875`, delta `2.5625`
- Mean luma p99.5: left `116.625`, right `119.125`, delta `2.5`
- Mean upper-mid ratio: left `0.00010986328125`, right `0.00010850694444444444`, delta `-1.3563368055555643e-06`
- Mean near-highlight ratio: left `6.157769097222223e-05`, right `5.805121527777778e-05`, delta `-3.526475694444447e-06`
- Mean specular ratio: left `3.0653211805555556e-05`, right `2.604166666666667e-05`, delta `-4.611545138888888e-06`
- Mean frame contrast: left `196.5625`, right `195.0625`, delta `-1.5`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S253 tests a presentation-only tone/lighting lift against the accepted S246 baseline without changing simulation or material overlays.

The lift is visible without introducing broad haze. Mean luminance rises by
`2.5741634114583434`, `luma_p95` by `2.9375`, `luma_p99` by `2.5625`, and
`luma_p99.5` by `2.5`, while nonblank coverage is unchanged. Bright and
highlight deltas remain tiny, and specular ratio decreases slightly.

Surface-quality gate:

- `normal_rough`: `2`
- `stable`: `14`
- Stable ratio: `0.875`
- Blocked labels: `0`

## Next

Run S254 as a 32-frame motion review against S246 accepted. If the same bounded
readability lift survives motion review, promote the tone/lighting lift as the
next presentation preset candidate.
