# S136 Offscreen Source Impact Framing Pass

## Objective

Reduce the contained-source read by reframing the S133 source-breakup scene so the upper water generator is mostly out of frame and the shot focuses on water entering frame and impacting the pool.

## Inputs

- Baseline preset: `dam_break_falling_source_silhouette_breakup`
- Baseline review manifest: `build/shots/s133_falling_source_silhouette_breakup/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s135.md`

## Scope

- Add an inherited preset, tentatively `dam_break_offscreen_source_impact_framing`.
- Preserve the S133 source-breakup simulation scene.
- Adjust camera path, target, FOV, and review crops so the source mass is mostly cropped while the impact pool, lower water surface, spray, foam, and ripples remain visible.
- Keep visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates active.

## Non-Goals

- Do not change the pressure solver or source-breakup scene geometry in this milestone.
- Do not publish a new gallery until the S136 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_offscreen_source_impact_framing --out build\shots\s136_offscreen_source_impact_framing --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s133_falling_source_silhouette_breakup\review\review_manifest.json --report docs\reports\cinematic_offscreen_source_impact_framing_s136.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S133 is generated.
- Report records whether the upper source is mostly out of frame and what remains visually weak.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
