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
