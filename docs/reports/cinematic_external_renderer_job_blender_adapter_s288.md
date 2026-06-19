# S288 External Renderer Job Blender Adapter

Generated UTC: `2026-06-19T20:43:20Z`
Source job: `build/shots/s285_external_renderer_job/external_renderer_job.json`
Dry-run directory: `build/shots/s288_external_renderer_job_blender_adapter/dry`
Bridge summary: `build/shots/s288_external_renderer_job_blender_adapter/dry/bridge_summary.json`
Scene spec: `build/shots/s288_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`
Driver script: `build/shots/s288_external_renderer_job_blender_adapter/dry/blender_driver.py`

## Command

`python tools/render_bridge_blender.py build/shots/s285_external_renderer_job/external_renderer_job.json build/shots/s288_external_renderer_job_blender_adapter/dry --dry-run --render-preset dam_break_water_mesh_smoothing --frames 8 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 31`

## Result

- Status: `dry_run`
- Frames: `8`
- Resolution: `960 x 540`
- Samples: `12`
- Source window: `0..31`
- Render preset: `dam_break_water_mesh_smoothing`
- First water mesh faces: `20000`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- First render-data source frame: `20`
- Camera path target distance:
  `26.261378486286667..29.63448160504921`

## Decision

S288 proves the S285 renderer job can be adapted into the existing Blender
bridge scene-spec format without going back through the older converted
sequence entry point.

## Next

Run a bounded Blender render from the S288 job path, then compare it against
the S282 accepted high-resolution bridge review.
