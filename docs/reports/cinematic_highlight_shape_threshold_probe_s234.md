# S234 Highlight Shape Threshold Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s234_highlight_shape_threshold_probe\comparison_s230eq\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `71.31790364583334`, right `71.52114908854166`, delta `0.20324544270832234`
- Minimum contrast: left `90.0`, right `90.0`, delta `0.0`
- Mean bright ratio: left `0.00017605251736111112`, right `0.0001784939236111111`, delta `2.441406249999975e-06`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

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

## Secondary Count Check

Direct secondary counts match the S230-equivalent accepted foreground-volume baseline on all `16` probe frames.

## Visual Finding

S234 tests a bounded overlay-only highlight shape pass with tighter brighter segmented glint/reflection strokes.

## Decision

Keep S234 as a safe but insufficient opt-in probe. It preserves coverage, minimum contrast, and direct secondary counts while improving mean luminance and bright ratio, but the aggregate highlight ratio is unchanged.

## Next

Do not promote S234 to motion review. The next step should be render-metric calibration or a real material/specular pass rather than more overlay-only strip tuning.
