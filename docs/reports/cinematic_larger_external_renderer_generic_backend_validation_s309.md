# S309 Larger External Renderer Generic Backend Validation

Generated UTC: `2026-06-19T21:57:24.579341+00:00`
Validation JSON: `build/shots/s309_larger_external_renderer_generic_backend_validation/backend_validation.json`
Status: `ready`
Target renderer: `generic_path_tracer`
Renderer command: `generic_path_tracer`
Renderer executable found: `False`
Renderer executable required: `False`

## Adapter Manifest

- Manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`

## Checks

- Frames: `48`
- Scene descriptors read: `48`
- Command count: `48`
- Command mismatches: `0`
- Output frames sequential: `True`
- Failures: `0`
- Warnings: `1`
- Referenced asset bytes: `2.05 GB`

## Supported Encodings

- `csv`
- `json_camera`
- `obj`

## Frame Samples

| Output | Scene Descriptor | Asset Bytes | Water Faces | Secondary Total |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s308_larger_external_renderer_generic_adapter/scenes/frame_0000_scene.json` | 46018874 | 20000 | 256 |
| 24 | `build/shots/s308_larger_external_renderer_generic_adapter/scenes/frame_0024_scene.json` | 45732399 | 17912 | 256 |
| 47 | `build/shots/s308_larger_external_renderer_generic_adapter/scenes/frame_0047_scene.json` | 46237934 | 22300 | 964 |

## Warnings

- `renderer_executable_missing`

## Next

Add a renderer-specific adapter backend that maps the validated scene descriptors into an actual renderer scene format or command invocation.
