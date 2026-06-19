# S218 Water Overlay Highlight Probe Gallery

Generated UTC: `2026-06-19T11:38:00Z`
Title: `S218 Water Overlay Highlight Probe`
Gallery directory: `build/shots/s218_overlay_highlight_probe/gallery`
Manifest: `build/shots/s218_overlay_highlight_probe/gallery/gallery_manifest.json`

## Assets

| Asset | Size | Dimensions | Path |
| --- | ---: | --- | --- |
| Shot GIF | 1.29 MB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/shot.gif` |
| S214 Accepted vs S218 Overlay Highlight | 991.45 KB | `1008 x 1772` | `build/shots/s218_overlay_highlight_probe/gallery/assets/comparison.png` |
| Keyframe 1 | 279.48 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_00.png` |
| Keyframe 2 | 285.31 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_01.png` |
| Keyframe 3 | 291.19 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_02.png` |
| Keyframe 4 | 291.29 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_03.png` |
| Keyframe 5 | 289.37 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_04.png` |
| Keyframe 6 | 286.22 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_05.png` |
| Keyframe 7 | 281.58 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_06.png` |
| Keyframe 8 | 275.68 KB | `640 x 360` | `build/shots/s218_overlay_highlight_probe/gallery/assets/keyframe_07.png` |

## Metadata Files

- `build/shots/s218_overlay_highlight_probe/gallery/assets/bridge_summary.json` (40.50 KB)
- `build/shots/s218_overlay_highlight_probe/gallery/assets/comparison_summary.json` (11.74 KB)

## Decision

S218 is the current safe overlay-highlight candidate. It leaves the accepted
water material, volume scattering, mesh smoothing, and `normal_rough` quality
smoothing unchanged, then tunes only reflection/glint overlays.

Metric deltas against S214 accepted:

- Minimum contrast delta: `0.0`
- Mean nonblank ratio delta: `0.0`
- Mean bright ratio delta: `0.0`
- Mean highlight ratio delta: `0.0`
- Mean luminance delta: `0.1124663628472149`

The gallery shows a subtle increase in surface streak readability without the
darkening seen in S216/S217.

## Next

Use S219 to either promote S218 into the accepted preset or A/B it against one
slightly stronger overlay-only candidate.
