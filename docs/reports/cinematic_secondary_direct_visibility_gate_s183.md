# S183 Secondary Direct Visibility Gate

Date: 2026-06-19

## Status

Passed.

S183 adds `dam_break_secondary_direct_visibility_gate`, a bounded renderer pass
that thins direct secondary spheres while preserving the S180 soft mist and
streak passes.

## Inputs

- Baseline shot: `build/shots/s180_secondary_mist_debeading`
- Source sequence:
  `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar:
  `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- New preset: `dam_break_secondary_direct_visibility_gate`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s183_secondary_direct_gate_dry --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_secondary_direct_visibility_gate --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s183_secondary_direct_gate_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_secondary_direct_visibility_gate --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s183_secondary_direct_visibility_gate\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_secondary_direct_visibility_gate --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s183_secondary_direct_visibility_gate\blender\frames build\shots\s183_secondary_direct_visibility_gate\shot.gif --fps 12.0
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s180_secondary_mist_debeading\blender\frames --right build\shots\s183_secondary_direct_visibility_gate\blender\frames --left-label S180 --right-label S183 --out-dir build\shots\s183_secondary_direct_visibility_gate\comparison --summary-left build\shots\s180_secondary_mist_debeading\blender\bridge_summary.json --summary-right build\shots\s183_secondary_direct_visibility_gate\blender\bridge_summary.json --report docs\reports\cinematic_secondary_direct_visibility_gate_comparison_s183.md --title "S183 Secondary Direct Visibility Gate Comparison" --finding "S183 keeps S180 soft mist/streak visibility while thinning direct secondary spheres. The diff is concentrated around direct secondary particles, with water-surface and exposure stable." --next "Package or publish S183 if visual review confirms direct bead density is reduced without losing secondary readability; otherwise tune per-channel keep ratios upward."
```

## Artifacts

- Bridge summary:
  `build/shots/s183_secondary_direct_visibility_gate/blender/bridge_summary.json`
- Render frames: `build/shots/s183_secondary_direct_visibility_gate/blender/frames`
- GIF: `build/shots/s183_secondary_direct_visibility_gate/shot.gif`
- Comparison sheet:
  `build/shots/s183_secondary_direct_visibility_gate/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_comparison_s183.md`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: min `80.06622612847222`, mean `83.29766405647183`, max `93.61925564236111`
- Bright ratio: min `0.00002387152777777778`, mean `0.00023549021026234569`, max `0.0006694878472222223`
- Highlight ratio: min `0.000006510416666666667`, mean `0.0001398533950617284`, max `0.0004242621527777778`

S180 comparison deltas:

- Mean luminance delta: `-0.04208423755787294`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.00000015070408950615725`
- Mean highlight ratio delta: `0.00000006028163580248458`
- Mean nonblank ratio delta: `0.0`

Direct secondary gate:

- Enabled: `true`
- Direct max count scale: `0.82`
- Keep ratios: droplet `0.55`, spray `0.42`, foam `0.62`, bubble `0.35`

## Visual Read

The direct tan/gold secondary spheres are visibly reduced compared with S180,
while the soft spray/foam mist, streaks, water surface, and exposure remain
stable. The comparison diff is localized around direct secondary particles.

## Next

S184 should publish an updated gallery for public review. If the public view
confirms the direct particle density is acceptable, the next visual pass should
move from secondary de-beading to water surface continuity and surface
reconstruction artifacts.
