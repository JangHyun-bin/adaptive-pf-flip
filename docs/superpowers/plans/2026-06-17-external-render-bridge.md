# S42 External Renderer Bridge

**Goal:** Produce the first external-renderer-backed cinematic PNG sequence from LSFS converted cache assets.

**Architecture:** Keep Blender as an optional bridge outside the C++ build. `tools/render_bridge_blender.py` reads an S38 `sequence.json` bundle, resolves S41 OBJ water meshes, writes a renderer-neutral `blender_scene_spec.json`, generates a Blender Python driver under the output directory, then runs Blender in background mode when a Blender executable is available. The same command supports `--check` and `--dry-run` so CI and developer machines without Blender still get deterministic validation.

**Renderer choice:** Blender first. S38 already emits camera JSON and particle CSV files, and S41 already emits OBJ water meshes. USD/OpenVDB remains a later bridge if mesh flicker or volumetric spray fidelity blocks the cinematic target.

## Files

- Create `tools/render_bridge_blender.py`
- Modify `tools/convert_render_cache.py`
- Modify `README.md`
- Modify `docs/render_bridge_decision.md`
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`

## Implementation Checklist

- [ ] Add Blender dependency discovery from PATH and standard Windows install paths.
- [ ] Add `--check` to print a dependency report without requiring source assets.
- [ ] Add `--dry-run` to generate `blender_scene_spec.json`, `blender_driver.py`, and `bridge_summary.json` without launching Blender.
- [ ] Consume S38 `sequence.json` camera/particle assets and S41 `water_reconstruction.json` OBJ meshes.
- [ ] Generate a Blender driver that imports water OBJ meshes, instantiates bounded secondary particles, sets camera/lights/materials, and renders PNG frames.
- [ ] Validate rendered frames for existence, nonblank pixels, and positive luminance contrast.
- [ ] Record `bridge_summary.json` with dependency info, command paths, frame count, mesh stats, and render stats.
- [ ] Document commands and mark S42 done.

## Validation Commands

```powershell
python -m py_compile tools\render_bridge_blender.py tools\convert_render_cache.py
python tools\render_bridge_blender.py --check
python tools\convert_render_cache.py build\s40_sparse_manifest.json build\s42_convert_with_mesh --require-cinematic --water-reconstruction build\s41_water_mesh\water_reconstruction.json
python tools\render_bridge_blender.py build\s42_convert_with_mesh\sequence.json build\s42_blender_dry --frames 8 --width 320 --height 180 --dry-run
python tools\render_bridge_blender.py build\s42_convert_with_mesh\sequence.json build\s42_blender --frames 8 --width 320 --height 180 --samples 8 --timeout-seconds 240
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Acceptance Gate

- One command writes at least 8 renderer-backed PNG frames when Blender is installed.
- Frames are nonblank and camera framing is stable enough for inspection.
- `--check` reports the selected Blender executable or a clear missing-dependency result.
- `--dry-run` works without Blender.
- Missing Blender produces a clear `status=missing_dependency` summary instead of an ambiguous traceback.
- No slow external render is added to default `ctest`.

## Commit

```powershell
git add README.md tools\render_bridge_blender.py tools\convert_render_cache.py docs\render_bridge_decision.md docs\superpowers\plans\2026-06-17-external-render-bridge.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add external render bridge"
git push origin main
```
