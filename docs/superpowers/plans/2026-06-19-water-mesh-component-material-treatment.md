# S204 Water Mesh Component Material Treatment

## Goal

Preserve the visible secondary water mesh component while testing whether a
softer component-specific water material improves readability better than
deleting the component.

## Scope

- Add an opt-in `water_mesh_component_material_pass` renderer config.
- Add a `dam_break_water_component_material_probe` preset.
- Detect connected polygon components in imported water OBJ meshes inside the
  generated Blender driver.
- Assign a secondary water material to components below a face-ratio threshold.
- Render the early component-visible window and compare it against S202
  original frames.
- Reuse the component overlay diagnostic on the treated render.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s204_component_material_probe_dry --frames 2 --width 320 --height 180 --samples 4 --render-preset dam_break_water_component_material_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 2 --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s204_component_material_probe\treated --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_component_material_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 8 --timeout-seconds 900
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s202_island_filter_early_probe\original\frames --right build\shots\s204_component_material_probe\treated\frames --left-label S202-original --right-label S204-treated --summary-left build\shots\s202_island_filter_early_probe\original\bridge_summary.json --summary-right build\shots\s204_component_material_probe\treated\bridge_summary.json --out-dir build\shots\s204_component_material_probe\comparison --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_mesh_component_material_comparison_s204.md --title "S204 Component Material Treatment Comparison" --finding "S204 preserves the visible secondary water component but assigns sub-threshold mesh components a softer/deeper water material instead of pruning them." --next "Accept no baseline change unless the component remains readable as water while reducing the dark back-mass read; otherwise tune alpha/material or keep labels only."
```

```powershell
python tools\build_water_mesh_component_overlay.py build\shots\s204_component_material_probe\treated\blender_scene_spec.json build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json --out-dir build\shots\s204_component_material_probe\overlay --filter-threshold 0.24 --thumb-width 520 --max-points 800 --report docs\reports\cinematic_water_mesh_component_material_overlay_s204.md --title "S204 Component Material Overlay"
```

## Result

S204 passed as an opt-in diagnostic/treatment, but it should not replace the
S191 accepted cinematic baseline.

- Mean luminance delta: `0.6512272135416737`
- Minimum contrast delta: `-2.0`
- Mean changed ratio: `0.000341796875`
- Max changed ratio: `0.0010546875`
- Strong changed ratio mean: `0.0`
- Nonblank ratio delta: `0.0`
- Visible would-filter components: `7`

The pass is safer than pruning because it preserves component 2 as visible
water, but the visual delta is too small and the minimum contrast regresses
slightly. Keep it available for targeted component treatment only.

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\render_bridge_blender.py`
- `python -m py_compile build\shots\s204_component_material_probe_dry\blender_driver.py`
- S204 treated Blender render, 8 frames at 640x360, 8 samples
- S204 frame comparison report
- S204 component overlay report
- `git diff --check`

## Next

S205 should move toward exported surface-quality data rather than component
deletion. Candidate work: water mesh normal/continuity metadata, depth/phase
surface attributes, or a no-regression gate that proves component treatment is
inactive on the accepted S191 source window before investing further in
component-specific materials.
