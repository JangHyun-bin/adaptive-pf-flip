# S186 Water Surface Continuity Stabilization

Date: 2026-06-19

## Status

Passed.

S186 adds `dam_break_water_surface_continuity_stabilized`, a bounded render-look
pass that reduces overly dense surface glint, reflection strip, contact foam,
and impact ripple overlays while keeping the S183 secondary visibility gate.

## Inputs

- Baseline shot: `build/shots/s183_secondary_direct_visibility_gate`
- Source sequence:
  `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar:
  `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- New preset: `dam_break_water_surface_continuity_stabilized`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s186_water_surface_continuity_dry --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_surface_continuity_stabilized --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s186_water_surface_continuity_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_surface_continuity_stabilized --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s186_water_surface_continuity_stabilized\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_water_surface_continuity_stabilized --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s186_water_surface_continuity_stabilized\blender\frames build\shots\s186_water_surface_continuity_stabilized\shot.gif --fps 12.0
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s183_secondary_direct_visibility_gate\blender\frames --right build\shots\s186_water_surface_continuity_stabilized\blender\frames --left-label S183 --right-label S186 --out-dir build\shots\s186_water_surface_continuity_stabilized\comparison --summary-left build\shots\s183_secondary_direct_visibility_gate\blender\bridge_summary.json --summary-right build\shots\s186_water_surface_continuity_stabilized\blender\bridge_summary.json --report docs\reports\cinematic_water_surface_continuity_comparison_s186.md --title "S186 Water Surface Continuity Comparison" --finding "S186 keeps S183 secondary visibility while reducing surface glint, reflection strip, contact foam, and impact ripple overlay density. The diff is concentrated on water-surface continuity cues with nonblank coverage preserved." --next "Publish S186 if visual review confirms the surface reads less banded without losing water-body readability; otherwise rebound glint/reflection alpha slightly."
```

## Artifacts

- Bridge summary:
  `build/shots/s186_water_surface_continuity_stabilized/blender/bridge_summary.json`
- Render frames:
  `build/shots/s186_water_surface_continuity_stabilized/blender/frames`
- GIF: `build/shots/s186_water_surface_continuity_stabilized/shot.gif`
- Comparison sheet:
  `build/shots/s186_water_surface_continuity_stabilized/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_water_surface_continuity_comparison_s186.md`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `181`
- Mean luminance: min `78.29256727430555`, mean `81.63827217761381`, max `92.2898828125`
- Bright ratio: min `0.000009765625`, mean `0.0001566719714506173`, max `0.0005750868055555556`
- Highlight ratio: min `0.000006510416666666667`, mean `0.00009690272955246914`, max `0.00033094618055555557`

S183 comparison deltas:

- Mean luminance delta: `-1.6593918788580169`
- Minimum contrast delta: `-4.0`
- Mean bright ratio delta: `-0.0000788182388117284`
- Mean highlight ratio delta: `-0.00004295066550925926`
- Mean nonblank ratio delta: `0.0`

Surface continuity diagnostics:

- Glint configured count: `141`
- Estimated glint strip count: `122.67`
- Estimated glint segment count: `245.34`
- Reflection configured count: `49`
- Estimated reflection strip count: `42.14`
- Estimated reflection segment count: `126.42`
- Surface contact foam mean count: `43.19444444444444`
- Impact ripple mean count: `62.0`
- Water volume scattering layers: `18`

## Visual Read

The S186 comparison diff is concentrated on water-surface overlay cues. Long
reflection strips, dense glint bands, contact foam patches, and impact rings are
less dominant than S183. Secondary particles remain visible, and the water body
is still readable.

## Next

S187 should publish the S186 gallery. If the public view accepts this pass, the
next substantial visual target should move beyond overlay tuning and toward
actual water surface reconstruction continuity.
