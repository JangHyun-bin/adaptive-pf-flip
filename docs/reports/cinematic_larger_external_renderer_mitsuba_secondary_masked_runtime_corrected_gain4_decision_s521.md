# S521 Runtime Corrected Gain4 Decision

Generated UTC: `2026-06-20T19:55:12Z`

## Inputs

- Adapter tool: `tools/apply_mitsuba_low_frequency_runtime_to_render.py`
- Raw render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Runtime import preview: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`
- Gain1 review: `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/runtime_render_adapter_summary.json`
- Gain4 review: `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/runtime_render_adapter_summary.json`

## Adapter Gate

- S520 gain1 status: `ready`
- S521 gain4 status: `ready`
- Render source frames: `48`
- Runtime source frames: `8`
- Corrected frames: `8`
- Missing references: `0`
- Dimension mismatches: `0`

## Gain Comparison

| Candidate | Max Change | Max Mean Change | Mean Luma Mean | P95 Mean | P99 Mean | Bright >= 220 Mean | Highlight >= 245 Mean | Clip >= 254.5 Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `S520_gain1` | `23` | `0.30087319958847736` | `166.331861` | `168.537375` | `191.811600` | `0.005130` | `0.004571` | `0.003684` |
| `S521_gain4` | `85` | `1.1587422839506172` | `166.543744` | `170.119550` | `194.712975` | `0.005730` | `0.004804` | `0.004159` |

S517 raw full48 baseline had mean luminance `166.265066`, P95 mean `168.113571`, P99 mean `186.392717`, bright ratio `0.004165`, highlight ratio `0.003620`, and nonblank ratio `1.0`.

## Decision

Keep `S521_gain4` as the current corrected-real-render review candidate.

The gain1 path is useful as a contract-preserving adapter proof, but it is too subtle visually. Gain4 moves the S515 raw render in the intended direction: P95/P99 lift, highlight occupancy increases, and the strip view shows more visible surface response without a large average clipping increase. It still does not solve the renderer-native material problem, and it should not be called final photoreal output.

## Next

Publish the S521 gallery through Cloudflare and use it as the current corrected-real-render visual review surface. The next implementation pass should make this correction adaptive per frame or derive its deltas from the actual render family instead of reusing the S491 runtime texture package directly.
