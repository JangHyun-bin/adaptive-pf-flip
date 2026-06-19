# S202 Early Window Island Filter Probe

## Goal

Render the source window where S198/S199 component fragmentation actually
appears, then decide whether component filtering is visually safe.

## Scope

- Render the original S168 water reconstruction over source indices `0..8`.
- Render the S200 filtered reconstruction over the same source indices.
- Compare the two 8-frame probes.
- Run component visibility diagnostics on the original early-window scene spec.

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s202_island_filter_early_probe\original --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_mesh_island_filter_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 8 --timeout-seconds 900
```

```powershell
python tools\render_bridge_blender.py build\shots\s200_island_filter_probe\converted\sequence.json build\shots\s202_island_filter_early_probe\filtered --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_mesh_island_filter_probe --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 0 --source-end-index 8 --timeout-seconds 900
```

## Result

The filter is visible in the early window, but it is not clearly safe.

- Would-filter component rows: `7`
- Visible would-filter component rows: `7`
- Selected mesh frames with filtered components: `[0, 1, 2, 3, 4]`
- Mean changed ratio: `0.015128038194444445`
- Max changed ratio: `0.03657552083333333`
- Strong changed ratio mean: `0.0`
- Minimum contrast delta: `-2.0`
- Mean luminance delta: `1.172603624131952`

The filtered component is visible and substantial. It looks like a lower/back
part of the early water mass, not a tiny detached speck. This is not enough
evidence to enable pruning in the baseline.

## Artifacts

- Early comparison report:
  `docs/reports/cinematic_water_mesh_island_filter_early_comparison_s202.md`
- Early visibility report:
  `docs/reports/cinematic_water_mesh_component_visibility_s202.md`
- Comparison sheet:
  `build/shots/s202_island_filter_early_probe/comparison/comparison_sheet.png`

## Verification

- Original early-window Blender probe render
- Filtered early-window Blender probe render
- `python tools\compare_cinematic_frames.py ...`
- `python tools\analyze_water_mesh_component_visibility.py ...`
- visual inspection of the comparison sheet
- `git diff --check`

## Next

S203 should add a component label/overlay diagnostic. The key question is not
whether the filter works; it does. The question is whether component 2 is an
artifact or meaningful separated water.
