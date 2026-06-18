# Cinematic Water Reconstruction Reuse S111

## Summary

S111 adds opt-in water reconstruction reuse for repeated cinematic review runs.

- `tools/reconstruct_water.py --reuse-if-fresh` checks a SHA256 fingerprint for the reconstructor script, source cache inputs, and reconstruction options.
- The reusable reconstruction requires `water_reconstruction.json` and every referenced OBJ mesh to exist.
- `tools/run_cinematic_shot.py --reuse-water-mesh` enables the reuse path from the cinematic runner.
- Shot reports now include `Water reconstruction reused`.

## Probe Results

| Probe | Result |
| --- | --- |
| Reconstruct first run on `build/s37_sparse_manifest.json` | `reused=false`, `status=ok` |
| Reconstruct second run on the same output | `reused=true`, `status=reused` |
| Runner second 2-frame preview run | `validation_reused=True`, `water_reconstruction_reused=True`, `converted_sequence_reused=True` |
| Runner reconstruction log | `reused=true`, `status=reused` |

## Notes

The feature is opt-in. Default reconstruction behavior is unchanged.
