# S172 Render-Data Consumer Diagnostics

## Objective

Consume the S171 render-data sidecar in a lightweight diagnostic artifact before
wiring the metadata into new render behavior.

## Inputs

- Sidecar: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- S171 report: `docs/reports/cinematic_render_data_depth_export_s171.md`
- Visual baseline: `build/shots/s168_water_depth_foreground_separation`

## Scope

- Add a small diagnostic tool or report path that reads
  `render_data_summary.json`.
- Produce a human-readable depth/profile artifact from the sidecar:
  - per-frame water bounds/depth spans,
  - mesh face count trend,
  - secondary total count trend,
  - source-frame mapping.
- Keep it independent from Blender rendering.
- Use the artifact to decide how the next renderer pass should consume depth
  metadata.

## Non-Goals

- Do not rerender S168.
- Do not change render visuals yet.
- Do not parse raw cache JSONL again if the sidecar has the needed data.

## Acceptance Gate

- Diagnostic artifact is generated from the S171 sidecar.
- It records enough per-frame trends to guide the next render-data consumer
  implementation.
- A checked-in report records findings and selected next step.

## Result

S172 added `tools/render_data_profile_diagnostics.py`.

Generated diagnostics:

```powershell
python tools\render_data_profile_diagnostics.py build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --out-dir build\shots\s168_water_depth_foreground_separation\diagnostics\render_data_profile --report docs\reports\cinematic_render_data_profile_diagnostics_s172.md
```

Output:

- Status: `ok`
- Frames: `36`
- CSV: `build/shots/s168_water_depth_foreground_separation/diagnostics/render_data_profile/render_data_profile.csv`
- SVG: `build/shots/s168_water_depth_foreground_separation/diagnostics/render_data_profile/render_data_profile.svg`
- Summary: `build/shots/s168_water_depth_foreground_separation/diagnostics/render_data_profile/render_data_profile_summary.json`
- Report: `docs/reports/cinematic_render_data_profile_diagnostics_s172.md`

Trend summary:

- Water Y span: min `11.0`, mean `13.555555555555555`, max `18.0`, delta `-6.0`
- Water Z span: min `23.0`, mean `26.88888888888889`, max `28.0`, delta `5.0`
- Mesh faces: min `17720.0`, mean `19426.222222222223`, max `22300.0`, delta `4060.0`
- Secondary total count: min `256.0`, mean `342.80555555555554`, max `964.0`, delta `708.0`

Findings:

- Water Z-depth span is near the full grid depth for much of the shot, so a
  renderer can use this sidecar to separate foreground and background water more
  deliberately.
- Mesh face counts remain high and stable enough for a metadata-driven render
  pass without re-reading raw cache JSONL.
- Secondary counts rise late in the shot, so depth-aware secondary attenuation
  should be frame dependent rather than a single constant.

Next:

- S173: consume `render_data_summary.json` in the Blender bridge as a bounded
  metadata-driven depth/secondary attenuation pass, then compare against S168
  without rerunning simulation.
