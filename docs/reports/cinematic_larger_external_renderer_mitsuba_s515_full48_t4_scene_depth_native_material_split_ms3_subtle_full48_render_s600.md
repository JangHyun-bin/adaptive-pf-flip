# S600 Scene Depth Native Material Split MS3 Subtle Full48 Render

Generated UTC: `2026-06-20T23:45:39.437026+00:00`
Render JSON: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/mitsuba_export.json`

## Checks

- Frames requested: `48`
- Frames rendered: `48`
- Failures: `0`
- Total elapsed ms: `10307`
- Image bytes: `137.83 MB`
- Preview bytes: `17.13 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/renders/frame_0000.exr` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/previews/frame_0000.png` | 296 |
| 24 | 32 | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/renders/frame_0024.exr` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/previews/frame_0024.png` | 202 |
| 47 | 55 | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/renders/frame_0047.exr` | `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/previews/frame_0047.png` | 196 |

## Next

Build a gallery and compute full48 direct S577/S585 metrics before deciding whether S599 scales beyond the 8-frame sample.
