# S216 Water Depth Reflection Probe

## Goal

Move beyond mesh-quality gating with a conservative visual probe that keeps the
accepted S214 mesh smoothing preset but tests slightly deeper water volume and
softer reflection/glint ribbons.

## Scope

- Add `dam_break_water_mesh_depth_reflection_probe`.
- Keep inherited `water_mesh_smoothing_pass` and `water_mesh_quality_smoothing_pass`.
- Use the S214 mixed source window (`8..55`) so the render includes
  `normal_rough: 1` and `stable: 7`.
- Render the probe and compare it against the S214 accepted mixed-window render.
- Package a gallery for visual review.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s216_depth_reflection_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_depth_reflection_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s216_depth_reflection_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s216_depth_reflection_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s216_depth_reflection_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_depth_reflection_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\blender\frames --right build\shots\s216_depth_reflection_probe\blender\frames --left-label S214-accepted --right-label S216-depth-reflection --summary-left build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --summary-right build\shots\s216_depth_reflection_probe\blender\bridge_summary.json --out-dir build\shots\s216_depth_reflection_probe\comparison --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_depth_reflection_probe_s216.md --title "S216 Water Depth Reflection Probe" --finding "S216 compares a conservative depth/reflection treatment against the accepted S214 mixed-window preset." --next "Promote S216 only if the probe improves depth readability without reducing nonblank coverage or highlight continuity."
python tools\assemble_frames.py build\shots\s216_depth_reflection_probe\blender\frames build\shots\s216_depth_reflection_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s216_depth_reflection_probe --out build\shots\s216_depth_reflection_probe\gallery --comparison-sheet build\shots\s216_depth_reflection_probe\comparison\comparison_sheet.png --comparison-summary build\shots\s216_depth_reflection_probe\comparison\comparison_summary.json --comparison-label "S214 Accepted vs S216 Probe" --title "S216 Water Depth Reflection Probe" --keyframes 8 --report docs\reports\cinematic_water_depth_reflection_gallery_s216.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Render: `build/shots/s216_depth_reflection_probe/blender`
- Comparison: `build/shots/s216_depth_reflection_probe/comparison/comparison_sheet.png`
- Gallery: `build/shots/s216_depth_reflection_probe/gallery/index.html`

Metric deltas S216 minus S214:

- Mean luminance: `-0.7349235026041754`
- Minimum contrast: `-8.0`
- Mean bright ratio: `4.9370659722222215e-05`
- Mean highlight ratio: `4.340277777777777e-05`
- Mean nonblank ratio: `0.0`

## Decision

Keep S216 as an opt-in probe, not the accepted baseline. It increases highlight
continuity and preserves coverage, but the contrast and luminance losses need a
follow-up tune.

## Next

S217 should tune the depth/reflection probe to recover contrast while preserving
the useful highlight increase, then compare against both S214 and S216.
