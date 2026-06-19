# S151 Source Edge Cleanup Framing

## Objective

Reduce the visible upper-edge source fragments in the S148 public gallery while preserving the close-up contact region, foreground water thickness/refraction cues, spray/foam readability, and all existing cinematic review gates.

## Inputs

- Baseline preset: `dam_break_foreground_water_thickness_refraction`
- Baseline review manifest: `build/shots/s148_foreground_water_thickness_refraction/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s150.md`

## Scope

- Add an inherited preset, tentatively `dam_break_source_edge_cleanup_framing`.
- Keep S148 water material, volume scattering, reflections, and contact/ripple passes.
- Use camera/source-window tuning to crop or de-emphasize the upper source region.
- Run a 36-frame Blender gate against S148.

## Non-Goals

- Do not change sparse 3D simulation physics.
- Do not remove physically generated secondaries.
- Do not publish a new gallery until the S151 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_source_edge_cleanup_framing --out build\shots\s151_source_edge_cleanup_framing --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s148_foreground_water_thickness_refraction\review\review_manifest.json --report docs\reports\cinematic_source_edge_cleanup_framing_s151.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S148 is generated.
- Early review frames show less upper-source distraction without losing contact-band spray/foam.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
