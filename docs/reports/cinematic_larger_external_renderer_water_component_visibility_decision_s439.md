# S439 Water Component Visibility Decision

Generated UTC: `2026-06-20T12:47:26+00:00`

## Scope

S439 checks whether the water reconstruction component issue seen in full
sequence quality diagnostics is actually present in the current full48 cinematic
render window.

## Inputs

- Scene spec:
  `build/shots/s305_larger_external_renderer_job_blender_full48/blender_scene_spec.json`
- Baseline reconstruction:
  `build/shots/s168_water_depth_foreground_separation/water_mesh/water_reconstruction.json`
- Tetra-soft reconstruction:
  `build/shots/s432_water_reconstruction_tetra_soft/water_reconstruction.json`
- Filter threshold: `0.24`

## Results

| Metric | Baseline S168 | Tetra Soft S432 |
| --- | ---: | ---: |
| Render frames | 48 | 48 |
| Selected mesh frames | 5..35 | 5..35 |
| Component rows | 48 | 48 |
| Would-filter components | 0 | 0 |
| Visible would-filter components | 0 | 0 |
| Mean inside vertex ratio | 0.857484 | 0.852124 |
| Mean clipped screen area | 0.912638 | 0.920853 |

The full48 scene selects mesh frames `5..35`. In that window, both the baseline
and tetra-soft reconstructions appear as a single selected component per render
frame. The early two-component frames that triggered the quality warning are not
part of the current full48 selected render window.

## Visual Artifacts

- Baseline overlay sheet:
  `build/reports/s439_water_component_overlay_s168/component_overlay_sheet.png`
- Tetra-soft overlay sheet:
  `build/reports/s439_water_component_overlay_tetra_soft/component_overlay_sheet.png`
- Baseline visibility report:
  `docs/reports/cinematic_larger_external_renderer_water_component_visibility_s168_s439.md`
- Tetra-soft visibility report:
  `docs/reports/cinematic_larger_external_renderer_water_component_visibility_tetra_soft_s439.md`

## Decision

Do not make component pruning the next renderer task. The component split is a
valid full-sequence topology warning, but it is not the current full48 visual
gap driver.

The next useful diagnostic should compare the projected water silhouette/depth
against the gap frames. S438 showed that smoothing improves mesh metrics but
worsens target gap; S439 shows component filtering is not active in the render
window. That leaves screen-space shape, thickness, and depth response as the
next likely primary-water causes.

## Next

S440 should build a water silhouette/depth alignment diagnostic against
`SS1_Native`, `S432_TetraSoftTS1`, and the target-gap strips before another
replacement render.
