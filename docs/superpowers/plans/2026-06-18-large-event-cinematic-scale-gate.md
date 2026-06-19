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

## Result

- Status: passed.
- Preset added: `dam_break_large_event_scale_gate`.
- Output: `build/shots/s160_large_event_scale_gate`.
- Report: `docs/reports/cinematic_large_event_scale_gate_s160.md`.
- Grid/steps: `36 x 44 x 28`, `56` simulation steps, `36` rendered frames.
- Secondary physical particles: `256`.
- Validation: `56` cache frames, `16647683` particles, `2482565` phase cells, max volume drift `0.0011012159806506408`.
- Source window: frames `16..55`, `40` selected source frames.
- QA gates: visual, temporal, focus, secondary-depth, secondary-framing, ripple-readability, and camera stability all passed.
- Timing: export `265.23s`, validation `255.78s`, water reconstruction `140.95s`, convert `287.99s`, Blender render `414.96s`, GIF assembly `2.74s`.
- Visual read: S157 look stack holds on the larger event and produces denser mist/water-surface coverage, but the shot still reads mostly as foreground surface/mist detail rather than a broad establishing large-scale water event.

## Follow-Up

- S161: package and publish the S160 artifacts through the static gallery + Cloudflare tunnel path.
- S162: add an establishing scale composition pass with a wider camera/source window or derived preset so the larger physical event reads as a broad falling-water scene.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
