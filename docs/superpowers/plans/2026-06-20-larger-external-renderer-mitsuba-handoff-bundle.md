# S327 Mitsuba Renderer Handoff Bundle

## Goal

Promote the S325/S326 review contract into a renderer-facing handoff bundle that
can be consumed by future renderer-side secondary and look-development work.

## Scope

- Add `tools/build_mitsuba_renderer_handoff_bundle.py`.
- Read the S325 renderer-review contract.
- Optionally read the S326 validation result and require it to be passed.
- Copy contract, validation, and source metadata into a bundle directory.
- Copy gallery review assets into the bundle.
- Optionally copy per-frame base preview, secondary layer, composite, and graded
  reference images into the bundle.
- Emit a handoff manifest with public URL, look intent, per-frame references,
  copied-file totals, and missing-reference diagnostics.

## Commands

```powershell
python tools\build_mitsuba_renderer_handoff_bundle.py `
  build\shots\s325_mitsuba_renderer_review_contract\renderer_review_contract.json `
  --validation build\shots\s326_mitsuba_renderer_review_contract_validation\validation.json `
  --out-dir build\shots\s327_mitsuba_renderer_handoff_bundle `
  --manifest build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_handoff_bundle_s327.md `
  --copy-reference-images `
  --title "S327 Mitsuba Renderer Handoff Bundle" `
  --next "Use this bundle as the renderer-facing reference package before replacing post-composite secondary and grade with renderer-side implementations."
```

## Outputs

- Handoff manifest:
  `build/shots/s327_mitsuba_renderer_handoff_bundle/handoff_manifest.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_handoff_bundle_s327.md`
- Bundle root:
  `build/shots/s327_mitsuba_renderer_handoff_bundle`

## Acceptance

- Bundle status is `ready`.
- Frame count is `8`.
- Copied files are `41`.
- Missing references are `0`.
- The bundle records the current public proof URL and preserves the S325 look
  intent for Mitsuba, secondary layer representation, and review grade.
