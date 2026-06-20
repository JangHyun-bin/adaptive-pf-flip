# S361 Mitsuba Secondary Visibility Cache Validation

Generated UTC: `2026-06-20T03:23:40.386591+00:00`
Validation JSON: `build/shots/s361_mitsuba_secondary_visibility_cache_validation/secondary_visibility_cache_validation.json`
Status: `passed`

## Checks

- Frames: `8`
- Projected particles: `2877`
- Max layer coverage: `0.1105054012345679`
- Layer bytes: `540.24 KB`
- Failed checks: `0`

## Frame Samples

| Frame | Output | Coverage | Layer |
| ---: | ---: | ---: | --- |
| 0 | 0 | 0.054421296296296294 | `build/shots/s360_mitsuba_secondary_visibility_cache_sv1/layers/frame_0000_secondary_layer.png` |
| 4 | 27 | 0.03892168209876543 | `build/shots/s360_mitsuba_secondary_visibility_cache_sv1/layers/frame_0004_secondary_layer.png` |
| 7 | 47 | 0.1105054012345679 | `build/shots/s360_mitsuba_secondary_visibility_cache_sv1/layers/frame_0007_secondary_layer.png` |

## Next

Use the validated SV1 visibility cache as a stable input contract for the next renderer-facing secondary pass.
