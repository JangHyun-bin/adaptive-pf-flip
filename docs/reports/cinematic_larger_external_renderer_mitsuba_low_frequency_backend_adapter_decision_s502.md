# S502 Mitsuba Low Frequency Backend Adapter Decision

Generated UTC: `2026-06-20T18:58:00Z`

## Decision

Promote S502 as the first backend-adapter skeleton for the Mitsuba low-frequency renderer job path.

S502 consumes the S499 `renderer_job_manifest.json` and emits backend scene descriptors plus a command list. Each descriptor carries the texture bindings, shader references, accepted reference frame, output targets, and zero-diff validation expectations needed by a renderer-specific implementation.

## Evidence

- Backend adapter report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_backend_adapter_s502.md`
- Backend adapter validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_backend_adapter_validation_s502.md`
- Backend adapter manifest: `build/shots/s502_mitsuba_low_frequency_backend_adapter/backend_adapter_manifest.json`
- Backend adapter validation JSON: `build/shots/s502_mitsuba_low_frequency_backend_adapter/backend_adapter_validation.json`
- Command list: `build/shots/s502_mitsuba_low_frequency_backend_adapter/backend_commands.txt`
- Scene descriptor sample: `build/shots/s502_mitsuba_low_frequency_backend_adapter/scenes/frame_0000_backend_scene.json`
- Source job: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest.json`

## Key Checks

- Adapter status: `ready`
- Validation status: `passed`
- Validation checks: `185`
- Validation failures: `0`
- Source job status: `ready`
- Frames: `8`
- Scene descriptors: `8`
- Required inputs present: `24`
- Required inputs total: `24`
- Missing inputs: `0`
- Missing shaders: `0`
- Reference hash mismatches: `0`
- Output targets: `24`
- Scene descriptor bytes: `38345`

## Interpretation

S502 is not a native backend renderer yet. It is the contract-preserving adapter skeleton that a Mitsuba or external path-tracer backend can implement next.

The useful movement is that the pipeline now has a stable handoff sequence:
S498 acceptance package -> S499 renderer job manifest -> S500 executable dry run -> S502 backend scene descriptors.

## Next Step

S503 should add a backend descriptor dry-run executor that reads the S502 scene descriptors and reproduces the S500 outputs through the descriptor layer, proving the backend adapter contract is executable before swapping in a real renderer process.
