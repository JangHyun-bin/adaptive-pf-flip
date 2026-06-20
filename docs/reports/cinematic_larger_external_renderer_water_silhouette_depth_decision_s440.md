# S440 Water Silhouette/Depth Decision

Generated UTC: `2026-06-20T12:50:14+00:00`

## Scope

S440 compares projected water-mesh screen masks for the current SS1 baseline and
the S432 tetra-soft water replacement. This checks whether the replacement
changed the screen-space explanation of the target dark/bright regions enough to
justify another surface-reconstruction render.

## Inputs

- Target summary:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Actual secondary composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- SS1 export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Tetra-soft export:
  `build/shots/s432_mitsuba_tetra_soft_ts1/mitsuba_export.json`

## Results

| Metric | SS1 | Tetra Soft |
| --- | ---: | ---: |
| Frames | 8 | 8 |
| Water candidates | 49 | 49 |
| Best dark-secondary F1 | 0.612175 | 0.612175 |
| Best water dark-secondary F1 | 0.612175 | 0.612175 |
| Best water highlight F1 | 0.052949 | 0.053415 |
| Gallery bytes | 4.05 MB | 4.05 MB |

The strongest dark-secondary explanation is already
`water_all_secondary_source_luma_0_75`, and it is identical between SS1 and
tetra-soft. The tetra-soft replacement slightly changes normal-classified water
masks, but it does not change the main dark-secondary screen-region explanation.

For target highlights, water geometry remains a poor explanation in both cases:
the best water-highlight F1 stays near `0.053`, while the non-water
`source_highlight_120` mask reaches F1 `0.888140`.

## Visual Artifacts

- SS1 gallery:
  `build/reports/s440_water_mesh_screen_masks_ss1/gallery/index.html`
- Tetra-soft gallery:
  `build/reports/s440_water_mesh_screen_masks_tetra_soft/gallery/index.html`
- SS1 strip sample:
  `build/reports/s440_water_mesh_screen_masks_ss1/gallery/assets/strip_00.png`
- Tetra-soft strip sample:
  `build/reports/s440_water_mesh_screen_masks_tetra_soft/gallery/assets/strip_00.png`

## Decision

Do not run another tetra/smoothing replacement render for this target. The
replacement improved mesh quality metrics, but S440 shows it does not materially
change the projected screen-region explanation that matters for the current
visual gap.

The dark-secondary response is already explainable by water plus secondary
luma, but the score leader remains ahead because the highlight/primary response
is not native yet. The next step should isolate highlight/light/volume response
as a render input, not mutate the water triangle mesh again.

## Next

S441 should build a target-free highlight/light response probe that uses the
nonsecondary source-highlight mask as evidence, but avoids post-composite CR21
wholesale grading.
