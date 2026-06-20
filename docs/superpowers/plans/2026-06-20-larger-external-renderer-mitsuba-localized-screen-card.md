# Larger External Renderer: Mitsuba Localized Screen Card

Status: complete

## Goal

Test whether the native Mitsuba screen-card path can use a localized mask source
instead of the older depth-aware secondary layer only.

## Scope

- Keep the existing `add_mitsuba_secondary_screen_cards.py` positional CLI.
- Allow the mask source to be one of:
  - `lsfs_mitsuba_depth_aware_secondary_composite`
  - `lsfs_mitsuba_secondary_composite`
  - `lsfs_mitsuba_composite_grade`
- Read mask image paths from `secondary_layer_repo_path`, `secondary_layer_path`,
  `layer_repo_path`, `layer_path`, or a nested layer object.
- Run one S396 candidate from:
  - base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
  - mask source: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`

## Validation

- `python -m py_compile tools\add_mitsuba_secondary_screen_cards.py`
- S396 export: `ready`, `8` frames, `0` missing references
- S396 Mitsuba render: `ready`, `8` frames, `0` failures
- S396 target-gap comparison against the renderer target preview
- S396 native-to-C1E replacement comparison

## Result

The compatibility change is useful, but the SV1-localized screen-card candidate
does not improve the image metric.

- SS1 max target MAD: `23.951853137860084`
- S396 max target MAD: `23.988894675925927`
- SS1 mean target MAD: `19.146412117412552`
- S396 mean target MAD: `19.222715486754115`
- S396 max candidate-vs-C1E MAD: `22.189097865226337`

## Decision

Do not replace SS1 or post-composite CR21 with this screen-card candidate.
Keep the mask-source compatibility path because it lets future native-renderer
experiments consume visibility/composite/grade summaries without regenerating
depth-aware bridge data.

## Next

Move away from broad diffuse screen-card overlays. The next useful renderer-side
step is a local secondary response that is attached to actual secondary/material
or AOV data, or a small bridge that converts residual-mask analysis into a
single alpha mask suitable for a narrower native render experiment.
