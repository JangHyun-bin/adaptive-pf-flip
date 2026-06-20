# S481 Mitsuba Response Control Light Full Decision

Generated UTC: `2026-06-20T16:44:04+00:00`

## Decision

Keep the S481 renderer-native light-only candidate as a working baseline, but do not promote it over the S478 `p4_soft_wide` proxy gate yet.

S481 proves the S479 light contract can be consumed into a full 8-frame Mitsuba XML export and rendered successfully. The visual gap is still worse than the promoted proxy because this pass only carries localized light/glint controls; the remaining water-body response is still waiting for the S479 material contract consumer.

## Inputs

- Full light XML export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- Render manifest: `build/shots/s481_mitsuba_response_control_light_full_render/mitsuba_render.json`
- Target-gap summary: `build/shots/s481_mitsuba_response_control_light_full_target_gap/renderer_target_gap_summary.json`
- Current proxy gate: `build/shots/s478_mitsuba_response_control_proxy_sweep/p4_soft_wide_target_gap/renderer_target_gap_summary.json`

## Render Checks

| Metric | Value |
| --- | ---: |
| Frames rendered | `8` |
| Failures | `0` |
| Total elapsed ms | `1293` |
| Image bytes | `17.56 MB` |
| Preview bytes | `2.07 MB` |
| LLVM runtime | `build/envs/llvm18_runtime/Library/bin/LLVM-C.dll` |

## Gap Comparison

| Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| --- | ---: | ---: | ---: | --- |
| S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current proxy gate |
| S481 native light-only | `19.215028131430042` | `23.98206790123457` | `219` | working native baseline, not promoted |

## Evidence

- S480 full export consumed sparse contract frames correctly: `5` matched frames, `3` missing contract frames ignored, `8` localized anchors, `8` lights inserted.
- S481 render used the Mitsuba-capable Python runtime and LLVM DLL path; the earlier conda Python failure was an environment issue (`No module named 'mitsuba'`), not an XML/export failure.
- The target-gap gallery is ready at `build/shots/s481_mitsuba_response_control_light_full_target_gap/gallery/index.html`.

## Next

Build the S479 material response contract consumer and combine it with the S481 light baseline. That is the next native-renderer step most likely to close the gap to the S478 `p4_soft_wide` proxy.
