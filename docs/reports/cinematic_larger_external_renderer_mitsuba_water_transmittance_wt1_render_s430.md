# S430 Mitsuba Water Transmittance WT1 Render

Generated UTC: `2026-06-20T12:06:14.015633+00:00`
Render JSON: `build/shots/s430_mitsuba_water_transmittance_wt1_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s430_mitsuba_water_transmittance_wt1/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1767`
- Image bytes: `20.20 MB`
- Preview bytes: `2.55 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s430_mitsuba_water_transmittance_wt1_render/renders/frame_0000.exr` | `build/shots/s430_mitsuba_water_transmittance_wt1_render/previews/frame_0000.png` | 327 |
| 27 | 35 | `build/shots/s430_mitsuba_water_transmittance_wt1_render/renders/frame_0004.exr` | `build/shots/s430_mitsuba_water_transmittance_wt1_render/previews/frame_0004.png` | 176 |
| 47 | 55 | `build/shots/s430_mitsuba_water_transmittance_wt1_render/renders/frame_0007.exr` | `build/shots/s430_mitsuba_water_transmittance_wt1_render/previews/frame_0007.png` | 189 |

## Next

Scale the Mitsuba render path to a longer frame range and package the visual output.
