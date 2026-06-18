# Render Frame Reuse

## Goal

Skip preview/Blender rendering on repeated cinematic review runs only when renderer inputs, renderer options, and existing frame outputs are unchanged.

## Scope

- Add `--reuse-render-frames` to `tools/run_cinematic_shot.py`.
- Store a render stamp under the selected renderer output directory.
- Fingerprint renderer command, renderer tool script, and renderer input assets.
- For preview, fingerprint the manifest and water reconstruction assets.
- For Blender, fingerprint the converted sequence assets and render preset config.
- Require `render_summary` plus all `frame_####.png` outputs to exist before reuse.
- Record `render_frames_reused` in shot metrics and reports.
- Keep default render behavior unchanged; reuse is opt-in.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py tools\summarize_shot_commands.py
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s114_render_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --no-build --timeout-seconds 120
python tools\run_cinematic_shot.py --preset bubble_cinematic --out build\s114_render_reuse_probe --frames 2 --sim-steps 2 --width 320 --height 180 --renderer preview --review-frames 2 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted --reuse-render-frames --no-build --timeout-seconds 120
python tools\summarize_shot_commands.py build\s114_render_reuse_probe\shot_summary.json --out docs\reports\cinematic_render_reuse_s114.md
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

- Runner probe second run: `export_cache_reused=True`, `validation_reused=True`, `water_reconstruction_reused=True`, `converted_sequence_reused=True`, `render_frames_reused=True`.
- Warm export record elapsed: `0.0ms`.
- Warm preview render record elapsed: `0.0ms`.
- Warm-cache total command time in the 2-frame probe: `1.27s`.
- Warm-cache reused command time: `989.46ms`.

## Next

S115 should run a warm-cache larger-grid preview benchmark to measure the full reuse path before returning to render quality.
