# S294 Larger External Render Bundle 48

## Goal

Create a larger 48-frame external-render input bundle from the accepted source
window.

## Scope

- Extend `tools/build_bridge_external_render_bundle.py` with
  `--public-review-manifest`.
- Preserve the existing handoff-manifest input path.
- Override stale public-review metadata from S271 with the current S292 publish
  manifest.
- Generate a 48-frame `lsfs_bridge_external_render_bundle`.
- Record a Markdown report.

## Command

`python tools/build_bridge_external_render_bundle.py --handoff-manifest build/shots/s271_accepted_handoff/handoff_manifest.json --public-review-manifest build/shots/s292_external_renderer_job_blender_full32_publish/publish_manifest.json --frames 48 --out build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json --report docs/reports/cinematic_larger_external_render_bundle_s294.md --title "S294 Larger External Render Bundle 48" --next "Use S294 as the 48-frame larger-shot external-render input bundle before creating a larger renderer job."`

## Result

- Tool update:
  `tools/build_bridge_external_render_bundle.py`
- Bundle:
  `build/shots/s294_larger_external_render_bundle_48/external_render_bundle.json`
- Report:
  `docs/reports/cinematic_larger_external_render_bundle_s294.md`
- Schema: `lsfs_bridge_external_render_bundle`
- Frames: `48`
- Source window: `8..55`
- Public URL:
  `https://shall-warnings-critical-quite.trycloudflare.com`
- Missing assets: `0`
- Particle CSV footprint: `1.92 GB`
- Phase-cell CSV footprint: `50.49 MB`
- Water mesh OBJ footprint: `80.07 MB`

## Decision

S294 supersedes S273 for larger-shot input planning. It still references the
same accepted source window and assets, but it preserves more temporal samples.

## Next

Build a larger 48-frame `lsfs_external_renderer_job` from S294, then run a
visual preview gate before attempting another Blender render.
