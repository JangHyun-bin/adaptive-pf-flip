# S177 Surface Reflection Breakup

## Objective

Reduce the long, uniform horizontal glint/reflection ribbon read identified in
the S176 public gallery triage, while preserving S173 metadata-depth attenuation.

## Scope

- Add optional breakup fields to `water_surface_glint_pass` and
  `water_reflection_pass`.
- Keep existing presets behavior-compatible by default.
- Add `dam_break_surface_reflection_breakup`.
- Render and compare against S173 without rerunning simulation.

## Implemented Controls

- `angle_jitter_degrees`
- `length_jitter`
- `width_jitter`
- `segment_count`
- `segment_gap`
- `dropout`

## Result

Generated artifacts:

- Gate report: `docs/reports/cinematic_surface_reflection_breakup_s177.md`
- Comparison report:
  `docs/reports/cinematic_surface_reflection_breakup_comparison_s177.md`
- Bridge summary:
  `build/shots/s177_surface_reflection_breakup/blender/bridge_summary.json`
- GIF: `build/shots/s177_surface_reflection_breakup/shot.gif`
- Comparison sheet:
  `build/shots/s177_surface_reflection_breakup/comparison/comparison_sheet.png`

Gate summary:

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: `83.72829559702933`
- Mean bright ratio delta vs S173: `-0.0007917691454475309`
- Mean nonblank ratio delta vs S173: `0.0`

Finding:

- S177 reduces the most uniform strip read while keeping the S173 water body and
  metadata attenuation intact.

## Next

S178 should package/publish S177 for public gallery review.
