# S223 Secondary Readability Acceptance

## Goal

Fold the S222 soft/streak secondary readability controls into the accepted
`dam_break_water_mesh_smoothing` preset and verify accepted-preset parity.

## Scope

- Add S222 `secondary_soft_pass` and `secondary_streak_pass` overrides to
  `dam_break_water_mesh_smoothing`.
- Keep `secondary_direct_pass` unchanged.
- Render the S220 mixed source window (`8..55`) through the accepted preset.
- Compare against S220 accepted and S222 probe renders.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s223_accepted_secondary_readability\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s223_accepted_secondary_readability\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s223_accepted_secondary_readability\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s223_accepted_secondary_readability\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s220_accepted_overlay_highlight\blender\frames --right build\shots\s223_accepted_secondary_readability\blender\frames --left-label S220-accepted --right-label S223-accepted-secondary --summary-left build\shots\s220_accepted_overlay_highlight\blender\bridge_summary.json --summary-right build\shots\s223_accepted_secondary_readability\blender\bridge_summary.json --out-dir build\shots\s223_accepted_secondary_readability\comparison_s220 --frames 8 --thumb-width 320 --report docs\reports\cinematic_secondary_readability_acceptance_s223.md --title "S223 Secondary Readability Acceptance" --finding "S223 folds the S222 soft/streak secondary readability controls into the accepted water mesh smoothing preset." --next "Keep S223 only if accepted-preset rendering preserves direct secondary thinning and S222 visual gain."
python tools\compare_cinematic_frames.py --left build\shots\s222_secondary_readability_strong_probe\blender\frames --right build\shots\s223_accepted_secondary_readability\blender\frames --left-label S222-strong-secondary --right-label S223-accepted-secondary --summary-left build\shots\s222_secondary_readability_strong_probe\blender\bridge_summary.json --summary-right build\shots\s223_accepted_secondary_readability\blender\bridge_summary.json --out-dir build\shots\s223_accepted_secondary_readability\comparison_s222 --frames 8 --thumb-width 320 --report docs\reports\cinematic_secondary_readability_s222_s223_parity.md --title "S222 vs S223 Secondary Readability Parity" --finding "S223 accepted-preset render is compared against the S222 probe to verify the fold." --next "Treat S223 as accepted only if parity holds within render noise."
python tools\assemble_frames.py build\shots\s223_accepted_secondary_readability\blender\frames build\shots\s223_accepted_secondary_readability\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s223_accepted_secondary_readability --out build\shots\s223_accepted_secondary_readability\gallery --comparison-sheet build\shots\s223_accepted_secondary_readability\comparison_s220\comparison_sheet.png --comparison-summary build\shots\s223_accepted_secondary_readability\comparison_s220\comparison_summary.json --comparison-label "S220 Accepted vs S223 Accepted Secondary" --title "S223 Accepted Secondary Readability" --keyframes 8 --report docs\reports\cinematic_secondary_readability_acceptance_gallery_s223.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Direct secondary pass: unchanged
- Accepted render: `build/shots/s223_accepted_secondary_readability/blender`
- S220 comparison: `build/shots/s223_accepted_secondary_readability/comparison_s220/comparison_sheet.png`
- S222 parity comparison: `build/shots/s223_accepted_secondary_readability/comparison_s222/comparison_sheet.png`
- Gallery: `build/shots/s223_accepted_secondary_readability/gallery/index.html`

S223 minus S220:

- Mean luminance: `0.17866536458332405`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

S223 minus S222:

- Mean luminance: `1.7903645826322645e-05`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Accept S223. The S222 soft/streak secondary readability controls are now part of
`dam_break_water_mesh_smoothing`.

## Next

Use S223 as the accepted baseline for wider-window review or publish the gallery
for external visual inspection.
