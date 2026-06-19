# S310 Larger External Renderer Mitsuba XML Export

## Goal

Add the first concrete non-Blender scene format export from the renderer-neutral
S308 adapter manifest.

## Scope

- Add `tools/export_external_renderer_mitsuba_xml.py`.
- Consume `lsfs_external_renderer_adapter_manifest` scene descriptors.
- Emit Mitsuba XML scene files.
- Connect each frame's camera and water OBJ mesh.
- Preserve phase-cell CSV and particle CSV as sidecar comments in the XML.
- Emit Mitsuba command lines without requiring Mitsuba to be installed.
- Run the exporter on all `48` S308 larger-job scene descriptors.

## Result

- Tool:
  `tools/export_external_renderer_mitsuba_xml.py`
- Export JSON:
  `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_export.json`
- Command list:
  `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_render_commands.txt`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_s310.md`
- Status: `ready`
- Frames exported: `48`
- Failures: `0`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `74.38 KB`

## Decision

S310 proves the non-Blender path can produce a concrete renderer scene format
from the accepted larger-job adapter contract. It currently maps water meshes
and cameras directly, while phase volume and secondary particles remain sidecar
contracts for the next backend expansion.

## Next

Validate these XML scenes with a Mitsuba executable when available, then add
particle proxy expansion or volume conversion for phase and secondary channels.
