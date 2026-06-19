# S195 Water Mesh Smoothing Strong Full-Shot

## Goal

Promote the S194-selected stronger smoothing probe into a full-shot candidate
and compare it against the accepted S191 water mesh smoothing shot.

## Scope

- Add `dam_break_water_mesh_smoothing_strong` as a non-probe preset.
- Render a 36-frame 1280x720 Blender shot from the same S168 converted cache.
- Assemble a GIF for local visual review.
- Generate a S191-vs-S195 comparison sheet and Markdown report.
- Do not publish automatically; require visual review because the full-shot
  contrast delta is slightly negative against S191.

## Result

S195 rendered successfully and is a review candidate.

- S191 min contrast: `186`
- S195 min contrast: `181`
- S186 min contrast floor: `181`
- S195 mean nonblank ratio: `1.0`
- S195 mean luminance delta from S191: `-0.020953987027397147`

The stronger smoothing preset stays inside the S186 floor and preserves frame
coverage, but it is not a clear numeric improvement over S191. It should be
published for visual review before replacing the current accepted baseline.

## Artifacts

- Shot GIF: `build/shots/s195_water_mesh_smoothing_strong/shot.gif`
- Bridge summary:
  `build/shots/s195_water_mesh_smoothing_strong/blender/bridge_summary.json`
- Comparison sheet:
  `build/shots/s195_water_mesh_smoothing_strong/comparison/comparison_sheet.png`
- Comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_comparison_s195.md`

## Verification

- `python -m json.tool configs\cinematic_presets.json > $null`
- `python tools\render_bridge_blender.py ... --render-preset dam_break_water_mesh_smoothing_strong ...`
- `python tools\assemble_frames.py build\shots\s195_water_mesh_smoothing_strong\blender\frames build\shots\s195_water_mesh_smoothing_strong\shot.gif --fps 12.0`
- `python tools\compare_cinematic_frames.py ... --report docs\reports\cinematic_water_mesh_smoothing_strong_comparison_s195.md`
- `git diff --check`

## Next

Package S195 into a gallery and publish it for external review. If the smoother
water body reads better despite the S191 contrast delta, accept S195. If not,
keep S191 and move the next work to reconstruction/export smoothing.
