# S171 Render-Data And Depth Export Milestone

## Objective

Add richer per-frame render/depth metadata so later cinematic render passes are
not limited to a flat mesh-plus-secondary handoff.

## Inputs

- Current visual baseline: `dam_break_water_depth_foreground_separation`
- Baseline shot output: `build/shots/s168_water_depth_foreground_separation`
- Baseline report: `docs/reports/cinematic_water_depth_foreground_separation_s168.md`
- Triage report: `docs/reports/cinematic_visual_review_s170.md`

## Scope

- Extend the converted render-cache sequence or adjacent metadata with bounded
  water/depth fields derived from existing cache contents.
- Preserve the current `sequence.json`, mesh, secondary channel, report, and
  gallery flows unless a narrow schema addition is required.
- Include enough metadata for later render passes to distinguish:
  - water volume region bounds,
  - approximate depth range or layer samples,
  - liquid/air/secondary channel counts,
  - camera/reference grid context.
- Add a validation or summary tool/report that proves the metadata is present
  and numerically sane.

## Non-Goals

- Do not replace Blender rendering in this milestone.
- Do not add a new volumetric renderer yet.
- Do not rerender the full S168 shot unless the export metadata must be proven
  in a render artifact.
- Do not change simulation physics.

## Candidate Implementation

- Add a sidecar file such as `render_data_summary.json` under the converted shot
  directory, or add a backward-compatible `render_data` section to
  `sequence.json`.
- Reuse existing cache manifest and water reconstruction data instead of reading
  raw particles repeatedly where possible.
- Add a checked-in report, tentatively
  `docs/reports/cinematic_render_data_depth_export_s171.md`.

## Acceptance Gate

- Existing S168 gallery/report artifacts remain valid.
- New render-data metadata is generated for S168 without rerunning simulation.
- The metadata includes per-frame or summary bounds/depth/channel values and
  passes sanity checks.
- A checked-in report records the schema, generated files, metrics, and next
  renderer-facing recommendation.

## Result

S171 added `tools/export_render_data_summary.py`.

Generated S168 sidecar:

```powershell
python tools\export_render_data_summary.py build\shots\s168_water_depth_foreground_separation --out build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --report docs\reports\cinematic_render_data_depth_export_s171.md
```

Output:

- Status: `ok`
- Render frames: `36`
- Sidecar: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- Report: `docs/reports/cinematic_render_data_depth_export_s171.md`

Sidecar coverage:

- Cache frames: `56`
- Converted frames: `56`
- Render frames: `36`
- Water bounds min/max: `[0.0, 0.0, 0.0]` / `[36.0, 18.0, 28.0]`
- Secondary bounds min/max: `[0.8209928534387421, 1.8794251318275923, 1.2065613181922015]` / `[34.861209101819036, 11.429350955039258, 27.283772267343274]`
- Water Y-depth span mean: `13.555555555555555`
- Water Z-depth span mean: `26.88888888888889`
- Phase-field liquid volume mean: `3352.0731566816607`
- Water mesh face count mean: `19426.222222222223`
- Secondary total count mean: `342.80555555555554`

Sanity checks:

- `render_frame_count_positive`: `True`
- `all_frames_have_water_bounds`: `True`
- `all_frames_have_mesh_faces`: `True`
- `all_frames_have_secondary_counts`: `True`
- `source_frames_are_monotonic`: `True`

Next:

- S172: consume this sidecar in a depth/profile diagnostic artifact before
  wiring it into render behavior.
