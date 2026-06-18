# S142 Impact-Timed Review Window

## Objective

Add a cinematic render-window control so a shot can render a later portion of an exported cache. Use it to remove the long calm-pool lead-in from S139 while keeping the same source-breakup simulation and low-angle impact framing.

## Inputs

- Baseline preset: `dam_break_low_angle_impact_closeup`
- Baseline review manifest: `build/shots/s139_low_angle_impact_closeup/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s141.md`

## Scope

- Add render-window support to `tools/render_bridge_blender.py`.
- Thread the option through `tools/run_cinematic_shot.py` via preset config so normal CLI usage stays simple.
- Add an inherited preset, tentatively `dam_break_low_angle_impact_timed`, with a later render window.
- Run a 36-frame Blender gate against S139.
- Keep visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates active.

## Non-Goals

- Do not change the simulation/export cache schema.
- Do not delete early cache frames; the window is render-time selection only.
- Do not publish a new gallery until the S142 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_low_angle_impact_timed --out build\shots\s142_impact_timed_window --frames 36 --sim-steps 48 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s139_low_angle_impact_closeup\review\review_manifest.json --report docs\reports\cinematic_impact_timed_window_s142.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- The render summary records the selected source-frame window.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S139 is generated.
- Review/contact sheets start closer to visible impact than S139.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python tools\render_bridge_blender.py build\shots\s139_low_angle_impact_closeup\converted\sequence.json build\s142_window_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_low_angle_impact_timed --preset-config configs\cinematic_presets.json
git diff --check
```
