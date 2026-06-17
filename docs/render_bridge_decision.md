# Render Bridge Decision

## S41 Water Representation Choice

Decision: use OBJ mesh reconstruction first.

Why:

- Current render caches provide sparse phase cells and particle channels, not a dense signed-distance volume.
- OBJ mesh assets can be generated with Python standard library only.
- OBJ is easy to inspect and is directly importable by Blender, which keeps S42 external-renderer bridge work pragmatic.
- Volume/OpenVDB output remains a later option if mesh flicker or spray-heavy density becomes the limiting factor.

S41 validation commands:

```powershell
python tools\reconstruct_water.py build\s40_sparse_manifest.json build\s41_water_mesh --frames 8 --threshold 0.02
python tools\cinematic_render_stub.py build\s40_sparse_manifest.json build\s41_cinematic_mesh --frames 8 --width 640 --height 360 --water-reconstruction build\s41_water_mesh\water_reconstruction.json
```

Next S42 bridge preference:

- Try Blender first because it can consume OBJ meshes and particle CSV/JSON data from the existing S38/S41 bundles without native build dependencies.
- Revisit USD/OpenVDB only after measuring whether OBJ mesh flicker or volumetric spray fidelity blocks the first cinematic shot.
