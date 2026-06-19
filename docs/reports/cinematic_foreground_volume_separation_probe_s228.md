# S228 Foreground Volume Separation Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s228_foreground_volume_separation_probe\comparison_s224\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.63853515625`, right `71.31790364583334`, delta `0.6793684895833394`
- Minimum contrast: left `90.0`, right `90.0`, delta `0.0`
- Mean bright ratio: left `0.00018256293402777777`, right `0.00017605251736111112`, delta `-6.510416666666654e-06`
- Mean highlight ratio: left `0.00012369791666666668`, right `0.00012044270833333334`, delta `-3.2552083333333407e-06`
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

Direct secondary counts match the S224 accepted baseline on all `16` review frames.

## Visual Finding

S228 tests a bounded foreground water separation pass by slightly strengthening rim and volume-scattering cues over the accepted S224 baseline.

## Next

Keep S228 as the foreground separation promotion candidate, but do not fold it into the accepted preset until a 32-frame motion review confirms the small bright/highlight ratio drop stays harmless.
