# S173 Metadata Depth Attenuation Gate

Date: 2026-06-19

## Status

Passed.

S173 consumes the S171/S172 render-data sidecar in the Blender bridge and
applies a bounded, frame-aware render pass over the S168 warm cache. It does not
rerun simulation.

## Inputs

- Baseline preset: `dam_break_water_depth_foreground_separation`
- New preset: `dam_break_metadata_depth_attenuation`
- Source sequence: `build/shots/s168_water_depth_foreground_separation/converted/sequence.json`
- Render-data sidecar: `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json`

## Commands

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\s173_metadata_depth_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_metadata_depth_attenuation --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 700
```

```powershell
python tools\render_bridge_blender.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s173_metadata_depth_attenuation\blender --frames 36 --width 1280 --height 720 --samples 12 --render-preset dam_break_metadata_depth_attenuation --preset-config configs\cinematic_presets.json --render-data-summary build\shots\s168_water_depth_foreground_separation\converted\render_data_summary.json --timeout-seconds 2400
```

```powershell
python tools\assemble_frames.py build\shots\s173_metadata_depth_attenuation\blender\frames build\shots\s173_metadata_depth_attenuation\shot.gif --fps 12.0
```

## Artifacts

- Bridge summary: `build/shots/s173_metadata_depth_attenuation/blender/bridge_summary.json`
- Render frames: `build/shots/s173_metadata_depth_attenuation/blender/frames`
- GIF: `build/shots/s173_metadata_depth_attenuation/shot.gif`

## Gate Metrics

- Frames: `36`
- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance: min `81.43809678819444`, mean `84.78030921465084`, max `94.78654188368056`
- Bright ratio: min `0.00042100694444444444`, mean `0.0010237931616512346`, max `0.0020746527777777777`
- Highlight ratio: min `0.000007595486111111111`, mean `0.00013512128665123455`, max `0.00041341145833333334`

## Sidecar Use

The bridge reports the sidecar as active:

- Sidecar frames: `36`
- Simulation dims: `[36, 44, 28]`
- Water Z span: min `23.0`, mean `26.88888888888889`, max `28.0`
- Secondary total count: min `256.0`, mean `342.80555555555554`, max `964.0`

Applied bounded factors:

- Water alpha multiplier: min `0.88`, max `1.28`
- Water emission multiplier: min `0.68`, max `1.04`
- Water layer scale: min `0.86`, max `1.18`
- Secondary alpha multiplier: min `0.72`, max `1.0`
- Secondary channel scale: min `0.78`, max `1.0`
- Secondary particle cap scale: min `0.72`, max `1.0`

## Visual Read

The early frame preserves the existing S168 surface ripple and foreground water
read. The mid and late frames keep secondary particles visible while reducing
late-frame density and brightness through sidecar-driven attenuation. No blank
or over-dark frames were observed in the inspected keyframes.

## Notes

This gate intentionally used the direct Blender bridge instead of
`run_cinematic_shot.py`, because the S173 non-goal was to avoid rerunning
simulation. The next step should package/compare S173 against S168 with review
artifacts, or add a source-shot reuse path to the runner so review gates can be
run on existing converted caches without simulation regeneration.
