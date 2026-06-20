# S442 Mitsuba Light Response Contract LR1 Decision

Generated UTC: `2026-06-20T13:08:00+00:00`

## Decision

Keep the LR1 contract consumer as the next Mitsuba visual-quality candidate. The export and XML validation path is ready; image rendering is blocked by the local Mitsuba/Dr.Jit LLVM runtime, not by malformed scene XML.

## Evidence

- Consumer tool: `tools/add_mitsuba_light_response_contract.py`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_light_response_contract_lr1_export_s442.md`
- Validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_light_response_contract_lr1_validate_s442.md`
- Render probe report: `docs/reports/cinematic_larger_external_renderer_mitsuba_light_response_contract_lr1_render_s442.md`

## Export Result

- Status: `ready`
- Frames exported: `8`
- Contract frames matched: `8`
- Anchors consumed: `49`
- Lights inserted: `49`
- Localized anchors: `49`
- XML scene bytes: `1.37 MB`

## Validation Result

- Status: `ready`
- XML parsed: `8`
- Failures: `0`
- Warnings: `0`
- OBJ shapes: `8`
- Sphere shapes: `2926`

## Render Runtime Blocker

The repository default `python` is the conda environment and cannot import `mitsuba`. Python 3.11 has `mitsuba==3.8.0` and `drjit==1.3.1`, but the render probe still fails during Dr.Jit LLVM backend startup:

`jit_init_thread_state(): the LLVM backend is inactive because the LLVM shared library ("LLVM-C.dll") could not be found`

The probe set `DRJIT_LIBLLVM_PATH` to `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\Llvm\x64\bin`. Directly pointing to `LLVM-C.dll` caused the process to terminate before writing a report, so this looks like a local Dr.Jit/LLVM compatibility or loader issue rather than an LSFS XML export issue.

## Next

Fix or isolate the Mitsuba runtime path, then render the existing LR1 export without changing the LSFS consumer. After a successful render, compare LR1 against `SS1_Native`, `S401_CR21_Profile`, and `S417_WP4_H18_D90` before tuning radiance strength.
