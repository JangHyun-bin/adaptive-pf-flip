# S214 Mixed-Window Accepted Preset Gallery

Generated UTC: `2026-06-19T11:17:32Z`
Title: `S214 Mixed-Window Accepted Preset`
Gallery directory: `build/shots/s214_mixed_window_accepted_preset/gallery`
Manifest: `build/shots/s214_mixed_window_accepted_preset/gallery/gallery_manifest.json`

## Assets

| Asset | Size | Dimensions | Path |
| --- | ---: | --- | --- |
| Shot GIF | 1.29 MB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/shot.gif` |
| No Quality Smoothing vs Accepted | 687.70 KB | `1008 x 1772` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/comparison.png` |
| Keyframe 1 | 278.04 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_00.png` |
| Keyframe 2 | 284.54 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_01.png` |
| Keyframe 3 | 290.13 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_02.png` |
| Keyframe 4 | 289.85 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_03.png` |
| Keyframe 5 | 288.39 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_04.png` |
| Keyframe 6 | 284.70 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_05.png` |
| Keyframe 7 | 280.03 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_06.png` |
| Keyframe 8 | 274.56 KB | `640 x 360` | `build/shots/s214_mixed_window_accepted_preset/gallery/assets/keyframe_07.png` |

## Metadata Files

- `build/shots/s214_mixed_window_accepted_preset/gallery/assets/bridge_summary.json` (40.57 KB)
- `build/shots/s214_mixed_window_accepted_preset/gallery/assets/comparison_summary.json` (11.86 KB)

## Decision

The accepted mixed-window preset is visually safe after the S213 fold. The
gallery covers 8 rendered frames, including `normal_rough: 1` and `stable: 7`,
and compares the accepted preset against the same preset with
`water_mesh_quality_smoothing_pass` disabled.

Metric deltas stay within a no-regression band for this review:

- Minimum contrast delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Mean luminance delta: `0.00014919704861426908`
- Mean bright ratio delta: `5.425347222222257e-07`

## Next

Publish this gallery through `tools/publish_cinematic_gallery.py --cftunnel` if
remote review is needed. Otherwise continue with the next cinematic treatment on
top of the accepted mixed-window preset.
