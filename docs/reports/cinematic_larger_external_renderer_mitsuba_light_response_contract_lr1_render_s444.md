# S444 Mitsuba Light Response Contract LR1 Render

Generated UTC: `2026-06-20T13:18:51.485342+00:00`
Render JSON: `build/shots/s444_mitsuba_light_response_contract_lr1_render/mitsuba_render.json`
Status: `ready`

## Runtime

- Variant: `scalar_rgb`
- SPP: `12`
- Output format: `exr`
- PNG preview: `True`
- DRJIT_LIBLLVM_PATH: `D:\HB\Rhizome\lsfs\build\envs\llvm18_runtime\Library\bin\LLVM-C.dll`

## Supervisor

- Worker exit code: `3221226505`
- Accepted ready manifest: `True`

## Inputs

- Mitsuba export: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `3239`
- Image bytes: `22.35 MB`
- Preview bytes: `1.91 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s444_mitsuba_light_response_contract_lr1_render/renders/frame_0000.exr` | `build/shots/s444_mitsuba_light_response_contract_lr1_render/previews/frame_0000.png` | 374 |
| 27 | 35 | `build/shots/s444_mitsuba_light_response_contract_lr1_render/renders/frame_0004.exr` | `build/shots/s444_mitsuba_light_response_contract_lr1_render/previews/frame_0004.png` | 395 |
| 47 | 55 | `build/shots/s444_mitsuba_light_response_contract_lr1_render/renders/frame_0007.exr` | `build/shots/s444_mitsuba_light_response_contract_lr1_render/previews/frame_0007.png` | 419 |

## Next

Compare LR1 render frames against target preview, SS1_Native, S401_CR21_Profile, and S417_WP4_H18_D90; then tune radiance or switch to volume/glint metadata.
