# S280 External Bundle Preview Benchmark

Generated UTC: `2026-06-19T20:10:11.639540+00:00`
Summary JSON: `build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json`
Status: `passed`

## Config

- Frames: `24`
- Resolution: `1280 x 720`
- Secondary channel: `all`
- Min occupancy gate: `0.01`

## Result

- Preview min occupancy: `0.056202256944444445`
- GIF: `build/shots/s280_external_bundle_preview_benchmark/preview.gif` (903.32 KB)
- Gallery: `build/shots/s280_external_bundle_preview_benchmark/gallery/index.html`
- Gallery assets: `9`
- Total elapsed: `70.72s`

## Steps

| Step | Return | Elapsed |
| --- | ---: | ---: |
| render_preview | 0 | 69.25s |
| assemble_gif | 0 | 1.28s |
| build_gallery | 0 | 0.20s |

## Next

Use S280 as the bounded larger preview benchmark for the external-bundle path; next publish the S280 gallery if this higher-resolution preview should replace S278.
