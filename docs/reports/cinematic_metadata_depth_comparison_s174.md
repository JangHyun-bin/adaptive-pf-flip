# S174 Metadata Depth Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s174_metadata_depth_comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `86.9082305832851`, right `84.78030921465084`, delta `-2.1279213686342615`
- Minimum contrast: left `184.0`, right `185.0`, delta `1.0`
- Mean bright ratio: left `0.0012959044656635802`, right `0.0010237931616512346`, delta `-0.0002721113040123457`
- Mean highlight ratio: left `0.00015106577932098766`, right `0.00013512128665123455`, delta `-1.5944492669753106e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S173 preserves the S168 water-surface readability while lowering late-frame secondary density and highlight pressure. The diff panel remains concentrated in the water-volume and secondary-particle regions rather than showing broad framing or exposure drift.

## Next

Package the S173 comparison for the public gallery, then choose the next visual pass from the comparison rather than tuning by eye alone.
