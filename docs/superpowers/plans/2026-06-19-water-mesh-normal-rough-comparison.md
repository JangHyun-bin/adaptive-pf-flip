# S209 Water Mesh Normal-Rough Comparison

## Goal

Compare the S208 `normal_rough` label-gated treatment against an untreated
normal-rough render window before considering baseline promotion.

## Scope

- Render source index `8..11` with untreated label-gated component preset.
- Compare untreated frames against the S208 treated normal-rough render.
- Decide whether S208 should remain opt-in or be promoted.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s209_normal_rough_comparison\untreated --frames 2 --width 320 --height 180 --samples 4 --render-preset dam_break_water_component_material_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s209_normal_rough_comparison\untreated\frames --right build\shots\s208_normal_rough_labeled_probe\normal_rough_render\frames --left-label S209-untreated --right-label S208-treated --summary-left build\shots\s209_normal_rough_comparison\untreated\bridge_summary.json --summary-right build\shots\s208_normal_rough_labeled_probe\normal_rough_render\bridge_summary.json --out-dir build\shots\s209_normal_rough_comparison\comparison --frames 2 --thumb-width 320 --report docs\reports\cinematic_water_mesh_normal_rough_comparison_s209.md --title "S209 Normal-Rough Treatment Comparison" --finding "S209 compares untreated normal_rough water frames against the S208 label-gated material treatment." --next "Keep S208 only if the treated normal_rough frames improve readability without contrast loss; otherwise leave the pass as an opt-in diagnostic."
```

## Result

S209 passed.

- Untreated labels: `{'normal_rough': 2}`
- Treated labels: `{'normal_rough': 2}`
- Mean luminance delta: `0.18618055555555202`
- Minimum contrast delta: `4.0`
- Mean bright ratio delta: `-0.00010416666666666667`
- Mean highlight ratio delta: `-6.076388888888889e-05`
- Mean nonblank ratio delta: `0.0`
- Mean changed ratio: roughly `0.0148`

## Decision

Keep S208 as an opt-in treatment. The minimum contrast improvement is useful,
but the highlight reduction and small delta are not enough for baseline
promotion.

## Verification

- Untreated normal-rough Blender render
- S209 comparison report and comparison sheet
- `git diff --check`

## Next

S210 should either run a wider normal-rough comparison or tune a less
highlight-suppressing variant before attempting baseline promotion.
