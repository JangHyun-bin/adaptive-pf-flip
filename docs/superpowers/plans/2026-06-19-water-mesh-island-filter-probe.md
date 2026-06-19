# S200 Water Mesh Island Filter Probe

## Goal

Check whether reconstruction component filtering produces a visible improvement
over the accepted S191 water mesh smoothing look.

## Scope

- Add `dam_break_water_mesh_island_filter_probe` as a probe preset.
- Reconstruct the S168 water mesh with the same baseline reconstruction options
  plus `--min-component-face-ratio 0.24`.
- Convert the existing S168 render cache with the filtered water mesh.
- Render an 8-frame 640x360 probe using S191 render styling.
- Compare against the existing S191 8-frame probe.

## Commands

```powershell
python tools\reconstruct_water.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s200_island_filter_probe\water_mesh --frames 36 --threshold 0.02 --surface-mode tetra --implicit-iso 0.45 --implicit-blur-iterations 1 --smooth-iterations 3 --smooth-alpha 0.16 --write-normals --component-detail-limit 4 --min-component-face-ratio 0.24
```

```powershell
python tools\convert_render_cache.py build\shots\s168_water_depth_foreground_separation\cache\manifest.json build\shots\s200_island_filter_probe\converted --require-cinematic --water-reconstruction build\shots\s200_island_filter_probe\water_mesh\water_reconstruction.json
```

```powershell
python tools\render_bridge_blender.py build\shots\s200_island_filter_probe\converted\sequence.json build\shots\s200_island_filter_probe\blender --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_mesh_island_filter_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 900
```

## Result

The filter mechanism worked, but the visual probe did not change the rendered
shot.

- Filtered reconstruction component count: `1` for all 36 frames
- Removed faces: `22656`
- Mesh quality status: `ok`
- S191 vs S200 probe changed ratio: `0.0`
- Minimum contrast delta: `0.0`
- Mean nonblank delta: `0.0`

The removed island is not visible in this 8-frame review window, or it has no
observable contribution under the current camera/material stack.

## Artifacts

- Mesh quality report:
  `docs/reports/cinematic_water_mesh_island_filter_quality_s200.md`
- Comparison report:
  `docs/reports/cinematic_water_mesh_island_filter_comparison_s200.md`
- Comparison sheet:
  `build/shots/s200_island_filter_probe/comparison/comparison_sheet.png`

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\reconstruct_water.py tools\run_cinematic_shot.py tools\analyze_water_mesh_quality.py`
- S200 filtered reconstruction run
- S200 converted sequence generation
- S200 Blender probe render
- S191-vs-S200 probe comparison
- visual inspection of `comparison_sheet.png`
- `git diff --check`

## Next

Do not promote the island filter as a baseline. S201 should add component
visibility or labeling diagnostics so we can identify whether removed islands
are offscreen, occluded/internal, or meaningful separated water.
