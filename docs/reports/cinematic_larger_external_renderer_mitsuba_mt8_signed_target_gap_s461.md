# S461 Mitsuba MT8 Signed Target Gap

Generated UTC: `2026-06-20T15:13:38.069393+00:00`
Summary JSON: `build/shots/s461_mitsuba_mt8_signed_target_gap/signed_target_gap_analysis.json`
Gallery: `build/shots/s461_mitsuba_mt8_signed_target_gap/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Requests: `20`
- Max positive luma gap: `169.1914`
- Max negative luma gap abs: `107.8848`
- GIF bytes: `8.16 MB`

## Aggregate Regions

| Region | Coverage | Mean Abs Luma | Signed Luma | Positive Px | Positive Mean | Negative Px | Negative Mean Abs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `all` | 1.000000 | 17.685456 | 5.040850 | 2316049 | 19.402234 | 1103111 | 23.098458 |
| `highlight` | 0.003992 | 102.519436 | 102.507081 | 16546 | 102.568530 | 4 | 22.814100 |
| `channel_band` | 0.000452 | 27.816061 | -22.850127 | 218 | 18.806948 | 1346 | 34.777228 |

## Top Response Requests

| Rank | Output | Region | Direction | Score | Mean Abs | Max Abs | Area | BBox | Strength |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 47 | `highlight` | `brighten` | 5793.591 | 103.224 | 168.191 | 3578 | `[329, 229, 606, 257]` | 0.6072 |
| 2 | 40 | `highlight` | `brighten` | 5007.930 | 99.588 | 167.123 | 4131 | `[322, 226, 552, 275]` | 0.5858 |
| 3 | 47 | `highlight` | `brighten` | 4354.012 | 103.941 | 167.979 | 1993 | `[309, 260, 442, 291]` | 0.6114 |
| 4 | 47 | `highlight` | `brighten` | 2852.131 | 100.432 | 130.522 | 916 | `[302, 243, 391, 271]` | 0.5908 |
| 5 | 0 | `highlight` | `brighten` | 2530.639 | 131.791 | 158.374 | 393 | `[441, 139, 478, 159]` | 0.7752 |
| 6 | 40 | `highlight` | `brighten` | 1819.815 | 104.863 | 169.191 | 492 | `[433, 190, 474, 209]` | 0.6168 |
| 7 | 34 | `highlight` | `brighten` | 1719.481 | 100.566 | 126.047 | 299 | `[454, 214, 490, 225]` | 0.5916 |
| 8 | 27 | `highlight` | `brighten` | 1557.430 | 85.184 | 162.911 | 414 | `[531, 211, 560, 239]` | 0.5011 |
| 9 | 34 | `highlight` | `brighten` | 1459.701 | 117.815 | 167.838 | 157 | `[446, 197, 473, 206]` | 0.6930 |
| 10 | 40 | `highlight` | `brighten` | 1299.675 | 110.013 | 167.264 | 228 | `[412, 216, 470, 225]` | 0.6471 |
| 11 | 0 | `highlight` | `brighten` | 1274.959 | 96.256 | 149.472 | 187 | `[562, 28, 581, 45]` | 0.5662 |
| 12 | 13 | `highlight` | `brighten` | 1119.886 | 93.650 | 126.246 | 143 | `[364, 122, 385, 137]` | 0.5509 |
| 13 | 34 | `highlight` | `brighten` | 1054.363 | 104.559 | 121.260 | 104 | `[511, 234, 528, 243]` | 0.6151 |
| 14 | 13 | `highlight` | `brighten` | 1018.579 | 103.421 | 124.119 | 97 | `[548, 96, 560, 109]` | 0.6084 |
| 15 | 7 | `highlight` | `brighten` | 1008.498 | 99.020 | 118.993 | 110 | `[559, 101, 569, 112]` | 0.5825 |
| 16 | 7 | `highlight` | `brighten` | 1003.292 | 99.416 | 124.783 | 108 | `[548, 74, 560, 90]` | 0.5848 |
| 17 | 0 | `highlight` | `brighten` | 927.887 | 97.771 | 142.753 | 96 | `[379, 44, 386, 65]` | 0.5751 |
| 18 | 13 | `highlight` | `brighten` | 908.875 | 106.376 | 125.119 | 73 | `[559, 136, 574, 151]` | 0.6257 |
| 19 | 27 | `highlight` | `brighten` | 852.770 | 94.904 | 123.355 | 100 | `[364, 223, 375, 236]` | 0.5583 |
| 20 | 7 | `highlight` | `brighten` | 727.740 | 105.982 | 131.853 | 50 | `[569, 91, 579, 100]` | 0.6234 |

## Next

Use the top signed frame-aware requests to build a bounded S462 response candidate from mt8_secondary_light.
