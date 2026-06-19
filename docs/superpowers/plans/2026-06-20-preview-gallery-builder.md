# S275 External Bundle Preview Gallery

## Goal

Package the S274 external-bundle preview output into a lightweight static
gallery that can be opened locally or served through the existing gallery
publisher.

## Scope

- Add `tools/build_preview_gallery.py`.
- Copy a preview GIF to `assets/shot.gif` for compatibility with
  `tools/publish_cinematic_gallery.py`.
- Copy evenly sampled preview keyframes.
- Copy the preview `render_summary.json`.
- Emit `index.html`, `gallery_manifest.json`, and a checked-in Markdown report.

## Validation

- Script compile:
  `python -m py_compile tools/build_preview_gallery.py`
- Gallery build:
  `python tools/build_preview_gallery.py --render-summary build/shots/s274_external_bundle_preview/preview/render_summary.json --gif build/shots/s274_external_bundle_preview/preview.gif --preview-dir build/shots/s274_external_bundle_preview/preview --out build/shots/s275_external_bundle_preview_gallery/gallery --title "S275 External Bundle Preview Gallery" --keyframes 8 --report docs/reports/cinematic_external_bundle_preview_gallery_s275.md --next "Publish this preview gallery if a lightweight external-render handoff URL is needed; otherwise use it as the local visual smoke page before larger-shot work."`
- Manifest JSON validation:
  `python -m json.tool build/shots/s275_external_bundle_preview_gallery/gallery/gallery_manifest.json`
- Visual inspection:
  `build/shots/s275_external_bundle_preview_gallery/gallery/assets/keyframe_07.png`

## Result

- Gallery schema: `lsfs_preview_gallery`
- Version: `1`
- Assets: `9`
- Metadata files: `1`
- Preview frames represented: `8`
- Minimum occupancy: `0.0608984375`
- `index.html`: present
- `assets/shot.gif`: present

## Decision

S275 passes as the lightweight gallery packaging layer for S274. It makes the
external-bundle preview publishable without requiring a comparison sheet or the
heavier bridge-render gallery format.

## Next

Publish the S275 gallery through a separate quick tunnel when a lightweight
external-render handoff URL is useful.
