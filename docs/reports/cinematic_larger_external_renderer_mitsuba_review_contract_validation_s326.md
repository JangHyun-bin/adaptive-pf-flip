# S326 Mitsuba Renderer Review Contract Validation

Generated UTC: `2026-06-19T23:32:12.894264+00:00`
Validation JSON: `build/shots/s326_mitsuba_renderer_review_contract_validation/validation.json`
Status: `passed`
Contract: `build/shots/s325_mitsuba_renderer_review_contract/renderer_review_contract.json`
Public check: `True`

## Summary

- Total checks: `77`
- Failed checks: `0`
- Skipped checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `contract:schema` | `ok` | schema |
| `contract:version` | `ok` | version |
| `contract:status` | `ok` | status |
| `source:grade_summary` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/grade_summary.json |
| `source_schema:grade_summary` | `ok` | schema matches |
| `source:mitsuba_export` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json |
| `source_schema:mitsuba_export` | `ok` | schema matches |
| `source:mitsuba_render` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/mitsuba_render.json |
| `source_schema:mitsuba_render` | `ok` | schema matches |
| `source:publish_manifest` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_publish/publish_manifest.json |
| `source:secondary_composite_summary` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/secondary_composite_summary.json |
| `source_schema:secondary_composite_summary` | `ok` | schema matches |
| `artifact:gallery_index` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/gallery/index.html |
| `artifact:shot_gif` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/gallery/assets/shot.gif |
| `frames:count` | `ok` | contract frame count |
| `frames:grade_frames` | `ok` | source frame count matches |
| `frames:composite_frames` | `ok` | source frame count matches |
| `frames:render_frames` | `ok` | source frame count matches |
| `frames:missing_assets` | `ok` | missing frame assets must stay zero |
| `frame:0:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0000.png |
| `frame:0:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0000_secondary_layer.png |
| `frame:0:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0000.png |
| `frame:0:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0000.png |
| `frame:0:graded_sha256` | `ok` | graded frame hash |
| `frame:0:particles_projected` | `ok` | non-negative projected particle count |
| `frame:0:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:1:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0001.png |
| `frame:1:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0001_secondary_layer.png |
| `frame:1:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0001.png |
| `frame:1:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0001.png |
| `frame:1:graded_sha256` | `ok` | graded frame hash |
| `frame:1:particles_projected` | `ok` | non-negative projected particle count |
| `frame:1:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:2:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0002.png |
| `frame:2:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0002_secondary_layer.png |
| `frame:2:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0002.png |
| `frame:2:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0002.png |
| `frame:2:graded_sha256` | `ok` | graded frame hash |
| `frame:2:particles_projected` | `ok` | non-negative projected particle count |
| `frame:2:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:3:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0003.png |
| `frame:3:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0003_secondary_layer.png |
| `frame:3:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0003.png |
| `frame:3:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0003.png |
| `frame:3:graded_sha256` | `ok` | graded frame hash |
| `frame:3:particles_projected` | `ok` | non-negative projected particle count |
| `frame:3:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:4:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0004.png |
| `frame:4:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0004_secondary_layer.png |
| `frame:4:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0004.png |
| `frame:4:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0004.png |
| `frame:4:graded_sha256` | `ok` | graded frame hash |
| `frame:4:particles_projected` | `ok` | non-negative projected particle count |
| `frame:4:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:5:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0005.png |
| `frame:5:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0005_secondary_layer.png |
| `frame:5:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0005.png |
| `frame:5:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0005.png |
| `frame:5:graded_sha256` | `ok` | graded frame hash |
| `frame:5:particles_projected` | `ok` | non-negative projected particle count |
| `frame:5:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:6:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0006.png |
| `frame:6:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0006_secondary_layer.png |
| `frame:6:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0006.png |
| `frame:6:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0006.png |
| `frame:6:graded_sha256` | `ok` | graded frame hash |
| `frame:6:particles_projected` | `ok` | non-negative projected particle count |
| `frame:6:layer_coverage` | `ok` | coverage in [0, 1] |
| `frame:7:base_preview` | `ok` | build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/actual_render/previews/frame_0007.png |
| `frame:7:secondary_layer` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/layers/frame_0007_secondary_layer.png |
| `frame:7:composite` | `ok` | build/shots/s323_larger_external_renderer_mitsuba_secondary_composite_subtle/composites/frame_0007.png |
| `frame:7:graded` | `ok` | build/shots/s324_larger_external_renderer_mitsuba_composite_grade_soft/frames/frame_0007.png |
| `frame:7:graded_sha256` | `ok` | graded frame hash |
| `frame:7:particles_projected` | `ok` | non-negative projected particle count |
| `frame:7:layer_coverage` | `ok` | coverage in [0, 1] |
| `public:index` | `ok` | {'status': 200, 'content_type': 'text/html', 'sample_bytes': 1024} |
| `public:shot_gif` | `ok` | {'status': 200, 'content_type': 'image/gif', 'sample_bytes': 1024} |
