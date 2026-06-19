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
