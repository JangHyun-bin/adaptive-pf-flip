# S216 Water Depth Reflection Probe

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s216_depth_reflection_probe\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `69.80939507378473`, right `69.07447157118055`, delta `-0.7349235026041754`
- Minimum contrast: left `201.0`, right `193.0`, delta `-8.0`
- Mean bright ratio: left `0.00019097222222222223`, right `0.00024034288194444445`, delta `4.9370659722222215e-05`
- Mean highlight ratio: left `0.00012044270833333334`, right `0.0001638454861111111`, delta `4.340277777777777e-05`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Label Routing

- Source window: `8..55`
- Render labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Normal-rough quality smoothing remains inherited from the accepted preset.

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S216 compares a conservative depth/reflection treatment against the accepted S214 mixed-window preset.

Visual inspection shows the probe reads as slightly deeper and preserves the
water coverage, but it also darkens the sequence and lowers the minimum contrast
floor.

## Decision

Keep `dam_break_water_mesh_depth_reflection_probe` as an opt-in probe, but do not
promote it into the accepted preset. The added highlight energy is useful, but
the `-8.0` minimum contrast delta and `-0.7349235026041754` mean luminance delta
need a follow-up tune before baseline promotion.

## Next

S217 should recover contrast while keeping the useful highlight increase. Start
by easing the water depth darkening and/or raising reflection/glint emission less
aggressively, then compare against both S214 accepted and this S216 probe.
