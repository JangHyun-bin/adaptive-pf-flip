# S392 Larger External Renderer Mitsuba Secondary Material Response Compare

## Goal

Visually compare the S391 renderer-side CR21 material response against the
existing SS1 native render baseline, plus Target and C1E references.

## Work

- Reused `tools/build_mitsuba_candidate_compare_gallery.py`.
- Built a 4-column comparison gallery:
  `Target`, `C1E`, `SS1`, `S391_CR21_Material`.
- Compared the three output frames rendered by S391: `0`, `27`, and `47`.
- Checked one SS1/S391 frame diff for nonzero visible response.

## Results

- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_compare_s392.md`
- Summary:
  `build/shots/s392_mitsuba_secondary_material_cr21_compare/candidate_compare_gallery.json`
- Gallery:
  `build/shots/s392_mitsuba_secondary_material_cr21_compare/gallery/index.html`
- Frames: `3`
- Columns: `4`
- GIF size: `3.48 MB`

For output frame `27`, the SS1 to S391 preview diff mean is approximately
`[0.6444, 0.6950, 0.7492]`, with max channel deltas `[64, 69, 76]`. This proves
the renderer-side material scale is not a no-op, and the visual strip shows a
slightly darker secondary-particle response than SS1.

## Decision

Treat S391 as a live renderer/material knob, not yet as the accepted CR21
replacement. The visible response is useful but subtler than the post-composite
CR21 crop response, so the next step should either publish the S392 gallery for
review or run a small scale/opacity sweep against the target-gap harness.
