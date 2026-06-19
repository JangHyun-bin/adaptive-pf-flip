# S298 Larger External Renderer Job Blender Adapter

Generated UTC: `2026-06-19T21:13:06Z`
Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
Dry-run directory: `build/shots/s298_larger_external_renderer_job_blender_adapter/dry`
Bridge summary: `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/bridge_summary.json`
Scene spec: `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`
Driver script: `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/blender_driver.py`

## Command

`python tools/render_bridge_blender.py build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json build/shots/s298_larger_external_renderer_job_blender_adapter/dry --dry-run --render-preset dam_break_water_mesh_smoothing --frames 12 --width 960 --height 540 --samples 12 --source-start-index 0 --source-end-index 47`

## Result

- Status: `dry_run`
- Frames: `12`
- Resolution: `960 x 540`
- Samples: `12`
- Source window: `0..47`
- Selected source frames: `48`
- Render preset: `dam_break_water_mesh_smoothing`
- Camera target distance:
  `26.261378486286667..29.63448160504921`
- First water mesh faces: `20000`
- Middle water mesh faces: `18576`
- Last water mesh faces: `22300`
- First secondary total: `256`
- Last secondary total: `964`
- First render-data source frame: `20`
- Last render-data source frame: `55`

## Decision

S298 proves the 48-frame S295 larger renderer job can be adapted into the
existing Blender scene-spec path before doing heavier Blender rendering.

## Next

Render a bounded 12-frame Blender sample from S295, then compare it against
S291/S282 before attempting a full 48-frame Blender run.
