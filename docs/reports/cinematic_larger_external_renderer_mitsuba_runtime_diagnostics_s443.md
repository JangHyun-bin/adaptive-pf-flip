# S443 Mitsuba Runtime Diagnostics

Generated UTC: `2026-06-20T13:13:25.525450+00:00`
Diagnostics JSON: `build/reports/s443_mitsuba_runtime_diagnostics/mitsuba_runtime_diagnostics.json`
Status: `blocked`

## Inputs

- Mitsuba export: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`
- XML scene: `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0000.xml`

## Checks

- Python candidates: `2`
- LLVM candidates: `4`
- Import-ready Python entries: `1`
- Scene-load-ready entries: `5`
- Render-ready entries: `0`

## Python Probe

| Python | Exit | Result |
| --- | ---: | --- |
| `C:\ProgramData\miniconda3\python.exe` | 1 | `failed` |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | 0 | `ok` |

## Render Probe

| Python | LLVM | Load Exit | Render Exit | Rendered Bytes |
| --- | --- | ---: | ---: | ---: |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `none` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `2022_Community_VC_Tools_Llvm_x64_bin` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `vs_2022_Community_VC_Tools_Llvm_bin` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `18_Community_VC_Tools_Llvm_x64_bin` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `vs_18_Community_VC_Tools_Llvm_bin` | 0 | 1 | 0 |

## Notable Failures

- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`none` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`2022_Community_VC_Tools_Llvm_x64_bin` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`vs_2022_Community_VC_Tools_Llvm_bin` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`18_Community_VC_Tools_Llvm_x64_bin` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`vs_18_Community_VC_Tools_Llvm_bin` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.

## Next

Fix or isolate a render-ready Mitsuba runtime, then rerun the S442 LR1 render and image-gap comparison.
