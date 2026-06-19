# S323 Larger External Renderer Mitsuba Secondary Composite

## Goal

Create a non-sphere secondary representation path for the actual Mitsuba proof,
using the existing particle stream and camera data to build a soft screen-space
mist/foam layer.

## Changes

- Add `tools/composite_mitsuba_secondary_layer.py`.
- Read `lsfs_mitsuba_xml_render` manifests and their source Mitsuba XML export.
- Match rendered frames back to XML/export frames.
- Parse Mitsuba XML camera `lookat`, FOV, and film size.
- Project secondary particle CSV rows into screen space.
- Render a blurred RGBA secondary layer per frame.
- Composite the layer over actual Mitsuba preview PNGs.
- Build a static gallery with `assets/shot.gif`, keyframes, and metadata.

## Outputs

- Composite report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_composite_subtle_s323.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_composite_publish_s323.md`
- Composite summary:
  `build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/secondary_composite_summary.json`
- Gallery:
  `build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/gallery/index.html`
- Public URL:
  `https://fixes-achieve-pledge-cells.trycloudflare.com`

## Verification

- `python -m py_compile tools/composite_mitsuba_secondary_layer.py`
- `python tools/composite_mitsuba_secondary_layer.py ...`
- `python tools/publish_cinematic_gallery.py ... --cftunnel`
- Public checks:
  - `GET /index.html` returned `200`, `3377` bytes.
  - `HEAD /assets/shot.gif` returned `200`, `1360178` bytes.

## Result

S323 composites `8` frames, projects `2877 / 2877` selected secondary particles,
and publishes a `1.36 MB` GIF. The layer is still a screen-space approximation,
but it proves a renderer-facing secondary path that is not encoded only as
opaque sphere geometry.

## Next

Promote this from post-composite proof to renderer contract: export secondary
layer metadata alongside the external renderer bundle, then allow the final
renderer to consume mist/foam layers directly.
