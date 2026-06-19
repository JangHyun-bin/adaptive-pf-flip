# S173 Metadata-Driven Depth Attenuation Pass

## Objective

Consume the S171/S172 render-data sidecar in the Blender bridge to apply a
bounded, frame-aware depth/secondary attenuation render pass over the S168
baseline.

## Inputs

- Baseline preset: `dam_break_water_depth_foreground_separation`
- Baseline shot output: `build/shots/s168_water_depth_foreground_separation`
- Render-data sidecar: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`
- S172 diagnostic report: `docs/reports/cinematic_render_data_profile_diagnostics_s172.md`

## Scope

- Add an optional renderer/CLI path for the Blender bridge to read
  `render_data_summary.json`.
- Use sidecar values only as bounded multipliers or pass settings; do not change
  simulation data.
- Target visible improvements:
  - slightly stronger far-water attenuation when water Z span is high,
  - frame-aware secondary attenuation when secondary counts rise late,
  - preserve existing glint, ripple, focus, temporal, and secondary gates.
- Add a derived preset, tentatively `dam_break_metadata_depth_attenuation`.
- Run a warm-cache Blender gate against S168, comparing to S168 review artifacts.

## Non-Goals

- Do not rerun simulation.
- Do not replace the current water mesh representation.
- Do not add a new volumetric renderer in this pass.
- Do not weaken visual gates.

## Candidate Probe

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s173_metadata_depth_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_metadata_depth_attenuation --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

## Candidate Full Gate

```powershell
python tools\run_cinematic_shot.py --preset dam_break_metadata_depth_attenuation --out build\shots\s173_metadata_depth_attenuation --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s168_water_depth_foreground_separation\review\review_manifest.json --report docs\reports\cinematic_metadata_depth_attenuation_s173.md --no-build --timeout-seconds 2400 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted
```

## Acceptance Gate

- Blender bridge accepts and reports the render-data sidecar.
- Full gate passes visual, temporal, focus, secondary-depth,
  secondary-framing, ripple-readability, and camera-stability checks.
- Comparison sheet shows the sidecar-driven pass does not regress the S168 depth
  read and preferably reduces the flat sheet read.
- Report records sidecar settings, metrics, and next recommendation.

## Result

S173 added `--render-data-summary` to `tools/render_bridge_blender.py` and the
`dam_break_metadata_depth_attenuation` preset.

Because this pass must not rerun simulation, the gate used the direct Blender
bridge over the S168 converted cache instead of a fresh `run_cinematic_shot.py`
output directory.

Generated artifacts:

- Report: `docs/reports/cinematic_metadata_depth_attenuation_s173.md`
- Bridge summary: `build/shots/s173_metadata_depth_attenuation/blender/bridge_summary.json`
- Render frames: `build/shots/s173_metadata_depth_attenuation/blender/frames`
- GIF: `build/shots/s173_metadata_depth_attenuation/shot.gif`

Gate summary:

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: `84.78030921465084`
- Metadata pass status: `active`
- Water alpha multiplier: min `0.88`, max `1.28`
- Secondary particle cap scale: min `0.72`, max `1.0`

Next:

- S174 should package/compare S173 against S168 and preferably add a source-shot
  reuse path to the runner so review gates can run on existing converted caches
  without simulation regeneration.
