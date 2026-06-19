# S197 S195 Public Gallery Triage

## Goal

Decide whether the publicly published S195 strong smoothing candidate should
replace the accepted S191 baseline.

## Inputs

- Public gallery:
  `https://dicke-automotive-fitness-category.trycloudflare.com`
- S195 comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_comparison_s195.md`
- S196 gallery report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_gallery_s196.md`
- S196 publish report: `docs/reports/cinematic_gallery_publish_s196.md`

## Review

A compact S191-vs-S195 contact sheet was generated from the published source
frames:

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s191_water_mesh_smoothing\blender\frames --right build\shots\s195_water_mesh_smoothing_strong\blender\frames --left-label S191 --right-label S195 --out-dir build\shots\s197_s195_public_triage\review_comparison --summary-left build\shots\s191_water_mesh_smoothing\blender\bridge_summary.json --summary-right build\shots\s195_water_mesh_smoothing_strong\blender\bridge_summary.json --frames 4 --thumb-width 280 --title "S197 S195 Public Triage Review" --finding "Compact review sheet for deciding whether S195 should replace S191." --next "Accept S195 only if the smoother water body reads visibly better than S191 despite the small contrast loss."
```

## Decision

Keep S191 as the accepted baseline.

S195 preserves nonblank coverage and the S186 contrast floor, but it is 5
minimum contrast points below S191. The visual improvement is too subtle to
justify replacing S191.

## Next

Start a reconstruction/export smoothing milestone. The renderer-side smoothing
knob has reached diminishing returns, so the next visible improvement should
come from better water surface data rather than stronger post reconstruction
smoothing.
