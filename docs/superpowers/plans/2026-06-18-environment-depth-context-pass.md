# S130 Environment Depth Context Pass

## Objective

Reduce the visible side-wall/enclosure bands in the S127 non-boxed falling-water shot and add stronger large-scale depth context without regressing the S127 visual/review gates.

## Inputs

- Baseline preset: `dam_break_nonboxed_falling_water`
- Baseline review manifest: `build/shots/s127_nonboxed_falling_water/review/review_manifest.json`
- Baseline public gallery: `https://fields-diary-motivated-record.trycloudflare.com`
- Triage report: `docs/reports/cinematic_visual_review_s129.md`

## Scope

- Add an inherited cinematic preset, tentatively `dam_break_environment_depth_context`.
- Preserve the `nonboxed-water-event` scene and S127 physics/export settings.
- Soften or reduce visible side/background enclosure bands in the Blender render path.
- Add subtle depth context through camera, floor/world, haze, or background treatment.
- Keep the existing contact, focus, secondary-depth, ripple, temporal, and secondary-framing gates active.

## Non-Goals

- Do not change sparse 3D two-phase solver behavior in this milestone.
- Do not replace the current water reconstruction or secondary-particle render stack.
- Do not make a new public gallery until the S130 render gate passes locally.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_environment_depth_context --out build\shots\s130_environment_depth_context --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s127_nonboxed_falling_water\review\review_manifest.json --report docs\reports\cinematic_environment_depth_context_s130.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- All S127 review gates remain passing.
- `docs/reports/cinematic_environment_depth_context_s130.md` records the preset changes, measured metrics, and visual limitations.
- The comparison sheet against S127 is generated for direct inspection.

## Result

- Preset: `dam_break_environment_depth_context`
- Shot output: `build/shots/s130_environment_depth_context`
- Report: `docs/reports/cinematic_environment_depth_context_s130.md`
- Status: `ok`
- Frames: `36`
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates passed.
- Visual note: floor/world/mist treatment is softer than S127, but late frames still read as a contained vertical water mass.

## Verification

```powershell
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
