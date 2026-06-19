# S165 Source-Slab Silhouette De-Emphasis Scene Pass

## Objective

Reduce the ceiling-like upper source mass visible in S162 by adding a source-breakup scene or preset variant with thinner upper lobes and stronger vertical gaps, then run it through the cinematic gate.

## Inputs

- Baseline preset: `dam_break_establishing_scale_composition`
- Baseline shot output: `build/shots/s162_establishing_scale_composition`
- Baseline report: `docs/reports/cinematic_establishing_scale_composition_s162.md`
- Triage report: `docs/reports/cinematic_visual_review_s164.md`

## Scope

- Add a new source-breakup variant, tentatively `source-slab-deemphasis-water-event`.
- Expose the new scene through `apps/export_render_cache3d.cpp` and `tools/run_cinematic_shot.py`.
- Add an inherited cinematic preset, tentatively `dam_break_source_slab_deemphasis`.
- Preserve S162 grid size, secondary physical particles, water material, mist/foam/ripple stack, and broad impact-pool camera.
- Use dry-run and a short Blender probe before committing to the full 36-frame gate.

## Non-Goals

- Do not increase grid size.
- Do not rewrite the renderer material stack in this pass.
- Do not add the long cinematic gate to default `ctest`.

## Candidate Dry Run

```powershell
python tools\render_bridge_blender.py build\shots\s162_establishing_scale_composition\converted\sequence.json build\s165_source_slab_deemphasis_dry --frames 6 --width 640 --height 360 --dry-run --render-preset dam_break_source_slab_deemphasis --preset-config configs\cinematic_presets.json --max-secondary-particles 512 --secondary-radius-scale 3.0
```

## Candidate Full Gate

```powershell
python tools\run_cinematic_shot.py --preset dam_break_source_slab_deemphasis --out build\shots\s165_source_slab_deemphasis --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s162_establishing_scale_composition\review\review_manifest.json --report docs\reports\cinematic_source_slab_deemphasis_s165.md --no-build --timeout-seconds 2100
```

## Acceptance Gate

- New scene initializes and exports finite cinematic cache frames.
- Full gate passes visual, temporal, focus, secondary-depth, secondary-framing, ripple-readability, and camera-stability gates.
- Contact/comparison sheets show reduced ceiling-like upper source mass versus S162.
- Report records timing and visual tradeoffs.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
