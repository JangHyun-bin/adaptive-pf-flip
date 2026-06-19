# S298 Larger External Renderer Job Blender Adapter

## Goal

Validate that the S295 48-frame larger renderer job can feed the Blender bridge
scene-spec path.

## Scope

- Use `tools/render_bridge_blender.py`.
- Source: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`.
- Run dry-run only.
- Use accepted `dam_break_water_mesh_smoothing` preset.
- Sample `12` Blender frames from source window `0..47`.
- Write bridge summary, scene spec, and driver script.

## Result

- Dry-run summary:
  `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/bridge_summary.json`
- Scene spec:
  `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`
- Driver:
  `build/shots/s298_larger_external_renderer_job_blender_adapter/dry/blender_driver.py`
- Report:
  `docs/reports/cinematic_larger_external_renderer_job_blender_adapter_s298.md`
- Status: `dry_run`
- Frames: `12`
- Resolution: `960 x 540`
- Samples: `12`
- Source window: `0..47`

## Decision

S298 is the Blender adapter gate for the larger job path. It confirms the
larger job can become a Blender scene spec without falling back to the older
converted-sequence input.

## Next

Render a bounded 12-frame Blender sample from S295 and compare it against the
current full32 proof.
