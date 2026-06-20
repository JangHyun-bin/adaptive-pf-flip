# S362 Mitsuba Secondary Visibility Cache Apply

## Goal

Consume the S360 SV1 secondary visibility cache directly, without rebuilding the
visibility layer from particle CSV files. This proves the cache is usable as a
renderer-facing review input.

## Changes

- Added `tools/apply_mitsuba_secondary_visibility_cache.py`.
- The tool reads:
  - a `lsfs_mitsuba_xml_render` manifest,
  - a `lsfs_mitsuba_secondary_visibility_cache` manifest.
- It applies each cached RGBA layer over the matching rendered preview frame by
  `output_frame`.
- It writes a `lsfs_mitsuba_secondary_composite` summary so the existing target
  gap harness can evaluate the result unchanged.

## Result

- Apply report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_apply_sv1_s362.md`
- Target-gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_cache_apply_sv1_gap_s362.md`
- Public quick-tunnel preview:
  `https://must-lightweight-develops-sign.trycloudflare.com/index.html`

The cache consumer applies `8` frames with `2877` projected particles and max
layer coverage `0.1105054012345679`. The target-gap recheck preserves the S359
SV1 result exactly: mean target MAD `19.103672839506174`, max target MAD
`23.72217142489712`.

## Next

Use this cache-consumer output as the stable renderer-facing review package.
The next work should move the same cache into a native renderer import pass.
