# S326 Mitsuba Renderer Review Contract Validation

## Goal

Add a repeatable validation gate for the S325 renderer-review contract so the
visual proof handoff can be checked after renderer, composite, or publishing
changes.

## Scope

- Add `tools/validate_mitsuba_renderer_review_contract.py`.
- Validate the S325 `lsfs_mitsuba_renderer_review_contract` schema and version.
- Validate source JSON files, source hashes, and source schemas.
- Validate gallery artifact hashes and sizes.
- Validate per-frame base preview, secondary layer, composite, and graded frame
  paths.
- Validate graded frame hashes, non-negative projected-particle counts, and
  layer coverage bounds.
- Optionally validate the public review URL.

## Commands

```powershell
python tools\validate_mitsuba_renderer_review_contract.py `
  build\shots\s325_mitsuba_renderer_review_contract\renderer_review_contract.json `
  --out build\shots\s326_mitsuba_renderer_review_contract_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_review_contract_validation_s326.md `
  --title "S326 Mitsuba Renderer Review Contract Validation" `
  --check-public `
  --timeout 20
```

## Outputs

- Validation JSON:
  `build/shots/s326_mitsuba_renderer_review_contract_validation/validation.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_review_contract_validation_s326.md`

## Acceptance

- Validation status is `passed`.
- Total checks are `77`.
- Failed checks are `0`.
- Skipped checks are `0`.
- Public `index.html` and `assets/shot.gif` checks pass while the Cloudflare
  tunnel is live.
