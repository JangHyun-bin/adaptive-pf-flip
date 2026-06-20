# S386 Larger External Renderer Mitsuba Secondary Channel Residual Masks

## Goal

Use the high-precision secondary-channel evidence from S385 to recover part of
the DS6 target-dark recall gap without broad DS6 dilation. This pass searches
target-free masks that combine DS6 with channel-local source-luminance bands.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export and sidecar particle CSVs:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`

## Work

- Added `tools/analyze_mitsuba_secondary_channel_residual_masks.py`.
- Reused projected secondary-channel union masks from S385.
- Swept 109 masks over:
  - channel union dilation radii `0, 2, 4, 6, 8, 12, 16, 24, 32`
  - source-luma residual bands `75..85`, `75..95`, `75..105`, `85..105`
  - full source-luma ranges `0..75`, `0..85`, `0..95`, `0..105`
  - DS6 union variants
- Built visual grids showing target dark, DS6 miss, channel union, DS6,
  best mask, added band, and overlay.

## Results

- Frames: `8`
- Candidate masks: `109`
- Status: `beats_ds6`
- DS6 baseline F1: `0.6121749824314828`
- Best mask: `ds6_or_channel_union_r0_source_luma_75_85`
- Best F1: `0.6553528823212499`

Top target-dark-secondary candidates:

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_or_channel_union_r0_source_luma_75_85` | `0.751346` | `0.581110` | `0.655353` | `0.002733` |
| 2 | `channel_union_r12_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 3 | `channel_union_r16_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 4 | `channel_union_r24_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 5 | `channel_union_r32_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |

The winning mask does not dilate the channel union. It keeps the original
secondary-channel footprint and adds only the source-luma `75..85` band on top
of DS6. This raises recall from `0.475602` to `0.581110` while precision stays
usable at `0.751346`.

## Decision

Promote `ds6_or_channel_union_r0_source_luma_75_85` to the next visual response
candidate. This is the first post-DS6 target-free mask that beats DS6 on the
target-dark-secondary diagnostic. The next pass should apply a bounded response
using this added band and compare the full target-gap gate against DS6.

## Artifacts

- New tool:
  `tools/analyze_mitsuba_secondary_channel_residual_masks.py`
- Report:
  `docs/reports/2026-06-20-s386-mitsuba-secondary-channel-residual-masks-sv1.md`
- Summary:
  `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/secondary_channel_residual_mask_summary.json`
- CSV:
  `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/secondary_channel_residual_mask_candidates.csv`
- Gallery:
  `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/gallery/index.html`

## Next

Apply the winning mask as a bounded visual response: keep DS6 darkening, add a
weaker channel-local luma `75..85` dark-secondary response, then compare max and
mean target MAD against DS6.
