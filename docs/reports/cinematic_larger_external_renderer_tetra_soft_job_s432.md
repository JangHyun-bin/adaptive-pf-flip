# S432 External Renderer Job With Tetra Soft Water Mesh

Generated UTC: `2026-06-20T12:18:26.879204+00:00`
Job JSON: `build/shots/s432_external_renderer_job_tetra_soft/external_renderer_job.json`
Status: `ready`

## Replacement

- Source job: `build/shots/s295_larger_external_renderer_job_48/external_renderer_job.json`
- Reconstruction: `build/shots/s432_water_reconstruction_tetra_soft/water_reconstruction.json`
- Surface mode: `tetra`
- Threshold: `0.015`
- Implicit iso: `0.4`
- Implicit blur iterations: `1`
- Smooth iterations: `4`
- Smooth alpha: `0.16`

## Gates

- Replaced frames: `48`
- Replacement failures: `0`
- Minimum water mesh faces: `17736`
- Minimum water mesh faces required: `1000`
- Quality labels: `{'tetra_reconstruction': 48}`

## Input Footprint

- Water mesh OBJ: `81.02 MB`
- Total: `2.05 GB`

## Frame Samples

| Output | Sequence | Mesh Index | Recon Frame | Source Frame | Water Faces | Water Vertices |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 8 | 5 | 5 | 8 | 19980 | 9992 |
| 24 | 32 | 20 | 20 | 31 | 18068 | 9036 |
| 47 | 55 | 35 | 35 | 55 | 22368 | 11186 |

## Next

Build a Mitsuba adapter from this replacement-water job, render a SS1-equivalent candidate, and compare target gap against SS1_Native.
