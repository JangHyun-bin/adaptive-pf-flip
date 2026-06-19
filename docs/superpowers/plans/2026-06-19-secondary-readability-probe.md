# S221 Secondary Readability Probe

## Goal

Improve spray/foam/bubble readability without increasing direct secondary
particle clutter.

## Scope

- Add `dam_break_secondary_readability_probe`.
- Keep `secondary_direct_pass` unchanged from S220.
- Tune only `secondary_soft_pass` and `secondary_streak_pass`.
- Render the S220 mixed source window (`8..55`) and compare against S220.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s221_secondary_readability_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_secondary_readability_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s221_secondary_readability_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s221_secondary_readability_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s221_secondary_readability_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_secondary_readability_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s220_accepted_overlay_highlight\blender\frames --right build\shots\s221_secondary_readability_probe\blender\frames --left-label S220-accepted --right-label S221-secondary-readability --summary-left build\shots\s220_accepted_overlay_highlight\blender\bridge_summary.json --summary-right build\shots\s221_secondary_readability_probe\blender\bridge_summary.json --out-dir build\shots\s221_secondary_readability_probe\comparison_s220 --frames 8 --thumb-width 320 --report docs\reports\cinematic_secondary_readability_probe_s221.md --title "S221 Secondary Readability Probe" --finding "S221 strengthens soft mist and streak secondary passes while leaving direct secondary particle thinning unchanged." --next "Promote S221 only if soft spray/foam readability improves without obvious direct-particle clutter or contrast loss."
python tools\assemble_frames.py build\shots\s221_secondary_readability_probe\blender\frames build\shots\s221_secondary_readability_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s221_secondary_readability_probe --out build\shots\s221_secondary_readability_probe\gallery --comparison-sheet build\shots\s221_secondary_readability_probe\comparison_s220\comparison_sheet.png --comparison-summary build\shots\s221_secondary_readability_probe\comparison_s220\comparison_summary.json --comparison-label "S220 Accepted vs S221 Secondary Readability" --title "S221 Secondary Readability Probe" --keyframes 8 --report docs\reports\cinematic_secondary_readability_gallery_s221.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Direct secondary pass: unchanged from S220
- Direct secondary counts: unchanged from S220 on all review frames
- Render: `build/shots/s221_secondary_readability_probe/blender`
- Gallery: `build/shots/s221_secondary_readability_probe/gallery/index.html`

S221 minus S220:

- Mean luminance: `0.0604996744791606`
- Minimum contrast: `0.0`
- Mean bright ratio: `0.0`
- Mean highlight ratio: `0.0`
- Mean nonblank ratio: `0.0`

## Decision

Keep S221 as a safe opt-in candidate. It improves mist/streak readability only
slightly, so do not promote it yet.

## Next

S222 should test a stronger soft/streak-only secondary readability candidate,
still without changing direct secondary thinning.
