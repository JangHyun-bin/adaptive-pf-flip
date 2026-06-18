# Blender Quality Warm Cache Return

## Goal

Return from preview-only warm-cache work to a Blender quality gate while keeping the full warm-cache controls enabled.

## Scope

- Use `dam_break_large_grid_render_quality_followup`.
- Keep the S106-style full 36-frame Blender quality gate.
- Enable all warm-cache flags:
  - `--reuse-export-cache`
  - `--reuse-validation`
  - `--reuse-water-mesh`
  - `--reuse-converted`
  - `--reuse-render-frames`
  - `--reuse-gif`
- Run the shot twice and summarize the warm second run.
- Keep the quality gate strict; do not relax luminance or framing thresholds.

## Command

```powershell
python tools\run_cinematic_shot.py --preset dam_break_large_grid_render_quality_followup --out build\shots\s118_blender_quality_warm_cache_return --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 1800
python tools\summarize_shot_commands.py build\shots\s118_blender_quality_warm_cache_return\shot_summary.json --out docs\reports\cinematic_blender_warm_cache_s118.md
```

## Result

S118 passed and produced `docs/reports/cinematic_blender_warm_cache_s118.md`.

- Status: `ok`.
- Visual QA gate: passed.
- Focus review gate: passed.
- Secondary depth review gate: passed.
- Ripple readability gate: passed.
- Warm run reused export, validation, water reconstruction, conversion, Blender frames, and GIF.
- Warm run total command time: `4.64s`.

The first attempt with `--sim-steps 8` failed focus luminance (`69.22` below `70`), so the final S118 command keeps the full `--sim-steps 36` quality horizon rather than weakening the quality gate.

## Next

S119 should add a side-by-side Blender quality comparison against the previous large-grid baseline.
