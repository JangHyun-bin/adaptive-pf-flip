# S361 Mitsuba Secondary Visibility Cache Validation

## Goal

Add a validation gate for the S360 renderer-facing secondary visibility cache.
Before a renderer-native pass consumes the cache, the repository should verify
that the cache schema and RGBA layer files are still intact.

## Changes

- Added `tools/validate_mitsuba_secondary_visibility_cache.py`.
- The validator checks:
  - schema is `lsfs_mitsuba_secondary_visibility_cache`,
  - every RGBA layer exists,
  - layer sha256 and byte size match the manifest,
  - measured alpha coverage matches manifest coverage,
  - projected particle and aggregate layer-byte checks match,
  - layer coverage stays under the configured cap.

## Result

- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_validation_s361.md`
- Validation JSON:
  `build/shots/s361_mitsuba_secondary_visibility_cache_validation/secondary_visibility_cache_validation.json`

S361 validates the S360 SV1 cache with `8` frames, `2877` projected particles,
max layer coverage `0.1105054012345679`, `540.24 KB` of layer data, and `0`
failed checks.

## Next

Use this passed validation as the gate for the next renderer-facing secondary
pass. The next implementation step should consume the cache rather than
reconstructing the visibility layer ad hoc.
