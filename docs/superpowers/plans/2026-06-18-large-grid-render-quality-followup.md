# Large Grid Render Quality Followup

## Goal

Improve the S104 larger-grid camera framing where early secondary particles were visible near the top edge but still failed the stricter close-up-style frame-inside metric.

## Scope

- Add `dam_break_large_grid_render_quality_followup` as an inherited S104 preset.
- Keep simulation size, water volume scattering, secondary render materials, and review stack unchanged.
- Raise the large-grid camera target band for early frames.
- Increase the large-grid FOV pad from `4` to `8` degrees.
- Tighten S106 frame-inside gate relative to S104 from `0.1` to `0.3`.
- Keep this as an opt-in larger-grid cinematic gate, not default `ctest`.

## Probe

Using the existing S104 converted sequence:

```powershell
python tools\render_bridge_blender.py build\shots\s104_large_grid_cinematic_benchmark\converted\sequence.json build\shots\s106_large_grid_camera_probe --frames 8 --width 640 --height 360 --samples 8 --max-secondary-particles 1536 --secondary-radius-scale 3.0 --render-preset dam_break_large_grid_render_quality_followup --preset-config configs\cinematic_presets.json --timeout-seconds 700
```

The probe improved first-frame secondary framing from S104's `0.1445` to `0.3873`, with mean inside ratio `0.9234`.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python tools\run_cinematic_shot.py --preset dam_break_large_grid_render_quality_followup --out build\shots\s106_large_grid_render_quality_followup --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s106.md --compare-review-manifest build\shots\s104_large_grid_cinematic_benchmark\review\review_manifest.json --no-build --timeout-seconds 1800
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S106 passed the full opt-in cinematic gate.

- First-frame secondary framing improved from S104's `0.1445` to `0.3873`.
- Mean secondary inside ratio improved to `0.9830`.
- Visual QA passed with mean luminance `102.31` and min contrast `165`.
- Focus review passed with mean luminance `93.33` and min contrast `130`.
- Secondary depth review passed with mean crop particles `171.375` and normalized depth span `0.3883`.
- Ripple readability passed with mean edge strength `31.04`.
- Render time was `281.93s`; total staged command time was about `693.48s`.

## Next

S107 should refresh the compact benchmark summary with S106 included, then choose between a larger-grid quality lock-in and a cache/export performance pass from measured deltas.
