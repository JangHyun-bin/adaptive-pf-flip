# S210 Normal-Rough Soft-Highlight Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s210_normal_rough_soft_highlight\comparison_untreated\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.70723090277778`, right `68.78196180555557`, delta `0.07473090277778738`
- Minimum contrast: left `74.0`, right `79.0`, delta `5.0`
- Mean bright ratio: left `0.00018229166666666667`, right `8.680555555555556e-05`, delta `-9.548611111111112e-05`
- Mean highlight ratio: left `0.00013020833333333333`, right `6.944444444444444e-05`, delta `-6.076388888888889e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S210 compares untreated normal_rough water frames against a less highlight-suppressing label-gated material treatment.

Compared with untreated frames, S210 improves the minimum contrast by `5` and
keeps nonblank coverage unchanged. It still reduces bright/highlight ratios, so
it is not ready for baseline promotion.

## Decision

Keep S210 as the preferred opt-in `normal_rough` candidate over S208, but do
not promote it as a default baseline change yet.

## Next

Run a wider comparison or a keyframe/gallery review before any baseline
promotion.
