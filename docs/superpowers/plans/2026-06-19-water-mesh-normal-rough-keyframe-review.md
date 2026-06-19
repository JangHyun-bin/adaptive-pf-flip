# S211 Water Mesh Normal-Rough Keyframe Review

## Goal

Run a wider visual comparison before deciding whether the S210 normal-rough
soft-highlight treatment should be promoted.

## Scope

- Render the full source index `8..11` normal-rough window untreated.
- Render the same window with S210.
- Compare four 640x360 frames.
- Decide whether S210 remains a candidate.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s211_normal_rough_keyframe_review\untreated --frames 4 --width 640 --height 360 --samples 8 --render-preset dam_break_water_component_material_labeled_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s211_normal_rough_keyframe_review\s210 --frames 4 --width 640 --height 360 --samples 8 --render-preset dam_break_water_normal_rough_labeled_soft_highlight_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 8 --source-end-index 11 --timeout-seconds 900
```

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s211_normal_rough_keyframe_review\untreated\frames --right build\shots\s211_normal_rough_keyframe_review\s210\frames --left-label S211-untreated --right-label S211-S210 --summary-left build\shots\s211_normal_rough_keyframe_review\untreated\bridge_summary.json --summary-right build\shots\s211_normal_rough_keyframe_review\s210\bridge_summary.json --out-dir build\shots\s211_normal_rough_keyframe_review\comparison --frames 4 --thumb-width 320 --report docs\reports\cinematic_water_mesh_normal_rough_keyframe_review_s211.md --title "S211 Normal-Rough Keyframe Review" --finding "S211 compares a 4-frame 640x360 untreated normal_rough window against the S210 soft-highlight treatment." --next "Promote S210 only if the wider keyframe review shows contrast/readability benefit without unacceptable highlight loss."
```

## Result

S211 passed, and rejects S210 for baseline promotion.

- Frame count: `4`
- Untreated labels: `{'normal_rough': 4}`
- S210 labels: `{'normal_rough': 4}`
- Mean luminance delta: `-0.035657552083321775`
- Minimum contrast delta: `-8.0`
- Mean bright ratio delta: `-4.557291666666666e-05`
- Mean highlight ratio delta: `-3.472222222222222e-05`
- Mean nonblank ratio delta: `0.0`

## Decision

Do not promote S210. The wider keyframe review shows contrast and highlight
regression. Further `normal_rough` work should target geometry/normal
continuity rather than material suppression.

## Verification

- Untreated 4-frame Blender render
- S210 4-frame Blender render
- S211 comparison report and sheet
- `git diff --check`

## Next

S212 should test label-gated mesh smoothing or normal-continuity treatment on
`normal_rough` frames.
