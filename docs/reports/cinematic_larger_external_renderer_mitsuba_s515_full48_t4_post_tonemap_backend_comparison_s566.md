# S566 Mitsuba S515 Full48 T4 Post Tonemap Backend Comparison

Generated UTC: `2026-06-20T21:20:00Z`

## Summary

S564 replaces the S562 process stub executable with
`tools/mitsuba_low_frequency_post_tonemap_backend.py` while preserving the same
S560 backend scene descriptors and process CLI boundary.

The new backend runs the full 48-frame S515/S552 T4 contract as
`post_tonemap_texture_backend`, emits
`lsfs_mitsuba_low_frequency_post_tonemap_backend_result`, and reproduces the
accepted references with zero image diff.

## Public Proofs

- S562 process stub proof:
  `https://passport-ground-excerpt-equipped.trycloudflare.com`
- S565 post-tonemap backend proof:
  `https://providence-secrets-stats-last.trycloudflare.com`

## Validation

- S564 process summary:
  `build/shots/s564_mitsuba_s515_full48_t4_post_tonemap_backend_process/backend_process_summary.json`
- S564 validation:
  `build/shots/s564_mitsuba_s515_full48_t4_post_tonemap_backend_process/backend_process_validation.json`
- S564 report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_post_tonemap_backend_process_s564.md`
- S564 validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_post_tonemap_backend_process_validation_s564.md`
- S565 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s515_full48_t4_post_tonemap_backend_publish_s565.md`

## Checks

- S564 status: `passed`
- S564 frames: `48`
- S564 passed frames: `48`
- S564 process failures: `0`
- S564 max image diff: `0`
- S564 max mean image diff: `0.0`
- S564 validation checks: `1481`
- S564 validation failures: `0`
- S565 public `GET /index.html`: `200`, `4138` bytes
- S565 public `HEAD /assets/shot.gif`: `200`, `7108171` bytes

## Stub vs Backend GIF Parity

| Artifact | SHA256 | Bytes |
| --- | --- | ---: |
| S562 stub GIF | `8C6E621C4656B3F5D7AA85C44418CA3CFC455B4E03F5BD07892C62A14B544ACF` | `7108171` |
| S564 backend GIF | `8C6E621C4656B3F5D7AA85C44418CA3CFC455B4E03F5BD07892C62A14B544ACF` | `7108171` |

Result: `identical`.

## Current Meaning

The S515 full48 T4 correction is now executable through a non-stub backend
script while keeping the renderer/backend process contract stable. This still
applies a post-tonemap texture correction, but the execution boundary is now
ready for a real renderer-native implementation to replace the image backend.

## Next

Move the same descriptor/process boundary toward renderer-native response:
material/light/volume logic should consume the scene contract before tonemapped
reference deltas become the accepted output.
