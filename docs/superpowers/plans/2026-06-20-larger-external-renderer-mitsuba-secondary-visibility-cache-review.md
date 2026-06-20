# S363 Mitsuba Secondary Visibility Cache Review

## Goal

Make the S362 cache-consumer result visually inspectable against the accepted
target and the C1E depth-aware composite reference.

## Changes

- Extended `tools/build_mitsuba_candidate_compare_gallery.py` so candidates can
  be either:
  - `lsfs_mitsuba_xml_render`,
  - `lsfs_mitsuba_secondary_composite`.
- Generated a four-column review gallery:
  `Target | C1E | SS1 | SV1-cache`.

## Result

- Review report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_review_s363.md`
- Local gallery:
  `build/shots/s363_mitsuba_secondary_visibility_cache_review/gallery/index.html`
- Public quick-tunnel preview:
  `https://limiting-movie-differential-cleaning.trycloudflare.com/index.html`

The S363 strips confirm that `SV1-cache` makes the secondary mass much more
inspectable than `SS1`, while the remaining visible gap is mostly global
tone/background and C1E-like integration rather than cache availability.

## Next

Use this review to split the next work into two separate tracks:

- preserve SV1-cache visibility as the secondary data contract,
- add a tone/integration pass that moves the cache-consumed render closer to
  the target/C1E look without directly copying target pixels.
