# S319 Larger External Renderer Mitsuba Command Validation

Generated UTC: `2026-06-19T22:45:15.011032+00:00`
Validation JSON: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_validation.json`
Status: `ready`

## Mitsuba

- Command: `build\s319_mitsuba_venv\Scripts\mitsuba.exe`
- Found: `True`
- Required: `True`
- Path: `build\s319_mitsuba_venv\Scripts\mitsuba.exe`

## Export

- Export manifest: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_export.json`

## Checks

- Frames: `48`
- XML parsed: `48`
- Command count: `48`
- OBJ shapes: `48`
- Sphere shapes: `7680`
- BSDFs: `288`
- Failures: `0`
- Warnings: `0`

## Frame Samples

| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0000.xml` | 1 | 160 | 6 |
| 24 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0024.xml` | 1 | 160 | 6 |
| 47 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0047.xml` | 1 | 160 | 6 |

## Next

Run the Python API render probe with DRJIT_LIBLLVM_PATH set to the Visual Studio LLVM-C.dll.
