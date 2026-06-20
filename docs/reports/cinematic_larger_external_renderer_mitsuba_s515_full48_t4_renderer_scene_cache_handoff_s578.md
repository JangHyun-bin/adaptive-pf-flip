# S578 Mitsuba Renderer Scene Cache Handoff

Generated UTC: `2026-06-20T21:59:01.690358+00:00`
Summary JSON: `build/shots/s578_mitsuba_renderer_scene_cache_handoff/renderer_scene_cache_handoff_summary.json`
Gallery: `build/shots/s578_mitsuba_renderer_scene_cache_handoff/gallery/index.html`
Status: `ready`

## Checks

- Scene frames: `36`
- Visual frames: `48`
- Handoff frames: `48`
- Unique scene frames mapped: `36`
- Mapping mode: `nearest_normalized_scene_frame`
- Missing references: `0`
- Camera assets: `36`
- Particle assets: `36`
- Phase-cell assets: `36`
- Water meshes: `36`
- Texture bytes: `73.92 MB`
- Max texture reconstruction diff: `0`
- Max visual expected diff: `0`

## Scene Statistics

- Particle count: `{'min': 219072.0, 'max': 219072.0, 'mean': 219072.0}`
- Phase-cell count: `{'min': 32905.0, 'max': 33280.0, 'mean': 33188.083333333336}`
- Secondary count: `{'min': 192.0, 'max': 192.0, 'mean': 192.0}`

## Frame Samples

| Visual | Scene | Time | Particles | Phase Cells | Secondary | Strip |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.02 | 219072 | 33280 | 192 | `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/strips/frame_0000_texture_consumer.png` |
| 24 | 18 | 0.38000000000000006 | 219072 | 33246 | 192 | `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/strips/frame_0024_texture_consumer.png` |
| 47 | 35 | 0.7200000000000003 | 219072 | 32905 | 192 | `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/strips/frame_0047_texture_consumer.png` |

## Next

Validate this handoff as S579, then consume scene depth, water bounds, secondary counts, and low-frequency textures in the next metadata-driven renderer depth/material pass.
