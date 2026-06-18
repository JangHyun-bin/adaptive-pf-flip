# Cinematic Export Cache Reuse S112

## Summary

S112 adds opt-in export cache reuse for repeated cinematic review runs.

- `tools/run_cinematic_shot.py --reuse-export-cache` checks an export stamp before calling the C++ cache exporter.
- The stamp fingerprints the exporter binary and full export command.
- Reuse requires `manifest.json` and all referenced cache frames to still exist with the manifest-declared byte counts.
- Export metrics from the original exporter run are restored for downstream gates when reuse is active.

## Probe Results

| Probe | Result |
| --- | --- |
| Runner second 2-frame preview run | `export_cache_reused=True`, `validation_reused=True`, `water_reconstruction_reused=True`, `converted_sequence_reused=True` |
| Warm export record elapsed | `0.0ms` |
| Warm validation reuse elapsed | `152.94ms` |
| Warm water reconstruction reuse elapsed | `233.27ms` |
| Warm converted sequence reuse elapsed | `150.54ms` |

## Notes

The feature is opt-in. Default export behavior is unchanged.
