# S191 Water Mesh Smoothing

Date: 2026-06-19

## Status

Passed.

S191 adds `dam_break_water_mesh_smoothing`, a bounded renderer-side mesh
smoothing pass for imported water OBJ meshes. It keeps the accepted S186 overlay
density and applies a low-strength Blender Smooth modifier to soften structural
water sheet seams.

## Inputs

- Baseline shot: `build/shots/s186_water_surface_continuity_stabilized`
- Source sequence:
  `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar:
  `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- New preset: `dam_break_water_mesh_smoothing`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s191_water_mesh_smoothing_dry --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s191_water_mesh_smoothing_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s191_water_mesh_smoothing\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s191_water_mesh_smoothing\blender\frames build\shots\s191_water_mesh_smoothing\shot.gif --fps 12.0
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s186_water_surface_continuity_stabilized\blender\frames --right build\shots\s191_water_mesh_smoothing\blender\frames --left-label S186 --right-label S191 --out-dir build\shots\s191_water_mesh_smoothing\comparison --summary-left build\shots\s186_water_surface_continuity_stabilized\blender\bridge_summary.json --summary-right build\shots\s191_water_mesh_smoothing\blender\bridge_summary.json --report docs\reports\cinematic_water_mesh_smoothing_comparison_s191.md --title "S191 Water Mesh Smoothing Comparison" --finding "S191 keeps S186 surface overlay density while applying a bounded Smooth modifier to imported water meshes. The diff is concentrated on water body shading and seam softness, with secondary readability and nonblank coverage preserved." --next "Publish or triage S191 if visual review confirms the mesh seams are softer without washing out the water body; otherwise reduce smoothing factor or iterations."
```

## Artifacts

- Bridge summary: `build/shots/s191_water_mesh_smoothing/blender/bridge_summary.json`
- Render frames: `build/shots/s191_water_mesh_smoothing/blender/frames`
- GIF: `build/shots/s191_water_mesh_smoothing/shot.gif`
- Comparison sheet:
  `build/shots/s191_water_mesh_smoothing/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_comparison_s191.md`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `186`
- Mean luminance: min `77.64534396701389`, mean `80.94749951774692`, max `91.58619683159722`
- Bright ratio: min `0.000009765625`, mean `0.00015896267361111113`, max `0.0005240885416666666`
- Highlight ratio: min `0.000006510416666666667`, mean `0.00010582441165123457`, max `0.0003689236111111111`

S186 comparison deltas:

- Mean luminance delta: `-0.6907726598668944`
- Minimum contrast delta: `5.0`
- Mean bright ratio delta: `0.000002290702160493845`
- Mean highlight ratio delta: `0.000008921682098765428`
- Mean nonblank ratio delta: `0.0`

Water mesh smoothing pass:

- Enabled: `true`
- Shade smooth: `true`
- Smooth factor: `0.075`
- Smooth iterations: `2`

## Visual Read

S191 keeps the S186 surface overlay balance while slightly softening water body
shading and visible mesh seams. The change is small, bounded, and does not erase
secondary particle readability.

## Next

S192 should publish the S191 gallery for public review. If accepted, the next
structural pass should decide between stronger reconstruction/export smoothing
and renderer-side volume occlusion for the worst continuity frames.
