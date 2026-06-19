# S180 Secondary Mist De-Beading

## Objective

Reduce the tan/gold bead-like direct secondary particle read identified in S179,
while preserving S177 water-surface strip breakup and S173 metadata-depth
attenuation.

## Scope

- Add a preset extending `dam_break_surface_reflection_breakup`.
- Reduce direct secondary radius scale and channel radius scales.
- Shift secondary materials cooler and less opaque.
- Keep soft spray/foam mist visible.
- Render and compare against S177 without rerunning simulation.

## Result

Added preset:

- `dam_break_secondary_mist_debeading`

Generated artifacts:

- Gate report: `docs/reports/cinematic_secondary_mist_debeading_s180.md`
- Comparison report:
  `docs/reports/cinematic_secondary_mist_debeading_comparison_s180.md`
- Bridge summary:
  `build/shots/s180_secondary_mist_debeading/blender/bridge_summary.json`
- GIF: `build/shots/s180_secondary_mist_debeading/shot.gif`
- Comparison sheet:
  `build/shots/s180_secondary_mist_debeading/comparison/comparison_sheet.png`

Gate summary:

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: `83.3397482940297`
- Mean nonblank ratio delta vs S177: `0.0`
- Mean bright ratio delta vs S177: `0.000003315489969135839`

Finding:

- S180 keeps the S177 water surface and strip breakup while reducing direct
  secondary bead scale/opacity.

## Next

S181 should package/publish S180 for public gallery review.
