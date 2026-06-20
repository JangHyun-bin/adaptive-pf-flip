# S486 Mitsuba Proxy Native Parity Analysis

Generated UTC: `2026-06-20T17:23:06.714478+00:00`
Summary JSON: `build/shots/s486_mitsuba_proxy_native_parity/proxy_native_parity_summary.json`
CSV: `build/shots/s486_mitsuba_proxy_native_parity/proxy_native_parity_regions.csv`
Gallery: `build/shots/s486_mitsuba_proxy_native_parity/gallery/index.html`
Status: `ready`

## Aggregate Regions

| Region | Coverage | Native Err | Proxy Err | Mean Improvement | Positive Coverage | Regression Coverage | Proxy-Native Luma |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `all` | 1.000000 | 17.760277 | 17.627199 | 0.133078 | 0.050950 | 0.043759 | 0.116710 |
| `response_mask` | 0.004900 | 78.811218 | 69.132545 | 9.678673 | 0.003757 | 0.000589 | 9.742218 |
| `outside_response_mask` | 0.995100 | 17.459644 | 17.373571 | 0.086072 | 0.047193 | 0.043170 | 0.069311 |
| `response_alpha` | 0.004900 | 78.811218 | 69.132545 | 9.678673 | 0.003757 | 0.000589 | 9.742218 |
| `response_luma` | 0.002133 | 101.134328 | 89.319417 | 11.814911 | 0.001764 | 0.000191 | 11.814911 |
| `target_highlight` | 0.006175 | 97.184997 | 90.638356 | 6.546641 | 0.003672 | 0.001577 | 6.546133 |
| `target_dark` | 0.025024 | 39.930545 | 41.414790 | -1.484246 | 0.007646 | 0.007940 | 1.623872 |

## Interpretation

Proxy mean improvement over native is `0.133078` luma over all pixels.
Inside response_mask the mean improvement is `9.678673` at coverage `0.004900`.
Outside response_mask the mean improvement is `0.086072` at coverage `0.995100`.
Most total improvement is outside the sparse response mask; this points toward low-frequency tone/texture parity, not another tiny localized glint.

## Next

Use this parity analysis to choose whether the next native representation should be low-frequency texture/tone parity or localized response controls.
