# S486 Mitsuba Proxy Native Parity vs LRS4

Generated UTC: `2026-06-20T17:23:44.658747+00:00`
Summary JSON: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/proxy_native_parity_summary.json`
CSV: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/proxy_native_parity_regions.csv`
Gallery: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/gallery/index.html`
Status: `ready`

## Aggregate Regions

| Region | Coverage | Native Err | Proxy Err | Mean Improvement | Positive Coverage | Regression Coverage | Proxy-Native Luma |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `all` | 1.000000 | 17.760087 | 17.627199 | 0.132888 | 0.050949 | 0.043760 | 0.116526 |
| `response_mask` | 0.004900 | 78.791013 | 69.132545 | 9.658468 | 0.003757 | 0.000589 | 9.722013 |
| `outside_response_mask` | 0.995100 | 17.459553 | 17.373571 | 0.085981 | 0.047192 | 0.043171 | 0.069225 |
| `response_alpha` | 0.004900 | 78.791013 | 69.132545 | 9.658468 | 0.003757 | 0.000589 | 9.722013 |
| `response_luma` | 0.002133 | 101.088676 | 89.319417 | 11.769259 | 0.001764 | 0.000191 | 11.769259 |
| `target_highlight` | 0.006175 | 97.169310 | 90.638356 | 6.530954 | 0.003672 | 0.001577 | 6.530447 |
| `target_dark` | 0.025024 | 39.930587 | 41.414790 | -1.484204 | 0.007647 | 0.007939 | 1.623836 |

## Interpretation

Proxy mean improvement over native is `0.132888` luma over all pixels.
Inside response_mask the mean improvement is `9.658468` at coverage `0.004900`.
Outside response_mask the mean improvement is `0.085981` at coverage `0.995100`.
Most total improvement is outside the sparse response mask; this points toward low-frequency tone/texture parity, not another tiny localized glint.

## Next

Use this latest-native parity analysis to decide whether S487 should implement low-frequency texture/tone parity.
