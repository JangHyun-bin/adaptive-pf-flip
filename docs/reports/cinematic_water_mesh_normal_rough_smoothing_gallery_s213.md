# S213 Normal-Rough Smoothing Review Gallery

Generated UTC: `2026-06-19T11:06:07Z`
Title: `S213 Normal-Rough Smoothing Review`
Gallery directory: `build/shots/s213_normal_rough_review/gallery`
Manifest: `build/shots/s213_normal_rough_review/gallery/gallery_manifest.json`

## Assets

| Asset | Size | Dimensions | Path |
| --- | ---: | --- | --- |
| Shot GIF | 670.12 KB | `640 x 360` | `build/shots/s213_normal_rough_review/gallery/assets/shot.gif` |
| Untreated vs S212 Smoothing | 777.13 KB | `1008 x 892` | `build/shots/s213_normal_rough_review/gallery/assets/comparison.png` |
| Keyframe 1 | 292.15 KB | `640 x 360` | `build/shots/s213_normal_rough_review/gallery/assets/keyframe_00.png` |
| Keyframe 2 | 288.96 KB | `640 x 360` | `build/shots/s213_normal_rough_review/gallery/assets/keyframe_01.png` |
| Keyframe 3 | 284.78 KB | `640 x 360` | `build/shots/s213_normal_rough_review/gallery/assets/keyframe_02.png` |
| Keyframe 4 | 287.90 KB | `640 x 360` | `build/shots/s213_normal_rough_review/gallery/assets/keyframe_03.png` |

## Metadata Files

- `build/shots/s213_normal_rough_review/gallery/assets/bridge_summary.json` (28.54 KB)
- `build/shots/s213_normal_rough_review/gallery/assets/comparison_summary.json` (6.99 KB)

## Decision

Fold the S212 mesh smoothing pass into the accepted
`dam_break_water_mesh_smoothing` preset as a label-gated `normal_rough` treatment.

The gallery packages the S212 4-frame visual review plus the untreated comparison
sheet. The comparison keeps nonblank coverage unchanged, raises minimum contrast
by `45.0`, nudges mean luminance by `0.004424913194455371`, and keeps
bright/highlight energy effectively stable for this window.

The accepted preset validation remains conservative:

- Stable accepted-window dry-run: `build/shots/s213_normal_rough_review/accepted_preset_dry`
- Stable gate: `passed`, labels `stable: 4`, stable ratio `1.0`
- Normal-rough dry-run: `build/shots/s213_normal_rough_review/accepted_preset_normal_rough_dry`
- Normal-rough window labels: `normal_rough: 4`
- Preset quality smoothing: enabled for `normal_rough`, `factor: 0.04`, `iterations: 1`

## Next

Run a mixed-window accepted-preset render to check that stable and
`normal_rough` frames route correctly in one review sequence. If external review
is needed, publish this gallery through
`tools/publish_cinematic_gallery.py --cftunnel`.
