# S478 Mitsuba Response Control Proxy Sweep Summary

## Decision

Promote `p4_soft_wide` as the current low-dimensional response-control proxy setting.

This is not yet renderer-native XML/material output, but it is the strongest evidence so far that the S476 response controls can carry the useful visual response with fewer degrees of freedom than the S473 AOV import layer.

## Inputs

- Control spec: `build/shots/s476_mitsuba_visual_cache_response_controls/response_control_spec.json`
- AOV package: `build/shots/s473_mitsuba_visual_cache_aov_import_package/visual_cache_aov_summary.json`
- Baseline AOV import target-gap: `build/shots/s473_mitsuba_visual_cache_aov_import_consumer_target_gap/renderer_target_gap_summary.json`

## Results

| Candidate | Gain | Material | Falloff | Mean MAD | Max MAD | Max Gap | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `S473_AOV_import` | n/a | n/a | n/a | `19.10240579989712` | `23.950307355967077` | `176` | previous bridge gate |
| `p1_baseline` | `1.00` | `0.70` | `1.50` | `19.100656266075102` | `23.949926697530863` | `176` | improves slightly |
| `p2_material_heavy` | `1.00` | `0.95` | `1.50` | `19.08900575488683` | `23.949926697530863` | `176` | better mean, same max |
| `p3_hot` | `1.15` | `0.80` | `1.50` | `19.089579073431068` | `23.949411008230452` | `176` | better max |
| `p4_soft_wide` | `1.05` | `0.85` | `1.00` | `19.079715470679012` | `23.9488554526749` | `176` | promote |

## Artifacts

- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p1_baseline_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p1_baseline_target_gap_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p2_material_heavy_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p2_material_heavy_target_gap_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p3_hot_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p3_hot_target_gap_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p4_soft_wide_s478.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_response_control_proxy_sweep_p4_soft_wide_target_gap_s478.md`

## Interpretation

The bbox-level control proxy is not losing the S473 AOV import signal. In this sweep it slightly improves both mean and max target-gap MAD.

That matters because the next renderer-native implementation does not need to reproduce the full response layer pixel-for-pixel. It can start from a small set of fitted controls:

- `8` localized light/glint controls
- `2` volume/material controls
- best proxy setting: gain `1.05`, material weight `0.85`, falloff `1.0`

## Next

Use `p4_soft_wide` as the S479 native-control target. The next pass should convert these controls into a renderer-facing package, keeping the S473 AOV import and S478 p4 target-gap as gates.
