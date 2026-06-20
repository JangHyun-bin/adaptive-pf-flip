# S385 Larger External Renderer Mitsuba Secondary Channel AOV Package

## Goal

Localize the remaining target-dark residuals inside the broad S384 water
material AOVs by separating secondary particle channels. If spray, foam, bubble,
or channel density explains the residual better than DS6, it can guide the next
material or shadow pass.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export and sidecar particle CSVs:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`

## Work

- Added `tools/build_mitsuba_secondary_channel_aov_package.py`.
- Projected sidecar secondary particles through the Mitsuba camera by channel:
  - spray
  - foam
  - bubble
  - droplet
- Built 11-panel AOV grids for all 8 frames:
  - Target
  - Actual
  - Layer Alpha
  - Source Luma
  - Spray Density
  - Foam Density
  - Bubble Density
  - Union Density
  - DS6 Mask
  - Target Dark
  - Channel Overlay
- Evaluated 45 channel/density candidate masks against the
  target-dark-secondary diagnostic.

## Results

- Frames: `8`
- AOVs per frame: `11`
- Candidate masks: `45`
- GIF bytes: `7923443`
- Status: `baseline_still_best`

Top target-dark-secondary candidates:

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_secondary_source_luma_0_75` | `0.858780` | `0.475602` | `0.612175` | `0.001957` |
| 2 | `all_secondary_channels_source_luma_0_75` | `0.940143` | `0.215451` | `0.350564` | `0.000810` |
| 3 | `secondary_channel_union_source_luma_0_75` | `0.940143` | `0.215451` | `0.350564` | `0.000810` |
| 4 | `spray_or_foam_source_luma_0_75` | `0.954737` | `0.201529` | `0.332807` | `0.000746` |
| 5 | `spray_source_luma_0_75` | `0.947479` | `0.153893` | `0.264780` | `0.000574` |

The useful signal is precision: channel/source-luma candidates are very
accurate when they fire, but they miss too much of the target-dark residual.
Density thresholds recover more recall but lose precision quickly. Output `34`
shows this clearly: the spray/foam cluster is localized near the top center,
while target-dark residuals also appear across nearby water-surface speckles.

## Decision

Do not replace DS6 with secondary-channel density. Keep the AOV package as a
diagnostic for where the currently rendered spray/foam/bubble layer is too
narrow. The next useful pass should cluster residuals spatially or add a
renderer-side shadow/occlusion cue that can expand around high-precision
channel hits without darkening the whole water body.

## Artifacts

- New tool:
  `tools/build_mitsuba_secondary_channel_aov_package.py`
- Report:
  `docs/reports/2026-06-20-s385-mitsuba-secondary-channel-aov-package-sv1.md`
- Summary:
  `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/secondary_channel_aov_summary.json`
- CSV:
  `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/secondary_channel_aov_candidates.csv`
- Gallery:
  `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/gallery/index.html`

## Next

Build a target-diagnostic residual clustering pass around DS6 misses and
high-precision secondary-channel hits. Use it to decide whether a target-free
shadow/occlusion approximation is plausible before applying another response.
