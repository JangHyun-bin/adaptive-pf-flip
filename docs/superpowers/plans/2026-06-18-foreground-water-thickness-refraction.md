# S148 Foreground Water Thickness Refraction

## Objective

Reduce the broad thin-slab read in the S145 foreground water body by adding stronger near-field depth, volume, and refraction-style cues while preserving the S145 timing, camera, secondary readability, and gate thresholds.

## Inputs

- Baseline preset: `dam_break_foreground_surface_detail_foam`
- Baseline review manifest: `build/shots/s145_foreground_surface_detail_foam/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s147.md`

## Scope

- Add an inherited preset, tentatively `dam_break_foreground_water_thickness_refraction`.
- Keep S145 source window, simulation scene, camera path, and gate set.
- Tune renderer-only controls for foreground water volume/scattering, depth/rim response, broad reflection softness, and subtle refractive layering.
- Run a 36-frame Blender gate against S145.

## Non-Goals

- Do not change sparse 3D simulation physics.
- Do not add more secondary brightness as the primary fix.
- Do not publish a new gallery until the S148 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_foreground_water_thickness_refraction --out build\shots\s148_foreground_water_thickness_refraction --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s145_foreground_surface_detail_foam\review\review_manifest.json --report docs\reports\cinematic_foreground_water_thickness_refraction_s148.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S145 is generated.
- The review sheet shows stronger foreground water-body depth/thickness without washing out contact ripples or spray/foam.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
