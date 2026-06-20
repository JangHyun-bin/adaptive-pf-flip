# S442 Mitsuba Light Response Contract LR1 Render Probe

Generated UTC: `2026-06-20T13:07:37.665805+00:00`
Render JSON: `build/shots/s442_mitsuba_light_response_contract_lr1_render/mitsuba_render.json`
Status: `failed`

## Runtime

- Variant: `scalar_rgb`
- SPP: `1`
- Output format: `exr`
- PNG preview: `True`
- DRJIT_LIBLLVM_PATH: `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\x64\bin`

## Inputs

- Mitsuba export: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`

## Checks

- Frames requested: `1`
- Frames rendered: `0`
- Failures: `1`
- Total elapsed ms: `72`
- Image bytes: `0 B`
- Preview bytes: `0 B`

## Frame Samples

| Output | Sequence | Image | Preview | Elapsed ms |
| ---: | ---: | --- | --- | ---: |

## Failures

- `frame_render_error` jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.

## Next

Render LR1 after the Mitsuba/Dr.Jit LLVM runtime path is fixed, then compare target gap against SS1_Native and S417_WP4_H18_D90.
