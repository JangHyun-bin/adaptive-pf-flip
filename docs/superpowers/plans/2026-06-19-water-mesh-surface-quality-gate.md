# S206 Water Mesh Surface Quality Gate

## Goal

Use S205 surface-quality metadata as a no-op/QA gate before adding any
label-driven render treatment.

## Scope

- Add `tools/validate_water_mesh_surface_quality_gate.py`.
- Match rendered water mesh frames to annotated sequence metadata by mesh OBJ
  basename.
- Fail the gate on missing metadata, duplicate mesh-label conflicts, blocked
  labels, or a stable-ratio floor miss.
- Keep `normal_rough` and `sharp_edges` as warning labels by default.
- Preserve `water_mesh_surface_quality` through `render_bridge_blender.py`
  scene specs and bridge summaries.
- Validate the accepted S191 render window against the S205 annotated sequence.

## Commands

```powershell
python tools\validate_water_mesh_surface_quality_gate.py build\shots\s191_water_mesh_smoothing\blender\bridge_summary.json build\shots\s205_surface_quality_annotation\converted\sequence.json --out-dir build\shots\s206_surface_quality_gate --report docs\reports\cinematic_water_mesh_surface_quality_gate_s206.md --title "S206 S191 Surface Quality Gate" --min-stable-ratio 1.0 --next "Use this passing gate before enabling label-driven water surface treatment. The accepted S191 window is stable-only, so component-aware treatment should remain a no-op there; future treatments should target component_fragmented or normal_rough labels explicitly."
```

```powershell
python tools\render_bridge_blender.py build\shots\s205_surface_quality_annotation\converted\sequence.json build\shots\s206_surface_quality_gate\bridge_dry --frames 4 --width 320 --height 180 --samples 4 --render-preset dam_break_water_mesh_smoothing --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --source-start-index 20 --source-end-index 55 --dry-run
```

## Result

S206 passed.

- S191 gate frames: `36`
- S191 labels: `{'stable': 36}`
- Stable ratio: `1.0`
- Component treatment no-op: `True`
- Blocked labels: `0`
- Warning labels: `0`
- Dry-run bridge frames: `4`
- Dry-run bridge labels: `{'stable': 4}`
- Dry-run scene-spec labels: `{'stable': 4}`

The accepted S191 source window is stable-only. Label-driven treatment should
not affect it unless a future render intentionally selects earlier
`component_fragmented` or `normal_rough` frames.

## Verification

- `python -m py_compile tools\validate_water_mesh_surface_quality_gate.py tools\render_bridge_blender.py`
- `python tools\validate_water_mesh_surface_quality_gate.py --help`
- S206 S191 gate run with `--min-stable-ratio 1.0`
- S206 render bridge dry-run with S205 annotated sequence
- Python JSON inspection confirming bridge summary and scene spec preserve
  `water_mesh_surface_quality`
- `git diff --check`

## Next

S207 can safely add a label-driven render treatment because S206 gives a
baseline no-op gate. Start with a conservative normal/continuity treatment for
`normal_rough` frames or a component treatment gated only to
`component_fragmented` frames, and require the S206 gate to remain passing for
the accepted S191 window.
