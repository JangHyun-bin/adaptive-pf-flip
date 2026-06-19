# S331 Mitsuba Renderer Native Gap Pass

## Goal

Make the first renderer-native Mitsuba pass that measurably moves the actual
Mitsuba output toward the accepted S328 target preview.

## Scope

- Extend `tools/compare_mitsuba_renderer_target_gap.py` with
  `--actual-render-manifest`.
- Export a calibrated Mitsuba XML pass from the S308 adapter manifest.
- Render `8` actual Mitsuba frames with the Python API.
- Compare the new actual render against the S328 accepted target.
- Publish the new gap gallery through Cloudflare Tunnel.

## Commands

```powershell
python tools\export_external_renderer_mitsuba_xml.py `
  build\shots\s308_larger_external_renderer_generic_adapter\adapter_manifest.json `
  build\shots\s331_mitsuba_renderer_native_gap_pass `
  --frames 8 `
  --samples 32 `
  --camera-position 18,20,58 `
  --camera-target 18,8,14 `
  --camera-fov 34 `
  --background-radiance 0.24,0.30,0.39 `
  --water-alpha 0.018 `
  --secondary-proxy-limit 384 `
  --secondary-proxy-radius 0.11 `
  --secondary-opacity 0.18 `
  --manifest-name mitsuba_export.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_native_gap_export_s331.md `
  --title "S331 Mitsuba Renderer Native Gap Export" `
  --next "Render this calibrated Mitsuba pass and compare it against the accepted S328 target."

build\s319_mitsuba_venv\Scripts\python.exe tools\render_mitsuba_xml_export.py `
  build\shots\s331_mitsuba_renderer_native_gap_pass\mitsuba_export.json `
  build\shots\s331_mitsuba_renderer_native_gap_pass\actual_render `
  --frames 8 `
  --spp 4 `
  --write-png `
  --llvm-dll "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll" `
  --manifest-name mitsuba_render.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_native_gap_render_s331.md `
  --title "S331 Mitsuba Renderer Native Gap Render" `
  --next "Compare this actual Mitsuba pass against the S328 accepted target and publish the gap."

python tools\compare_mitsuba_renderer_target_gap.py `
  build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  build\shots\s328_mitsuba_renderer_target_preview\renderer_target_preview_summary.json `
  build\shots\s331_mitsuba_renderer_native_target_gap `
  --actual-render-manifest build\shots\s331_mitsuba_renderer_native_gap_pass\actual_render\mitsuba_render.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_native_target_gap_s331.md `
  --title "S331 Mitsuba Renderer Native Target Gap" `
  --next "Use this measured gap delta to drive the next renderer-native material and secondary representation pass."

python tools\publish_cinematic_gallery.py `
  build\shots\s331_mitsuba_renderer_native_target_gap\gallery `
  --port 8948 `
  --cftunnel `
  --manifest build\shots\s331_mitsuba_renderer_native_target_gap_publish\publish_manifest.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_native_target_gap_publish_s331.md `
  --timeout-seconds 180
```

## Outputs

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_export_s331.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_gap_render_s331.md`
- Gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_target_gap_s331.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_target_gap_publish_s331.md`
- Public URL:
  `https://tan-afford-direct-wanting.trycloudflare.com`

## Acceptance

- Export status is `ready`.
- Render status is `ready`.
- Gap status is `ready`.
- Frames are `8`.
- Missing references are `0`.
- Mean gap mean absolute diff improves from S330 `74.16963405028292` to
  S331 `55.544113136574076`.
- Max gap mean absolute diff improves from S330 `104.48981417181069` to
  S331 `85.7207773919753`.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
