# S201 Water Mesh Component Visibility Diagnostics

## Goal

Explain why S200's island-filtered reconstruction produced a pixel-identical
render compared with the S191 probe.

## Scope

- Add `tools/analyze_water_mesh_component_visibility.py`.
- Read the final Blender scene spec so source-window and camera-motion choices
  are included.
- Recompute water mesh components from a reference `water_reconstruction.json`.
- Map selected render mesh frames back to reference mesh frames.
- Project component vertices through the final render camera.
- Report whether threshold-filtered components are selected and visible.

## Command

```powershell
python tools\analyze_water_mesh_component_visibility.py build\shots\s200_island_filter_probe\blender\blender_scene_spec.json build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json --out-dir build\shots\s201_component_visibility_diagnostics --filter-threshold 0.24 --report docs\reports\cinematic_water_mesh_component_visibility_s201.md --title "S201 Water Mesh Component Visibility Diagnostics" --next "S200 was pixel-identical because the active render window selected mesh frames without threshold-filtered components. Use an earlier source-window review or component labels before deciding whether island pruning should affect visible shots."
```

## Result

S201 passed.

- Render frames: `8`
- Selected mesh frames: `[13, 16, 19, 22, 26, 29, 32, 35]`
- Would-filter component rows: `0`
- Visible would-filter component rows: `0`
- Selected mesh frames with filtered components: `[]`

S200 was pixel-identical because the active render window did not select any
mesh frames containing components below the `0.24` threshold. The filter changed
the full reconstruction, but not the frames actually rendered in that probe.

## Artifacts

- Tool: `tools/analyze_water_mesh_component_visibility.py`
- Report: `docs/reports/cinematic_water_mesh_component_visibility_s201.md`
- CSV:
  `build/shots/s201_component_visibility_diagnostics/water_mesh_component_visibility.csv`
- JSON:
  `build/shots/s201_component_visibility_diagnostics/water_mesh_component_visibility_summary.json`

## Verification

- `python -m py_compile tools\analyze_water_mesh_component_visibility.py`
- `python tools\analyze_water_mesh_component_visibility.py --help`
- S201 visibility diagnostic command
- `git diff --check`

## Next

S202 should make an earlier-window component-label probe. The active S191/S200
review window starts too late to evaluate island filtering, so the next visual
test needs to target the early mesh frames where the secondary component exists.
