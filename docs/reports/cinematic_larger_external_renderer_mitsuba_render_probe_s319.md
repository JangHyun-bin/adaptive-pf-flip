# S319 Larger External Renderer Mitsuba Render Probe

Generated UTC: `2026-06-19T22:48:30.675754+00:00`
Render JSON: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_export.json`

## Checks

- Frames requested: `3`
- Frames rendered: `3`
- Failures: `0`
- Total elapsed ms: `377`
- Image bytes: `3.04 MB`
- Preview bytes: `387.82 KB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/renders/frame_0000.exr` | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/previews/frame_0000.png` | 132 |
| 24 | 32 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/renders/frame_0001.exr` | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/previews/frame_0001.png` | 109 |
| 47 | 55 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/renders/frame_0002.exr` | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/previews/frame_0002.png` | 103 |

## Next

Scale this Python API path beyond the 3-frame spp=1 probe, then package/publish the rendered preview.
