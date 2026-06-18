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

## Result

S127 passed and produced `build/shots/s127_nonboxed_falling_water/shot.gif` plus S126 comparison review sheets.

Key metrics from the full 36-frame Blender gate:

- visual QA gate: pass
- focus review gate: pass
- secondary framing gate: pass
- secondary depth gate: pass
- ripple readability gate: pass
- temporal highlight gate: pass
- selected scene: `nonboxed-water-event`
- visual mean luminance: `90.66`
- visual mean contrast: `232.22`
- secondary framing min/mean inside ratio: `1.0` / `1.0`
- secondary depth crop ratio mean: `1.0`
- ripple edge mean: `25.76`
- warm-cache rerun command time: `4.81s`

Visual inspection of the S127 contact and comparison sheets confirms that the upper water silhouette is less rectangular than S126, with a rounded/tapered falling source and more varied lower edge. The scene still has a stylized contained-water look, but this is the first pass where the main visible issue moved from a rectangular source block toward broader scene/render art direction.

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
cmake --build build --config Release --target unit_tests export_render_cache3d
.\build\Release\unit_tests.exe --test-case="sparse 3D nonboxed water event uses rounded falling source"
python tools\summarize_shot_commands.py build\shots\s127_nonboxed_falling_water\shot_summary.json --out docs\reports\cinematic_nonboxed_falling_water_s127.md
git diff --check
ctest --test-dir build -C Release --output-on-failure
```

## Next

S128 should package and publish the S127 gallery so the current non-boxed scene can be reviewed externally.
