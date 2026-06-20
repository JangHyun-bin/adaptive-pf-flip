# S513 Mitsuba Secondary Masked 16F SPP4 Validation

Generated UTC: `2026-06-20T19:32:43.884322+00:00`
Validation JSON: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/backend_command_adapter_validation.json`
Status: `passed`
Summary: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/backend_command_adapter_summary.json`

## Summary

- Total checks: `82`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `summary:schema` | `ok` | schema |
| `summary:version` | `ok` | version |
| `source:export` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json |
| `source:schema` | `ok` | export schema |
| `source:status` | `ok` | export status |
| `runtime:render_script` | `ok` | tools/render_mitsuba_xml_export.py |
| `runtime:gallery_script` | `ok` | tools/build_mitsuba_render_gallery.py |
| `runtime:python` | `ok` | renderer python exists |
| `runtime:llvm_dll` | `ok` | build/envs/llvm18_runtime/Library/bin/LLVM-C.dll |
| `runtime:spp` | `ok` | spp |
| `runtime:write_png` | `ok` | png previews enabled |
| `process:render:command` | `ok` | command present |
| `process:render:returncode` | `ok` | return code |
| `process:render:timeout` | `ok` | not timed out |
| `process:render:elapsed` | `ok` | elapsed |
| `process:render:stdout` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/logs/render_stdout.log |
| `process:render:stderr` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/logs/render_stderr.log |
| `process:gallery:command` | `ok` | command present |
| `process:gallery:returncode` | `ok` | return code |
| `process:gallery:timeout` | `ok` | not timed out |
| `process:gallery:elapsed` | `ok` | elapsed |
| `process:gallery:stdout` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/logs/gallery_stdout.log |
| `process:gallery:stderr` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/logs/gallery_stderr.log |
| `render:manifest` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/mitsuba_render.json |
| `render:schema` | `ok` | render schema |
| `render:status` | `ok` | render status |
| `render:frame_count` | `ok` | all frames rendered |
| `render:failures` | `ok` | failures |
| `render:image_bytes` | `ok` | image bytes |
| `render:preview_bytes` | `ok` | preview bytes |
| `render:frame:0:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0000.exr |
| `render:frame:0:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0000.png |
| `render:frame:1:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0001.exr |
| `render:frame:1:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0001.png |
| `render:frame:2:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0002.exr |
| `render:frame:2:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0002.png |
| `render:frame:3:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0003.exr |
| `render:frame:3:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0003.png |
| `render:frame:4:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0004.exr |
| `render:frame:4:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0004.png |
| `render:frame:5:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0005.exr |
| `render:frame:5:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0005.png |
| `render:frame:6:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0006.exr |
| `render:frame:6:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0006.png |
| `render:frame:7:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0007.exr |
| `render:frame:7:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0007.png |
| `render:frame:8:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0008.exr |
| `render:frame:8:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0008.png |
| `render:frame:9:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0009.exr |
| `render:frame:9:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0009.png |
| `render:frame:10:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0010.exr |
| `render:frame:10:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0010.png |
| `render:frame:11:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0011.exr |
| `render:frame:11:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0011.png |
| `render:frame:12:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0012.exr |
| `render:frame:12:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0012.png |
| `render:frame:13:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0013.exr |
| `render:frame:13:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0013.png |
| `render:frame:14:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0014.exr |
| `render:frame:14:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0014.png |
| `render:frame:15:image` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/renders/frame_0015.exr |
| `render:frame:15:preview` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/previews/frame_0015.png |
| `gallery:manifest` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/gallery_manifest.json |
| `gallery:schema` | `ok` | gallery schema |
| `gallery:index` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/index.html |
| `gallery:asset:Shot GIF` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/shot.gif |
| `gallery:asset:Keyframe 1 output 0` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/keyframe_00.png |
| `gallery:asset:Keyframe 2 output 16` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/keyframe_01.png |
| `gallery:asset:Keyframe 3 output 31` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/keyframe_02.png |
| `gallery:asset:Keyframe 4 output 47` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/keyframe_03.png |
| `gallery:shot_gif` | `ok` | shot gif present |
| `gallery:metadata:Mitsuba render manifest` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/mitsuba_render.json |
| `gallery:metadata:Mitsuba export manifest` | `ok` | build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/assets/mitsuba_export.json |
| `summary:status` | `ok` | status |
| `checks:frames` | `ok` | frame count |
| `checks:render_failures` | `ok` | render failures |
| `checks:process_failures` | `ok` | process failures |
| `checks:image_bytes` | `ok` | image bytes |
| `checks:preview_bytes` | `ok` | preview bytes |
| `checks:gif_bytes` | `ok` | gif bytes |
| `checks:gallery_assets` | `ok` | gallery assets |
| `checks:stdout_bytes` | `ok` | stdout bytes |
