# S388 Larger External Renderer Mitsuba Secondary Channel Response Fine Tune

## Goal

Fine-tune the S387 channel-local response. CR2 proved the cue works, but the
band and strength were only coarsely sampled. This pass searches nearby
target-free settings to lower the full target-gap gate without broadening the
response footprint.

## Inputs

- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export and sidecar particle CSVs:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Current target-free response:
  `build/shots/s387_mitsuba_secondary_channel_response_cr2/source_region_response_summary.json`

## Work

- Swept 19 channel-local response candidates, `CR4` through `CR22`.
- Kept the response target-free:
  - DS6 primary response remains unchanged.
  - secondary channel union dilation stays `0`.
  - only source-luma band and darkening strength/max-delta vary.
- Compared every candidate with the existing target-gap harness.
- Ran region analysis for the best hard-gate candidate, `CR21`.
- Built a Target/C1E/SV1/DS6/CR2/CR21/RR5 visual review gallery.

## Results

Top candidates by max target MAD:

| Candidate | Band | Strength / Max delta | Max target MAD | Mean target MAD |
| --- | --- | ---: | ---: | ---: |
| `RR5` | target-fit | target-fit | `23.459497814` | `18.309769162` |
| `CR21` | `75..82` | `0.60 / 56` | `23.552905093` | `18.657217962` |
| `CR19` | `75..83` | `0.60 / 56` | `23.553244599` | `18.657767731` |
| `CR20` | `75..82` | `0.55 / 52` | `23.553431070` | `18.657099007` |
| `CR14` | `75..83` | `0.55 / 52` | `23.553731996` | `18.657480630` |
| `CR15` | `75..82` | `0.50 / 48` | `23.553960905` | `18.657047486` |
| `CR2` | `75..85` | `0.50 / 48` | `23.556300154` | `18.660959684` |
| `DS6` | `0..75` | primary only | `23.560514403` | `18.662580617` |

Region comparison:

| Region | DS6 MAD | CR2 MAD | CR21 MAD | DS6 signed luma | CR2 signed luma | CR21 signed luma |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `all` | `18.662581` | `18.660960` | `18.657218` | `-4.440509` | `-4.471850` | `-4.461869` |
| `secondary` | `20.538978` | `20.503029` | `20.420048` | `-2.561741` | `-3.256791` | `-3.035454` |
| `secondary_dark_target` | `32.980914` | `29.172706` | `29.787734` | `22.254368` | `18.055028` | `18.494426` |

CR21 is best for the hard max target-gap gate and secondary-region MAD. CR2 is
still slightly better for the narrow `secondary_dark_target` MAD, but the
project goal has been using max target MAD as the primary acceptance gate.

## Decision

Promote CR21 as the current target-free response baseline. It improves the DS6
max target MAD by `0.007609310` and improves the S387 CR2 max target MAD by
`0.003395061`. The gain is still incremental, but it is consistent with the
current evidence: keep the channel-local cue narrow, avoid channel dilation, and
avoid wider luma bands like `75..90`, which regressed to max target MAD
`23.602254372`.

## Artifacts

- CR21 response report:
  `docs/reports/2026-06-20-s388-mitsuba-secondary-channel-response-cr21.md`
- CR21 gap report:
  `docs/reports/2026-06-20-s388-mitsuba-secondary-channel-response-cr21-gap.md`
- CR21 region report:
  `docs/reports/2026-06-20-s388-mitsuba-secondary-channel-response-cr21-regions.md`
- Visual review:
  `docs/reports/2026-06-20-s388-mitsuba-secondary-channel-response-review.md`
- Main review gallery:
  `build/shots/s388_mitsuba_secondary_channel_response_review/gallery/index.html`

## Next

Use CR21 as the current target-free baseline. The next useful work is to move
the same narrow channel-local cue into the renderer/material path, or to build a
larger visual review package that compares CR21 against DS6 across more frames
and more visible crops.
