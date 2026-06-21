# S628 Mitsuba Response AOV Scene Native Probe Guard S075

Generated UTC: `2026-06-21T03:20:20.122795+00:00`
Summary JSON: `build/shots/s628_mitsuba_response_aov_scene_native_probe_guard_s075/response_aov_scene_native_probe_guard_summary.json`
Gallery: `build/shots/s628_mitsuba_response_aov_scene_native_probe_guard_s075/gallery/index.html`
Status: `ready`
Candidate: `BOLD_SAFE`

## Guard Checks

- Max abs delta from S623: `7`
- Max mean abs delta from S623: `0.5889236111111111`
- Late max abs delta from S623: `6`
- Late max mean abs delta from S623: `0.5678240740740741`
- Peak frame count: `4`
- Late frame count: `12`
- Max abs tolerance: `10`
- Max MAD tolerance: `0.75`
- Late max MAD tolerance: `0.75`
- Guard status: `passed`

## Guard Frames

| Kind | Frame | Scene | Source | Max Delta | Max MAD | Strip |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `peak_delta` | 22 | 16 | 16 | 7 | 0.4847100051440329 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0022_BOLD_SAFE.png` |
| `peak_delta` | 47 | 35 | 35 | 6 | 0.5044611625514404 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0047_BOLD_SAFE.png` |
| `peak_delta` | 46 | 34 | 34 | 6 | 0.4855221193415638 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0046_BOLD_SAFE.png` |
| `peak_delta` | 45 | 34 | 34 | 6 | 0.48545267489711935 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0045_BOLD_SAFE.png` |
| `peak_mad` | 0 | 0 | 0 | 5 | 0.5889236111111111 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0000_BOLD_SAFE.png` |
| `peak_mad` | 1 | 1 | 1 | 6 | 0.580664866255144 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0001_BOLD_SAFE.png` |
| `peak_mad` | 2 | 1 | 1 | 6 | 0.5792226080246914 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0002_BOLD_SAFE.png` |
| `peak_mad` | 36 | 27 | 27 | 6 | 0.5678240740740741 | `build/shots/s626_mitsuba_response_aov_scene_native_probe_sweep_s075/BOLD_SAFE/strips/frame_0036_BOLD_SAFE.png` |

## Next

Promote BOLD_SAFE into the external backend path if visual review accepts the public S627 gallery; otherwise run a smaller late-frame guard adjustment.
