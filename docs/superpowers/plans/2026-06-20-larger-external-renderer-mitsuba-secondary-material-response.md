# S391 Larger External Renderer Mitsuba Secondary Material Response

## Goal

Move part of the CR21 dark-secondary cue from post-composite response toward
renderer-side material controls. The immediate step is to make secondary
particle diffuse reflectance configurable in the Mitsuba XML export while
preserving the existing default output.

## Work

- Added `--secondary-channel-reflectance-scale` to
  `tools/export_external_renderer_mitsuba_xml.py`.
- The option accepts per-channel scales:
  `spray=v,foam=v,bubble=v,droplet=v`.
- Existing scenes remain unchanged when the option is omitted.
- Generated a CR21 material-profile XML export using the S357 SS1 camera,
  water, sidecar, opacity, billboard, and proxy settings, with all secondary
  reflectance scales set to `0.60`.
- Validated the XML export.
- Rendered a 3-frame Mitsuba Python API probe with Python 3.11 and
  `LLVM-C.dll`.
- Built a render gallery for the probe.

## Results

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_export_s391.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_validation_s391.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_render_s391.md`
- Gallery report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_cr21_gallery_s391.md`
- XML export:
  `build/shots/s391_mitsuba_secondary_material_cr21/mitsuba_export.json`
- Render manifest:
  `build/shots/s391_mitsuba_secondary_material_cr21_render/mitsuba_render.json`
- Gallery:
  `build/shots/s391_mitsuba_secondary_material_cr21_gallery/gallery/index.html`

Validation exported and parsed `8` XML frames with `0` failures and `0`
warnings. The render probe produced `3` PNG/EXR frames with `0` failures. The
supervised Mitsuba worker returned exit code `3221226505` during teardown, but
the render tool accepted the ready manifest, matching the prior Dr.Jit teardown
pattern used in the Mitsuba pipeline.

## Decision

Keep the reflectance-scale option as a renderer-side material control. It does
not yet replace CR21 post-composite response by itself, but it creates the
correct integration point for turning secondary-channel evidence into actual
Mitsuba material output.

## Next

Compare the CR21 material-profile render against SS1, Target, and C1E before
using it as a candidate in target-gap scoring.
