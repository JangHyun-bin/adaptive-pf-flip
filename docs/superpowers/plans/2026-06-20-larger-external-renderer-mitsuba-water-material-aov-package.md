# S384 Larger External Renderer Mitsuba Water Material AOV Package

## Goal

Build renderer-side water material AOV evidence so the next photoreal pass is
not driven by broader screen-space darkening. The package should expose water
coverage, surface depth, facing, flatness, silhouette edges, a screen-thickness
proxy, and an absorption proxy next to the target-dark diagnostic.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`

## Work

- Added `tools/build_mitsuba_water_material_aov_package.py`.
- Rasterized water mesh material evidence through the Mitsuba camera:
  - water coverage
  - depth-near value
  - camera-facing value
  - normal-y flatness
  - silhouette edge
  - screen-thickness proxy
  - absorption proxy
- Built a 14-panel AOV grid per frame:
  - Target
  - Actual
  - Layer Alpha
  - Source Luma
  - Water Mask
  - Depth Near
  - Facing
  - Flatness
  - Silhouette Edge
  - Thickness Proxy
  - Absorption Proxy
  - DS6 Mask
  - Target Dark
  - Overlay
- Evaluated 33 target-free material-AOV candidate masks against the
  target-dark-secondary diagnostic.

## Results

- Frames: `8`
- AOVs per frame: `14`
- Candidate masks: `33`
- GIF bytes: `8662539`
- Status: `baseline_still_best`

Top target-dark-secondary candidates:

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_secondary_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 2 | `water_secondary_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 3 | `water_facing_ge_160_secondary_source_luma_0_95` | `0.122242` | `0.763530` | `0.210744` | `0.022069` |
| 4 | `water_facing_ge_128_secondary_source_luma_0_95` | `0.117812` | `0.830478` | `0.206350` | `0.024906` |
| 5 | `water_facing_ge_96_secondary_source_luma_0_95` | `0.113872` | `0.858323` | `0.201068` | `0.026632` |

The material AOVs explain that the remaining target-dark misses lie on the
water surface, but they are too broad to replace DS6 directly. Depth/facing and
absorption proxies raise recall, but precision collapses because they cover
large parts of the water mound.

## Decision

Keep DS6 as the current target-free response mask. Promote the S384 AOV package
as renderer/material evidence, not as a response mask. The next useful pass
should localize residuals inside these broad material AOVs using secondary
particle density, spray/foam channel state, or a renderer-side shadow/occlusion
cue.

## Artifacts

- New tool:
  `tools/build_mitsuba_water_material_aov_package.py`
- Report:
  `docs/reports/2026-06-20-s384-mitsuba-water-material-aov-package-sv1.md`
- Summary:
  `build/shots/s384_mitsuba_water_material_aov_package_sv1/water_material_aov_summary.json`
- CSV:
  `build/shots/s384_mitsuba_water_material_aov_package_sv1/water_material_aov_candidates.csv`
- Gallery:
  `build/shots/s384_mitsuba_water_material_aov_package_sv1/gallery/index.html`

## Next

Build a residual-localization pass that intersects S384 material AOVs with
secondary channel density or visibility state. Avoid global absorption/darkening
until a target-free cue can isolate the output `34` style residual without
covering the whole water body.
