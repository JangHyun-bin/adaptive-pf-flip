# S495 Mitsuba Low Frequency Runtime Import Preview Decision

Generated UTC: `2026-06-20T18:28:00Z`

## Decision

Promote S495 as the renderer UI/export import gate for the S494 low-frequency runtime handoff bundle.

The important change is direction of dependency: S495 consumes only `runtime_handoff_bundle.json` and reconstructs a UI-facing frame list, runtime bindings, shader references, proof images, and static preview HTML from that bundle. It does not need to rediscover the older S489-S493 source artifacts.

## Evidence

- Import preview report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_runtime_import_preview_s495.md`
- Import preview validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_runtime_import_preview_validation_s495.md`
- Import preview JSON: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`
- Import preview HTML: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/index.html`
- Validation JSON: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview_validation.json`
- Source bundle: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json`

## Key Checks

- Preview status: `ready`
- Validation status: `passed`
- Validation checks: `230`
- Validation failures: `0`
- Frames: `8`
- Ready frames: `8`
- Required bindings per frame: `3`
- Required bindings found: `24`
- Missing required bindings: `0`
- Hash mismatches: `0`
- Size mismatches: `0`
- Dimension mismatches: `0`
- Bundle-local violations: `0`
- Source dependency leaks: `0`
- Proof failures: `0`
- Runtime HTML resolved: `true`
- Shader references resolved: `true`

## Interpretation

S494 proved the portable handoff bundle exists. S495 proves that a consumer can load that bundle as the integration boundary and build a usable preview/import description from it.

This matters for the cinematic target because the renderer UI/export path now has a small, deterministic contract: load one bundle manifest, enumerate frames, bind `base_rgb`, `positive_delta_rgb`, and `negative_delta_rgb`, optionally inspect `dark_damping_weight_luma`, and compare against oracle/WebGL proof assets.

## Next Step

S496 should turn this into a shareable/public review surface: publish the S495 `index.html` preview through the existing static preview or Cloudflare quick-tunnel workflow, then record the reachable URL and HTTP verification. After that, the next production step is to wire this bundle-import manifest into the real renderer-side preview/export runner.
