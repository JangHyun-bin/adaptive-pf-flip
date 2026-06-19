# S319 Larger External Renderer Mitsuba Render Probe

## Goal

Move the Mitsuba XML path from export/preview proof into a real renderer runtime
probe, without making Mitsuba a default test dependency.

## Changes

- Fix generated Mitsuba command lines from the legacy `mitsuba render ...` form
  to the actual `mitsuba -m scalar_rgb scene.xml -o frame.exr` CLI shape.
- Extend `tools/validate_mitsuba_xml_export.py` so it catches legacy
  `render` subcommands in command lists.
- Add `tools/render_mitsuba_xml_export.py`, an opt-in Mitsuba Python API runner
  that:
  - sets `DRJIT_LIBLLVM_PATH` before importing Mitsuba,
  - renders selected XML frames to EXR,
  - writes optional PNG previews,
  - records a JSON/Markdown report,
  - supervises the worker process so a ready manifest can survive a Windows
    Dr.Jit teardown exit code.

## Outputs

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_command_fix_s319.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_command_validation_s319.md`
- Render probe report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_render_probe_s319.md`
- Export JSON:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_export.json`
- Validation JSON:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_validation.json`
- Render JSON:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/mitsuba_render.json`
- Rendered EXR/PNG probe frames:
  `build/shots/s319_larger_external_renderer_mitsuba_render_probe/actual_render/`

## Verification

- `python -m py_compile tools/export_external_renderer_mitsuba_xml.py tools/validate_mitsuba_xml_export.py tools/render_mitsuba_xml_export.py`
- `git diff --check`
- `python tools/validate_mitsuba_xml_export.py ... --require-mitsuba`
- `.\\build\\s319_mitsuba_venv\\Scripts\\python.exe tools\\render_mitsuba_xml_export.py ... --frames 3 --spp 1 --write-png --llvm-dll "C:\\Program Files\\Microsoft Visual Studio\\18\\Community\\VC\\Tools\\Llvm\\x64\\bin\\LLVM-C.dll"`

## Result

S319 validates all `48` XML frames and renders `3` selected frames through the
real Mitsuba Python API path with `0` manifest failures. The worker process
still exits with Windows code `3221226505` after writing valid artifacts, so the
supervisor records that code and accepts the ready manifest.

## Next

Package and publish the 3-frame actual Mitsuba probe, then scale the render
runner toward a longer frame range and higher spp once camera/material framing is
improved.
