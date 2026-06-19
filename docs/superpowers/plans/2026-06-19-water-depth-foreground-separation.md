# S168 Water Depth And Foreground Separation Pass

## Objective

Improve S165 visual depth so foreground, midground, and background water do not
collapse into a single flat blue sheet.

## Inputs

- Baseline preset: `dam_break_source_slab_deemphasis`
- Baseline shot output: `build/shots/s165_source_slab_deemphasis`
- Baseline report: `docs/reports/cinematic_source_slab_deemphasis_s165.md`
- Triage report: `docs/reports/cinematic_visual_review_s167.md`

## Scope

- Add an inherited render preset, tentatively
  `dam_break_water_depth_foreground_separation`.
- Preserve S165 simulation scene, source window, camera, grid, and secondary
  physical particles.
- Tune only bounded render-side depth/readability controls:
  - water volume scatter alpha/emission and region bounds
  - foreground reflection/glint strength
  - water material depth/rim strength
  - optional lower foreground haze if available in the current renderer stack
- Run a warm-cache Blender gate against S165 artifacts.

## Non-Goals

- Do not change source initialization in this pass.
- Do not increase grid size.
- Do not add new renderer systems unless existing preset controls are
  insufficient.
- Do not weaken acceptance gates to pass the shot.

## Candidate Probe

```powershell
python tools\render_bridge_blender.py build\shots\s165_source_slab_deemphasis\converted\sequence.json build\s168_depth_separation_probe --frames 8 --width 640 --height 360 --samples 8 --render-preset dam_break_water_depth_foreground_separation --preset-config configs\cinematic_presets.json --timeout-seconds 600
```

## Candidate Full Gate

```powershell
python tools\run_cinematic_shot.py --preset dam_break_water_depth_foreground_separation --out build\shots\s168_water_depth_foreground_separation --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s165_source_slab_deemphasis\review\review_manifest.json --report docs\reports\cinematic_water_depth_foreground_separation_s168.md --no-build --timeout-seconds 2400 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted
```

## Acceptance Gate

- Full gate passes visual, temporal, focus, secondary-depth,
  secondary-framing, ripple-readability, and camera-stability checks.
- Comparison sheet shows stronger foreground/midground separation than S165.
- Glint/reflection changes remain below temporal highlight and ripple highlight
  limits.
- Report records the visual tradeoff and next recommendation.
