# S125 Contact-Volume Integration Pass

## Objective

Add a conservative large-grid contact-volume integration preset that softens the water body and secondary spray/foam material without relaxing the S124 visual, focus, secondary-depth, ripple, temporal, or secondary framing gates.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_contact_volume_integrated --out build\shots\s125_contact_volume_integrated --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s124_contact_band_composition\review\review_manifest.json --no-build --timeout-seconds 1800
python tools\run_cinematic_shot.py --preset dam_break_contact_volume_integrated --out build\shots\s125_contact_volume_integrated --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s124_contact_band_composition\review\review_manifest.json --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s125_contact_volume_integrated\shot_summary.json --out docs\reports\cinematic_contact_volume_integrated_s125.md
```

## Result

S125 passed and produced `build/shots/s125_contact_volume_integrated/shot.gif` plus the S124 comparison review sheets.

Key metrics from the full 36-frame Blender gate:

- visual QA gate: pass
- focus review gate: pass
- secondary framing gate: pass
- secondary depth gate: pass
- ripple readability gate: pass
- temporal highlight gate: pass
- comparison sources: `2`
- visual mean luminance: `98.93`
- visual mean contrast: `227.86`
- secondary framing min/mean inside ratio: `0.341` / `0.982`
- ripple edge mean: `29.64`
- warm-cache rerun command time: `4.66s`

Visual inspection of the S125 contact and comparison sheets shows a slightly fuller lower contact haze and water-body scattering while preserving the S124 composition and diagnostics. The remaining dominant issue is still compositional: the scene reads as a boxed/tank volume with a broad back wall. S126 should attack that explicitly instead of further small material tweaks.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\summarize_shot_commands.py tools\build_cinematic_gallery.py tools\package_cinematic_artifacts.py
python tools\summarize_shot_commands.py build\shots\s125_contact_volume_integrated\shot_summary.json --out docs\reports\cinematic_contact_volume_integrated_s125.md
git diff --check
ctest --test-dir build -C Release --output-on-failure
```

## Next

S126 should add a scene/background/camera composition pass that reduces the boxed/tank read without relaxing the S125 gates.
