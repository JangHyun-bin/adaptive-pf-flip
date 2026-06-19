# S191 Water Mesh Smoothing Comparison

## Status

Passed.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s191_water_mesh_smoothing\comparison\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `81.63827217761381`, right `80.94749951774692`, delta `-0.6907726598668944`
- Minimum contrast: left `181.0`, right `186.0`, delta `5.0`
- Mean bright ratio: left `0.0001566719714506173`, right `0.00015896267361111113`, delta `2.290702160493845e-06`
- Mean highlight ratio: left `9.690272955246914e-05`, right `0.00010582441165123457`, delta `8.921682098765428e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.04, 'min': 0.68}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S191 keeps S186 surface overlay density while applying a bounded Smooth modifier to imported water meshes. The diff is concentrated on water body shading and seam softness, with secondary readability and nonblank coverage preserved.

## Next

Publish or triage S191 if visual review confirms the mesh seams are softer without washing out the water body; otherwise reduce smoothing factor or iterations.
