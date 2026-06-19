# S222 Strong Secondary Readability Probe

## Goal

Run a stronger soft/streak-only secondary readability A/B before promoting the
secondary pass into the accepted preset.

## Scope

- Add `dam_break_secondary_readability_strong_probe`.
- Keep `secondary_direct_pass` unchanged.
- Tune only `secondary_soft_pass` and `secondary_streak_pass`.
- Compare against S220 accepted and S221.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s222_secondary_readability_strong_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_secondary_readability_strong_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s222_secondary_readability_strong_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s222_secondary_readability_strong_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s222_secondary_readability_strong_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_secondary_readability_strong_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s220_accepted_overlay_highlight\blender\frames --right build\shots\s222_secondary_readability_strong_probe\blender\frames --left-label S220-accepted --right-label S222-strong-secondary --summary-left build\shots\s220_accepted_overlay_highlight\blender\bridge_summary.json --summary-right build\shots\s222_secondary_readability_strong_probe\blender\bridge_summary.json --out-dir build\shots\s222_secondary_readability_strong_probe\comparison_s220 --frames 8 --thumb-width 320 --report docs\reports\cinematic_secondary_readability_strong_probe_s222.md --title "S222 Strong Secondary Readability Probe" --finding "S222 tests a stronger soft/streak-only secondary readability pass while keeping direct secondary thinning unchanged." --next "Prefer S222 only if secondary readability clearly improves without direct clutter or contrast loss."
python tools\compare_cinematic_frames.py --left build\shots\s221_secondary_readability_probe\blender\frames --right build\shots\s222_secondary_readability_strong_probe\blender\frames --left-label S221-secondary --right-label S222-strong-secondary --summary-left build\shots\s221_secondary_readability_probe\blender\bridge_summary.json --summary-right build\shots\s222_secondary_readability_strong_probe\blender\bridge_summary.json --out-dir build\shots\s222_secondary_readability_strong_probe\comparison_s221 --frames 8 --thumb-width 320 --report docs\reports\cinematic_secondary_readability_s221_s222_comparison.md --title "S221 vs S222 Secondary Readability A/B" --finding "S222 is compared against S221 to decide whether the stronger soft/streak pass is worth promoting." --next "Use the stronger pass only if the added readability is visible and bounded."
python tools\assemble_frames.py build\shots\s222_secondary_readability_strong_probe\blender\frames build\shots\s222_secondary_readability_strong_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s222_secondary_readability_strong_probe --out build\shots\s222_secondary_readability_strong_probe\gallery --comparison-sheet build\shots\s222_secondary_readability_strong_probe\comparison_s220\comparison_sheet.png --comparison-summary build\shots\s222_secondary_readability_strong_probe\comparison_s220\comparison_summary.json --comparison-label "S220 Accepted vs S222 Strong Secondary" --title "S222 Strong Secondary Readability Probe" --keyframes 8 --report docs\reports\cinematic_secondary_readability_strong_gallery_s222.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Direct secondary pass: unchanged from S220
- Direct secondary counts: unchanged from S220/S221 on all review frames
- Render: `build/shots/s222_secondary_readability_strong_probe/blender`
- Gallery: `build/shots/s222_secondary_readability_strong_probe/gallery/index.html`

S222 minus S220:

- Mean luminance: `0.17864746093749773`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

S222 minus S221:

- Mean luminance: `0.11814778645833712`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Prefer S222 over S221 as the secondary readability promotion candidate.

## Next

S223 should fold S222 into `dam_break_water_mesh_smoothing` and rerun accepted
mixed-window validation.
