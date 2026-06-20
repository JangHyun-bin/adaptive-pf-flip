# S380 Larger External Renderer Mitsuba Water Mesh Screen Mask Candidates

## Goal

Project the renderer water OBJ through the Mitsuba camera and test whether
screen-space water coverage or simple face-normal classes improve the
target-free dark-secondary mask.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active water/secondary Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`

## Work

- Add `tools/analyze_mitsuba_water_mesh_screen_masks.py`.
- Parse each water OBJ and Mitsuba XML camera.
- Rasterize:
  - `water_all`
  - flat-water masks by `abs(normal.y)`
  - tilted-water masks by `abs(normal.y)`
  - camera-facing water masks
- Cross those water masks with secondary alpha and source-luma bands.
- Compare against the DS6-equivalent `secondary_source_luma_0_75` baseline.

## Results

- Best dark-secondary mask remains `secondary_source_luma_0_75`.
  - Precision: `0.858780`
  - Recall: `0.475602`
  - F1: `0.612175`
- Best water mask is `water_all_secondary_source_luma_0_75`, exactly tied with
  the baseline at F1 `0.612175`.
- Normal/angle submasks improve precision slightly but lose recall:
  - `water_tilt_abs_y_lt_070_secondary_source_luma_0_75`: F1 `0.604012`
  - `water_camera_facing_060_secondary_source_luma_0_75`: F1 `0.600942`
  - `water_camera_facing_080_secondary_source_luma_0_75`: F1 `0.572895`
- Water masks are weak highlight evidence; best water highlight F1 is
  `0.052949`.

## Decision

Do not add a water-normal response candidate yet. Projected water coverage
explains why DS6 works, but the simple normal classes do not add useful recall.
The next spatial evidence should be explicit contact particles, contact foam
proxies, or renderer AOVs rather than broad water surface classes.

## Artifacts

- New tool:
  `tools/analyze_mitsuba_water_mesh_screen_masks.py`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_screen_mask_candidates_sv1_s380.md`
- Main gallery:
  `build/shots/s380_mitsuba_water_mesh_screen_mask_candidates_sv1/gallery/index.html`
- Public quick-tunnel review:
  `https://graphical-landscapes-settings-understood.trycloudflare.com/index.html`

## Next

Move to explicit contact-particle/contact-foam masks or renderer AOV export.
Simple projected water coverage and face-normal splits are not enough.
