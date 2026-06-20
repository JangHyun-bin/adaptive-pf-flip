# S333 Mitsuba Secondary Halo

## Goal

Add a renderer-side soft secondary halo option to the Mitsuba XML exporter and
measure whether it reduces the accepted S328 target gap beyond the S332-B
baseline.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py` with opt-in secondary
  halo proxy settings.
- Keep existing secondary proxy behavior unchanged unless halo options are
  passed.
- Render two halo candidates, H1 and H2.
- Compare H1 and H2 against the S328 accepted target.
- Rank S330 baseline, S331 native pass, S332-B, H1, and H2.
- Publish the best H2 gap gallery through Cloudflare Tunnel.

## New Export Options

- `--secondary-halo-opacity`
- `--secondary-halo-radius-scale`

When halo opacity is enabled, each selected secondary proxy also emits a larger
low-opacity Mitsuba sphere with a dedicated halo BSDF. The original secondary
proxy sphere is still emitted.

## Candidate Settings

H1:

- Based on S332-B
- `secondary-halo-opacity 0.045`
- `secondary-halo-radius-scale 2.4`

H2:

- Based on S332-B
- `secondary-proxy-radius 0.095`
- `secondary-opacity 0.14`
- `secondary-halo-opacity 0.075`
- `secondary-halo-radius-scale 3.0`

## Outputs

- H1 export/render/gap reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h1_export_s333.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h1_render_s333.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h1_gap_s333.md`
- H2 export/render/gap reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_export_s333.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_render_s333.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_gap_s333.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_sweep_summary_s333.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_halo_h2_publish_s333.md`
- Public URL:
  `https://timer-symbol-referrals-competent.trycloudflare.com`

## Acceptance

- H1 and H2 export/render/gap reports are `ready`.
- Best candidate is `halo_h2`.
- H2 frames are `8`.
- H2 missing references are `0`.
- H2 max gap mean absolute diff is `67.40660365226337`.
- H2 improves over S332-B max gap `67.67647762345679`.
- Public `index.html` and `assets/shot.gif` return HTTP `200`.
- The remaining gap is documented as a sign that halo spheres are only a
  marginal improvement and that a true screen-space or volumetric secondary
  representation is still needed.
