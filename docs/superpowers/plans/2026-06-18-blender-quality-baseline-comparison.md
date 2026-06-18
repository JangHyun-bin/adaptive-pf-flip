# Blender Quality Baseline Comparison

## Goal

Produce a direct visual comparison package between the S106 large-grid Blender baseline and the current warm-cache Blender quality output.

## Scope

- Use `dam_break_large_grid_render_quality_followup`.
- Compare against `build/shots/s106_large_grid_render_quality_followup/review/review_manifest.json`.
- Keep full Blender quality settings: 36 frames, 36 sim steps, 1280x720, samples 12.
- Enable all warm-cache flags.
- Generate comparison sheets for contact, focus, secondary-depth, and ripple readability diagnostics.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_large_grid_render_quality_followup --out build\shots\s119_blender_quality_baseline_comparison --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s106_large_grid_render_quality_followup\review\review_manifest.json --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s119_blender_quality_baseline_comparison\shot_summary.json --out docs\reports\cinematic_blender_baseline_comparison_s119.md
```

## Result

S119 passed and produced `docs/reports/cinematic_blender_baseline_comparison_s119.md`.

- Status: `ok`.
- Comparison source count: `2`.
- Focus comparison source count: `2`.
- Secondary-depth comparison source count: `2`.
- Ripple readability comparison source count: `2`.
- Warm run reused export, validation, water reconstruction, conversion, Blender frames, and GIF.
- Warm run total command time: `4.59s`.

Visual inspection of `comparison_sheet.png`, `focus_comparison_sheet.png`, and `secondary_depth_comparison_sheet.png` shows S119 matches the S106 large-grid render-quality baseline.

## Next

S120 should package the current Blender comparison artifacts for quick visual inspection and sharing.
