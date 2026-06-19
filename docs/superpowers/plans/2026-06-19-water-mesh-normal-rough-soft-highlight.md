# S210 Water Mesh Normal-Rough Soft-Highlight Variant

## Goal

Tune the S208 `normal_rough` material pass so it suppresses highlights less
while retaining the contrast gain and stable-window no-op behavior.

## Scope

- Add `dam_break_water_normal_rough_labeled_soft_highlight_probe`.
- Keep the pass label-gated to `normal_rough`.
- Make the pass less suppressive than S208:
  `alpha_scale=0.985`, `emission_scale=0.94`,
  `rim_strength_scale=0.92`, `roughness_min=0.56`,
  `transmission_max=0.3`.
- Validate accepted S191 no-op behavior.
- Render the source index `8..11` normal-rough window.
- Compare S210 against untreated and S208.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s210_normal_rough_soft_highlight\accepted_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_labeled_soft_highlight_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
```

```powershell
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s210_normal_rough_soft_highlight\accepted_dry\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s210_normal_rough_soft_highlight\accepted_gate --min-stable-ratio 1.0
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s210_normal_rough_soft_highlight\normal_rough_render --frames 2 --width 320 --height 180 --samples 4 --render-preset dam_break_water_normal_rough_labeled_soft_highlight_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

## Result

S210 passed.

- Accepted labels: `{'stable': 4}`
- Accepted gate status: `passed`
- S210 render labels: `{'normal_rough': 2}`
- Untreated-vs-S210 minimum contrast delta: `5.0`
- Untreated-vs-S210 mean bright ratio delta:
  `-9.548611111111112e-05`
- S208-vs-S210 minimum contrast delta: `1.0`
- S208-vs-S210 mean bright ratio delta: `8.680555555555557e-06`
- S208-vs-S210 highlight ratio delta: `0.0`

## Decision

Prefer S210 over S208 for future `normal_rough` probes. Keep it opt-in; do not
promote it to the accepted cinematic baseline yet.

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python -m py_compile tools\render_bridge_blender.py`
- Accepted window dry-run
- Accepted window S206 gate
- Normal-rough Blender render
- Untreated-vs-S210 comparison report
- S208-vs-S210 comparison report
- `git diff --check`

## Next

S211 should run a wider S210 keyframe comparison or package an inspectable
gallery/contact sheet before any baseline decision.
