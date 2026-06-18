# S139 Low-Angle Impact Close-Up Framing

## Objective

Create a lower, closer impact-focused composition from the S136 source-breakup scene so the top water source is fully cropped out and the water/contact/spray/ripple band carries the shot.

## Inputs

- Baseline preset: `dam_break_offscreen_source_impact_framing`
- Baseline review manifest: `build/shots/s136_offscreen_source_impact_framing/review/review_manifest.json`
- Triage report: `docs/reports/cinematic_visual_review_s138.md`

## Scope

- Add an inherited preset, tentatively `dam_break_low_angle_impact_closeup`.
- Preserve the `source-breakup-water-event` simulation scene.
- Move the camera lower and closer toward the contact band.
- Tighten review crops so the upper source is excluded while surface ripple, secondary particles, and contact foam remain visible.
- Keep visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates active.

## Non-Goals

- Do not change the sparse 3D simulation scene geometry in this milestone.
- Do not publish a new gallery until the S139 render gate passes.
- Do not add this long gate to default `ctest`.

## Candidate Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_low_angle_impact_closeup --out build\shots\s139_low_angle_impact_closeup --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s136_offscreen_source_impact_framing\review\review_manifest.json --report docs\reports\cinematic_low_angle_impact_closeup_s139.md --no-build --timeout-seconds 1800
```

## Acceptance Gate

- `shot_summary.json` status is `ok`.
- Visual, focus, secondary-depth, ripple, temporal, camera-stability, and secondary-framing gates pass.
- Comparison sheet against S136 is generated.
- Review frames show contact/impact as the primary subject and no large top-source slab dominating the frame.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
git diff --check
```
