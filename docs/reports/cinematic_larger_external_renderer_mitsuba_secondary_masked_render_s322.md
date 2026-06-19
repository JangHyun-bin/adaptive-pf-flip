# S322 Larger External Renderer Mitsuba Secondary Masked Render

Generated UTC: `2026-06-19T23:06:59.796350+00:00`
Render JSON: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1784`
- Image bytes: `22.42 MB`
- Preview bytes: `2.44 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/renders/frame_0000.exr` | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0000.png` | 213 |
| 27 | 35 | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/renders/frame_0004.exr` | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0004.png` | 220 |
| 47 | 55 | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/renders/frame_0007.exr` | `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0007.png` | 207 |

## Next

Package and publish this masked secondary proof if it is visually no worse than S321 and keeps secondary particles readable.
