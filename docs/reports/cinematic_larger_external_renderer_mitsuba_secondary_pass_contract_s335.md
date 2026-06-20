# S335 Mitsuba Secondary Pass Contract

Generated UTC: `2026-06-20T00:15:43.424764+00:00`
Contract JSON: `build/shots/s335_mitsuba_secondary_pass_contract/secondary_pass_contract.json`
Status: `ready`
Public URL: `https://laundry-tanks-prot-until.trycloudflare.com`

## Checks

- Frames: `8`
- Missing frame assets: `0`
- Mean overlay MAD: `12.566030735596708`
- Max overlay MAD: `18.040229552469135`
- Max overlay max diff: `214`
- Public URL present: `True`

## Sources

- overlay_summary: `build/shots/s334_mitsuba_secondary_overlay_hybrid/secondary_overlay_summary.json` (`lsfs_mitsuba_render_secondary_overlay`)
- actual_render_manifest: `build/shots/s333_mitsuba_secondary_halo_h2/actual_render/mitsuba_render.json` (`lsfs_mitsuba_xml_render`)
- handoff_manifest: `build/shots/s327_mitsuba_renderer_handoff_bundle/handoff_manifest.json` (`lsfs_mitsuba_renderer_handoff_bundle`)
- target_summary: `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json` (`lsfs_mitsuba_renderer_target_preview`)
- publish_manifest: `build/shots/s334_mitsuba_secondary_overlay_hybrid_publish/publish_manifest.json` (`n/a`)

## Artifacts

| Label | Role | Size | Path |
| --- | --- | ---: | --- |
| gallery index | `review_page` | 3.36 KB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/index.html` |
| overlay gif | `animated_review` | 2.65 MB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/shot.gif` |
| Overlay Strip 1 | `review_strip` | 2.28 MB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_00.png` |
| Overlay Strip 2 | `review_strip` | 2.12 MB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_01.png` |
| Overlay Strip 3 | `review_strip` | 2.25 MB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_02.png` |
| Overlay Strip 4 | `review_strip` | 2.52 MB | `build/shots/s334_mitsuba_secondary_overlay_hybrid/gallery/assets/overlay_strip_03.png` |

## Frame Samples

| Frame | Output | Overlay MAD | Overlay | Target |
| ---: | ---: | ---: | --- | --- |
| 0 | 0 | 15.619526105967077 | `build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0000.png` | `build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0000.png` |
| 4 | 27 | 10.831884645061729 | `build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0004.png` | `build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0004.png` |
| 7 | 47 | 18.040229552469135 | `build/shots/s334_mitsuba_secondary_overlay_hybrid/overlay_graded/frame_0007.png` | `build/shots/s328_mitsuba_renderer_target_preview/renderer_target/frame_0007.png` |

## Next

Use this contract to replace the hybrid screen-space overlay with a renderer-native secondary pass while preserving target-diff gates.
