# GIF Assembly Reuse

## Goal

Skip GIF assembly on repeated cinematic review runs when the rendered frames and GIF options are unchanged.

## Scope

- Add `--reuse-gif` to `tools/run_cinematic_shot.py`.
- Store `gif_stamp.json` next to `shot.gif`.
- Fingerprint `assemble_frames.py`, the assemble command, and every `frame_####.png` input.
- Require the existing `shot.gif` to exist before reuse.
- Record `gif_reused` in shot metrics and warm-cache summaries.
- Keep default GIF assembly behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py tools\summarize_shot_commands.py
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s117_gif_reuse_smoke --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset dam_break_large_grid_warm_cache_preview --out build\shots\s117_gif_reuse_probe --frames 36 --sim-steps 8 --width 640 --height 360 --renderer preview --review-frames 4 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --reuse-gif --no-build --timeout-seconds 900
python tools\summarize_shot_commands.py build\shots\s117_gif_reuse_probe\shot_summary.json --out docs\reports\cinematic_gif_reuse_s117.md
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S117 produced `docs/reports/cinematic_gif_reuse_s117.md`.

- Export cache reused: `True`.
- Validation reused: `True`.
- Water reconstruction reused: `True`.
- Converted sequence reused: `True`.
- Render frames reused: `True`.
- GIF reused: `True`.
- Large-grid warm-cache total command time: `1.44s`.

## Next

S118 should return to Blender render-quality work with the full warm-cache path enabled.
