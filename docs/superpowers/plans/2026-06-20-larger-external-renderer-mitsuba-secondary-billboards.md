# S339 Mitsuba Secondary Billboards

## Goal

Add an opt-in renderer-native camera-facing secondary disk path and compare it
against the corrected S338 mist-shell baseline under the same S333 H2 background
settings.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py` with secondary
  billboard options:
  - `--secondary-billboard-opacity`
  - `--secondary-billboard-radius-scale`
  - `--secondary-billboard-aspect`
- Keep billboard output disabled by default.
- Add billboard proxy counts to the export manifest and report.
- Re-render the S333 H2 export as a runtime control.
- Render B4, a background-controlled H2-plus-billboard candidate.
- Compare B4 against the S335 secondary-pass contract with the S337 gate.

## Commands

H2 runtime control:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe `
  tools\render_mitsuba_xml_export.py `
  build\shots\s333_mitsuba_secondary_halo_h2\mitsuba_export.json `
  build\shots\s339_mitsuba_runtime_h2_rerender_control\actual_render `
  --frames 8 `
  --spp 4 `
  --write-png `
  --llvm-dll "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll" `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_runtime_h2_rerender_control_s339.md `
  --title "S339 Mitsuba Runtime H2 Rerender Control"
```

B4 export:

```powershell
python tools\export_external_renderer_mitsuba_xml.py `
  build\shots\s308_larger_external_renderer_generic_adapter\adapter_manifest.json `
  build\shots\s339_mitsuba_secondary_billboard_b4 `
  --frames 8 `
  --samples 32 `
  --camera-position 18,20,58 `
  --camera-target 18,8,14 `
  --camera-fov 34 `
  --background-radiance 0.16,0.23,0.32 `
  --water-alpha 0.014 `
  --secondary-proxy-limit 384 `
  --secondary-proxy-radius 0.095 `
  --secondary-opacity 0.14 `
  --secondary-halo-opacity 0.075 `
  --secondary-halo-radius-scale 3.0 `
  --secondary-billboard-opacity 0.035 `
  --secondary-billboard-radius-scale 1.15 `
  --secondary-billboard-aspect 1.0 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_export_s339.md `
  --title "S339 Mitsuba Secondary Billboard B4 Export"
```

## Outputs

- Updated exporter:
  `tools/export_external_renderer_mitsuba_xml.py`
- H2 rerender control:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_runtime_h2_rerender_control_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_runtime_h2_rerender_control_candidate_gap_s339.md`
- B4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_export_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_render_s339.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_billboard_b4_candidate_gap_s339.md`

## Result

H2 rerender control:

- Mean candidate-to-target MAD: `37.58172702867798`
- Max candidate-to-target MAD: `67.40660365226337`

B4:

- Status: `ready`
- Decision: `candidate_needs_work`
- Mean candidate-to-target MAD: `37.57644900977366`
- Max candidate-to-target MAD: `67.3997678755144`

Corrected S338 M1:

- Mean candidate-to-target MAD: `37.286685796039094`
- Max candidate-to-target MAD: `66.5063766718107`

## Decision

Camera-facing disk billboards are renderer-valid, but B4 only improves over H2
by a tiny amount and trails corrected S338 M1. Keep billboard support as an
experimental native path, but use S338 M1 as the current best native Mitsuba
secondary baseline. The next concrete step should be a depth-aware
post-render/renderer-composite secondary pass, because pure native geometry is
still far from the S335 screen-space contract.
