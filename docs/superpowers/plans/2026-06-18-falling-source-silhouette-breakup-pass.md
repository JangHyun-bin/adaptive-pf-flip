# S133 Falling Source Silhouette Breakup Pass

## Objective

Reduce the contained late-frame read by breaking the upper falling-water mass into staggered rounded lobes with less continuous vertical side-wall structure.

## Inputs

- Baseline preset: `dam_break_environment_depth_context`
- Baseline review manifest: `build/shots/s130_environment_depth_context/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s132.md`

## Scope

- Add a scene or preset path, tentatively `dam_break_falling_source_silhouette_breakup`.
- Preserve the S130 render stack and QA gates.
- Change the non-boxed falling-water source shape itself rather than only changing world, floor, or haze treatment.
- Prefer staggered rounded lobes, tapered edges, and reduced continuous side columns over another rectangular sheet.

## Non-Goals

- Do not change pressure solver behavior.
- Do not add a new default `ctest` long render.
- Do not publish a gallery until the S133 gate passes.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_falling_source_silhouette_breakup --out build\shots\s133_falling_source_silhouette_breakup --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s130_environment_depth_context\review\review_manifest.json --report docs\reports\cinematic_falling_source_silhouette_breakup_s133.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S130 is generated.
- Report records whether the continuous upper-source side-wall read is reduced and what remains.

## Result

- Scene: `source-breakup-water-event`
- Preset: `dam_break_falling_source_silhouette_breakup`
- Shot output: `build/shots/s133_falling_source_silhouette_breakup`
- Report: `docs/reports/cinematic_falling_source_silhouette_breakup_s133.md`
- Status: `ok`
- Frames: `36`
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates passed.
- Visual note: the upper source is no longer a single flat slab, but late frames still form a large contained water mass.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
