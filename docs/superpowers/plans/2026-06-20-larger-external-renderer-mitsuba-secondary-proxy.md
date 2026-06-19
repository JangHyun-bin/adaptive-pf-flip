# S311 Larger External Renderer Mitsuba Secondary Proxy

## Goal

Expand the Mitsuba XML export so secondary particles become visible scene
proxies instead of sidecar-only CSV references.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py`.
- Keep secondary proxy export opt-in through `--secondary-proxy-limit`.
- Read secondary rows from the particle CSV stream.
- Preserve channel distribution across `spray`, `foam`, `bubble`, and
  `droplet` when sampling proxies.
- Emit per-channel diffuse BSDFs.
- Emit sampled secondary particles as Mitsuba sphere shapes.
- Keep phase-cell CSV as a sidecar contract for future volume conversion.
- Export the S308 larger-job adapter manifest to a full48 Mitsuba XML bundle
  with `96` secondary proxies per frame.

## Result

- Updated tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- Export JSON:
  `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_export.json`
- Command list:
  `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_render_commands.txt`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_proxy_s311.md`
- Status: `ready`
- Frames exported: `48`
- Failures: `0`
- Secondary proxies emitted: `4608`
- Secondary particles available: `15413`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `995.47 KB`

## Verification

- `python -m py_compile tools/export_external_renderer_mitsuba_xml.py`
- S311 export command completed with status `ready`.
- `python -m json.tool` accepted the S311 export manifest.
- XML parsing passed for frames `0000`, `0024`, and `0047`.
- Those sample frames each contain `1` water OBJ shape and `96` secondary
  sphere proxy shapes.

## Decision

S311 is the first non-Blender scene export where secondary particles are actual
renderer scene geometry. It remains a proxy representation, but it is a direct
step toward visible spray/foam/bubble review outside Blender.

## Next

Validate these XML scenes with a Mitsuba executable when available, then tune
proxy radius/channel materials or expand phase volume conversion.
