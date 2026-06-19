# S205 Water Mesh Surface Quality Annotation

## Goal

Move the cinematic water-mesh work from geometry deletion/material guesses
toward exported surface-quality metadata that downstream render passes can use.

## Scope

- Add `tools/annotate_water_mesh_surface_quality.py`.
- Reuse OBJ quality metrics from `tools/analyze_water_mesh_quality.py`.
- Write an annotated `water_reconstruction.json` copy with per-frame
  `surface_quality` metadata.
- Preserve mesh geometry and rebase mesh paths when the annotated copy is
  written outside the original reconstruction directory.
- Pass annotated per-frame quality into converted sequence frames as
  `water_mesh_surface_quality`.
- Pass reconstruction-level annotation summary through
  `sequence["water_reconstruction"]["surface_quality_annotation"]`.

## Commands

```powershell
python tools\annotate_water_mesh_surface_quality.py build\shots\s168_water_depth_foreground_separation\water_mesh\water_reconstruction.json --out build\shots\s205_surface_quality_annotation\water_reconstruction.json --out-dir build\shots\s205_surface_quality_annotation --report docs\reports\cinematic_water_mesh_surface_quality_annotation_s205.md --title "S205 Water Mesh Surface Quality Annotation" --next "Feed the annotated reconstruction through convert_render_cache so downstream render frames carry water_mesh_surface_quality metadata for surface treatment, no-op gates, and future normal/continuity shading."
```

```powershell
python tools\convert_render_cache.py build\shots\s168_water_depth_foreground_separation\cache\manifest.json build\shots\s205_surface_quality_annotation\converted --require-cinematic --water-reconstruction build\shots\s205_surface_quality_annotation\water_reconstruction.json
```

## Result

S205 passed.

- Annotated reconstruction frames: `36`
- Annotation label counts:
  `{'component_fragmented': 5, 'normal_rough': 3, 'stable': 28}`
- Converted render frames: `56`
- Converted frames missing `water_mesh_surface_quality`: `0`
- Converted frame label counts:
  `{'component_fragmented': 8, 'normal_rough': 4, 'stable': 44}`

The annotation is a metadata-only pass. It does not change OBJ mesh geometry,
but it gives later render/export stages frame-local signals for fragmented
components, rough normals, and stable surface frames.

## Verification

- `python -m py_compile tools\annotate_water_mesh_surface_quality.py tools\convert_render_cache.py`
- `python tools\annotate_water_mesh_surface_quality.py --help`
- S205 annotation probe on S168 water reconstruction
- S205 conversion probe with annotated reconstruction
- Python JSON inspection confirming no converted frame is missing
  `water_mesh_surface_quality`
- `git diff --check`

## Next

S206 should use `water_mesh_surface_quality` in a renderer no-op/QA gate first:
prove the accepted S191 source window is mostly stable, then selectively attach
normal/continuity shading or component material treatment only on labeled frames.
