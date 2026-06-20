# S377 Larger External Renderer Mitsuba Projected Secondary Mask Candidates

## Goal

Test whether S353 projected secondary 3D sidecar metadata can provide a better
target-free dark-secondary mask than the current DS6 evidence mask.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Secondary 3D sidecar:
  `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- Current DS6 mask evidence:
  `layer_secondary_source_luma_0_75` from S375.

## Work

- Add `tools/analyze_mitsuba_projected_secondary_masks.py`.
- Rasterize sidecar particles through their stored `camera.ndc`, `depth`,
  `channel`, `radius`, `speed`, and `volume` metadata.
- Evaluate projected-only masks and projected-plus-source-luma masks against:
  - `target_highlight`
  - `target_dark_secondary`
- Compare against the existing layer/source-luma baseline in the same report.
- Run a small radius/blur sensitivity sweep before deciding whether to generate
  a response candidate.

## Results

- Baseline dark-secondary mask remains best:
  `layer_secondary_source_luma_0_75`.
  - Precision: `0.858780`
  - Recall: `0.475602`
  - F1: `0.612175`
- Best default projected dark-secondary mask:
  `projected_all_source_luma_0_75`.
  - Precision: `0.615419`
  - Recall: `0.475602`
  - F1: `0.536552`
- Best sensitivity-sweep projected setting:
  `r060_b24/projected_all_source_luma_0_75`.
  - Precision: `0.776458`
  - Recall: `0.459633`
  - F1: `0.577442`
- Projected masks are also poor highlight evidence. The best projected
  highlight mask is `projected_depth_far_33` at F1 `0.083346`, while
  `source_highlight_120` stays at F1 `0.888140`.

## Decision

Do not promote projected sidecar masks to a response candidate for this shot.
The current visibility layer alpha plus source-luma evidence is a better
target-free proxy than re-rasterizing the sidecar positions directly. The
projected sidecar remains useful as metadata, but not as the next dark-secondary
response mask.

## Artifacts

- New tool:
  `tools/analyze_mitsuba_projected_secondary_masks.py`
- Main report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_projected_secondary_mask_candidates_sv1_s377.md`
- Main gallery:
  `build/shots/s377_mitsuba_projected_secondary_mask_candidates_sv1/gallery/index.html`
- Public quick-tunnel review:
  `https://resident-adds-associate-isbn.trycloudflare.com/index.html`

## Next

Move from point-projection evidence to local visibility-layer density, surface
normal, or water-contact evidence. The next likely useful mask is not another
global secondary-position raster; it should explain where the visibility layer
is too bright over target-dark water detail.
