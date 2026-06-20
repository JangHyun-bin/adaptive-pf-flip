# S353 Mitsuba Secondary 3D Sidecar

Generated UTC: `2026-06-20T02:34:22.476200+00:00`
Summary JSON: `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
Status: `ready`

## Checks

- Frames: `8`
- Sidecar JSONL files: `8`
- Secondary particles: `2877`
- In-front particles: `2877`
- In-frame particles: `2877`
- Missing references: `0`
- Sidecar bytes: `1.11 MB`

## Channel Counts

| Channel | Count | In front | In frame |
| --- | ---: | ---: | ---: |
| spray | `2052` | `2052` | `2052` |
| foam | `548` | `548` | `548` |
| bubble | `277` | `277` | `277` |
| droplet | `0` | `0` | `0` |

## Frame Samples

| Output | Sequence | Particles | In frame | Sidecar |
| ---: | ---: | ---: | ---: | --- |
| 0 | 8 | 256 | 256 | `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d/frame_0000_secondary_3d.jsonl` |
| 7 | 15 | 256 | 256 | `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d/frame_0001_secondary_3d.jsonl` |
| 13 | 21 | 256 | 256 | `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d/frame_0002_secondary_3d.jsonl` |
| 47 | 55 | 964 | 964 | `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d/frame_0007_secondary_3d.jsonl` |

## Next

Validate the sidecar, then wire it into a native Mitsuba secondary import pass.
