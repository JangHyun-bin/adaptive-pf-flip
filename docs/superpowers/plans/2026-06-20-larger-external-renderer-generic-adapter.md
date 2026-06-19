# S308 Larger External Renderer Generic Adapter

## Goal

Add a renderer-neutral adapter manifest path so the larger external renderer job
is no longer tied only to Blender.

## Scope

- Add `tools/build_external_renderer_adapter_manifest.py`.
- Read `lsfs_external_renderer_job` manifests.
- Emit one renderer-neutral scene descriptor JSON per selected frame.
- Emit a placeholder command list for a target renderer.
- Preserve required camera, water mesh, phase volume, and particle stream asset
  contracts.
- Include material/channel contracts for water surface, phase volume, spray,
  foam, bubbles, and droplets.
- Validate missing assets, monotonic frame order, and minimum water mesh faces.
- Run the adapter on the S295 larger 48-frame job.

## Result

- Tool:
  `tools/build_external_renderer_adapter_manifest.py`
- Adapter manifest:
  `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list:
  `build/shots/s308_larger_external_renderer_generic_adapter/render_commands.txt`
- Report:
  `docs/reports/cinematic_larger_external_renderer_generic_adapter_s308.md`
- Target renderer: `generic_path_tracer`
- Status: `ready`
- Frames: `48`
- Scene descriptors: `48`
- Missing assets: `0`
- Minimum water mesh faces: `17720`
- Referenced asset footprint: `2.05 GB`

## Decision

S308 establishes the non-Blender adapter contract without invoking an offline
renderer. The next backend can consume the generated scene descriptors instead
of reverse-engineering the Blender bridge.

## Next

Implement a renderer-specific dry-run validator that consumes the S308 scene
descriptors and validates command resolution, output paths, and supported asset
encodings before invoking a real offline renderer.
