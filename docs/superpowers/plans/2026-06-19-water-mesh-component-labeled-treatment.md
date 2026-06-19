# S207 Water Mesh Component Labeled Treatment

## Goal

Make the S204 component material treatment metadata-driven so it only affects
frames labeled by S205/S206 as `component_fragmented`.

## Scope

- Add `quality_labels` to `water_mesh_component_material_pass`.
- Preserve old behavior when `quality_labels` is empty.
- Add a label gate inside the generated Blender driver before assigning the
  secondary component water material.
- Add `dam_break_water_component_material_labeled_probe`.
- Validate the accepted S191 window remains no-op.
- Smoke render an early fragmented window to exercise the generated driver.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s207_component_material_labeled_probe\accepted_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_component_material_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
```

```powershell
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s207_component_material_labeled_probe\accepted_dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s207_component_material_labeled_probe\accepted_gate --min-stable-ratio 1.0
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s207_component_material_labeled_probe\early_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_component_material_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 8 --dry-run
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s207_component_material_labeled_probe\early_render --frames 2 --width 320 --height 180 --samples 4 --render-preset dam_break_water_component_material_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 3 --timeout-seconds 900
```

## Result

S207 passed.

- Accepted dry-run labels: `{'stable': 4}`
- Accepted gate status: `passed`
- Accepted component treatment no-op: `True`
- Early dry-run labels: `{'component_fragmented': 3, 'normal_rough': 1}`
- Runtime smoke labels: `{'component_fragmented': 2}`
- Runtime smoke nonblank ratio: `1.0`

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\render_bridge_blender.py`
- Accepted window dry-run
- Accepted window S206 gate
- Early fragmented window dry-run
- Generated driver `py_compile`
- Early fragmented window Blender smoke render
- `git diff --check`

## Next

S208 should add a separate label-gated treatment for `normal_rough` frames. Keep
it conservative and keep S206/S207 accepted-window no-op gates passing.
