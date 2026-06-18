# Cinematic Convert Reuse S109

## Summary

S109 adds opt-in converted-sequence reuse for repeated cinematic review runs.

- `tools/convert_render_cache.py --reuse-if-fresh` writes and checks a SHA256 fingerprint for the converter script, manifest, cache frames, water reconstruction index, and water mesh files.
- `tools/run_cinematic_shot.py --reuse-converted` forwards the reuse request to the converter.
- Shot reports now include `Converted sequence reused`.

## Probe Results

| Probe | Result |
| --- | --- |
| Converter first run on `build/s37_sparse_manifest.json` | `reused=false`, `status=ok` |
| Converter second run on the same output | `reused=true`, `status=reused` |
| Runner second 2-frame preview run | `converted_sequence_reused=True` |
| Runner converter log | `reused=true`, `status=reused` |
| Runner reused convert elapsed | `177.79ms` |

## Notes

The feature is opt-in. Default conversion behavior is unchanged.
