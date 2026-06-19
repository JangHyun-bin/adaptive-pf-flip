# S329 Mitsuba Renderer Target Preview Validation

## Goal

Add a regression gate for the S328 renderer target preview so future
renderer-side secondary and grade implementations can be compared against the
accepted target without relying on manual visual inspection alone.

## Scope

- Add `tools/validate_mitsuba_renderer_target_preview.py`.
- Validate S328 summary schema, version, and status.
- Validate frame counts and missing-reference count.
- Validate composite and target diff thresholds.
- Validate target, strip, diff, and renderer-secondary image paths.
- Validate target image hashes.
- Optionally validate the published public URL from the publish manifest.

## Commands

```powershell
python tools\validate_mitsuba_renderer_target_preview.py `
  build\shots\s328_mitsuba_renderer_target_preview\renderer_target_preview_summary.json `
  --publish-manifest build\shots\s328_mitsuba_renderer_target_preview_publish\publish_manifest.json `
  --check-public `
  --out build\shots\s329_mitsuba_renderer_target_preview_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_target_preview_validation_s329.md `
  --title "S329 Mitsuba Renderer Target Preview Validation" `
  --timeout 30
```

## Outputs

- Validation JSON:
  `build/shots/s329_mitsuba_renderer_target_preview_validation/validation.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_target_preview_validation_s329.md`

## Acceptance

- Validation status is `passed`.
- Total checks are `62`.
- Failed checks are `0`.
- Skipped checks are `0`.
- Public `index.html` and `assets/shot.gif` checks pass while the Cloudflare
  tunnel is live.
