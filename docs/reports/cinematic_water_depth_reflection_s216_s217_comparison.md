# S216 vs S217 Depth Reflection Tune

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s217_depth_reflection_contrast_probe\comparison_s216\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.07447157118055`, right `69.48267686631945`, delta `0.4082052951388988`
- Minimum contrast: left `193.0`, right `188.0`, delta `-5.0`
- Mean bright ratio: left `0.00024034288194444445`, right `0.00025987413194444446`, delta `1.9531250000000017e-05`
- Mean highlight ratio: left `0.0001638454861111111`, right `0.00016167534722222223`, delta `-2.1701388888888758e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S217 is compared against S216 to verify the contrast-preserving tune.

Compared with S216, S217 raises mean luminance by `0.4082052951388988` and keeps
nonblank coverage unchanged, but it further lowers minimum contrast by `-5.0`
and slightly reduces mean highlight ratio.

## Decision

S217 is not a better promotion candidate than S216. It is a useful diagnostic:
water-material easing helps luminance, but the combined material/scatter/overlay
tune still hurts contrast. The next pass should isolate reflection/glint overlay
changes and leave the accepted water material alone.

## Next

Use S214 accepted as the baseline for S218 and treat S216/S217 as diagnostics,
not promotion candidates.
