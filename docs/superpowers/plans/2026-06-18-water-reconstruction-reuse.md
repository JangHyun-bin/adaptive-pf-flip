# Water Reconstruction Reuse

## Goal

Skip `reconstruct_water` on repeated cinematic review runs only when the source cache and reconstruction options are unchanged.

## Scope

- Add `--reuse-if-fresh` to `tools/reconstruct_water.py`.
- Store a SHA256 reconstruction fingerprint for the reconstructor script, source manifest/sequence/frame inputs, and reconstruction options.
- Require `water_reconstruction.json` and every referenced OBJ mesh to exist before reuse.
- Add `--reuse-water-mesh` to `tools/run_cinematic_shot.py`.
- Record `water_reconstruction_reused` in shot metrics and reports.
- Keep default reconstruction behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\reconstruct_water.py tools\run_cinematic_shot.py
python tools\reconstruct_water.py build\s37_sparse_manifest.json build\s111_water_reuse_probe --frames 2 --surface-mode voxel --reuse-if-fresh
python tools\reconstruct_water.py build\s37_sparse_manifest.json build\s111_water_reuse_probe --frames 2 --surface-mode voxel --reuse-if-fresh
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s111_runner_water_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-validation --reuse-water-mesh --reuse-converted --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s111_runner_water_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-validation --reuse-water-mesh --reuse-converted --no-build --timeout-seconds 120
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

- Reconstruct probe first run: `reused=false`, `status=ok`.
- Reconstruct probe second run: `reused=true`, `status=reused`.
- Runner probe second run: `validation_reused=True`, `water_reconstruction_reused=True`, `converted_sequence_reused=True`.
- Runner reconstruction stdout log: `reused=true`, `status=reused`.

## Next

S112 should add conservative export cache reuse so repeated review runs can skip the C++ cache exporter when the requested simulation/export config and existing cache files are unchanged.
