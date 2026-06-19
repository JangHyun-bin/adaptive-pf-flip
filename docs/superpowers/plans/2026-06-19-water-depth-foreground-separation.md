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

## Result

S168 landed as the inherited `dam_break_water_depth_foreground_separation`
preset. It preserves the S165 source scene, source window, camera, grid, and
secondary settings while tuning bounded render-side water depth/rim/scatter and
glint/reflection controls.

The full gate passed:

```powershell
python tools\run_cinematic_shot.py --preset dam_break_water_depth_foreground_separation --out build\shots\s168_water_depth_foreground_separation --frames 36 --sim-steps 56 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --compare-review-manifest build\shots\s165_source_slab_deemphasis\review\review_manifest.json --report docs\reports\cinematic_water_depth_foreground_separation_s168.md --no-build --timeout-seconds 2400 --reuse-export-cache --reuse-validation --reuse-water-mesh --reuse-converted
```

Key gate metrics:

- Status: `ok`
- Visual QA: `passed`, mean luminance `86.9082305832851`, mean bright ratio `0.0012959044656635802`, min contrast `184.0`
- Temporal highlight QA: `passed`, pair count `35`, max peak delta `159`
- Camera stability: `passed`, min target distance `26.10153252205701`, max vertical FOV `38.0`
- Secondary framing: `passed`, mean inside ratio `0.9185529911257326`
- Secondary depth: `passed`, mean depth span `13.85923744136715`
- Ripple readability: `passed`, mean edge value `28.55730614920156`

Artifacts:

- `docs/reports/cinematic_water_depth_foreground_separation_s168.md`
- `build/shots/s168_water_depth_foreground_separation/shot.gif`
- `build/shots/s168_water_depth_foreground_separation/review/contact_sheet.png`
- `build/shots/s168_water_depth_foreground_separation/review/comparison_sheet.png`

Visual read:

- S168 gives a modestly deeper foreground/midground read than S165 while
  preserving all QA gates.
- The improvement is conservative; remaining limitations are still driven by
  coarse sparse phase-cell mesh thickness and the late-frame upper water band.

Next:

- S169: package and publish the S168 artifacts through the static gallery and
  Cloudflare tunnel path.
