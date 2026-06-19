# S160 Large Event Cinematic Scale Gate

## Objective

Move beyond same-shot renderer-side look-dev by piloting a larger physical event with the S157 render stack, then measure whether framing, secondary readability, runtime, and visual gates still hold.

## Inputs

- Baseline preset: `dam_break_contact_foam_sheet_continuity`
- Baseline review manifest: `build/shots/s157_contact_foam_sheet_continuity/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s159.md`

## Scope

- Add an inherited preset, tentatively `dam_break_large_event_scale_gate`.
- Preserve S157 water, mist, foam, ripple, and source-window look where possible.
- Increase event scale in a bounded way: either a modest larger grid/event preset or a longer source window that produces visibly larger motion without uncontrolled runtime.
- Start with dry-run/summary validation before committing to the full 36-frame Blender gate.
- Run a full Blender gate only if dry-run framing and expected cost look sane.

## Non-Goals

- Do not attempt the final gigantic production scene in one jump.
- Do not change solver algorithms during this render-scale gate.
- Do not publish a new gallery until the S160 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Dry Run

```powershell
python tools\render_bridge_blender.py build\shots\s157_contact_foam_sheet_continuity\converted\sequence.json build\s160_large_event_scale_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_large_event_scale_gate --preset-config configs\cinematic_presets.json --max-secondary-particles 512 --secondary-radius-scale 3.0
```

## Candidate Full Gate

```powershell
python tools\run_cinematic_shot.py --preset dam_break_large_event_scale_gate --out build\shots\s160_large_event_scale_gate --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s157_contact_foam_sheet_continuity\review\review_manifest.json --report docs\reports\cinematic_large_event_scale_gate_s160.md --no-build --timeout-seconds 2100
```

## Acceptance Gate

- Dry-run confirms source window, camera stability, and secondary framing before the full run.
- Full gate either passes visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates, or records a measured scale-limit failure.
- Report includes timing, grid/event settings, and direct comparison against S157.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
