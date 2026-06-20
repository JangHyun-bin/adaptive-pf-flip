# Larger External Renderer: Mitsuba Residual Mask Source

Status: complete

## Goal

Convert the S386 secondary-channel residual-mask analysis into a reusable
per-frame alpha mask source, then test whether that narrower mask makes the
native Mitsuba screen-card path viable.

## Scope

- Add `tools/build_mitsuba_residual_mask_source.py`.
- Read `lsfs_mitsuba_secondary_channel_residual_mask_analysis` summaries.
- Rebuild the selected residual candidate mask per frame.
- Export a `lsfs_mitsuba_secondary_composite`-compatible summary with
  `layer_repo_path` pointing at generated RGBA alpha masks.
- Use the generated mask source in `add_mitsuba_secondary_screen_cards.py`.
- Render and score the residual-local screen-card candidate.

## Validation

- `python -m py_compile tools\build_mitsuba_residual_mask_source.py`
- S397 residual mask source: `ready`, `8` frames
- S397 screen-card export: `ready`, `8` frames, `0` missing references
- S397 Mitsuba render: `ready`, `8` frames, `0` render failures
- S397 target-gap comparison against the renderer target preview
- S397 native-to-C1E replacement comparison

## Result

The mask-source bridge works. The screen-card candidate still does not improve
the target metric.

- Residual mask candidate: `ds6_or_channel_union_r0_source_luma_75_85`
- Max residual mask coverage: `0.00818479938271605`
- Mean residual mask coverage: `0.002732687114197531`
- S397 max target MAD: `23.988894675925927`
- S397 mean target MAD: `19.222715486754115`
- SS1 max target MAD: `23.951853137860084`
- SS1 mean target MAD: `19.146412117412552`

## Decision

Keep `build_mitsuba_residual_mask_source.py` as reusable renderer evidence
plumbing. Do not continue screen-card overlays as the primary CR21 replacement:
even with a narrow residual-local alpha mask, the result matches the S396
failure profile and remains worse than SS1.

## Next

Move the local residual response into a real secondary/material/AOV path instead
of a camera-facing diffuse overlay. A practical next step is a native secondary
pass variant whose opacity/reflectance is driven by residual mask/AOV evidence,
then scored under the same target and C1E gates.
