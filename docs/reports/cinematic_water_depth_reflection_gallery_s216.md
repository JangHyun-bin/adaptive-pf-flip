# S216 Water Depth Reflection Probe Gallery

Generated UTC: `2026-06-19T11:24:24Z`
Title: `S216 Water Depth Reflection Probe`
Gallery directory: `build/shots/s216_depth_reflection_probe/gallery`
Manifest: `build/shots/s216_depth_reflection_probe/gallery/gallery_manifest.json`

## Assets

| Asset | Size | Dimensions | Path |
| --- | ---: | --- | --- |
| Shot GIF | 1.27 MB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/shot.gif` |
| S214 Accepted vs S216 Probe | 1.59 MB | `1008 x 1772` | `build/shots/s216_depth_reflection_probe/gallery/assets/comparison.png` |
| Keyframe 1 | 274.15 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_00.png` |
| Keyframe 2 | 280.40 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_01.png` |
| Keyframe 3 | 286.10 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_02.png` |
| Keyframe 4 | 285.55 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_03.png` |
| Keyframe 5 | 283.66 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_04.png` |
| Keyframe 6 | 280.86 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_05.png` |
| Keyframe 7 | 275.25 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_06.png` |
| Keyframe 8 | 269.99 KB | `640 x 360` | `build/shots/s216_depth_reflection_probe/gallery/assets/keyframe_07.png` |

## Metadata Files

- `build/shots/s216_depth_reflection_probe/gallery/assets/bridge_summary.json` (40.43 KB)
- `build/shots/s216_depth_reflection_probe/gallery/assets/comparison_summary.json` (11.74 KB)

## Decision

Keep S216 as an opt-in probe, not as the accepted preset. The probe preserves
coverage and increases bright/highlight ratios, but it lowers the contrast floor
and darkens the sequence:

- Minimum contrast delta: `-8.0`
- Mean luminance delta: `-0.7349235026041754`
- Mean bright ratio delta: `4.9370659722222215e-05`
- Mean highlight ratio delta: `4.340277777777777e-05`
- Mean nonblank ratio delta: `0.0`

The gallery is still useful as the reference for a follow-up contrast-preserving
depth/reflection tune.

## Next

Tune the S216 preset before promotion: recover contrast and luminance while
keeping the additional highlight continuity.
