# S324 Larger External Renderer Mitsuba Composite Grade

## Goal

Reduce the flat gray read of the actual Mitsuba + secondary composite proof
without rerunning simulation or path tracing.

## Changes

- Add `tools/grade_mitsuba_composite.py`.
- Read `lsfs_mitsuba_secondary_composite` summaries from S323.
- Apply a lightweight review grade:
  - restrained exposure/contrast/saturation adjustment,
  - subtle cool tone,
  - small highlight bloom,
  - mild vignette,
  - GIF/gallery generation.

## Outputs

- Grade report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_composite_grade_soft_s324.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_composite_grade_publish_s324.md`
- Grade summary:
  `build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/grade_summary.json`
- Gallery:
  `build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/gallery/index.html`
- Public URL:
  `https://hydrocodone-becomes-attempted-unified.trycloudflare.com`

## Verification

- `python -m py_compile tools/grade_mitsuba_composite.py`
- `python tools/grade_mitsuba_composite.py ...`
- `python tools/publish_cinematic_gallery.py ... --cftunnel`
- Public checks:
  - `GET /index.html` returned `200`, `3256` bytes.
  - `HEAD /assets/shot.gif` returned `200`, `3010803` bytes.

## Result

S324 publishes an `8` frame, `2.87 MB` graded GIF from the S323 screen-space
secondary composite. A harsher first grade was rejected because it crushed water
detail; the committed proof uses a restrained grade that adds contrast and
focus while preserving more midtone information.

## Next

Promote grading/material settings into the renderer handoff contract so future
renderer backends can reproduce the review look without relying on ad hoc
post-process commands.
