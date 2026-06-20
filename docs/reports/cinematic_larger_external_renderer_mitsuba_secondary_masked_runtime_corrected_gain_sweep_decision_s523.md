# S523 Runtime Correction Gain Sweep Decision

Generated UTC: `2026-06-20T19:57:18Z`

## Inputs

- Raw render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Runtime import preview: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`
- Gain1 summary: `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/runtime_render_adapter_summary.json`
- Gain2 summary: `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain2_review/runtime_render_adapter_summary.json`
- Gain4 summary: `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/runtime_render_adapter_summary.json`
- Gain6 summary: `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/runtime_render_adapter_summary.json`

## Gate

All four candidates used the same 8 runtime-delta keyframes against the 48-frame S515 real Mitsuba render manifest. Every candidate reported `ready`, with `0` missing references and `0` dimension mismatches.

## Metrics

| Candidate | Max Change | Max Mean Change | Mean Luma | P95 | P99 | Bright >= 220 | Highlight >= 245 | Clip >= 254.5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gain1_s520` | `23` | `0.30087319958847736` | `166.331861` | `168.537375` | `191.811600` | `0.005130` | `0.004571` | `0.003684` |
| `gain2_s523` | `46` | `0.5931487911522634` | `166.403426` | `169.010800` | `192.793550` | `0.005204` | `0.004655` | `0.003890` |
| `gain4_s521` | `85` | `1.1587422839506172` | `166.543744` | `170.119550` | `194.712975` | `0.005730` | `0.004804` | `0.004159` |
| `gain6_s523` | `99` | `1.6686921296296295` | `166.678305` | `171.011950` | `196.309600` | `0.006349` | `0.005328` | `0.004366` |

## Decision

Promote `gain6_s523` as the next corrected-real-render review candidate.

Gain1 is too subtle. Gain2 is still conservative. Gain4 is a good stable default and is already published as S522. Gain6 gives the strongest visible lift in the tested range while keeping average clipping growth small. The strip view does not show an obvious blowout beyond the raw highlight region.

This remains a post-tonemap correction, not a renderer-native material solution. The next implementation step should derive deltas from the actual S515/S322 render family or make gain spatially/adaptively bounded instead of globally multiplying the S491 runtime delta package.

## Next

Publish the gain6 gallery as a stronger visual review URL, then add a proper render-family delta calibration pass.
