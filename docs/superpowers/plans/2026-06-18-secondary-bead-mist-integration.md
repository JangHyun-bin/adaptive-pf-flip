# S154 Secondary Bead Mist Integration

## Objective

Make S151 secondaries read less like bead-like debug particles and more like integrated spray/foam/mist while preserving the source-edge cleanup framing, foreground water thickness, and all existing cinematic gates.

## Inputs

- Baseline preset: `dam_break_source_edge_cleanup_framing`
- Baseline review manifest: `build/shots/s151_source_edge_cleanup_framing/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s153.md`

## Scope

- Add an inherited preset, tentatively `dam_break_secondary_mist_integrated`.
- Reduce direct secondary bead radius/brightness where possible through existing channel radius/material controls.
- Strengthen soft mist and velocity streak integration for spray/foam enough to read as motion and breakup, without washing out the water surface.
- Run a 36-frame Blender gate against S151.

## Non-Goals

- Do not change sparse 3D simulation physics in this pass.
- Do not add a new particle classification model.
- Do not publish a new gallery until the S154 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_secondary_mist_integrated --out build\shots\s154_secondary_mist_integration --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s151_source_edge_cleanup_framing\review\review_manifest.json --report docs\reports\cinematic_secondary_mist_integration_s154.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S151 is generated.
- Review sheets show less bead-like secondary read without losing the contact spray/foam band.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
