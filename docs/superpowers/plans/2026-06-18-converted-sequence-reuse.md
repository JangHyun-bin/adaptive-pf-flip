# Converted Sequence Reuse

## Goal

Skip `convert_render_cache` on repeated cinematic review runs when the converted sequence is already fresh for the current manifest, cache frames, water reconstruction, water meshes, and converter script.

## Scope

- Add `--reuse-if-fresh` to `tools/convert_render_cache.py`.
- Add SHA256-based conversion fingerprints to `sequence.json`.
- Require all converted camera, particle, phase-cell, and water-mesh assets to exist before reuse.
- Add `--reuse-converted` to `tools/run_cinematic_shot.py`.
- Record `converted_sequence_reused` in shot metrics and reports.
- Keep default behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\convert_render_cache.py tools\run_cinematic_shot.py
python tools\convert_render_cache.py build\s37_sparse_manifest.json build\s109_convert_reuse_probe --require-cinematic --reuse-if-fresh
python tools\convert_render_cache.py build\s37_sparse_manifest.json build\s109_convert_reuse_probe --require-cinematic --reuse-if-fresh
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s109_runner_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-converted --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s109_runner_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-converted --no-build --timeout-seconds 120
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

- Converter probe first run: `reused=false`, `status=ok`.
- Converter probe second run: `reused=true`, `status=reused`.
- Runner probe second run: `converted_sequence_reused=True`.
- Runner converter stdout log: `reused=true`, `status=reused`.
- Runner reused conversion elapsed time in the 2-frame probe: `177.79ms`.

## Next

S110 should add a conservative render-cache validation freshness stamp so repeated review runs can skip `validate_render_cache` only when the manifest and cache frame contents are unchanged.
