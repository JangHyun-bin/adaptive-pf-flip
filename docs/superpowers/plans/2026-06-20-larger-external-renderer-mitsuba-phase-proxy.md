# S312 Larger External Renderer Mitsuba Phase Proxy

## Goal

Expand the Mitsuba XML export so sparse phase-volume cells become visible scene
proxies alongside water mesh and secondary particle proxies.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py`.
- Keep phase volume proxy export opt-in through `--phase-volume-proxy-limit`.
- Read phase-cell CSV rows with positive `liquid_volume`.
- Sample phase cells into sparse sphere proxies.
- Emit a phase-volume diffuse BSDF.
- Preserve secondary particle proxy export from S311.
- Export the S308 larger-job adapter manifest to a full48 Mitsuba XML bundle
  with `96` secondary proxies and `64` phase-volume proxies per frame.

## Result

- Updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- Export JSON:
  `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/mitsuba_export.json`
- Command list:
  `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/mitsuba_render_commands.txt`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_phase_proxy_s312.md`
- Status: `ready`
- Frames exported: `48`
- Failures: `0`
- Secondary proxies emitted: `4608`
- Secondary particles available: `15413`
- Phase volume proxies emitted: `3072`
- Phase volume cells available: `261158`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `1.52 MB`

## Verification

- `python -m py_compile tools/export_external_renderer_mitsuba_xml.py`
- S312 export command completed with status `ready`.
- `python -m json.tool` accepted the S312 export manifest.
- XML parsing passed for frames `0000`, `0024`, and `0047`.
- Those sample frames each contain `1` water OBJ shape and `160` proxy sphere
  shapes: `96` secondary proxies plus `64` phase-volume proxies.

## Decision

S312 is the first non-Blender scene export where water mesh, secondary
particles, and sparse phase volume are all represented as actual renderer scene
geometry. The phase representation is still a sampled proxy, but it is now
visible to an offline renderer scene format.

## Next

Validate these XML scenes with a Mitsuba executable when available, then tune
proxy density/materials or implement true sparse-volume conversion.
