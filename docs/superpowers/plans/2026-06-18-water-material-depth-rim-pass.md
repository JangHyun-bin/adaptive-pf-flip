# S50 Water Material Depth / Rim Pass

**Goal:** Improve the Blender water look beyond a single flat translucent color by adding depth tint, rim highlights, and preset-recorded material response.

## Scope

- Keep simulation, cache schema, and water reconstruction unchanged.
- Extend only the Blender bridge and cinematic presets.
- Preserve existing material presets by making all new water fields optional.
- Record active water-material response in dry-run summaries and shot reports.

## Implementation

- `tools/render_bridge_blender.py`
  - Extend water material parsing with:
    - `depth_color`
    - `depth_strength`
    - `rim_color`
    - `rim_strength`
    - `rim_width`
    - `specular`
    - `coat_weight`
  - Create a water-specific material builder that blends base/depth color and uses a Layer Weight + ColorRamp rim tint.
  - Emit `water_material` summary in `bridge_summary.json`.

- `configs/cinematic_presets.json`
  - Add conservative depth/rim values to `bubble_cinematic`.
  - Add stronger depth/rim/specular/coat values to `dam_break_cinematic`.

- `tools/run_cinematic_shot.py`
  - Copy `water_material` from the Blender bridge summary into `shot_summary.json`.
  - Include water depth/rim values in generated markdown reports.

## Validation

```powershell
python -m py_compile tools\render_bridge_blender.py tools\run_cinematic_shot.py
python -m json.tool configs\cinematic_presets.json
python tools\render_bridge_blender.py build\s48_secondary_convert_mesh\sequence.json build\s50_water_dry --frames 2 --width 320 --height 180 --dry-run --max-secondary-particles 128 --secondary-radius-scale 2.4 --preset-config configs\cinematic_presets.json --render-preset dam_break_cinematic
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s50_water_material --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --report docs\reports\cinematic_gate_s50.md --no-build
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S51 should package review artifacts: contact sheet, GIF, shot report, summary JSON, and key frame thumbnails.
