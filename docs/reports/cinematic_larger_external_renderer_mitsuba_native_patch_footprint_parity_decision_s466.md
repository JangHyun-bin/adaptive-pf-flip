# S466 Mitsuba Native Patch Footprint Parity Decision

Generated UTC: `2026-06-20T16:00:00+00:00`

## Decision

Use the S466 parity result to stop treating S465 as a placement problem. The native patches land inside the intended signed-response regions; the remaining mismatch is energy/material/visibility transfer.

The next renderer-native step should not blindly increase patch radiance. It should test a different native response model: brighter but more camera-facing area lights, response material overlays, or a controlled compositor-compatible renderer pass that preserves the S463 image-space gain while remaining cacheable and explicit.

## Evidence

- Parity analyzer: `tools/analyze_mitsuba_native_patch_footprint_parity.py`
- Parity report: `docs/reports/cinematic_larger_external_renderer_mitsuba_native_patch_footprint_parity_nr2_s466.md`
- Parity summary: `build/shots/s466_mitsuba_native_patch_footprint_parity_nr2/native_patch_footprint_parity.json`
- Parity gallery: `build/shots/s466_mitsuba_native_patch_footprint_parity_nr2/gallery/index.html`
- Representative overlay: `build/shots/s466_mitsuba_native_patch_footprint_parity_nr2/gallery/assets/parity_frame_03.png`

## Findings

| Metric | Value | Interpretation |
| --- | ---: | --- |
| Frames analyzed | `8` | Full current target comparison frame set. |
| Requests | `12` | Same signed highlight/brighten request set used by S465. |
| Native patches matched | `12` | No request/patch matching failure. |
| Patches inside request bbox | `12` | All native patches land inside intended regions. |
| Inside bbox ratio | `1.0` | Placement is not the main failure mode. |
| Mean center error | `3.6841374126594757 px` | Small relative to request bbox sizes. |
| Max center error | `10.474084382901559 px` | Still inside bbox in the worst case. |

## Frame Notes

| Output | Requests | Patches | Inside | Mean Error | Max Error |
| ---: | ---: | ---: | ---: | ---: | ---: |
| `0` | `2` | `2` | `2` | `1.835` | `2.231` |
| `13` | `1` | `1` | `1` | `0.809` | `0.809` |
| `27` | `1` | `1` | `1` | `7.087` | `7.087` |
| `34` | `2` | `2` | `2` | `2.972` | `3.267` |
| `40` | `3` | `3` | `3` | `1.882` | `2.566` |
| `47` | `3` | `3` | `3` | `7.018` | `10.474` |

## Interpretation

S465 underperformed S463 even though the native patch centers are correctly placed. That means the local disk emitter path does not inject enough visible highlight energy into the final render. The missing behavior is not "find the right screen area"; it is "make the renderer produce the same response inside that area."

This argues for a response model change. A pure disk-emitter sweep is unlikely to catch up quickly unless the disk orientation, size, visibility, and material interaction are changed together.

## Next

S467 should prototype a compositor-compatible signed response pass as an explicit cache artifact: store the S463-style bounded response as a render layer with metadata, not as an ad hoc final PNG mutation. In parallel, keep native patches as experimental, but use parity reports as the gate before additional native tuning.
