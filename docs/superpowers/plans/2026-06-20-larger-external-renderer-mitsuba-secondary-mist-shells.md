# S338 Mitsuba Secondary Mist Shells

## Goal

Test whether a renderer-native soft mist shell can close the gap between native
Mitsuba secondary proxies and the S335 screen-space secondary-pass contract.
This is intentionally opt-in and measured against the S337 replacement gate.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py` with secondary mist
  shell options:
  - `--secondary-mist-opacity`
  - `--secondary-mist-radius-scale`
  - `--secondary-mist-shells`
  - `--secondary-mist-shell-spacing`
- Keep default export behavior unchanged.
- Emit mist proxy counts in the export manifest and markdown report.
- Render two candidates:
  - M1: visible mist shell strength.
  - M2: low-strength mist shell over the S333 H2 baseline.
- Compare both candidates with `tools/compare_mitsuba_secondary_native_candidate.py`.

## Commands

M2 export:

```powershell
python tools\export_external_renderer_mitsuba_xml.py `
  build\shots\s308_larger_external_renderer_generic_adapter\adapter_manifest.json `
  build\shots\s338_mitsuba_secondary_mist_m2 `
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
  --secondary-mist-opacity 0.004 `
  --secondary-mist-radius-scale 4.5 `
  --secondary-mist-shells 1 `
  --secondary-mist-shell-spacing 0.55 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_export_s338.md `
  --title "S338 Mitsuba Secondary Mist M2 Export"
```

M2 render:

```powershell
C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe `
  tools\render_mitsuba_xml_export.py `
  build\shots\s338_mitsuba_secondary_mist_m2\mitsuba_export.json `
  build\shots\s338_mitsuba_secondary_mist_m2\actual_render `
  --frames 8 `
  --spp 4 `
  --write-png `
  --llvm-dll "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Tools\Llvm\x64\bin\LLVM-C.dll" `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_render_s338.md `
  --title "S338 Mitsuba Secondary Mist M2 Render"
```

M2 contract comparison:

```powershell
python tools\compare_mitsuba_secondary_native_candidate.py `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  build\shots\s338_mitsuba_secondary_mist_m2\actual_render\mitsuba_render.json `
  build\shots\s338_mitsuba_secondary_mist_m2_candidate_gap `
  --candidate-label s338_mist_m2 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_candidate_gap_s338.md `
  --title "S338 Mitsuba Secondary Mist M2 Candidate Gap"
```

## Outputs

- Updated exporter:
  `tools/export_external_renderer_mitsuba_xml.py`
- M1 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_export_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_render_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m1_candidate_gap_s338.md`
- M2 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_export_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_render_s338.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_m2_candidate_gap_s338.md`

## Result

M1:

- Status: `ready`
- Decision: `candidate_needs_work`
- Mean candidate-to-target MAD: `37.286685796039094`
- Max candidate-to-target MAD: `66.5063766718107`

M2:

- Status: `ready`
- Decision: `candidate_needs_work`
- Mean candidate-to-target MAD: `37.38058802726338`
- Max candidate-to-target MAD: `66.78048096707819`

S333 H2 control:

- Mean candidate-to-target MAD: `37.58172702867798`
- Max candidate-to-target MAD: `67.40660365226337`

S335 contract:

- Mean overlay MAD: `12.566030735596708`
- Max overlay MAD: `18.040229552469135`

## Decision

The background must stay pinned to the S333 H2 baseline
`0.16,0.23,0.32`; otherwise the candidate gap is dominated by tone drift rather
than secondary behavior. Under that controlled background, mist shells are a
small native improvement over H2, with M1 the best measured candidate so far.
They still do not beat the S335 overlay contract, so the next step should keep
M1 as the native baseline and explore depth-aware compositing or a more direct
secondary-layer reconstruction.
