# S309 Larger External Renderer Generic Backend Validation

## Goal

Add a dry-run backend validation gate for the S308 renderer-neutral adapter
manifest.

## Scope

- Add `tools/validate_external_renderer_adapter_manifest.py`.
- Validate `lsfs_external_renderer_adapter_manifest` inputs.
- Read every scene descriptor JSON.
- Verify required camera, water surface, phase volume, and particle stream
  assets.
- Verify supported encodings: `json_camera`, `obj`, and `csv`.
- Verify command-list count and scene/output path matching.
- Verify output frame ordering.
- Treat a missing renderer executable as a warning unless `--require-renderer`
  is set.
- Run the validator on the S308 full48 adapter manifest.

## Result

- Tool:
  `tools/validate_external_renderer_adapter_manifest.py`
- Validation JSON:
  `build/shots/s309_larger_external_renderer_generic_backend_validation/backend_validation.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_generic_backend_validation_s309.md`
- Status: `ready`
- Frames: `48`
- Scene descriptors read: `48`
- Command count: `48`
- Command mismatches: `0`
- Failures: `0`
- Warnings: `1`
- Warning: `renderer_executable_missing`
- Referenced asset bytes: `2.05 GB`

## Decision

S309 proves the S308 scene descriptor contract is internally consumable by a
backend adapter. The only warning is expected because `generic_path_tracer` is a
placeholder command, not an installed renderer.

## Next

Add a renderer-specific adapter backend that maps validated scene descriptors
into a concrete scene format or command invocation.
