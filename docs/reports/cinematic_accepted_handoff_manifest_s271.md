# S271 Accepted Bridge Handoff Manifest

Generated UTC: `2026-06-19T19:40:39.249819+00:00`
Manifest JSON: `build/shots/s271_accepted_handoff/handoff_manifest.json`
Accepted preset: `dam_break_water_mesh_smoothing`
Git commit: `b53576c548a45406757f6b3f2740bc528f8278ef`

## Review Target

- Shot: `build/shots/s269_secondary_dewarm_acceptance`
- Gallery: `build/shots/s269_secondary_dewarm_acceptance/gallery/index.html`
- Public URL: `https://rfc-empirical-match-outstanding.trycloudflare.com`
- Local URL: `http://127.0.0.1:8900`
- Publish status: `running`

## Render Summary

- Status: `rendered`
- Preset: `dam_break_water_mesh_smoothing`
- Frames: `32`
- Resolution: `640 x 360`
- Samples: `16`

## Key Metrics

### s268_motion_review
- mean_luminance: `-0.24766113281251023`
- contrast_min: `0.0`
- bright_ratio: `1.3563368055554965e-07`
- highlight_ratio: `5.425347222222257e-07`
- nonblank_ratio: `0.0`

### s269_baseline_delta
- mean_luminance: `-0.24766167534723138`
- contrast_min: `0.0`
- bright_ratio: `1.3563368055554965e-07`
- highlight_ratio: `5.425347222222257e-07`
- nonblank_ratio: `0.0`

### s269_parity
- mean_luminance: `-5.425347211485132e-07`
- contrast_min: `0.0`
- bright_ratio: `0.0`
- highlight_ratio: `0.0`
- nonblank_ratio: `0.0`

## Source Fingerprints

| Source | Schema | Size | Path |
| --- | --- | ---: | --- |
| review_package | `lsfs_bridge_cinematic_review_package` | 34.13 KB | `build/shots/s270_accepted_review_package/review_package.json` |
| publish_manifest | `n/a` | 1.90 KB | `build/shots/s270_s269_gallery_publish/publish_manifest.json` |
| render_data_summary | `lsfs_render_data_summary` | 49.41 KB | `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json` |
| sequence | `n/a` | 112.31 KB | `build/shots/s205_surface_quality_annotation/converted/sequence.json` |
| preset_config | `n/a` | 99.83 KB | `configs/cinematic_presets.json` |

## Next

Use this handoff manifest as the accepted S269 baseline pointer for external renderer work, larger-shot reruns, and large-scale benchmark gates.
