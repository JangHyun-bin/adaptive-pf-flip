# S426 Mitsuba Phase Volume Proxy PV1 Render

Generated UTC: `2026-06-20T11:47:38.425909+00:00`
Render JSON: `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/mitsuba_render.json`
Status: `ready`

## Runtime

- Variant: `scalar_rgb`
- SPP: `1`
- Output format: `exr`
- PNG preview: `True`
- DRJIT_LIBLLVM_PATH: `C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll`

## Supervisor

- Worker exit code: `3221226505`
- Accepted ready manifest: `True`

## Inputs

- Mitsuba export: `build/shots/s426_mitsuba_phase_volume_proxy_pv1/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1383`
- Image bytes: `19.27 MB`
- Preview bytes: `2.27 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/renders/frame_0000.exr` | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/previews/frame_0000.png` | 203 |
| 27 | 35 | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/renders/frame_0004.exr` | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/previews/frame_0004.png` | 157 |
| 47 | 55 | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/renders/frame_0007.exr` | `build/shots/s426_mitsuba_phase_volume_proxy_pv1_render/previews/frame_0007.png` | 158 |

## Next

Compare PV1 to the renderer target and decide whether phase-volume proxies should be tuned or replaced with a smoother volume material.
