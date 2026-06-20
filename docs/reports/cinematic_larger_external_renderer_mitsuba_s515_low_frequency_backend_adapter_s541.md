# S541 Mitsuba S515 Low Frequency Backend Adapter

Generated UTC: `2026-06-20T20:17:21.377315+00:00`
Adapter manifest: `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/backend_adapter_manifest.json`
Status: `ready`
Target renderer: `mitsuba_or_external_path_tracer`
Backend kind: `process_stub`

## Source

- Source job: `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/renderer_job_manifest.json`
- Source job status: `ready`
- Command list: `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/backend_commands.txt`

## Checks

- Frames: `8`
- Scene descriptors: `8`
- Required inputs: `24` / `24`
- Missing inputs: `0`
- Missing shaders: `0`
- Reference hash mismatches: `0`
- Output targets: `24`

## Frame Descriptors

| Job | Frame | Output | Scene | Output Image |
| ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0000_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0000.png` |
| 1 | 1 | 7 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0001_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0001.png` |
| 2 | 2 | 13 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0002_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0002.png` |
| 3 | 3 | 20 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0003_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0003.png` |
| 4 | 4 | 27 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0004_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0004.png` |
| 5 | 5 | 34 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0005_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0005.png` |
| 6 | 6 | 40 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0006_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0006.png` |
| 7 | 7 | 47 | `build/shots/s541_mitsuba_s515_low_frequency_backend_adapter/scenes/frame_0007_backend_scene.json` | `build/shots/s539_mitsuba_s515_low_frequency_renderer_job_manifest/outputs/frame_0007.png` |

## Commands

- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0000_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0000.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0001_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0001.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0002_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0002.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0003_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0003.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0004_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0004.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0005_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0005.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0006_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0006.png" --mode low_frequency_post_tonemap`
- `python tools/mitsuba_low_frequency_backend_stub.py --scene "D:\HB\Rhizome\lsfs\build\shots\s541_mitsuba_s515_low_frequency_backend_adapter\scenes\frame_0007_backend_scene.json" --output "D:\HB\Rhizome\lsfs\build\shots\s539_mitsuba_s515_low_frequency_renderer_job_manifest\outputs\frame_0007.png" --mode low_frequency_post_tonemap`

## Next

Execute these S515-calibrated backend scene descriptors through descriptor dry-run and process-stub gates.
