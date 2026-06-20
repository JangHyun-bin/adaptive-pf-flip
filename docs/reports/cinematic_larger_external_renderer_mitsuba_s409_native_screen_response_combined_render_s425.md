# S425 Mitsuba S409 Native Screen Response Combined Render

Generated UTC: `2026-06-20T11:43:40.226598+00:00`
Render JSON: `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/mitsuba_render.json`
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

- Mitsuba export: `build/shots/s425_mitsuba_s409_native_screen_response_combined/mitsuba_export.json`

## Checks

- Frames requested: `8`
- Frames rendered: `8`
- Failures: `0`
- Total elapsed ms: `1510`
- Image bytes: `17.01 MB`
- Preview bytes: `2.02 MB`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |
| 0 | 8 | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/renders/frame_0000.exr` | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/previews/frame_0000.png` | 280 |
| 27 | 35 | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/renders/frame_0004.exr` | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/previews/frame_0004.png` | 158 |
| 47 | 55 | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/renders/frame_0007.exr` | `build/shots/s425_mitsuba_s409_native_screen_response_combined_render/previews/frame_0007.png` | 170 |

## Next

Compare the combined native screen response to the renderer target; keep it only if it improves over SS1 or exposes a clear native bridge direction.
