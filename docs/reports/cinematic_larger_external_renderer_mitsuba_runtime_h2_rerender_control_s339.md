# S339 Mitsuba Runtime H2 Rerender Control

Generated UTC: `2026-06-20T00:42:08.898101+00:00`
Render JSON: `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s333_mitsuba_secondary_halo_h2/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1811`
- Image bytes: `20.78 MB`
- Preview bytes: `2.35 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/renders/frame_0000.exr` | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/previews/frame_0000.png` | 235 |
| 27 | 35 | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/renders/frame_0004.exr` | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/previews/frame_0004.png` | 208 |
| 47 | 55 | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/renders/frame_0007.exr` | `build/shots/s339_mitsuba_runtime_h2_rerender_control/actual_render/previews/frame_0007.png` | 208 |

## Next

Compare this H2 rerender against the S335 contract to detect runtime drift.
