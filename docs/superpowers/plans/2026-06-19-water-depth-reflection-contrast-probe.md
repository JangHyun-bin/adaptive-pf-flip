# S217 Water Depth Reflection Contrast Probe

## Goal

Tune the S216 depth/reflection probe to recover contrast and luminance while
keeping the useful bright/highlight increase.

## Scope

- Add `dam_break_water_mesh_depth_reflection_contrast_probe`.
- Keep S214 accepted as the primary baseline.
- Compare S217 against both S214 accepted and S216.
- Package an S217 gallery with the S214 comparison.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s217_depth_reflection_contrast_probe\dry --frames 8 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_depth_reflection_contrast_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --dry-run
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s217_depth_reflection_contrast_probe\dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s217_depth_reflection_contrast_probe\mixed_gate --min-stable-ratio 0.8
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s217_depth_reflection_contrast_probe\blender --frames 8 --width 640 --height 360 --samples 16 --render-preset dam_break_water_mesh_depth_reflection_contrast_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 55 --timeout-seconds 600
python tools\compare_cinematic_frames.py --left build\shots\s214_mixed_window_accepted_preset\blender\frames --right build\shots\s217_depth_reflection_contrast_probe\blender\frames --left-label S214-accepted --right-label S217-contrast-probe --summary-left build\shots\s214_mixed_window_accepted_preset\blender\bridge_summary.json --summary-right build\shots\s217_depth_reflection_contrast_probe\blender\bridge_summary.json --out-dir build\shots\s217_depth_reflection_contrast_probe\comparison_s214 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_depth_reflection_contrast_probe_s217.md --title "S217 Water Depth Reflection Contrast Probe" --finding "S217 tunes the S216 depth/reflection probe to recover contrast while keeping more highlight continuity than S214." --next "Promote S217 only if it preserves S214 coverage/contrast better than S216 while retaining useful highlight gain."
python tools\compare_cinematic_frames.py --left build\shots\s216_depth_reflection_probe\blender\frames --right build\shots\s217_depth_reflection_contrast_probe\blender\frames --left-label S216-depth-reflection --right-label S217-contrast-probe --summary-left build\shots\s216_depth_reflection_probe\blender\bridge_summary.json --summary-right build\shots\s217_depth_reflection_contrast_probe\blender\bridge_summary.json --out-dir build\shots\s217_depth_reflection_contrast_probe\comparison_s216 --frames 8 --thumb-width 320 --report docs\reports\cinematic_water_depth_reflection_s216_s217_comparison.md --title "S216 vs S217 Depth Reflection Tune" --finding "S217 is compared against S216 to verify the contrast-preserving tune." --next "Use S217 as the new probe only if it recovers contrast or luminance without losing the useful S216 highlight gains."
python tools\assemble_frames.py build\shots\s217_depth_reflection_contrast_probe\blender\frames build\shots\s217_depth_reflection_contrast_probe\shot.gif --fps 8
python tools\build_bridge_cinematic_gallery.py build\shots\s217_depth_reflection_contrast_probe --out build\shots\s217_depth_reflection_contrast_probe\gallery --comparison-sheet build\shots\s217_depth_reflection_contrast_probe\comparison_s214\comparison_sheet.png --comparison-summary build\shots\s217_depth_reflection_contrast_probe\comparison_s214\comparison_summary.json --comparison-label "S214 Accepted vs S217 Contrast Probe" --title "S217 Water Depth Reflection Contrast Probe" --keyframes 8 --report docs\reports\cinematic_water_depth_reflection_contrast_gallery_s217.md
```

## Results

- Dry-run labels: `normal_rough: 1`, `stable: 7`
- Mesh-quality gate: `passed`
- Render: `build/shots/s217_depth_reflection_contrast_probe/blender`
- Gallery: `build/shots/s217_depth_reflection_contrast_probe/gallery/index.html`

S217 minus S214:

- Mean luminance: `-0.3267182074652766`
- Minimum contrast: `-13.0`
- Mean bright ratio: `6.890190972222223e-05`
- Mean highlight ratio: `4.12326388888889e-05`
- Mean nonblank ratio: `0.0`

S217 minus S216:

- Mean luminance: `0.4082052951388988`
- Minimum contrast: `-5.0`
- Mean bright ratio: `1.9531250000000017e-05`
- Mean highlight ratio: `-2.1701388888888758e-06`
- Mean nonblank ratio: `0.0`

## Decision

Do not promote S217. It partially fixes S216's luminance loss, but it makes the
contrast floor worse than both S214 and S216.

## Next

S218 should isolate reflection/glint overlay changes and leave the accepted
water material unchanged.
