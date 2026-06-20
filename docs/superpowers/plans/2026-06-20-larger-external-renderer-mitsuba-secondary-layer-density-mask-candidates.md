# S378 Larger External Renderer Mitsuba Secondary Layer Density Mask Candidates

## Goal

After S377 rejected raw projected sidecar masks, test whether the already better
SV1 visibility layer can produce a stronger target-free dark-secondary mask via
local alpha or blurred-density evidence.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Current best DS6 evidence mask:
  `alpha_ge_4_source_luma_0_75`, equivalent to the S375
  `layer_secondary_source_luma_0_75` mask.

## Work

- Add `tools/analyze_mitsuba_secondary_layer_density_masks.py`.
- Evaluate alpha-threshold and blurred-density candidates crossed with source
  luma bands.
- Keep the analysis target-free: no target pixels are used to construct the
  candidates.
- Compare all density candidates against `target_dark_secondary` and
  `target_highlight` diagnostics.

## Results

- Best dark-secondary mask:
  `alpha_ge_4_source_luma_0_75`.
  - Precision: `0.858780`
  - Recall: `0.475602`
  - F1: `0.612175`
- Best blurred-density variants only match or fall below that baseline.
  - `density_b1_ge_4_source_luma_0_75`: F1 `0.612175`
  - `density_b2_ge_4_source_luma_0_75`: F1 `0.593510`
  - `density_b3_ge_6_source_luma_0_75`: F1 `0.589290`
- Best highlight mask remains `source_highlight_120` at F1 `0.888140`.

## Decision

Do not add a new density-driven response candidate. The local density sweep
mostly rediscovered the DS6 mask and did not add recall without losing
precision. Wider layer-density gates are not the next useful direction.

## Artifacts

- New tool:
  `tools/analyze_mitsuba_secondary_layer_density_masks.py`
- Main report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_layer_density_mask_candidates_sv1_s378.md`
- Main gallery:
  `build/shots/s378_mitsuba_secondary_layer_density_mask_candidates_sv1/gallery/index.html`
- Public quick-tunnel review:
  `https://prove-place-bond-players.trycloudflare.com/index.html`

## Next

Move to surface-normal, water-contact, or renderer-side material evidence. The
remaining dark-secondary miss is not explained by global secondary position or
simple visibility-layer density.
