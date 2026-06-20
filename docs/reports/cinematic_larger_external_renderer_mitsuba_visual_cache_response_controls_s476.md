# S476 Mitsuba Visual Cache Response Controls

Generated UTC: `2026-06-20T16:22:21.357316+00:00`
Summary JSON: `build/shots/s476_mitsuba_visual_cache_response_controls/response_control_spec.json`
CSV: `build/shots/s476_mitsuba_visual_cache_response_controls/response_controls.csv`
Gallery: `build/shots/s476_mitsuba_visual_cache_response_controls/gallery/index.html`
Status: `ready`

## Checks

- Controls: `10`
- Frames with controls: `6`
- Localized light/glint controls: `8`
- Volume/material controls: `2`
- Max fit strength: `0.113725`
- GIF bytes: `943.06 KB`

## Top Controls

| Control | Frame | Output | Type | Strength | Pixels | BBox | Native Hint |
| --- | ---: | ---: | --- | ---: | ---: | --- | --- |
| `s476_f0006_c02` | 6 | 40 | `localized_light_or_glint` | 0.094118 | 577 | `[435, 190, 473, 209]` | surface glint texture or small area light fitted to water surface |
| `s476_f0000_c01` | 0 | 0 | `localized_light_or_glint` | 0.094118 | 560 | `[442, 139, 477, 159]` | surface glint texture or small area light fitted to water surface |
| `s476_f0006_c03` | 6 | 40 | `localized_light_or_glint` | 0.094118 | 408 | `[413, 216, 467, 225]` | surface glint texture or small area light fitted to water surface |
| `s476_f0005_c02` | 5 | 34 | `localized_light_or_glint` | 0.094118 | 160 | `[447, 197, 471, 206]` | surface glint texture or small area light fitted to water surface |
| `s476_f0005_c01` | 5 | 34 | `localized_light_or_glint` | 0.082353 | 292 | `[455, 214, 488, 225]` | surface glint texture or small area light fitted to water surface |
| `s476_f0002_c01` | 2 | 13 | `localized_light_or_glint` | 0.07451 | 242 | `[365, 122, 385, 137]` | surface glint texture or small area light fitted to water surface |
| `s476_f0000_c02` | 0 | 0 | `localized_light_or_glint` | 0.066667 | 247 | `[563, 28, 580, 44]` | surface glint texture or small area light fitted to water surface |
| `s476_f0004_c01` | 4 | 27 | `localized_light_or_glint` | 0.058824 | 443 | `[532, 215, 558, 237]` | surface glint texture or small area light fitted to water surface |
| `s476_f0007_c01` | 7 | 47 | `volume_or_material_response` | 0.113725 | 9907 | `[305, 230, 600, 290]` | water material/volume response texture carried by projected mask |
| `s476_f0006_c01` | 6 | 40 | `volume_or_material_response` | 0.094118 | 7480 | `[328, 228, 544, 272]` | water material/volume response texture carried by projected mask |

## Next

Use this response-control spec as the renderer-native fitting input; next build a proxy/native candidate and keep S473 AOV import plus target-gap as the gates.
