# S209 Normal-Rough Treatment Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s209_normal_rough_comparison\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.70723090277778`, right `68.89341145833333`, delta `0.18618055555555202`
- Minimum contrast: left `74.0`, right `78.0`, delta `4.0`
- Mean bright ratio: left `0.00018229166666666667`, right `7.8125e-05`, delta `-0.00010416666666666667`
- Mean highlight ratio: left `0.00013020833333333333`, right `6.944444444444444e-05`, delta `-6.076388888888889e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S209 compares untreated normal_rough water frames against the S208 label-gated material treatment.

The result is mixed but safe. S208 raises the minimum contrast by `4`, keeps
nonblank coverage unchanged, and slightly raises mean luminance. It also lowers
bright/highlight ratios and has a small pixel delta, so this is not enough
evidence to promote the pass into the accepted cinematic baseline.

## Decision

Keep S208 as an opt-in `normal_rough` treatment. Do not promote it as a default
baseline change yet.

## Next

Run a wider normal-rough comparison or tune a less highlight-suppressing variant
before any baseline promotion.
