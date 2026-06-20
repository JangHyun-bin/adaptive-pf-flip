# S387 Larger External Renderer Mitsuba Secondary Channel Response

## Goal

Promote the S386 winning target-free mask into an actual visual response and
compare the full renderer target-gap gate against DS6.

## Inputs

- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export and sidecar particle CSVs:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- DS6 baseline:
  `build/shots/s375_mitsuba_selective_dark_secondary_response_ds6/source_region_response_summary.json`

## Work

- Extended `tools/apply_mitsuba_source_region_response.py` with an optional
  secondary-channel band path.
- The new path is disabled by default and only activates when
  `--mitsuba-export` plus positive `--channel-band-strength` are provided.
- Applied DS6 plus the S386 channel-local source-luma band:
  - channel union dilation radius: `0`
  - channel band source luma: `75..85`
  - CR1 strength/max delta: `0.25 / 24`
  - CR2 strength/max delta: `0.50 / 48`
  - CR3 strength/max delta: `1.00 / 255`
- Compared each candidate with the existing target-gap harness.
- Built a Target/C1E/SV1/DS6/CR2/RR5 visual review gallery.

## Results

| Candidate | Max target MAD | Mean target MAD | Max changed coverage | Max channel-band coverage |
| --- | ---: | ---: | ---: | ---: |
| `SV1` | `23.722171` | `19.103673` | baseline | baseline |
| `DS6` | `23.560514` | `18.662581` | `0.018507` | `0.000000` |
| `CR1` | `23.557825` | `18.658845` | `0.020502` | `0.001995` |
| `CR2` | `23.556300` | `18.660960` | `0.020502` | `0.001995` |
| `CR3` | `23.558519` | `18.677963` | `0.020502` | `0.001995` |
| `RR5` | `23.459498` | `18.309769` | target-fit | target-fit |

CR2 is the best worst-frame candidate. It reduces max target MAD from DS6
`23.56051440329218` to `23.556300`, while CR1 has the best mean target MAD.
Region analysis also improves the dark-secondary diagnostic:

| Region | DS6 MAD | CR2 MAD | DS6 signed luma | CR2 signed luma |
| --- | ---: | ---: | ---: | ---: |
| `secondary` | `20.538978` | `20.503029` | `-2.561741` | `-3.256791` |
| `secondary_dark_target` | `32.980914` | `29.172706` | `22.254368` | `18.055028` |

## Decision

Promote CR2 as the current best target-free visual response. The gain is small
but real: unlike DS6 ring dilation, the channel-local band improves both the
target-dark diagnostic and the hard max target-gap gate without visibly broad
over-darkening.

## Artifacts

- Updated tool:
  `tools/apply_mitsuba_source_region_response.py`
- CR2 response report:
  `docs/reports/2026-06-20-s387-mitsuba-secondary-channel-response-cr2.md`
- CR2 gap report:
  `docs/reports/2026-06-20-s387-mitsuba-secondary-channel-response-cr2-gap.md`
- CR2 region report:
  `docs/reports/2026-06-20-s387-mitsuba-secondary-channel-response-cr2-regions.md`
- Visual review:
  `docs/reports/2026-06-20-s387-mitsuba-secondary-channel-response-review.md`
- Main review gallery:
  `build/shots/s387_mitsuba_secondary_channel_response_review/gallery/index.html`

## Next

Use CR2 as the new target-free baseline. The next useful pass is to tune the
channel-local band more finely or move the same cue into a renderer/material
parameter instead of post-composite darkening.
