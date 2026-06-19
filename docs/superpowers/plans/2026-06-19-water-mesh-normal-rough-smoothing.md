# S212 Water Mesh Normal-Rough Smoothing

## Goal

Replace material suppression for `normal_rough` frames with a label-gated mesh
smoothing treatment.

## Scope

- Add `water_mesh_quality_smoothing_pass`.
- Add `dam_break_water_normal_rough_smoothing_probe`.
- Apply an extra Smooth modifier only when
  `water_mesh_surface_quality.label == normal_rough`.
- Keep accepted S191 stable-window no-op behavior.
- Compare the 4-frame normal-rough window against untreated and S210 material
  treatment.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s212_normal_rough_smoothing\accepted_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_smoothing_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
```

```powershell
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s212_normal_rough_smoothing\accepted_dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s212_normal_rough_smoothing\accepted_gate --min-stable-ratio 1.0
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s212_normal_rough_smoothing\normal_rough_render --frames 4 --width 640 --height 360 --samples 8 --render-preset dam_break_water_normal_rough_smoothing_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

## Result

S212 passed and becomes the preferred `normal_rough` route.

- Accepted labels: `{'stable': 4}`
- Accepted gate status: `passed`
- Normal-rough render labels: `{'normal_rough': 4}`
- Untreated-vs-S212 minimum contrast delta: `45.0`
- Untreated-vs-S212 mean bright ratio delta:
  `3.2552083333333407e-06`
- Untreated-vs-S212 mean highlight ratio delta:
  `-3.255208333333327e-06`
- S210-vs-S212 minimum contrast delta: `53.0`
- S210-vs-S212 mean highlight ratio delta:
  `3.1467013888888895e-05`
- Nonblank ratio delta: `0.0`

## Decision

Prefer label-gated smoothing over material suppression for `normal_rough`
frames. Keep it label-gated so stable accepted frames remain unchanged.

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\render_bridge_blender.py`
- Accepted window dry-run
- Accepted window S206 gate
- Normal-rough Blender render
- Untreated-vs-S212 comparison
- S210-vs-S212 comparison
- Generated driver `py_compile`
- `git diff --check`

## Next

S213 should package a small visual review artifact for the normal-rough route
and then decide whether to fold S212 into the main accepted render preset.
