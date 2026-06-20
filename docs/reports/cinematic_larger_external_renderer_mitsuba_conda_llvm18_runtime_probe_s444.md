# S444 Mitsuba Conda LLVM18 Runtime Probe

Generated UTC: `2026-06-20T13:18:21.454145+00:00`
Diagnostics JSON: `build/reports/s444_mitsuba_conda_llvm18_probe/mitsuba_runtime_diagnostics.json`
Status: `ready`

## Inputs

- Mitsuba export: `build/shots/s442_mitsuba_light_response_contract_lr1/mitsuba_export.json`
- XML scene: `build/shots/s442_mitsuba_light_response_contract_lr1/scenes/frame_0000.xml`

## Checks

- Python candidates: `1`
- LLVM candidates: `2`
- Import-ready Python entries: `1`
- Scene-load-ready entries: `3`
- Render-ready entries: `1`

## Python Probe

| Python | Exit | Result |
| --- | ---: | --- |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | 0 | `ok` |

## Render Probe

| Python | LLVM | Load Exit | Render Exit | Rendered Bytes |
| --- | --- | ---: | ---: | ---: |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `none` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `Rhizome_lsfs_build_envs_llvm18_runtime_Library_bin` | 0 | 1 | 0 |
| `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` | `lsfs_build_envs_llvm18_runtime_Library_bin_LLVM-C_dll` | 0 | 0 | 2307984 |

## Notable Failures

- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`none` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.
- `render` python=`C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe` llvm=`Rhizome_lsfs_build_envs_llvm18_runtime_Library_bin` exit=`1` RuntimeError: jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found! Set the DRJIT_LIBLLVM_PATH environment variable to specify its path.

## Next

If this runtime is render-ready, use it for the S442 LR1 full render and target-gap comparison.
