# S633 Response AOV S585 Anchor Native Candidate S075

Generated UTC: `2026-06-21T04:04:19.219736+00:00`
Summary JSON: `build/shots/s633_response_aov_s585_anchor_native_candidate_s075/response_aov_s585_anchor_native_candidate_summary.json`
Gallery: `build/shots/s633_response_aov_s585_anchor_native_candidate_s075/gallery/index.html`
Status: `ready`
Decision: `s585_anchor_native_candidate_ready`
Selected candidate: `ANCHOR_SOFT_30`

## Selected Checks

- Frames: `48`
- Max candidate-vs-S585 abs diff: `2`
- Max candidate-vs-S585 mean diff: `0.09598251028806584`
- Mean candidate-vs-S585 mean diff: `0.07826358078275035`
- Max candidate-vs-S577 abs diff: `6`
- Max candidate-vs-S577 mean diff: `0.49603587962962964`
- Mean candidate-vs-S577 mean diff: `0.23535816668810014`
- Baseline max S585-vs-S577 mean diff: `0.4139242541152263`
- Strip GIF bytes: `32.42 MB`

## Candidate Sweep

| Candidate | Strength | S585 Max | S585 Max MAD | S585 Mean MAD | S577 Max | S577 Max MAD | S577 Mean MAD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ANCHOR_EDGE_20` | 0.2 | 1 | 0.00799511316872428 | 0.003559684177812071 | 6 | 0.41559477880658435 | 0.16065427008316188 |
| `ANCHOR_EDGE_26` | 0.26 | 1 | 0.028748713991769547 | 0.01724739315414952 | 6 | 0.42167116769547325 | 0.17434197905949933 |
| `ANCHOR_EDGE_32` | 0.32 | 1 | 0.041154835390946505 | 0.028379026813271604 | 6 | 0.4272479423868313 | 0.1854736127186214 |
| `ANCHOR_EDGE_38` | 0.38 | 2 | 0.05137345679012346 | 0.03833887924382716 | 6 | 0.4384304269547325 | 0.19543346514917695 |
| `ANCHOR_EDGE_44` | 0.44 | 2 | 0.06385545267489712 | 0.049249292695473255 | 6 | 0.45622878086419755 | 0.20634387860082304 |
| `ANCHOR_SOFT_18` | 0.18 | 1 | 0.04888824588477366 | 0.0311547952031893 | 6 | 0.4266261574074074 | 0.1882493811085391 |
| `ANCHOR_SOFT_22` | 0.22 | 1 | 0.06478716563786008 | 0.04737287272805213 | 6 | 0.4406687242798354 | 0.2044674586334019 |
| `ANCHOR_SOFT_26` | 0.26 | 1 | 0.07927597736625515 | 0.06219129104509602 | 6 | 0.4726408179012346 | 0.2192858769504458 |
| `ANCHOR_SOFT_30` | 0.3 | 2 | 0.09598251028806584 | 0.07826358078275035 | 6 | 0.49603587962962964 | 0.23535816668810014 |
| `ANCHOR_SOFT_34` | 0.34 | 2 | 0.12097993827160494 | 0.09569784700788753 | 7 | 0.5108757716049382 | 0.25279243291323733 |
| `ANCHOR_SOFT_40` | 0.4 | 2 | 0.15275913065843622 | 0.1226711596579218 | 7 | 0.5292200360082304 | 0.2797657455632716 |

## Next

Promote this S585-anchored native candidate into the process backend path, then publish if visual review is needed.
