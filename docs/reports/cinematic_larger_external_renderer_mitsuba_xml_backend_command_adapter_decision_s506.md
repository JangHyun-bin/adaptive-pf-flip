# S506 Mitsuba XML Backend Command Adapter Decision

## Decision

Keep S506 as the first real renderer backend command-adapter gate.

## Evidence

- Adapter summary: `build/shots/s506_mitsuba_xml_backend_command_adapter/backend_command_adapter_summary.json`
- Validation JSON: `build/shots/s506_mitsuba_xml_backend_command_adapter/backend_command_adapter_validation.json`
- Render manifest: `build/shots/s506_mitsuba_xml_backend_command_adapter/render/mitsuba_render.json`
- Gallery manifest: `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/gallery_manifest.json`
- Gallery index: `build/shots/s506_mitsuba_xml_backend_command_adapter/gallery/index.html`
- Source export: `build/shots/s488_mitsuba_low_frequency_native_screen_card_sweep/sc1_soft_card/mitsuba_export.json`

## Metrics

- Adapter status: `ready`
- Validation status: `passed`
- Frames requested: `8`
- Frames rendered: `8`
- Render failures: `0`
- Process failures: `0`
- Render process return code: `0`
- Gallery process return code: `0`
- Render elapsed ms: `5759.801`
- Gallery elapsed ms: `455.485`
- Image bytes: `18415437`
- Preview bytes: `2174507`
- GIF bytes: `1083586`
- Gallery assets: `5`
- Validation checks: `66`
- Failed validation checks: `0`

## Runtime

- Renderer Python: `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe`
- Variant: `scalar_rgb`
- SPP: `1`
- Output format: `exr`
- PNG preview: `true`
- LLVM DLL: `build/envs/llvm18_runtime/Library/bin/LLVM-C.dll`

## Why This Matters

S505 proved the process boundary with a deterministic stub. S506 replaces that proof with a real Mitsuba XML render command path while preserving the same kind of adapter evidence: command execution, stdout/stderr logs, process return code, output manifests, preview images, gallery artifacts, and a separate validator.

This is the first recent step in this chain that invokes an actual external renderer backend instead of reusing post-tonemap texture composition.

## Next

Publish the S506 gallery through the cftunnel flow, then scale the command adapter to a larger render sample or higher SPP preset once the public visual check is acceptable.
