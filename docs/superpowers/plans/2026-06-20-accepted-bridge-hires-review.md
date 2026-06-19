# S282 Accepted Bridge HiRes Review

## Goal

Validate the current accepted S269 bridge-render preset at a higher presentation
resolution while keeping the same 32-frame source window.

## Scope

- Use `dam_break_water_mesh_smoothing`.
- Keep source window `8..55` and frame count `32`.
- Render with Blender at `960 x 540`, `12` samples.
- Compare against the S269 accepted `640 x 360`, `16` sample bridge render.
- Build a review gallery.
- Do not change simulation, sequence conversion, render-data summary, camera,
  lighting, materials, or accepted preset settings.

## Validation

- Dry-run:
  `build/shots/s282_accepted_bridge_hires_review/dry`
- Surface-quality gate:
  `build/shots/s282_accepted_bridge_hires_review/mixed_gate/water_mesh_surface_quality_gate_summary.json`
- Blender render:
  `build/shots/s282_accepted_bridge_hires_review/blender`
- S269 comparison:
  `build/shots/s282_accepted_bridge_hires_review/comparison_s269`
- Gallery:
  `build/shots/s282_accepted_bridge_hires_review/gallery/index.html`

## Result

- Dry-run status: `ok`
- Surface gate: `passed`
- Surface labels: `normal_rough: 3`, `stable: 29`
- Render frames: `32`
- Resolution: `960 x 540`
- Samples: `12`
- Mean luminance delta vs S269: `-0.0636576033227243`
- Minimum contrast delta vs S269: `-9.0`
- Mean frame contrast delta vs S269: `1.65625`
- Bright ratio delta vs S269: `-2.1595896026234559e-05`
- Highlight ratio delta vs S269: `-2.2937162422839529e-05`
- Nonblank ratio delta vs S269: `0.0`
- Mean luma p95 delta: `-0.21875`
- Mean luma p99 delta: `2.8125`
- Mean luma p99.5 delta: `4.25`
- Specular ratio delta: approximately `0.0`

## Decision

Accept S282 as the higher-resolution bridge-render review artifact. The
coverage and motion read are preserved, broad bright/highlight pressure drops,
and the higher-resolution output is visibly sharper. The `-9.0` minimum
contrast delta is recorded as a local/resolution-related change rather than an
accepted-preset regression because mean contrast rises and nonblank coverage is
unchanged.

## Next

Package and publish S282 as the current high-resolution bridge review endpoint
if external review should use the sharper artifact instead of the S269 640 x
360 accepted gallery.
