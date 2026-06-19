# S217 Water Depth Reflection Contrast Probe Gallery

Generated UTC: `2026-06-19T11:30:12Z`
Title: `S217 Water Depth Reflection Contrast Probe`
Gallery directory: `build/shots/s217_depth_reflection_contrast_probe/gallery`
Manifest: `build/shots/s217_depth_reflection_contrast_probe/gallery/gallery_manifest.json`

## Assets

| Asset | Size | Dimensions | Path |
| --- | ---: | --- | --- |
| Shot GIF | 1.28 MB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/shot.gif` |
| S214 Accepted vs S217 Contrast Probe | 1.55 MB | `1008 x 1772` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/comparison.png` |
| Keyframe 1 | 276.55 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_00.png` |
| Keyframe 2 | 282.90 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_01.png` |
| Keyframe 3 | 288.43 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_02.png` |
| Keyframe 4 | 287.83 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_03.png` |
| Keyframe 5 | 286.62 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_04.png` |
| Keyframe 6 | 283.22 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_05.png` |
| Keyframe 7 | 277.76 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_06.png` |
| Keyframe 8 | 272.33 KB | `640 x 360` | `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/keyframe_07.png` |

## Metadata Files

- `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/bridge_summary.json` (40.66 KB)
- `build/shots/s217_depth_reflection_contrast_probe/gallery/assets/comparison_summary.json` (11.92 KB)

## Decision

Do not promote S217. The gallery confirms the probe preserves coverage and adds
surface highlight energy, but the contrast floor regresses:

- Minimum contrast delta vs S214: `-13.0`
- Mean luminance delta vs S214: `-0.3267182074652766`
- Mean bright ratio delta vs S214: `6.890190972222223e-05`
- Mean highlight ratio delta vs S214: `4.12326388888889e-05`
- Mean nonblank ratio delta vs S214: `0.0`

S217 improves luminance relative to S216, but it does not recover contrast.

## Next

S218 should keep the accepted water material and tune only the reflection/glint
overlay controls.
