# S631 Response Scale Gate Sweep S075

Generated UTC: `2026-06-21T03:46:12.948400+00:00`
Summary JSON: `build/shots/s631_response_scale_gate_sweep_s075/response_scale_gate_sweep_summary.json`
Gallery: `build/shots/s631_response_scale_gate_sweep_s075/gallery/index.html`
Status: `ready`
Decision: `response_scale_still_outside_gate`

## Selected Scale

- Scale: `0.75`
- Frames: `48`
- Failed frames: `0`
- Max scale-vs-S577 abs diff: `151`
- Max scale-vs-S577 mean diff: `5.5108699845679014`
- Mean scale-vs-S577 mean diff: `2.9732022274734224`
- Max scale-vs-S585 abs diff: `148`
- Max scale-vs-S585 mean diff: `5.524723508230453`
- Mean scale-vs-S585 mean diff: `2.982389550647291`
- Max S585-vs-S577 mean diff: `0.4139242541152263`
- GIF bytes: `44.04 MB`

## Scale Sweep

| Scale | Frames | Failed | S577 Max | S577 Max MAD | S577 Mean MAD | S585 Max | S585 Max MAD | S585 Mean MAD | Decision |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0.0 | 48 | 0 | 174 | 6.004408436213992 | 3.95164047764489 | 171 | 6.012960390946502 | 3.9582350474751373 | `measured` |
| 0.25 | 48 | 0 | 155 | 5.695960005144033 | 3.5287975019290125 | 152 | 5.705778677983539 | 3.5357163869598764 | `measured` |
| 0.5 | 48 | 0 | 143 | 5.534230324074074 | 3.16918844843107 | 140 | 5.540771604938271 | 3.1747733142575445 | `measured` |
| 0.75 | 48 | 0 | 151 | 5.5108699845679014 | 2.9732022274734224 | 148 | 5.524723508230453 | 2.982389550647291 | `measured` |
| 0.9 | 48 | 0 | 164 | 5.539096579218107 | 2.9776219296553497 | 161 | 5.556688528806585 | 2.988306970164609 | `measured` |
| 1.0 | 48 | 0 | 173 | 5.5758995627572014 | 3.038890683942044 | 172 | 5.595675154320988 | 3.050464838391632 | `measured` |
| 1.1 | 48 | 0 | 186 | 5.620531764403292 | 3.1456173509302126 | 185 | 5.64113683127572 | 3.1570717190715025 | `measured` |
| 1.25 | 48 | 0 | 205 | 5.725064300411523 | 3.3575997862011318 | 204 | 5.745953575102881 | 3.369008527842078 | `measured` |
| 1.5 | 48 | 0 | 218 | 5.9607053755144035 | 3.791210187328532 | 215 | 5.9814763374485596 | 3.8025017146776405 | `measured` |

## Next

Response-scale backoff alone does not recover the accepted S577/S585 envelope; branch the next renderer candidate from the S585 target contract instead of S617 response scale.
