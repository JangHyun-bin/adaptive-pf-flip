# Implicit Tetra Water Surface

## Goal

Reduce the visible voxel stair stepping in cinematic water surfaces without adding native dependencies.

## Approach

- Preserve the existing exposed-voxel OBJ exporter as `--surface-mode voxel`.
- Add opt-in `--surface-mode tetra`:
  - Build a scalar grid from neighboring occupied phase cells.
  - Optionally blur the scalar grid.
  - Extract an isosurface with marching tetrahedra.
  - Write triangle OBJ faces and vertex normals through the existing OBJ path.
- Enable tetra mode for `dam_break_cinematic`; keep `bubble_cinematic` on voxel mode for compatibility.

## Validation

```powershell
python -m py_compile tools\reconstruct_water.py tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json > $null
python tools\reconstruct_water.py build\shots\s52_visual_gate_v2\cache\manifest.json build\s53_tetra_mesh_smoke --frames 4 --threshold 0.02 --surface-mode tetra --implicit-iso 0.45 --implicit-blur-iterations 1 --smooth-iterations 3 --smooth-alpha 0.16 --write-normals
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s53_surface_tetra --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --review-frames 6 --report docs\reports\cinematic_gate_s53.md --no-build --timeout-seconds 600
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

The S53 contact sheet shows a visibly rounded water silhouette compared with the previous box-like voxel surface. The remaining quality limit is the low sparse phase-cell resolution, not the material or renderer path.

## Next

S54 should raise visual detail through higher-resolution/adaptive surface data and begin replacing demo secondary seeding with physical spray generation.
