# S360 Mitsuba Secondary Visibility Cache

## Goal

Turn the S359 SV1 diagnostic visibility bridge into a renderer-facing cache
contract instead of leaving it only as a composite preview.

## Changes

- Extended `tools/composite_mitsuba_secondary_layer.py`.
- Added `--profile-name` so tuned visibility profiles are named in outputs.
- Added `secondary_visibility_cache.json` with schema
  `lsfs_mitsuba_secondary_visibility_cache`.
- The cache records per-frame RGBA layer paths, sha256, byte size, projected
  counts, coverage, source manifests, and composition usage.

## Result

- S360 SV1 cache report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_sv1_s360.md`
- S360 SV1 gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_sv1_gap_s360.md`
- Cache manifest:
  `build/shots/s360_mitsuba_secondary_visibility_cache_sv1/secondary_visibility_cache.json`

The cache contains `8` frames, `2877` projected particles, max layer coverage
`0.1105054012345679`, and `540.24 KB` of RGBA layer data. Rechecking the
composite through the target-gap harness preserves the S359 SV1 result:
max target MAD `23.72217142489712`.

## Next

Consume this cache from a renderer-native pass or a stable external-renderer
review package. The cache is now the data contract; the current screen-space
composite remains a diagnostic preview path.
