# S389 Larger External Renderer Mitsuba Response Crop Review

## Goal

Build an inspectable crop/zoom review package for the current CR21 response
baseline. S388 improved the numeric target-gap gate, but the visual difference
is subtle enough that the next step should make the affected regions easy to
inspect before moving the cue deeper into the renderer/material path.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- DS6 response:
  `build/shots/s375_mitsuba_selective_dark_secondary_response_ds6/source_region_response_summary.json`
- CR2 response:
  `build/shots/s387_mitsuba_secondary_channel_response_cr2/source_region_response_summary.json`
- CR21 response:
  `build/shots/s388_mitsuba_secondary_channel_response_cr21/source_region_response_summary.json`
- RR5 target-fit reference:
  `build/shots/s371_mitsuba_target_region_response_rr5/target_region_response_summary.json`

## Work

- Added `tools/build_mitsuba_response_crop_review.py`.
- Built one 7-column crop strip per selected output frame:
  `Target`, `SV1`, `DS6`, `CR2`, `CR21`, `RR5`, and `Target Dark`.
- Crops are centered on the target-dark secondary mask from the CR21 reference
  layer, with padding and minimum crop dimensions so sparse masks remain
  visible.
- Wrote a gallery, animated GIF, summary JSON, and markdown report.

## Results

- Report:
  `docs/reports/2026-06-20-s389-mitsuba-response-crop-review-cr21.md`
- Summary:
  `build/shots/s389_mitsuba_response_crop_review_cr21/response_crop_review_summary.json`
- Gallery:
  `build/shots/s389_mitsuba_response_crop_review_cr21/gallery/index.html`
- Frames: `8`
- Columns: `7`
- Zoom: `2.0`
- GIF size: `8.51 MB`

The crop package makes the CR21/CR2 difference visible in the target-dark
secondary zones without relying on full-frame screenshots. CR21 remains the
current numeric baseline by max target MAD, while CR2 remains a useful fallback
for the narrower `secondary_dark_target` diagnostic if a future visual review
finds CR21 too broad or too dark.

## Decision

Keep CR21 as the current target-free visual baseline unless a human visual
review flags objectionable over-darkening in the crop package. The next useful
step is to either publish this gallery through a tunnel for visual review or
move the CR21 cue into the renderer/material path so it is no longer only a
post-composite response.

## Validation

- `python -m py_compile tools\build_mitsuba_response_crop_review.py`
- Summary JSON assertion:
  status `ready`, frames `8`, columns `7`, zoom `2.0`, gallery index exists.
- `git diff --check`
