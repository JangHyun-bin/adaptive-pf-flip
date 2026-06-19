# S194 Smoothing Occlusion Probe Matrix

## Goal

Choose the next full-shot water-body render candidate from a bounded probe
matrix instead of tuning by eye alone.

## Scope

- Add reusable probe-matrix tooling for cinematic candidate comparisons.
- Add three probe presets over the accepted S191 water mesh smoothing baseline:
  lighter smoothing, stronger smoothing, and renderer-side water-volume
  occlusion.
- Keep occlusion as an experimental render pass until metrics show it is local
  enough to avoid darkening the whole frame.
- Record the probe comparison and selected follow-up candidate in a report.

## Result

S194 selects `dam_break_water_mesh_smoothing_strong_probe` as the next full-shot
candidate.

The soft candidate loses too much minimum contrast. The occlusion candidate is
too global, with a selected-frame changed ratio near 0.5 and a clear luminance
drop. The strong smoothing probe keeps nonblank coverage at 1.0, improves
minimum contrast from 174 to 184, and keeps the diff localized.

## Artifacts

- Report: `docs/reports/cinematic_smoothing_occlusion_probe_matrix_s194.md`
- Matrix: `build/shots/s194_smoothing_occlusion_probe_matrix/probe_matrix.png`
- Summary:
  `build/shots/s194_smoothing_occlusion_probe_matrix/probe_matrix_summary.json`

## Verification

- `python -m py_compile tools\render_bridge_blender.py tools\build_cinematic_probe_matrix.py`
- `python -m json.tool configs\cinematic_presets.json > $null`
- `git diff --check`

## Next

Promote the strong smoothing candidate into a non-probe preset and render a
36-frame S195 full-shot comparison against S191.
