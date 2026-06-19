# S162 Establishing Scale Composition Pass

## Objective

Use the S160 larger physical event as input evidence, then widen the shot grammar so the scene reads as a broader impact-pool event instead of only a foreground water-surface and mist close-up.

## Inputs

- Baseline preset: `dam_break_large_event_scale_gate`
- Baseline shot output: `build/shots/s160_large_event_scale_gate`
- Baseline report: `docs/reports/cinematic_large_event_scale_gate_s160.md`
- Baseline review manifest: `build/shots/s160_large_event_scale_gate/review/review_manifest.json`

## Scope

- Add an inherited preset, tentatively `dam_break_establishing_scale_composition`.
- Preserve S160 grid, source-breakup scene, secondary lifecycle, water material, mist, foam, ripple, and temporal gates.
- Widen the camera enough to show more impact-pool width while avoiding dominant upper source-slab framing.
- Adjust source window only if needed to keep the active water body visible throughout the 36-frame render.
- Keep S160 render quality settings unless the wider shot exposes a specific artifact.

## Non-Goals

- Do not increase grid size again until S160 is published and the S162 framing gate passes.
- Do not rewrite renderer materials in the same pass.
- Do not add this gate to default `ctest`.

## Candidate Dry Run

```powershell
python tools\render_bridge_blender.py build\shots\s160_large_event_scale_gate\converted\sequence.json build\s162_establishing_scale_dry --frames 6 --width 640 --height 360 --dry-run --render-preset dam_break_establishing_scale_composition --preset-config configs\cinematic_presets.json --max-secondary-particles 512 --secondary-radius-scale 3.0
```

## Candidate Full Gate

```powershell
python tools\run_cinematic_shot.py --preset dam_break_establishing_scale_composition --out build\shots\s162_establishing_scale_composition --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s160_large_event_scale_gate\review\review_manifest.json --report docs\reports\cinematic_establishing_scale_composition_s162.md --no-build --timeout-seconds 2100
```

## Acceptance Gate

- Dry-run confirms camera stability and active secondary framing.
- Full gate passes visual, temporal, focus, secondary-depth, secondary-framing, ripple-readability, and camera-stability gates.
- Contact sheet visibly shows broader source/impact context than S160.
- Report records the cost of re-running the S160-sized physical event with the wider composition preset.

## Result

- Status: passed.
- Preset added: `dam_break_establishing_scale_composition`.
- Output: `build/shots/s162_establishing_scale_composition`.
- Report: `docs/reports/cinematic_establishing_scale_composition_s162.md`.
- Grid/steps: `36 x 44 x 28`, `56` simulation steps, `36` rendered frames.
- Source window: frames `16..55`, `40` selected source frames.
- QA gates: visual, temporal, focus, secondary-depth, secondary-framing, ripple-readability, and camera-stability all passed.
- Validation: `56` cache frames, `16647683` particles, `2482565` phase cells, max volume drift `0.0011012159806506408`.
- Timing: export `200.30s`, validation `259.96s`, water reconstruction `144.96s`, convert `296.91s`, Blender render `408.81s`, GIF assembly `2.85s`.
- Visual read: S162 opens the impact-pool composition relative to S160 while preserving gates. It still has some upper source-slab presence, so the next visual triage should decide whether to attack source-slab silhouette or continue widening event shape.

## Follow-Up

- S163: package and publish the S162 artifacts through the static gallery + Cloudflare tunnel path.
- S164: public gallery visual triage for the next visible adjustment.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
