# S127 Non-Boxed Falling-Water Scene Pass

## Objective

Change the falling-water scene/source shape so the top water silhouette no longer reads as a rectangular tank wall, while preserving the S126 visual, focus, secondary-depth, ripple, temporal, and secondary framing gates.

## Scope

- Add a new cinematic preset: `dam_break_nonboxed_falling_water`.
- Add the minimum exporter/simulation scene option needed for a non-rectangular falling-water source, if the current preset system cannot express it.
- Keep S126 render material, contact mist curtain, and comparison diagnostics as the baseline.
- Do not relax QA thresholds to hide the scene-shape change.

## Candidate Adjustments

- Use a rounded or tapered falling-water source footprint instead of a full rectangular slab.
- Stagger the source height or leading edge so the upper silhouette does not appear as a flat tank wall.
- Preserve the lower pool/contact timing enough that secondary spray, foam, ripples, and contact sheets remain comparable against S126.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_nonboxed_falling_water --out build\shots\s127_nonboxed_falling_water --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s126_scene_detank_composition\review\review_manifest.json --no-build --timeout-seconds 1800
python tools\run_cinematic_shot.py --preset dam_break_nonboxed_falling_water --out build\shots\s127_nonboxed_falling_water --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s126_scene_detank_composition\review\review_manifest.json --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s127_nonboxed_falling_water\shot_summary.json --out docs\reports\cinematic_nonboxed_falling_water_s127.md
```

## Acceptance Gate

- Visual QA gate passes.
- Focus review gate passes.
- Secondary framing gate passes without lowering thresholds.
- Secondary depth review gate passes.
- Ripple readability gate passes.
- Temporal highlight gate passes.
- Review comparison sheets are generated against S126.
- Direct visual inspection shows a less rectangular top-water silhouette than S126.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py tools\summarize_shot_commands.py tools\build_cinematic_gallery.py tools\package_cinematic_artifacts.py
git diff --check
ctest --test-dir build -C Release --output-on-failure
```
