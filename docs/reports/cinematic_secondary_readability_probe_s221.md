# S221 Secondary Readability Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s221_secondary_readability_probe\comparison_s220\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `70.24428819444445`, right `70.30478786892361`, delta `0.0604996744791606`
- Minimum contrast: left `201.0`, right `201.0`, delta `0.0`
- Mean bright ratio: left `0.00019151475694444446`, right `0.00019151475694444446`, delta `0.0`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.00012044270833333334`, delta `0.0`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Secondary Routing

- Direct secondary pass: unchanged from S220
- Direct secondary counts: unchanged from S220 on all 8 review frames
- Soft pass: spray/foam scale and alpha/emission increased
- Streak pass: spray/foam scale, length, alpha, and emission increased
- Mesh-quality gate: `passed`, labels `normal_rough: 1`, `stable: 7`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S221 strengthens soft mist and streak secondary passes while leaving direct secondary particle thinning unchanged.

Visual inspection shows a small readability gain in the upper spray/foam mist
without extra direct-particle clutter. The change is safe but subtle.

## Decision

Keep S221 as an opt-in secondary readability candidate, not yet accepted. The
metrics are safe, but the visual gain is smaller than the overlay-highlight
promotion in S220.

## Next

S222 should A/B a slightly stronger soft/streak-only secondary pass. Keep direct
secondary thinning unchanged.
