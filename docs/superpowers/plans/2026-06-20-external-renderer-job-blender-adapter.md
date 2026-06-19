# S288 External Renderer Job Blender Adapter

## Goal

Connect the S285 external renderer job schema to the existing Blender bridge
scene-spec path.

## Scope

- Extend `tools/render_bridge_blender.py` so `src` can be either:
  - S38 converted `sequence.json`
  - `lsfs_external_renderer_job`
- Preserve the existing converted-sequence behavior.
- Load job frame camera JSON, particle CSV, water mesh OBJ, render-data
  metadata, and surface-quality metadata.
- Fall back to job frame render-data when no separate render-data summary is
  supplied.
- Run a dry-run scene-spec build from S285 with the accepted
  `dam_break_water_mesh_smoothing` preset.

## Result

- Updated tool:
  `tools/render_bridge_blender.py`
- Dry-run summary:
  `build/shots/s288_external_renderer_job_blender_adapter/dry/bridge_summary.json`
- Scene spec:
  `build/shots/s288_external_renderer_job_blender_adapter/dry/blender_scene_spec.json`
- Driver:
  `build/shots/s288_external_renderer_job_blender_adapter/dry/blender_driver.py`
- Report:
  `docs/reports/cinematic_external_renderer_job_blender_adapter_s288.md`
- Status: `dry_run`
- Frames: `8`
- Resolution: `960 x 540`
- Samples: `12`
- Source window: `0..31`

## Decision

S288 makes the job schema renderer-specific for Blender without duplicating the
Blender bridge. It remains a dry-run adapter gate; the next step is a bounded
actual Blender render through the job path.

## Next

Render a short bounded Blender sequence from the S285 job path and compare it
against S282.
