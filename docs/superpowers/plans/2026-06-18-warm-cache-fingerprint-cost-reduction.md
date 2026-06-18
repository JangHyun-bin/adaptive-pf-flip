# Warm Cache Fingerprint Cost Reduction

## Goal

Reduce large-grid warm-cache fingerprint overhead without weakening freshness guarantees.

## Scope

- Keep the SHA256-based freshness model.
- Move `reconstruct_water.py --reuse-if-fresh` reuse detection before expensive phase-cell loading.
- Build the water reconstruction fingerprint from manifest/sequence metadata and source file hashes first.
- Only call `load_source()` when the reuse check misses.
- Keep default reconstruction behavior unchanged.

## Validation

```powershell
python -m py_compile tools\reconstruct_water.py
python tools\reconstruct_water.py build\s37_sparse_manifest.json build\s116_reconstruct_fast_reuse_smoke --frames 2 --surface-mode voxel --reuse-if-fresh
python tools\reconstruct_water.py build\s37_sparse_manifest.json build\s116_reconstruct_fast_reuse_smoke --frames 2 --surface-mode voxel --reuse-if-fresh
python tools\run_cinematic_shot.py --preset dam_break_large_grid_warm_cache_preview --out build\shots\s116_fingerprint_cost_probe --frames 36 --sim-steps 8 --width 640 --height 360 --renderer preview --review-frames 4 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --no-build --timeout-seconds 900
python tools\summarize_shot_commands.py build\shots\s116_fingerprint_cost_probe\shot_summary.json --out docs\reports\cinematic_fingerprint_cost_s116.md
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S116 produced `docs/reports/cinematic_fingerprint_cost_s116.md`.

- S115 large-grid warm-cache `reconstruct_water`: `11.92s`.
- S116 large-grid warm-cache `reconstruct_water`: `466.09ms`.
- S115 total command time: `13.60s`.
- S116 total command time: `2.22s`.
- All warm-cache reuse flags remained `True`.

## Next

S117 should add warm-cache GIF assembly reuse because the remaining repeated-preview work is now mostly assembling an unchanged frame sequence.
