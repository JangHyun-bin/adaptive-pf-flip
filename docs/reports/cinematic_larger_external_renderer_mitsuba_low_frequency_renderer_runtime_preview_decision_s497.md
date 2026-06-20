# S497 Mitsuba Low Frequency Renderer Runtime Preview Decision

Generated UTC: `2026-06-20T18:38:00Z`

## Decision

Promote S497 as the renderer-side runtime consumer gate for the Mitsuba low-frequency post-tonemap correction path.

S495 proved the import manifest can be loaded. S496 made that state publicly inspectable. S497 now proves a renderer-side preview/export consumer can read `runtime_import_preview.json`, bind the required runtime textures, regenerate corrected frames, and match both the oracle and WebGL proof outputs exactly.

## Evidence

- Runtime preview report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_renderer_runtime_preview_s497.md`
- Runtime preview validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_renderer_runtime_preview_validation_s497.md`
- Runtime preview summary: `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime_preview_summary.json`
- Runtime validation JSON: `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime_preview_validation.json`
- Runtime gallery: `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/gallery/index.html`
- Source import preview: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`

## Key Checks

- Runtime preview status: `ready`
- Validation status: `passed`
- Validation checks: `103`
- Validation failures: `0`
- Source frames: `8`
- Generated frames: `8`
- Missing references: `0`
- Dimension mismatches: `0`
- Max oracle abs diff: `0`
- Max oracle mean diff: `0.0`
- Max WebGL abs diff: `0`
- Max WebGL mean diff: `0.0`
- Runtime GIF bytes: `1191221`
- Runtime strip GIF bytes: `5633729`

## Interpretation

This is the first step after S494-S496 where the low-frequency correction is no longer only packaged or displayed. It is consumed by a renderer-side preview runner from the same import manifest that a production integration would receive.

The implementation is still a deterministic software preview path, not a full Mitsuba shader/backend integration. The integration boundary is now clear: the production renderer should reproduce the S497 binding and compositing contract, then pass the same oracle/WebGL parity checks.

## Next Step

S498 should turn the S497 consumer into an integration acceptance package: include the runtime preview summary, validation JSON, shader entrypoints, public S496 URL, and explicit pass/fail thresholds in one handoff manifest for the production renderer/export runner.
