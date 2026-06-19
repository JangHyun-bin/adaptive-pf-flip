# S213 Water Mesh Normal-Rough Review Gallery

## Goal

Package the S212 normal-rough smoothing review as an inspectable gallery and fold
the accepted result into the main water mesh smoothing preset only if the
accepted stable-window gate still passes.

## Scope

- Assemble the S212 4-frame normal-rough render into a GIF.
- Build a local HTML gallery with the GIF, keyframes, comparison sheet, and
  metadata.
- Add `water_mesh_quality_smoothing_pass` to
  `dam_break_water_mesh_smoothing`, gated to `normal_rough` labels only.
- Validate that the accepted stable window remains a no-op and that the
  normal-rough window carries the target labels.

## Commands

```powershell
python tools\assemble_frames.py build\shots\s213_normal_rough_review\blender\frames build\shots\s213_normal_rough_review\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s213_normal_rough_review --out build\shots\s213_normal_rough_review\gallery --comparison-sheet build\shots\s212_normal_rough_smoothing\comparison_untreated\comparison_sheet.png --comparison-summary build\shots\s212_normal_rough_smoothing\comparison_untreated\comparison_summary.json --comparison-label "Untreated vs S212 Smoothing" --title "S213 Normal-Rough Smoothing Review" --keyframes 4 --report docs\reports\cinematic_water_mesh_normal_rough_smoothing_gallery_s213.md
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s213_normal_rough_review\accepted_preset_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s213_normal_rough_review\accepted_preset_dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s213_normal_rough_review\accepted_preset_gate --min-stable-ratio 1.0
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s213_normal_rough_review\accepted_preset_normal_rough_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --dry-run
python -m json.tool configs\cinematic_presets.json
python -m py_compile tools\render_bridge_blender.py
python -m py_compile build\shots\s213_normal_rough_review\accepted_preset_dry\blender_driver.py build\shots\s213_normal_rough_review\accepted_preset_normal_rough_dry\blender_driver.py
```

## Results

- Gallery: `build/shots/s213_normal_rough_review/gallery/index.html`
- Report: `docs/reports/cinematic_water_mesh_normal_rough_smoothing_gallery_s213.md`
- S212 comparison carried into the gallery:
  - Minimum contrast delta: `45.0`
  - Mean luminance delta: `0.004424913194455371`
  - Bright ratio delta: `3.2552083333333407e-06`
  - Highlight ratio delta: `-3.255208333333327e-06`
  - Nonblank ratio delta: `0.0`
- Accepted preset stable dry-run: labels `stable: 4`
- Stable gate: `passed`, stable ratio `1.0`
- Normal-rough accepted-preset dry-run: labels `normal_rough: 4`
- Quality smoothing preset: enabled for `normal_rough`, factor `0.04`,
  iterations `1`

## Decision

Promote S212 into `dam_break_water_mesh_smoothing` as a conservative,
label-gated `normal_rough` mesh smoothing pass. This does not alter the stable
accepted window and avoids the highlight-suppressing material changes rejected
in S211.

## Next

S214 should run a mixed-window accepted-preset visual review so stable and
`normal_rough` frames are checked together in one sequence. If a remote review
page is useful, publish the S213 gallery with the Cloudflare tunnel publisher.
