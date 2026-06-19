# S208 Water Mesh Normal-Rough Labeled Treatment

## Goal

Add a conservative label-gated material treatment for frames marked
`normal_rough`, while preserving no-op behavior on the accepted S191 stable
window.

## Scope

- Add `water_mesh_quality_material_pass`.
- Add `dam_break_water_normal_rough_labeled_probe`.
- Apply water material changes only when `water_mesh_surface_quality.label`
  matches `quality_labels`.
- Keep the pass conservative: slightly higher roughness, lower emission/rim,
  and bounded transmission.
- Validate S191 accepted window no-op behavior.
- Smoke render a `normal_rough` window.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s208_normal_rough_labeled_probe\accepted_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
```

```powershell
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s208_normal_rough_labeled_probe\accepted_dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s208_normal_rough_labeled_probe\accepted_gate --min-stable-ratio 1.0
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s208_normal_rough_labeled_probe\normal_rough_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s208_normal_rough_labeled_probe\normal_rough_render --frames 2 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

## Result

S208 passed.

- Accepted labels: `{'stable': 4}`
- Accepted gate status: `passed`
- Normal-rough dry-run labels: `{'normal_rough': 4}`
- Normal-rough render labels: `{'normal_rough': 2}`
- Runtime smoke nonblank ratio: `1.0`
- Runtime smoke minimum contrast: `78.0`

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\render_bridge_blender.py`
- Accepted window dry-run
- Accepted window S206 gate
- Normal-rough dry-run
- Generated driver `py_compile`
- Normal-rough Blender smoke render
- `git diff --check`

## Next

S209 should render an untreated-vs-treated normal-rough comparison window. Keep
S208 only if the comparison improves water readability without contrast loss.
