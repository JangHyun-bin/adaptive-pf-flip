# S616 Mitsuba Response Buffer Base-Only Render

Generated UTC: `2026-06-21T01:55:50.591652+00:00`
Render JSON: `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/mitsuba_render.json`
Status: `ready`

## Runtime

- Variant: `scalar_rgb`
- SPP: `4`
- Output format: `exr`
- PNG preview: `True`
- DRJIT_LIBLLVM_PATH: `C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll`

## Supervisor

- Worker exit code: `3221226505`
- Accepted ready manifest: `True`

## Inputs

- Mitsuba export: `build/shots/s616_mitsuba_response_delta_buffer_probe/base_only/mitsuba_base_export.json`

## Checks

- Frames requested: `None`
- Frames rendered: `48`
- Failures: `0`
- Total elapsed ms: `10538`
- Image bytes: `133.88 MB`
- Preview bytes: `15.34 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/renders/frame_0000.exr` | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/previews/frame_0000.png` | 421 |
| 24 | 32 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/renders/frame_0024.exr` | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/previews/frame_0024.png` | 185 |
| 47 | 55 | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/renders/frame_0047.exr` | `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/previews/frame_0047.png` | 212 |

## Next

Subtract this base render from the S614 split full render to inspect and scale response contribution.
