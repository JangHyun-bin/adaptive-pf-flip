# S211 Normal-Rough Keyframe Review

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s211_normal_rough_keyframe_review\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `68.166298828125`, right `68.13064127604167`, delta `-0.035657552083321775`
- Minimum contrast: left `90.0`, right `82.0`, delta `-8.0`
- Mean bright ratio: left `9.54861111111111e-05`, right `4.991319444444444e-05`, delta `-4.557291666666666e-05`
- Mean highlight ratio: left `7.161458333333333e-05`, right `3.689236111111111e-05`, delta `-3.472222222222222e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S211 compares a 4-frame 640x360 untreated normal_rough window against the S210 soft-highlight treatment.

The wider keyframe review rejects S210 as a baseline candidate. The treated
frames keep nonblank coverage, but minimum contrast drops by `8`, mean
luminance drops slightly, and both bright/highlight ratios fall. The 2-frame
S210 probe was too narrow to prove a benefit.

## Decision

Do not promote S210. Keep all `normal_rough` material treatments opt-in only,
and prefer a geometry/normal-continuity approach for the next pass.

## Next

S212 should test label-gated mesh smoothing or normal-continuity treatment on
`normal_rough` frames instead of further suppressing the water material.
