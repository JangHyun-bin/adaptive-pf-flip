# S486 Mitsuba Proxy Native Parity Decision

Generated UTC: `2026-06-20T17:23:59.641041+00:00`

## Decision

Use S486 as the pivot from scalar light/material sweeps to low-frequency texture/tone parity.

The S478 `p4_soft_wide` proxy improves strongly inside the sparse response mask, but the response mask covers only about `0.49%` of pixels. The total image improvement is dominated by the outside-response area because that area covers the rest of the frame. S485 `lrs4_sparse_spec` confirms the same pattern after the best light/glint retune.

S487 should therefore implement a renderer-native low-frequency parity representation first, then optionally layer localized response controls on top. Another radius/radiance/material-alpha sweep is low leverage.

## Inputs

- S481 parity summary: `build/shots/s486_mitsuba_proxy_native_parity/proxy_native_parity_summary.json`
- S481 parity gallery: `build/shots/s486_mitsuba_proxy_native_parity/gallery/index.html`
- S485 LRS4 parity summary: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/proxy_native_parity_summary.json`
- S485 LRS4 parity gallery: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/gallery/index.html`
- AOV summary: `build/shots/s473_mitsuba_visual_cache_aov_import_package/visual_cache_aov_summary.json`

## Parity Results

| Native Baseline | Region | Coverage | Mean Improvement | Total Improvement | Proxy-Native Luma | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| S481 light-only | all | `1.0` | `0.13307790740739708` | `551900.6975999572` | `0.116710335358783` | proxy is globally closer |
| S481 light-only | response mask | `0.004900173611111111` | `9.678673250664357` | `196689.99780000106` | `9.742218334809621` | strong localized lift |
| S481 light-only | outside response mask | `0.9950998263888889` | `0.08607249833893899` | `355210.69980000384` | `0.06931141211346747` | broad low-frequency contribution |
| S485 LRS4 | all | `1.0` | `0.1328883421103292` | `551114.5323999573` | `0.11652550675152985` | same conclusion after light sweep |
| S485 LRS4 | response mask | `0.004900173611111111` | `9.65846820194868` | `196279.3908000011` | `9.722013286093944` | strong localized lift remains |
| S485 LRS4 | outside response mask | `0.9950998263888889` | `0.08598149535799314` | `354835.141600004` | `0.0692251691472349` | broad contribution remains |

## Negative Evidence

- S484 material masks did not close the gap and increased mean/max visual error.
- S485 light/glint parameter sweeps moved the score only in the fourth decimal place.
- S486 shows the missing proxy effect is not explained solely by the tiny response mask, even though that mask has high local impact.
- Target-dark pixels regress under the proxy (`-1.4842` mean improvement), so a naive global brighten would be wrong.

## Next

Implement S487 as a bounded low-frequency tone/texture parity pass: derive a smooth, target-aware residual field from proxy-vs-native parity, apply it as a conservative renderer-native texture/tone modulation, and compare against S478/S481/S485 gates. Keep localized glint/material controls available, but do not lead with them.
