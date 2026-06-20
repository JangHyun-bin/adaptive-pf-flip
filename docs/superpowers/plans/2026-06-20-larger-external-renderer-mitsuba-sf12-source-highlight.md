# Larger External Renderer: Mitsuba SF12 Source Highlight

Status: complete

## Goal

Use the S408 `SF12_SprayFoam` AOV attenuation probe as the dark/secondary
baseline, then add a separate target-free source-highlight pass.

## Result

S409 generated five SF12 plus source-highlight candidates:

- `SF12_H15`: strength `0.45`, max delta `55`
- `SF12_H16`: strength `0.55`, max delta `70`
- `SF12_H17`: strength `0.70`, max delta `90`
- `SF12_H18`: strength `0.85`, max delta `120`
- `SF12_H19`: strength `1.0`, max delta `255`

The highlight mask uses source luma `>= 120` and alpha `<= 3`, so it is
separate from secondary material/AOV coverage.

## Decision

Promote `SF12_H18` as the bounded source-highlight probe.

- SF12 max target MAD: `23.755951646090534`
- SF12_H18 max target MAD: `23.687431841563786`
- SF12_H19 max target MAD: `23.68549704218107`
- S401 CR21 max target MAD: `23.552905092592592`

H19 is useful as a highlight ceiling/reference, but H18 is the better bounded
candidate to migrate toward renderer-native controls.

## Artifacts

- S409 sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_source_highlight_sweep_summary_s409.md`
- S409 decision summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_source_highlight_summary_s409.md`
- S409 compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_source_highlight_compare_s409.md`
- S409 publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_source_highlight_compare_publish_s409.md`
- S409 public quick-tunnel URL:
  `https://angela-postcard-cooperation-hosting.trycloudflare.com/index.html`

## Next

S410 should migrate the split response into renderer-native controls: keep
`SF12` for spray/foam dark attenuation, keep `SF12_H18` as the accepted
highlight response, and test material/export/light-response equivalents before
adding another broad post-composite grade.
