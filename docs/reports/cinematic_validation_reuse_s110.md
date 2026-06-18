# Cinematic Validation Reuse S110

## Summary

S110 adds opt-in render-cache validation reuse for repeated cinematic review runs.

- `tools/validate_render_cache.py --stamp <path>` writes a successful validation fingerprint.
- `tools/validate_render_cache.py --reuse-if-fresh` reuses that stamp only when the validator script, manifest, cache frame contents, and validation options still match.
- `tools/run_cinematic_shot.py --reuse-validation` enables the stamp path in the cinematic runner.
- Shot reports now include `Render cache validation reused`.

## Probe Results

| Probe | Result |
| --- | --- |
| Validator first run on `build/s37_sparse_manifest.json` | `reused=false`, `status=ok` |
| Validator second run on the same stamp | `reused=true`, `status=reused` |
| Runner second 2-frame preview run | `validation_reused=True`, `converted_sequence_reused=True` |
| Runner validation log | `reused=true`, `status=reused` |

## Notes

The feature is opt-in. Default validation behavior is unchanged.
