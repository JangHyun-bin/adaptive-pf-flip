# S203 Water Mesh Component Overlay

## Goal

Make the visible water mesh components inspectable so the S202 filtered
component can be classified before any pruning threshold is promoted.

## Scope

- Add `tools/build_water_mesh_component_overlay.py`.
- Reuse S201 projection/component logic.
- Draw component bounding boxes, sampled projected vertices, and labels over
  rendered frames.
- Mark components below the candidate filter threshold in red.
- Generate an overlay sheet and Markdown report.

## Command

```powershell
python tools\build_water_mesh_component_overlay.py build\shots\s202_island_filter_early_probe\original\blender_scene_spec.json build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json --out-dir build\shots\s203_component_overlay --filter-threshold 0.24 --thumb-width 520 --max-points 1000 --report docs\reports\cinematic_water_mesh_component_overlay_s203.md --title "S203 Water Mesh Component Overlay"
```

## Result

S203 passed.

- Overlay frames: `8`
- Would-filter components: `7`
- Visible would-filter components: `7`
- Overlay sheet:
  `build/shots/s203_component_overlay/component_overlay_sheet.png`

The red component-2 overlay is a broad visible upper/back water mass, not a
small detached speck. It should not be removed by a face-ratio pruning rule.

## Verification

- `python -m py_compile tools\build_water_mesh_component_overlay.py tools\analyze_water_mesh_component_visibility.py`
- `python tools\build_water_mesh_component_overlay.py ...`
- visual inspection of `component_overlay_sheet.png`
- `git diff --check`

## Next

S204 should move from pruning to component-aware rendering diagnostics. Keep
component 2, but test whether it needs a different depth/material treatment so
the early water mass reads coherently.
