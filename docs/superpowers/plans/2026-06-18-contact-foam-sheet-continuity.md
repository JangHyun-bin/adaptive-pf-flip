# S157 Contact Foam Sheet Continuity

## Objective

Make S154 contact foam read more like connected surface foam/wake around the impact region instead of isolated small patches, while preserving secondary mist integration, source-edge framing, foreground water thickness, and all existing cinematic gates.

## Inputs

- Baseline preset: `dam_break_secondary_mist_integrated`
- Baseline review manifest: `build/shots/s154_secondary_mist_integration/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s156.md`

## Scope

- Add an inherited preset, tentatively `dam_break_contact_foam_sheet_continuity`.
- Broaden and slightly increase flow-aligned contact foam strokes around the impact region.
- Keep S154 secondary mist scale/material tuning and S151 source-window framing.
- Run a 36-frame Blender gate against S154.

## Non-Goals

- Do not change sparse 3D simulation physics.
- Do not add a new foam solver or particle classifier.
- Do not publish a new gallery until the S157 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_contact_foam_sheet_continuity --out build\shots\s157_contact_foam_sheet_continuity --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s154_secondary_mist_integration\review\review_manifest.json --report docs\reports\cinematic_contact_foam_sheet_continuity_s157.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S154 is generated.
- Review sheets show more continuous contact foam/wake without overpowering ripples or spray/foam mist.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
