# S379 Larger External Renderer Mitsuba Export Surface Quality Annotation

## Goal

After S377 and S378 exhausted global secondary-position and visibility-layer
density masks, preserve water mesh surface-quality metadata in the Mitsuba path
so the next material/normal evidence pass has a reliable frame-level input.

## Inputs

- Active SV1 Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Water mesh surface-quality CSV:
  `build/shots/s205_surface_quality_annotation/water_mesh_surface_quality_profile.csv`

## Work

- Add `tools/annotate_mitsuba_export_surface_quality.py`.
- Join Mitsuba export frames to S205 surface-quality rows by water OBJ path.
- Preserve `water_mesh.surface_quality` in
  `tools/export_external_renderer_mitsuba_xml.py` when scene descriptors already
  carry `diagnostics.water_mesh_surface_quality`.
- Generate an annotated manifest for the active SV1 export window.

## Results

- Frames annotated: `8 / 8`
- Missing quality frames: `0`
- Label counts: `{'normal_rough': 1, 'stable': 7}`
- Max normal discontinuity p95: `0.08905251265290359`
- Max mesh quality risk score: `0.13883554159123784`

## Decision

Use `water_mesh.surface_quality` as renderer/material metadata, not as the next
pixel mask by itself. The signal is available and now preserved, but it is
frame-level and too coarse to explain target-dark secondary pixels alone.

## Artifacts

- New tool:
  `tools/annotate_mitsuba_export_surface_quality.py`
- Updated exporter:
  `tools/export_external_renderer_mitsuba_xml.py`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_export_surface_quality_annotation_sv1_s379.md`
- Annotated manifest:
  `build/shots/s379_mitsuba_export_surface_quality_annotation_sv1/mitsuba_export_surface_quality.json`

## Next

Move from frame-level mesh quality to projected/per-pixel normal or
water-contact masks. Surface-quality labels are useful for material gating, but
the remaining S375/S376 dark-secondary miss needs spatial evidence.
