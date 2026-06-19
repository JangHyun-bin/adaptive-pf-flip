# S198 Water Mesh Quality Diagnostics

## Goal

Move beyond renderer-side smoothing by measuring the exported water
reconstruction meshes directly.

## Scope

- Add an OBJ-level water mesh quality diagnostic tool.
- Read `water_reconstruction.json` and all referenced OBJ meshes.
- Measure topology and continuity indicators:
  - vertex, face, normal, and occupied-cell counts
  - connected components and largest-component ratio
  - boundary, non-manifold, and degenerate face ratios
  - shared-edge normal discontinuity
  - edge-length and face-area variation
  - bounded mesh-quality risk score
- Emit CSV, JSON, and Markdown outputs.

## Command

```powershell
python tools\analyze_water_mesh_quality.py build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json --out-dir build\shots\s198_water_mesh_quality_diagnostics --report docs\reports\cinematic_water_mesh_quality_diagnostics_s198.md --title "S198 Water Mesh Quality Diagnostics" --next "Use these OBJ-level topology and normal-continuity metrics to choose the next reconstruction/export smoothing pass. Prefer export-side normal/gradient continuity over stronger renderer smoothing unless the worst-frame topology metrics are clean."
```

## Result

The diagnostic completed with `warning` status because the single dominant
component gate failed.

- Frames: `36`
- Degenerate face ratio: `0` across all frames
- Boundary edge ratio: `0` across all frames
- Non-manifold edge ratio: `0` across all frames
- Worst mesh-quality score: `0.17807311796838227`
- Worst largest-component ratio: `0.7677932405566601`
- Worst frames: early source frames `0` through `6`

The mesh topology is closed and valid, but early frames contain two substantial
water components. That explains why stronger renderer smoothing gave little
visual benefit: the remaining issue is component/island structure in exported
surface data, not just final material smoothing.

## Artifacts

- Tool: `tools/analyze_water_mesh_quality.py`
- Report: `docs/reports/cinematic_water_mesh_quality_diagnostics_s198.md`
- CSV:
  `build/shots/s198_water_mesh_quality_diagnostics/water_mesh_quality_profile.csv`
- JSON:
  `build/shots/s198_water_mesh_quality_diagnostics/water_mesh_quality_summary.json`

## Verification

- `python -m py_compile tools\analyze_water_mesh_quality.py`
- `python tools\analyze_water_mesh_quality.py ...`
- `git diff --check`

## Next

S199 should add reconstruction component metadata and an optional small-island
filter/labeling path. Keep it diagnostic-first: expose per-component face and
volume-ish size before deciding whether to prune, fade, or render islands
differently.
