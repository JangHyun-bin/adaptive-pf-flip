# S383 Larger External Renderer Mitsuba DS6 Ring Response

## Goal

Test a bounded target-free response that darkens only a narrow secondary ring
around the current DS6 dark-secondary mask. The intent was to recover part of
the remaining target-dark recall gap shown by the S382 evidence AOV package
without using target pixels directly.

## Inputs

- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Current target-free baseline:
  `build/shots/s375_mitsuba_selective_dark_secondary_response_ds6/source_region_response_summary.json`
- Target-fit diagnostic ceiling:
  `build/shots/s371_mitsuba_target_region_response_rr5/target_region_response_summary.json`

## Work

- Extended `tools/apply_mitsuba_source_region_response.py` with an optional
  dilated dark-secondary ring response:
  - `--dark-secondary-ring-radius`
  - `--dark-secondary-ring-source-luma-min`
  - `--dark-secondary-ring-source-luma-max`
  - `--dark-secondary-ring-strength`
  - `--dark-secondary-ring-max-delta`
- Tested three bounded variants:
  - `DR2`: radius `2`, luma `75..95`, strength `0.25`, max delta `24`
  - `DR3`: radius `3`, luma `75..95`, strength `0.20`, max delta `20`
  - `DR5`: radius `5`, luma `75..105`, strength `0.12`, max delta `16`
- Compared each candidate against the existing renderer target preview.
- Built a side-by-side review gallery with Target, C1E, SV1, DS6, DR2, and RR5.

## Results

| Candidate | Max target MAD | Mean target MAD | Max changed coverage | Max ring coverage |
| --- | ---: | ---: | ---: | ---: |
| `DS6` | `23.560514` | `18.662581` | `0.018507` | `0.000000` |
| `DR2` | `23.576083` | `18.682063` | `0.026819` | `0.008312` |
| `DR3` | `23.579101` | `18.684963` | `0.030106` | `0.011599` |
| `DR5` | `23.580107` | `18.685345` | `0.038567` | `0.020060` |
| `RR5` | `23.459498` | `18.309769` | target-fit | target-fit |

DR2 improves the narrow `secondary_dark_target` signed-luma diagnostic from
DS6's `+22.254368` to `+19.188976`, but worsens the global target gap. The
secondary-region MAD also increases from DS6's `20.538978` to DR2's
`20.971036`. Wider rings increase changed coverage and continue to worsen the
hard gate.

## Decision

Reject DS6 ring dilation for the current shot. The option is useful as a
reproducible experiment, but it should stay disabled by default. A simple
screen-space dilation catches some dark misses while also over-darkening
secondary regions that already matched the target well enough.

## Artifacts

- Updated tool:
  `tools/apply_mitsuba_source_region_response.py`
- DR2 response report:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-dr2.md`
- DR2 gap report:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-dr2-gap.md`
- DR2 region report:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-dr2-regions.md`
- DR3 gap report:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-dr3-gap.md`
- DR5 gap report:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-dr5-gap.md`
- Visual review:
  `docs/reports/2026-06-20-s383-mitsuba-ds6-ring-response-review.md`
- Main review gallery:
  `build/shots/s383_mitsuba_ds6_ring_response_review/gallery/index.html`

## Next

Move away from broader screen-space response masks. The next useful work should
export or approximate richer renderer-side AOVs: material/specular state,
water thickness, foam/spray density, or volume/absorption cues that can explain
the remaining target-dark gap without globally over-darkening secondary water.
