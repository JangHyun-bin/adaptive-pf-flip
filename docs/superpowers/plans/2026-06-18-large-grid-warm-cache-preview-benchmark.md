# Large Grid Warm Cache Preview Benchmark

## Goal

Measure the full opt-in warm-cache path on a larger-grid preview run before returning to Blender render-quality work.

## Scope

- Add `dam_break_large_grid_warm_cache_preview`.
- Keep the S106 large-grid simulation and camera baseline.
- Use preview rendering for a fast performance benchmark.
- Disable Blender-only focus, secondary-depth, and ripple review gates in the preview benchmark preset.
- Keep temporal highlight QA with a preview-friendly lower `min_mean_delta`.
- Run the shot twice and summarize the warm second run.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_large_grid_warm_cache_preview --out build\shots\s115_large_grid_warm_cache_preview --frames 36 --sim-steps 8 --width 640 --height 360 --renderer preview --review-frames 4 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --no-build --timeout-seconds 900
python tools\summarize_shot_commands.py build\shots\s115_large_grid_warm_cache_preview\shot_summary.json --out docs\reports\cinematic_large_grid_warm_cache_s115.md
```

## Result

S115 passed and produced `docs/reports/cinematic_large_grid_warm_cache_s115.md`.

- Export cache reused: `True`.
- Validation reused: `True`.
- Water reconstruction reused: `True`.
- Converted sequence reused: `True`.
- Render frames reused: `True`.
- Warm-cache total command time: `13.60s`.
- Warm water reconstruction reuse check: `11.92s`.

## Next

S116 should reduce warm-cache fingerprint overhead, especially water reconstruction asset hashing on larger grids.
