# S313 Larger External Renderer Mitsuba XML Validation

## Goal

Validate the S312 Mitsuba XML bundle as a renderer input package and separate
scene-contract issues from the external Mitsuba executable dependency.

## Scope

- Add `tools/validate_mitsuba_xml_export.py`.
- Read `lsfs_mitsuba_xml_export` manifests.
- Parse every generated XML scene.
- Count water OBJ shapes, proxy sphere shapes, and BSDFs.
- Verify Mitsuba command-list count.
- Check the Mitsuba executable with `shutil.which`.
- Treat missing Mitsuba as a warning unless `--require-mitsuba` is set.
- Run the validator on the S312 full48 Mitsuba phase-proxy export.

## Result

- Tool:
  `tools/validate_mitsuba_xml_export.py`
- Validation JSON:
  `build/shots/s313_larger_external_renderer_mitsuba_xml_validation/mitsuba_validation.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_validation_s313.md`
- Status: `ready`
- Frames: `48`
- XML parsed: `48`
- Command count: `48`
- OBJ shapes: `48`
- Sphere shapes: `7680`
- BSDFs: `288`
- Failures: `0`
- Warnings: `1`
- Warning: `mitsuba_executable_missing`

## Decision

S313 proves the S312 XML bundle is internally valid as a Mitsuba input package.
The remaining blocker for actual non-Blender rendered frames is the external
Mitsuba executable, not the LSFS export contract.

## Next

Install Mitsuba or configure a renderer command, then rerun this gate with
`--require-mitsuba` before invoking full48 renders.
