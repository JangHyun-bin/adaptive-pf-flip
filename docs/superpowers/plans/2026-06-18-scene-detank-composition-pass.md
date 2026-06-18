# S126 Scene De-Tank Composition Pass

## Objective

Reduce the remaining boxed/tank read in the large-grid cinematic shot while preserving the S125 material, contact-volume, secondary framing, focus, ripple, temporal, and comparison gates.

## Scope

- Add a new preset: `dam_break_scene_detank_composition`.
- Extend `dam_break_contact_volume_integrated`.
- Prefer scene/background/camera composition changes over gate relaxation.
- Keep the existing S125 material and contact-volume settings as the baseline.
- Do not change simulation physics in this slice.

## Candidate Adjustments

- Reframe the camera path only if secondary framing remains above the current S125 thresholds.
- Add or tune background depth/haze so the broad flat back wall recedes.
- Add foreground/side masking only if it does not hide the water surface or secondary diagnostics.
- Keep contact/focus/secondary-depth/ripple comparison sheets against S125.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_scene_detank_composition --out build\shots\s126_scene_detank_composition --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s125_contact_volume_integrated\review\review_manifest.json --no-build --timeout-seconds 1800
python tools\run_cinematic_shot.py --preset dam_break_scene_detank_composition --out build\shots\s126_scene_detank_composition --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s125_contact_volume_integrated\review\review_manifest.json --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s126_scene_detank_composition\shot_summary.json --out docs\reports\cinematic_scene_detank_composition_s126.md
```

## Acceptance Gate

- Visual QA gate passes.
- Focus review gate passes.
- Secondary framing gate passes without lowering thresholds.
- Secondary depth review gate passes.
- Ripple readability gate passes.
- Temporal highlight gate passes.
- Review comparison sheets are generated against S125.
- Direct visual inspection shows less boxed/tank read than S125.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\summarize_shot_commands.py tools\build_cinematic_gallery.py tools\package_cinematic_artifacts.py
git diff --check
ctest --test-dir build -C Release --output-on-failure
```
