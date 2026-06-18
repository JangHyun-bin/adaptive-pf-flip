# Render Cache Validation Reuse

## Goal

Skip `validate_render_cache` on repeated cinematic review runs only when the manifest and cache frame contents are unchanged.

## Scope

- Add `--stamp` and `--reuse-if-fresh` to `tools/validate_render_cache.py`.
- Store a SHA256 validation fingerprint for the validator script, manifest, cache frames, and relevant validation options.
- Add `--reuse-validation` to `tools/run_cinematic_shot.py`.
- Record `validation_reused` in shot metrics and reports.
- Keep default validation behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\validate_render_cache.py tools\run_cinematic_shot.py
python tools\validate_render_cache.py build\s37_sparse_manifest.json --require-cinematic --stamp build\s110_validation_reuse_probe\validation_stamp.json --reuse-if-fresh
python tools\validate_render_cache.py build\s37_sparse_manifest.json --require-cinematic --stamp build\s110_validation_reuse_probe\validation_stamp.json --reuse-if-fresh
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s110_runner_validation_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-converted --reuse-validation --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s110_runner_validation_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-converted --reuse-validation --no-build --timeout-seconds 120
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

- Validator probe first run: `reused=false`, `status=ok`.
- Validator probe second run: `reused=true`, `status=reused`.
- Runner probe second run: `validation_reused=True`, `converted_sequence_reused=True`.
- Runner validation stdout log: `reused=true`, `status=reused`.

## Next

S111 should add conservative water reconstruction reuse so repeated review runs can skip `reconstruct_water` when the manifest and reconstruction options are unchanged.
