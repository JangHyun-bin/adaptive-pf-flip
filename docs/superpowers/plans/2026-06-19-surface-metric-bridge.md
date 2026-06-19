# S190 Surface Metric Bridge

Date: 2026-06-19

## Goal

Make reconstruction/export metrics available to bridge summaries so surface
continuity diagnostics do not lose occupied-cell data.

## Scope

- Preserve `water_mesh_occupied_cell_count` in converted sequence frames.
- Include occupied-cell count in render-data sidecar frames and summary stats.
- Carry vertex and occupied-cell counts into Blender `bridge_summary.json`
  frame entries.
- Let `tools/analyze_surface_continuity.py` generate milestone-specific report
  titles and next recommendations.

## Implementation

- `tools/convert_render_cache.py`
  - Adds `water_mesh_occupied_cell_count` to converted frame records when water
    reconstruction data is available.
- `tools/export_render_data_summary.py`
  - Adds `water_mesh_occupied_cell_count` to frame rows and summary stats.
  - Includes occupied-cell count in the Markdown export report.
- `tools/render_bridge_blender.py`
  - Preserves occupied-cell counts from compact render-data sidecars.
  - Includes water mesh vertex and occupied-cell counts in bridge summary frame
    records.
- `tools/analyze_surface_continuity.py`
  - Adds `--title` and `--next` report overrides.

## Validation

```powershell
python -m py_compile tools\analyze_surface_continuity.py tools\convert_render_cache.py tools\export_render_data_summary.py tools\render_bridge_blender.py
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s190_surface_metric_bridge_dry --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_surface_continuity_stabilized --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --dry-run
```

```powershell
python tools\analyze_surface_continuity.py build\s190_surface_metric_bridge_dry\bridge_summary.json --out-dir build\shots\s190_surface_metric_bridge_diagnostics --report docs\reports\cinematic_surface_metric_bridge_s190.md --title "S190 Surface Metric Bridge Diagnostics" --next "S191 should use the now-complete mesh face, vertex, occupied-cell, and depth metrics to choose a bounded mesh-smoothing or renderer-side volume-occlusion pass for the worst continuity frames."
```

## Result

S190 passed:

- Frames analyzed: `8`
- Occupied-cell count trend: count `8`, min `5221`, mean `5393.75`, max
  `5663`, delta `279`
- Analyzer warnings: `[]`
- New report: `docs/reports/cinematic_surface_metric_bridge_s190.md`

## Follow-Up

S191 should use the complete metric set to choose and implement a bounded
mesh-smoothing or renderer-side water-volume occlusion pass for the worst
continuity frames.
