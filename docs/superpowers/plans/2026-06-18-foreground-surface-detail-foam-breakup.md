# S145 Foreground Surface Detail Foam Breakup

## Objective

Improve the S142 close-up look-dev without changing timing or camera framing: make the foreground water surface, contact foam, glints, and ripples read less smooth/coarse at the current close camera distance.

## Inputs

- Baseline preset: `dam_break_low_angle_impact_timed`
- Baseline review manifest: `build/shots/s142_impact_timed_window/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s144.md`

## Scope

- Add an inherited preset, tentatively `dam_break_foreground_surface_detail_foam`.
- Preserve S142 source window, simulation scene, camera path, and gates.
- Tune renderer-only controls for water surface detail, glint/reflection visibility, ripple readability, and contact foam breakup.
- Run a 36-frame Blender gate against S142.

## Non-Goals

- Do not change the sparse 3D simulation or source-window feature.
- Do not publish a new gallery until the S145 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_foreground_surface_detail_foam --out build\shots\s145_foreground_surface_detail_foam --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s142_impact_timed_window\review\review_manifest.json --report docs\reports\cinematic_foreground_surface_detail_foam_s145.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S142 is generated.
- Review sheets show stronger foreground surface/foam readability without overbright highlights.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
