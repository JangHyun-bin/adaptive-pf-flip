# S321 Larger External Renderer Mitsuba Closeup Render

Generated UTC: `2026-06-19T22:57:28.384050+00:00`
Render JSON: `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1730`
- Image bytes: `22.06 MB`
- Preview bytes: `2.39 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/renders/frame_0000.exr` | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/previews/frame_0000.png` | 215 |
| 27 | 35 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/renders/frame_0004.exr` | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/previews/frame_0004.png` | 206 |
| 47 | 55 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/renders/frame_0007.exr` | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/actual_render/previews/frame_0007.png` | 204 |

## Next

Package and publish this higher-readability actual Mitsuba probe, then tune materials/lighting further if the frame still reads too diagnostic.
