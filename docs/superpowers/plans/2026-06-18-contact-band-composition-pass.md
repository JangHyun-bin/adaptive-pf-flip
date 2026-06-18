# S124 Contact-Band Composition Pass

## Objective

Implement the S123 decision by adding a large-grid contact-band composition preset that lowers the camera target toward the impact/contact region while preserving the S119 visual, focus, secondary-depth, ripple, temporal, and comparison gates.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_contact_band_composition --out build\shots\s124_contact_band_composition --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s119_blender_quality_baseline_comparison\review\review_manifest.json --no-build --timeout-seconds 1800
python tools\run_cinematic_shot.py --preset dam_break_contact_band_composition --out build\shots\s124_contact_band_composition --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s119_blender_quality_baseline_comparison\review\review_manifest.json --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s124_contact_band_composition\shot_summary.json --out docs\reports\cinematic_contact_band_composition_s124.md
```

## Result

S124 passed and produced `build/shots/s124_contact_band_composition/shot.gif` plus the review comparison sheets.

Key metrics from the full 36-frame Blender gate:

- visual QA gate: pass
- focus review gate: pass
- secondary framing gate: pass
- secondary depth gate: pass
- ripple readability gate: pass
- temporal highlight gate: pass
- comparison sources: `2`
- camera target y range: `11.6` to `12.4`, lowered from S119's `12.9` to `13.7`
- warm-cache rerun command time: `4.55s`

Visual inspection of the S124 contact sheet confirms that the water/contact band is larger in frame than S119 while preserving the secondary band and comparison diagnostics. The remaining issue is that the shot still reads as a contained/boxed water volume in the wide background, so the next look-dev pass should integrate contact volume and background haze rather than only retuning camera placement.

## Verification

```powershell
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\run_cinematic_shot.py tools\summarize_shot_commands.py
python tools\summarize_shot_commands.py build\shots\s124_contact_band_composition\shot_summary.json --out docs\reports\cinematic_contact_band_composition_s124.md
git diff --check
ctest --test-dir build -C Release --output-on-failure
```

## Next

S125 should add a contact-volume/background integration preset that softens the remaining boxed/tank read without losing the S124 gates.
