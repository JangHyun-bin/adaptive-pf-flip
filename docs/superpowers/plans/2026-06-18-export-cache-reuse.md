# Export Cache Reuse

## Goal

Skip the C++ render-cache exporter on repeated cinematic review runs only when the requested export command and existing cache files are unchanged.

## Scope

- Add `--reuse-export-cache` to `tools/run_cinematic_shot.py`.
- Store an export stamp under the shot cache directory.
- Fingerprint the exporter binary and full export command.
- Require the manifest and every referenced cache frame to exist with the manifest-declared byte count.
- Restore exporter stdout metrics from the stamp so downstream secondary gates still receive the same export metrics.
- Keep default export behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s112_export_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s112_export_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --no-build --timeout-seconds 120
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

- Runner probe second run: `export_cache_reused=True`, `validation_reused=True`, `water_reconstruction_reused=True`, `converted_sequence_reused=True`.
- Warm export record elapsed: `0.0ms`.
- Warm validation reuse elapsed: `152.94ms`.
- Warm water reconstruction reuse elapsed: `233.27ms`.
- Warm converted sequence reuse elapsed: `150.54ms`.
- Default export behavior is unchanged unless `--reuse-export-cache` is passed.

## Next

S113 should add a warm-cache stage summary for shot summaries so reuse savings are easy to inspect without manually opening command logs.
