# S325 Larger External Renderer Mitsuba Review Contract

## Goal

Convert the current S324 public Mitsuba composite grade proof into a durable
renderer-review contract. The contract should tie together the grade summary,
secondary composite summary, actual Mitsuba render manifest, Mitsuba XML export
manifest, public review URL, and frame-level handoff data.

## Scope

- Add `tools/build_mitsuba_renderer_review_contract.py`.
- Read the S324 `lsfs_mitsuba_composite_grade` summary.
- Follow the source chain back through:
  - S323 `lsfs_mitsuba_secondary_composite`
  - S322 `lsfs_mitsuba_xml_render`
  - S322 `lsfs_mitsuba_xml_export`
- Include the S324 Cloudflare publish manifest when available.
- Emit a JSON contract with status, source hashes, artifact hashes, public URL
  checks, renderer expectations, and per-frame graded/composite/layer mappings.
- Emit a Markdown report for quick review.

## Commands

```powershell
python tools\build_mitsuba_renderer_review_contract.py `
  build\shots\s324_larger_external_renderer_mitsuba_composite_grade_soft\grade_summary.json `
  --publish-manifest build\shots\s324_larger_external_renderer_mitsuba_composite_grade_publish\publish_manifest.json `
  --out build\shots\s325_mitsuba_renderer_review_contract\renderer_review_contract.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_review_contract_s325.md `
  --title "S325 Mitsuba Renderer Review Contract" `
  --next "Use this contract to promote secondary layer and grade settings into renderer-facing handoff data."
```

## Outputs

- Contract JSON:
  `build/shots/s325_mitsuba_renderer_review_contract/renderer_review_contract.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_review_contract_s325.md`
- Current public proof:
  `https://hydrocodone-becomes-attempted-unified.trycloudflare.com`

## Acceptance

- Contract status is `ready`.
- Grade, composite, and actual render frame counts all match at `8`.
- Missing frame assets are `0`.
- The report names the public review URL and the renderer-facing expectations
  for secondary layer and grade settings.
