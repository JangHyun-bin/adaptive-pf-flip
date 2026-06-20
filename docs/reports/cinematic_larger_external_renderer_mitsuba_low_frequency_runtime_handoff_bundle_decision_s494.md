# S494 Mitsuba Low Frequency Runtime Handoff Bundle Decision

Generated UTC: `2026-06-20T18:20:00Z`

## Decision

Promote the S494 Mitsuba low-frequency runtime handoff bundle as the portable integration artifact for the next production renderer UI/export step.

This closes the previous gap where the WebGL proof, shader contract, texture package, oracle frames, proof frames, and reports existed as separate build artifacts. S494 now packages them behind one manifest and one validator result.

## Evidence

- Bundle report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_runtime_handoff_bundle_s494.md`
- Validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_runtime_handoff_bundle_validation_s494.md`
- Bundle manifest: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json`
- Validation JSON: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle_validation.json`

## Key Checks

- Bundle status: `ready`
- Frames: `8`
- Copied files: `66`
- Missing references: `0`
- Validator status: `passed`
- Validator checks: `161`
- Validator failures: `0`
- WebGL proof max oracle abs diff: `0`
- WebGL proof max oracle mean diff: `0.0`
- Target-gap mean MAD: `19.144350646219134`
- Target-gap max MAD: `23.95285943930041`
- Target-gap max abs diff: `214`

## Interpretation

S494 is not another visual tweak. It is a runtime handoff boundary: a renderer-facing bundle can now consume the post-tonemap low-frequency correction contract, its texture bindings, shader references, proof gallery, and validation metadata without rediscovering the earlier S489-S493 build tree.

The validator also proves that the copied files match their source hashes and that the WebGL proof remains exactly parity-equivalent to the CPU oracle at the current handoff boundary.

## Next Step

S495 should consume this bundle from a production-style preview/export path instead of reading scattered source artifacts. The useful gate is a small runtime-import check that loads only `runtime_handoff_bundle.json`, reconstructs the preview frame list, and verifies that a UI or external renderer integration can discover all required bindings from the bundle alone.
