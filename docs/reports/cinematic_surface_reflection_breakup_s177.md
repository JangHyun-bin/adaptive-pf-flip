# S177 Surface Reflection Breakup Gate

Date: 2026-06-19

## Status

Passed.

S177 adds bounded strip breakup controls for the Blender bridge
`water_surface_glint_pass` and `water_reflection_pass`, then applies them through
the `dam_break_surface_reflection_breakup` preset.

## Inputs

- Baseline shot: `build/shots/s173_metadata_depth_attenuation`
- Source sequence: `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar:
  `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- New preset: `dam_break_surface_reflection_breakup`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s177_surface_breakup_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_surface_reflection_breakup --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s177_surface_reflection_breakup\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_surface_reflection_breakup --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s177_surface_reflection_breakup\blender\frames build\shots\s177_surface_reflection_breakup\shot.gif --fps 12.0
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s173_metadata_depth_attenuation\blender\frames --right build\shots\s177_surface_reflection_breakup\blender\frames --left-label S173 --right-label S177 --out-dir build\shots\s177_surface_reflection_breakup\comparison --summary-left build\shots\s173_metadata_depth_attenuation\blender\bridge_summary.json --summary-right build\shots\s177_surface_reflection_breakup\blender\bridge_summary.json --report docs\reports\cinematic_surface_reflection_breakup_comparison_s177.md --title "S177 Surface Reflection Breakup Comparison" --finding "S177 preserves the S173 metadata-depth water read while breaking up the most uniform horizontal glint/reflection ribbons. Bright ratio drops substantially, contrast and nonblank coverage are unchanged, and the diff remains concentrated on the water-surface strip regions." --next "Package or publish S177 if visual review confirms the strip breakup reads less synthetic than S173; otherwise tune the breakup bounds before another full render."
```

## Artifacts

- Bridge summary: `build/shots/s177_surface_reflection_breakup/blender/bridge_summary.json`
- Render frames: `build/shots/s177_surface_reflection_breakup/blender/frames`
- GIF: `build/shots/s177_surface_reflection_breakup/shot.gif`
- Comparison sheet:
  `build/shots/s177_surface_reflection_breakup/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_surface_reflection_breakup_comparison_s177.md`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: min `80.3776953125`, mean `83.72829559702933`, max `93.78624348958333`
- Bright ratio: min `0.000022786458333333334`, mean `0.0002320240162037037`, max `0.0006467013888888889`
- Highlight ratio: min `0.000006510416666666667`, mean `0.0001351514274691358`, max `0.00041341145833333334`

S173 comparison deltas:

- Mean luminance delta: `-1.0520136176215118`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `-0.0007917691454475309`
- Mean highlight ratio delta: `0.00000003014081790124229`
- Mean nonblank ratio delta: `0.0`

## Visual Read

The long surface glint/reflection ribbons are now segmented with small angular
and length variation. The change is concentrated on the water-surface strip
regions, while metadata-depth water body and secondary attenuation remain
intact.

## Next

S178 should package/publish the S177 gallery for public inspection, then decide
whether to keep this breakup bound or tune it further.
