# S180 Secondary Mist De-Beading Gate

Date: 2026-06-19

## Status

Passed.

S180 adds `dam_break_secondary_mist_debeading`, a preset-only pass that keeps
S177 surface reflection breakup while reducing the tan/gold bead-like direct
secondary particle read.

## Inputs

- Baseline shot: `build/shots/s177_surface_reflection_breakup`
- Source sequence: `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar:
  `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- New preset: `dam_break_secondary_mist_debeading`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s180_secondary_mist_debeading_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_secondary_mist_debeading --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s180_secondary_mist_debeading\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_secondary_mist_debeading --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s180_secondary_mist_debeading\blender\frames build\shots\s180_secondary_mist_debeading\shot.gif --fps 12.0
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s177_surface_reflection_breakup\blender\frames --right build\shots\s180_secondary_mist_debeading\blender\frames --left-label S177 --right-label S180 --out-dir build\shots\s180_secondary_mist_debeading\comparison --summary-left build\shots\s177_surface_reflection_breakup\blender\bridge_summary.json --summary-right build\shots\s180_secondary_mist_debeading\blender\bridge_summary.json --report docs\reports\cinematic_secondary_mist_debeading_comparison_s180.md --title "S180 Secondary Mist De-Beading Comparison" --finding "S180 keeps the S177 water surface and strip breakup while reducing the tan bead-like read of direct secondary particles. The diff is concentrated around secondary particles and mist, with nonblank coverage unchanged and contrast preserved." --next "Package or publish S180 if visual review confirms the secondary de-beading remains readable; otherwise tune direct secondary alpha/radius upward slightly."
```

## Artifacts

- Bridge summary: `build/shots/s180_secondary_mist_debeading/blender/bridge_summary.json`
- Render frames: `build/shots/s180_secondary_mist_debeading/blender/frames`
- GIF: `build/shots/s180_secondary_mist_debeading/shot.gif`
- Comparison sheet:
  `build/shots/s180_secondary_mist_debeading/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_secondary_mist_debeading_comparison_s180.md`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: min `80.10749240451389`, mean `83.3397482940297`, max `93.62858940972222`
- Bright ratio: min `0.000024956597222222224`, mean `0.00023533950617283953`, max `0.0006684027777777777`
- Highlight ratio: min `0.000006510416666666667`, mean `0.00013979311342592591`, max `0.00042317708333333335`

S177 comparison deltas:

- Mean luminance delta: `-0.38854730299962625`
- Minimum contrast delta: `0.0`
- Mean bright ratio delta: `0.000003315489969135839`
- Mean highlight ratio delta: `0.00000464168595679012`
- Mean nonblank ratio delta: `0.0`

## Visual Read

The direct secondary particles are slightly smaller and cooler while the soft
mist/foam contribution remains visible. The comparison diff is concentrated in
secondary particle regions, not global exposure or camera framing.

## Next

S181 should package/publish S180 for public review and decide whether the
de-beading amount is sufficient or needs a small visibility rebound.
