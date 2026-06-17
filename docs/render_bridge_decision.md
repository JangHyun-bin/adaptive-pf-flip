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

## S42 External Renderer Bridge Choice

Decision: implement Blender first.

Why:

- The S38 converted bundle already writes camera JSON and particle CSV files.
- The S41 reconstruction index already writes OBJ water meshes.
- Blender can import OBJ meshes and render PNG frames from a generated Python driver without adding native dependencies to the LSFS C++ build.
- The bridge can be validated in two modes: dependency/dry-run checks without Blender, and renderer-backed frame generation when Blender is installed.

Bridge commands:

```powershell
python tools\render_bridge_blender.py --check
python tools\render_bridge_blender.py build\s41_convert_with_mesh\sequence.json build\s42_blender --frames 8 --width 640 --height 360
python tools\render_bridge_blender.py build\s41_convert_with_mesh\sequence.json build\s42_blender_dry --frames 8 --dry-run
```

S42 gate:

- `bridge_summary.json` must report `status=rendered` for renderer-backed runs.
- The generated scene spec must reference positive-face-count OBJ water meshes for every output frame.
- Rendered PNG frames must exist, be nonblank, and have positive luminance contrast.
- If Blender is not installed or not discoverable, the bridge writes a summary with `status=missing_dependency` instead of failing ambiguously.
