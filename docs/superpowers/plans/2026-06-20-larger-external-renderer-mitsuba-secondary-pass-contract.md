# S335 Mitsuba Secondary Pass Contract

## Goal

Promote the S334 secondary overlay hybrid from a visual proof into a
renderer-facing secondary pass contract. The contract should define what a
renderer-native replacement must preserve: frame mapping, secondary layer
semantics, grade settings, target-diff gates, and public review evidence.

## Scope

- Add `tools/build_mitsuba_secondary_pass_contract.py`.
- Read the S334 `lsfs_mitsuba_render_secondary_overlay` summary.
- Follow its source chain to:
  - S333 H2 actual Mitsuba render
  - S327 renderer handoff bundle
  - S328 renderer target preview
- Include the S334 publish manifest when available.
- Emit a contract JSON with source hashes, artifact hashes, per-frame paths,
  per-frame metrics, pass semantics, and future renderer expectations.

## Commands

```powershell
python tools\build_mitsuba_secondary_pass_contract.py `
  build\shots\s334_mitsuba_secondary_overlay_hybrid\secondary_overlay_summary.json `
  --publish-manifest build\shots\s334_mitsuba_secondary_overlay_hybrid_publish\publish_manifest.json `
  --out build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_s335.md `
  --title "S335 Mitsuba Secondary Pass Contract" `
  --next "Use this contract to replace the hybrid screen-space overlay with a renderer-native secondary pass while preserving target-diff gates."
```

## Outputs

- Contract JSON:
  `build/shots/s335_mitsuba_secondary_pass_contract/secondary_pass_contract.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_s335.md`
- Public URL inherited from S334:
  `https://laundry-tanks-prot-until.trycloudflare.com`

## Acceptance

- Contract status is `ready`.
- Frames are `8`.
- Missing frame assets are `0`.
- Max overlay mean absolute diff is `18.040229552469135`.
- Mean overlay mean absolute diff is `12.566030735596708`.
- Public URL is present.
- The contract explicitly states that this is a screen-space overlay hybrid and
  that a native renderer pass must preserve the same frame mapping and
  target-diff checks.
