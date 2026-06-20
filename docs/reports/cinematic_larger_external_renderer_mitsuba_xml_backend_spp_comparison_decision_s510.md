# S510 Mitsuba XML Backend SPP Comparison Decision

## Decision

Keep S508 SPP4 as the current real Mitsuba backend visual review baseline, with S506 SPP1 retained as the speed baseline.

## Evidence

- Comparison summary: `build/shots/s510_mitsuba_xml_backend_spp_comparison/comparison_summary.json`
- Comparison sheet: `build/shots/s510_mitsuba_xml_backend_spp_comparison/comparison_sheet.png`
- S506 SPP1 summary: `build/shots/s506_mitsuba_xml_backend_command_adapter/backend_command_adapter_summary.json`
- S508 SPP4 summary: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/backend_command_adapter_summary.json`
- S510 report: `docs/reports/cinematic_larger_external_renderer_mitsuba_xml_backend_spp_comparison_s510.md`

## Metrics

- Compared frame pairs: `8`
- Mean abs luma diff, average: `0.7493815104166667`
- Mean abs luma diff, max: `1.3529456018518518`
- Mean changed ratio: `0.02960913387345679`
- Max strong changed ratio: `0.003005401234567901`
- SPP1 render elapsed ms: `5759.801`
- SPP4 render elapsed ms: `6003.532`
- SPP1 image bytes: `18415437`
- SPP4 image bytes: `21582385`

## Interpretation

The SPP4 preview is visually close to SPP1 in average luminance, but the diff sheet shows concentrated changes in noisy surface and highlight regions. The small elapsed-time increase makes SPP4 a better review baseline for this scene.

The EXR output grows from `18415437` bytes to `21582385` bytes, so SPP4 should be treated as the default review-quality setting, not necessarily the cheapest batch setting.

## Next

Package the comparison sheet for public review, then choose the next axis: larger frame count, larger scene/export, or another SPP step.
