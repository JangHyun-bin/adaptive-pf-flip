# S562 Mitsuba S515 Full48 T4 Backend Process Stub Validation

Generated UTC: `2026-06-20T21:03:25.041573+00:00`
Validation JSON: `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/backend_process_stub_validation.json`
Status: `passed`
Summary: `build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/backend_process_stub_summary.json`

## Summary

- Total checks: `1481`
- Failed checks: `0`

## Failed Checks

- None

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `summary:schema` | `ok` | schema |
| `summary:version` | `ok` | version |
| `source:adapter` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/backend_adapter_manifest.json |
| `source:schema` | `ok` | adapter schema |
| `source:status` | `ok` | adapter status |
| `settings:stage` | `ok` | stage |
| `settings:backend_script` | `ok` | tools/mitsuba_low_frequency_backend_stub.py |
| `settings:frame_timeout` | `ok` | frame timeout |
| `summary:status` | `ok` | status |
| `checks:frame_count` | `ok` | all frames passed |
| `checks:failed` | `ok` | failed frames |
| `checks:process_failures` | `ok` | process failures |
| `checks:max_abs` | `ok` | max abs diff |
| `checks:max_mean` | `ok` | max mean diff |
| `checks:output_bytes` | `ok` | output bytes nonzero |
| `checks:gif_bytes` | `ok` | GIF bytes nonzero |
| `checks:strip_gif_bytes` | `ok` | strip GIF bytes nonzero |
| `checks:stdout_bytes` | `ok` | stdout bytes nonzero |
| `checks:stderr_bytes` | `ok` | stderr bytes empty |
| `checks:result_json_bytes` | `ok` | result JSON bytes nonzero |
| `frames:count` | `ok` | adapter frame count |
| `frame:0:status` | `ok` | frame status |
| `frame:0:returncode` | `ok` | process return code |
| `frame:0:elapsed` | `ok` | process elapsed |
| `frame:0:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0000_stdout.log |
| `frame:0:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0000_stderr.log |
| `frame:0:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0000_backend_process_result.json |
| `frame:0:result_schema` | `ok` | result schema |
| `frame:0:result_status` | `ok` | result status |
| `frame:0:result_max_abs` | `ok` | result max abs |
| `frame:0:result_mean_abs` | `ok` | result mean abs |
| `frame:0:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0000.png |
| `frame:0:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0000.json |
| `frame:0:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0000.json |
| `frame:0:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0000_backend_process_stub.png |
| `frame:0:max_abs` | `ok` | max abs diff |
| `frame:0:mean_abs` | `ok` | mean abs diff |
| `frame:0:reference_hash` | `ok` | reference hash |
| `frame:0:result_output_match` | `ok` | result output matches frame |
| `frame:0:target_match` | `ok` | output path matches adapter |
| `frame:0:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0000_backend_scene.json |
| `frame:0:scene_schema` | `ok` | scene schema |
| `frame:0:scene_match` | `ok` | scene path matches adapter |
| `frame:0:scene_output:image` | `ok` | scene output path |
| `frame:0:scene_output:metadata` | `ok` | scene output path |
| `frame:0:scene_output:validation` | `ok` | scene output path |
| `frame:0:metadata_schema` | `ok` | metadata schema |
| `frame:0:validation_schema` | `ok` | validation schema |
| `frame:0:validation_status` | `ok` | validation status |
| `frame:0:validation_max_abs` | `ok` | validation max abs |
| `frame:0:validation_mean_abs` | `ok` | validation mean abs |
| `frame:1:status` | `ok` | frame status |
| `frame:1:returncode` | `ok` | process return code |
| `frame:1:elapsed` | `ok` | process elapsed |
| `frame:1:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0001_stdout.log |
| `frame:1:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0001_stderr.log |
| `frame:1:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0001_backend_process_result.json |
| `frame:1:result_schema` | `ok` | result schema |
| `frame:1:result_status` | `ok` | result status |
| `frame:1:result_max_abs` | `ok` | result max abs |
| `frame:1:result_mean_abs` | `ok` | result mean abs |
| `frame:1:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0001.png |
| `frame:1:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0001.json |
| `frame:1:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0001.json |
| `frame:1:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0001_backend_process_stub.png |
| `frame:1:max_abs` | `ok` | max abs diff |
| `frame:1:mean_abs` | `ok` | mean abs diff |
| `frame:1:reference_hash` | `ok` | reference hash |
| `frame:1:result_output_match` | `ok` | result output matches frame |
| `frame:1:target_match` | `ok` | output path matches adapter |
| `frame:1:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0001_backend_scene.json |
| `frame:1:scene_schema` | `ok` | scene schema |
| `frame:1:scene_match` | `ok` | scene path matches adapter |
| `frame:1:scene_output:image` | `ok` | scene output path |
| `frame:1:scene_output:metadata` | `ok` | scene output path |
| `frame:1:scene_output:validation` | `ok` | scene output path |
| `frame:1:metadata_schema` | `ok` | metadata schema |
| `frame:1:validation_schema` | `ok` | validation schema |
| `frame:1:validation_status` | `ok` | validation status |
| `frame:1:validation_max_abs` | `ok` | validation max abs |
| `frame:1:validation_mean_abs` | `ok` | validation mean abs |
| `frame:2:status` | `ok` | frame status |
| `frame:2:returncode` | `ok` | process return code |
| `frame:2:elapsed` | `ok` | process elapsed |
| `frame:2:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0002_stdout.log |
| `frame:2:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0002_stderr.log |
| `frame:2:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0002_backend_process_result.json |
| `frame:2:result_schema` | `ok` | result schema |
| `frame:2:result_status` | `ok` | result status |
| `frame:2:result_max_abs` | `ok` | result max abs |
| `frame:2:result_mean_abs` | `ok` | result mean abs |
| `frame:2:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0002.png |
| `frame:2:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0002.json |
| `frame:2:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0002.json |
| `frame:2:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0002_backend_process_stub.png |
| `frame:2:max_abs` | `ok` | max abs diff |
| `frame:2:mean_abs` | `ok` | mean abs diff |
| `frame:2:reference_hash` | `ok` | reference hash |
| `frame:2:result_output_match` | `ok` | result output matches frame |
| `frame:2:target_match` | `ok` | output path matches adapter |
| `frame:2:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0002_backend_scene.json |
| `frame:2:scene_schema` | `ok` | scene schema |
| `frame:2:scene_match` | `ok` | scene path matches adapter |
| `frame:2:scene_output:image` | `ok` | scene output path |
| `frame:2:scene_output:metadata` | `ok` | scene output path |
| `frame:2:scene_output:validation` | `ok` | scene output path |
| `frame:2:metadata_schema` | `ok` | metadata schema |
| `frame:2:validation_schema` | `ok` | validation schema |
| `frame:2:validation_status` | `ok` | validation status |
| `frame:2:validation_max_abs` | `ok` | validation max abs |
| `frame:2:validation_mean_abs` | `ok` | validation mean abs |
| `frame:3:status` | `ok` | frame status |
| `frame:3:returncode` | `ok` | process return code |
| `frame:3:elapsed` | `ok` | process elapsed |
| `frame:3:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0003_stdout.log |
| `frame:3:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0003_stderr.log |
| `frame:3:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0003_backend_process_result.json |
| `frame:3:result_schema` | `ok` | result schema |
| `frame:3:result_status` | `ok` | result status |
| `frame:3:result_max_abs` | `ok` | result max abs |
| `frame:3:result_mean_abs` | `ok` | result mean abs |
| `frame:3:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0003.png |
| `frame:3:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0003.json |
| `frame:3:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0003.json |
| `frame:3:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0003_backend_process_stub.png |
| `frame:3:max_abs` | `ok` | max abs diff |
| `frame:3:mean_abs` | `ok` | mean abs diff |
| `frame:3:reference_hash` | `ok` | reference hash |
| `frame:3:result_output_match` | `ok` | result output matches frame |
| `frame:3:target_match` | `ok` | output path matches adapter |
| `frame:3:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0003_backend_scene.json |
| `frame:3:scene_schema` | `ok` | scene schema |
| `frame:3:scene_match` | `ok` | scene path matches adapter |
| `frame:3:scene_output:image` | `ok` | scene output path |
| `frame:3:scene_output:metadata` | `ok` | scene output path |
| `frame:3:scene_output:validation` | `ok` | scene output path |
| `frame:3:metadata_schema` | `ok` | metadata schema |
| `frame:3:validation_schema` | `ok` | validation schema |
| `frame:3:validation_status` | `ok` | validation status |
| `frame:3:validation_max_abs` | `ok` | validation max abs |
| `frame:3:validation_mean_abs` | `ok` | validation mean abs |
| `frame:4:status` | `ok` | frame status |
| `frame:4:returncode` | `ok` | process return code |
| `frame:4:elapsed` | `ok` | process elapsed |
| `frame:4:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0004_stdout.log |
| `frame:4:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0004_stderr.log |
| `frame:4:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0004_backend_process_result.json |
| `frame:4:result_schema` | `ok` | result schema |
| `frame:4:result_status` | `ok` | result status |
| `frame:4:result_max_abs` | `ok` | result max abs |
| `frame:4:result_mean_abs` | `ok` | result mean abs |
| `frame:4:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0004.png |
| `frame:4:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0004.json |
| `frame:4:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0004.json |
| `frame:4:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0004_backend_process_stub.png |
| `frame:4:max_abs` | `ok` | max abs diff |
| `frame:4:mean_abs` | `ok` | mean abs diff |
| `frame:4:reference_hash` | `ok` | reference hash |
| `frame:4:result_output_match` | `ok` | result output matches frame |
| `frame:4:target_match` | `ok` | output path matches adapter |
| `frame:4:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0004_backend_scene.json |
| `frame:4:scene_schema` | `ok` | scene schema |
| `frame:4:scene_match` | `ok` | scene path matches adapter |
| `frame:4:scene_output:image` | `ok` | scene output path |
| `frame:4:scene_output:metadata` | `ok` | scene output path |
| `frame:4:scene_output:validation` | `ok` | scene output path |
| `frame:4:metadata_schema` | `ok` | metadata schema |
| `frame:4:validation_schema` | `ok` | validation schema |
| `frame:4:validation_status` | `ok` | validation status |
| `frame:4:validation_max_abs` | `ok` | validation max abs |
| `frame:4:validation_mean_abs` | `ok` | validation mean abs |
| `frame:5:status` | `ok` | frame status |
| `frame:5:returncode` | `ok` | process return code |
| `frame:5:elapsed` | `ok` | process elapsed |
| `frame:5:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0005_stdout.log |
| `frame:5:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0005_stderr.log |
| `frame:5:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0005_backend_process_result.json |
| `frame:5:result_schema` | `ok` | result schema |
| `frame:5:result_status` | `ok` | result status |
| `frame:5:result_max_abs` | `ok` | result max abs |
| `frame:5:result_mean_abs` | `ok` | result mean abs |
| `frame:5:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0005.png |
| `frame:5:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0005.json |
| `frame:5:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0005.json |
| `frame:5:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0005_backend_process_stub.png |
| `frame:5:max_abs` | `ok` | max abs diff |
| `frame:5:mean_abs` | `ok` | mean abs diff |
| `frame:5:reference_hash` | `ok` | reference hash |
| `frame:5:result_output_match` | `ok` | result output matches frame |
| `frame:5:target_match` | `ok` | output path matches adapter |
| `frame:5:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0005_backend_scene.json |
| `frame:5:scene_schema` | `ok` | scene schema |
| `frame:5:scene_match` | `ok` | scene path matches adapter |
| `frame:5:scene_output:image` | `ok` | scene output path |
| `frame:5:scene_output:metadata` | `ok` | scene output path |
| `frame:5:scene_output:validation` | `ok` | scene output path |
| `frame:5:metadata_schema` | `ok` | metadata schema |
| `frame:5:validation_schema` | `ok` | validation schema |
| `frame:5:validation_status` | `ok` | validation status |
| `frame:5:validation_max_abs` | `ok` | validation max abs |
| `frame:5:validation_mean_abs` | `ok` | validation mean abs |
| `frame:6:status` | `ok` | frame status |
| `frame:6:returncode` | `ok` | process return code |
| `frame:6:elapsed` | `ok` | process elapsed |
| `frame:6:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0006_stdout.log |
| `frame:6:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0006_stderr.log |
| `frame:6:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0006_backend_process_result.json |
| `frame:6:result_schema` | `ok` | result schema |
| `frame:6:result_status` | `ok` | result status |
| `frame:6:result_max_abs` | `ok` | result max abs |
| `frame:6:result_mean_abs` | `ok` | result mean abs |
| `frame:6:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0006.png |
| `frame:6:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0006.json |
| `frame:6:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0006.json |
| `frame:6:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0006_backend_process_stub.png |
| `frame:6:max_abs` | `ok` | max abs diff |
| `frame:6:mean_abs` | `ok` | mean abs diff |
| `frame:6:reference_hash` | `ok` | reference hash |
| `frame:6:result_output_match` | `ok` | result output matches frame |
| `frame:6:target_match` | `ok` | output path matches adapter |
| `frame:6:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0006_backend_scene.json |
| `frame:6:scene_schema` | `ok` | scene schema |
| `frame:6:scene_match` | `ok` | scene path matches adapter |
| `frame:6:scene_output:image` | `ok` | scene output path |
| `frame:6:scene_output:metadata` | `ok` | scene output path |
| `frame:6:scene_output:validation` | `ok` | scene output path |
| `frame:6:metadata_schema` | `ok` | metadata schema |
| `frame:6:validation_schema` | `ok` | validation schema |
| `frame:6:validation_status` | `ok` | validation status |
| `frame:6:validation_max_abs` | `ok` | validation max abs |
| `frame:6:validation_mean_abs` | `ok` | validation mean abs |
| `frame:7:status` | `ok` | frame status |
| `frame:7:returncode` | `ok` | process return code |
| `frame:7:elapsed` | `ok` | process elapsed |
| `frame:7:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0007_stdout.log |
| `frame:7:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0007_stderr.log |
| `frame:7:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0007_backend_process_result.json |
| `frame:7:result_schema` | `ok` | result schema |
| `frame:7:result_status` | `ok` | result status |
| `frame:7:result_max_abs` | `ok` | result max abs |
| `frame:7:result_mean_abs` | `ok` | result mean abs |
| `frame:7:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0007.png |
| `frame:7:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0007.json |
| `frame:7:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0007.json |
| `frame:7:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0007_backend_process_stub.png |
| `frame:7:max_abs` | `ok` | max abs diff |
| `frame:7:mean_abs` | `ok` | mean abs diff |
| `frame:7:reference_hash` | `ok` | reference hash |
| `frame:7:result_output_match` | `ok` | result output matches frame |
| `frame:7:target_match` | `ok` | output path matches adapter |
| `frame:7:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0007_backend_scene.json |
| `frame:7:scene_schema` | `ok` | scene schema |
| `frame:7:scene_match` | `ok` | scene path matches adapter |
| `frame:7:scene_output:image` | `ok` | scene output path |
| `frame:7:scene_output:metadata` | `ok` | scene output path |
| `frame:7:scene_output:validation` | `ok` | scene output path |
| `frame:7:metadata_schema` | `ok` | metadata schema |
| `frame:7:validation_schema` | `ok` | validation schema |
| `frame:7:validation_status` | `ok` | validation status |
| `frame:7:validation_max_abs` | `ok` | validation max abs |
| `frame:7:validation_mean_abs` | `ok` | validation mean abs |
| `frame:8:status` | `ok` | frame status |
| `frame:8:returncode` | `ok` | process return code |
| `frame:8:elapsed` | `ok` | process elapsed |
| `frame:8:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0008_stdout.log |
| `frame:8:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0008_stderr.log |
| `frame:8:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0008_backend_process_result.json |
| `frame:8:result_schema` | `ok` | result schema |
| `frame:8:result_status` | `ok` | result status |
| `frame:8:result_max_abs` | `ok` | result max abs |
| `frame:8:result_mean_abs` | `ok` | result mean abs |
| `frame:8:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0008.png |
| `frame:8:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0008.json |
| `frame:8:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0008.json |
| `frame:8:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0008_backend_process_stub.png |
| `frame:8:max_abs` | `ok` | max abs diff |
| `frame:8:mean_abs` | `ok` | mean abs diff |
| `frame:8:reference_hash` | `ok` | reference hash |
| `frame:8:result_output_match` | `ok` | result output matches frame |
| `frame:8:target_match` | `ok` | output path matches adapter |
| `frame:8:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0008_backend_scene.json |
| `frame:8:scene_schema` | `ok` | scene schema |
| `frame:8:scene_match` | `ok` | scene path matches adapter |
| `frame:8:scene_output:image` | `ok` | scene output path |
| `frame:8:scene_output:metadata` | `ok` | scene output path |
| `frame:8:scene_output:validation` | `ok` | scene output path |
| `frame:8:metadata_schema` | `ok` | metadata schema |
| `frame:8:validation_schema` | `ok` | validation schema |
| `frame:8:validation_status` | `ok` | validation status |
| `frame:8:validation_max_abs` | `ok` | validation max abs |
| `frame:8:validation_mean_abs` | `ok` | validation mean abs |
| `frame:9:status` | `ok` | frame status |
| `frame:9:returncode` | `ok` | process return code |
| `frame:9:elapsed` | `ok` | process elapsed |
| `frame:9:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0009_stdout.log |
| `frame:9:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0009_stderr.log |
| `frame:9:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0009_backend_process_result.json |
| `frame:9:result_schema` | `ok` | result schema |
| `frame:9:result_status` | `ok` | result status |
| `frame:9:result_max_abs` | `ok` | result max abs |
| `frame:9:result_mean_abs` | `ok` | result mean abs |
| `frame:9:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0009.png |
| `frame:9:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0009.json |
| `frame:9:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0009.json |
| `frame:9:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0009_backend_process_stub.png |
| `frame:9:max_abs` | `ok` | max abs diff |
| `frame:9:mean_abs` | `ok` | mean abs diff |
| `frame:9:reference_hash` | `ok` | reference hash |
| `frame:9:result_output_match` | `ok` | result output matches frame |
| `frame:9:target_match` | `ok` | output path matches adapter |
| `frame:9:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0009_backend_scene.json |
| `frame:9:scene_schema` | `ok` | scene schema |
| `frame:9:scene_match` | `ok` | scene path matches adapter |
| `frame:9:scene_output:image` | `ok` | scene output path |
| `frame:9:scene_output:metadata` | `ok` | scene output path |
| `frame:9:scene_output:validation` | `ok` | scene output path |
| `frame:9:metadata_schema` | `ok` | metadata schema |
| `frame:9:validation_schema` | `ok` | validation schema |
| `frame:9:validation_status` | `ok` | validation status |
| `frame:9:validation_max_abs` | `ok` | validation max abs |
| `frame:9:validation_mean_abs` | `ok` | validation mean abs |
| `frame:10:status` | `ok` | frame status |
| `frame:10:returncode` | `ok` | process return code |
| `frame:10:elapsed` | `ok` | process elapsed |
| `frame:10:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0010_stdout.log |
| `frame:10:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0010_stderr.log |
| `frame:10:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0010_backend_process_result.json |
| `frame:10:result_schema` | `ok` | result schema |
| `frame:10:result_status` | `ok` | result status |
| `frame:10:result_max_abs` | `ok` | result max abs |
| `frame:10:result_mean_abs` | `ok` | result mean abs |
| `frame:10:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0010.png |
| `frame:10:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0010.json |
| `frame:10:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0010.json |
| `frame:10:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0010_backend_process_stub.png |
| `frame:10:max_abs` | `ok` | max abs diff |
| `frame:10:mean_abs` | `ok` | mean abs diff |
| `frame:10:reference_hash` | `ok` | reference hash |
| `frame:10:result_output_match` | `ok` | result output matches frame |
| `frame:10:target_match` | `ok` | output path matches adapter |
| `frame:10:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0010_backend_scene.json |
| `frame:10:scene_schema` | `ok` | scene schema |
| `frame:10:scene_match` | `ok` | scene path matches adapter |
| `frame:10:scene_output:image` | `ok` | scene output path |
| `frame:10:scene_output:metadata` | `ok` | scene output path |
| `frame:10:scene_output:validation` | `ok` | scene output path |
| `frame:10:metadata_schema` | `ok` | metadata schema |
| `frame:10:validation_schema` | `ok` | validation schema |
| `frame:10:validation_status` | `ok` | validation status |
| `frame:10:validation_max_abs` | `ok` | validation max abs |
| `frame:10:validation_mean_abs` | `ok` | validation mean abs |
| `frame:11:status` | `ok` | frame status |
| `frame:11:returncode` | `ok` | process return code |
| `frame:11:elapsed` | `ok` | process elapsed |
| `frame:11:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0011_stdout.log |
| `frame:11:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0011_stderr.log |
| `frame:11:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0011_backend_process_result.json |
| `frame:11:result_schema` | `ok` | result schema |
| `frame:11:result_status` | `ok` | result status |
| `frame:11:result_max_abs` | `ok` | result max abs |
| `frame:11:result_mean_abs` | `ok` | result mean abs |
| `frame:11:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0011.png |
| `frame:11:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0011.json |
| `frame:11:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0011.json |
| `frame:11:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0011_backend_process_stub.png |
| `frame:11:max_abs` | `ok` | max abs diff |
| `frame:11:mean_abs` | `ok` | mean abs diff |
| `frame:11:reference_hash` | `ok` | reference hash |
| `frame:11:result_output_match` | `ok` | result output matches frame |
| `frame:11:target_match` | `ok` | output path matches adapter |
| `frame:11:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0011_backend_scene.json |
| `frame:11:scene_schema` | `ok` | scene schema |
| `frame:11:scene_match` | `ok` | scene path matches adapter |
| `frame:11:scene_output:image` | `ok` | scene output path |
| `frame:11:scene_output:metadata` | `ok` | scene output path |
| `frame:11:scene_output:validation` | `ok` | scene output path |
| `frame:11:metadata_schema` | `ok` | metadata schema |
| `frame:11:validation_schema` | `ok` | validation schema |
| `frame:11:validation_status` | `ok` | validation status |
| `frame:11:validation_max_abs` | `ok` | validation max abs |
| `frame:11:validation_mean_abs` | `ok` | validation mean abs |
| `frame:12:status` | `ok` | frame status |
| `frame:12:returncode` | `ok` | process return code |
| `frame:12:elapsed` | `ok` | process elapsed |
| `frame:12:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0012_stdout.log |
| `frame:12:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0012_stderr.log |
| `frame:12:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0012_backend_process_result.json |
| `frame:12:result_schema` | `ok` | result schema |
| `frame:12:result_status` | `ok` | result status |
| `frame:12:result_max_abs` | `ok` | result max abs |
| `frame:12:result_mean_abs` | `ok` | result mean abs |
| `frame:12:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0012.png |
| `frame:12:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0012.json |
| `frame:12:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0012.json |
| `frame:12:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0012_backend_process_stub.png |
| `frame:12:max_abs` | `ok` | max abs diff |
| `frame:12:mean_abs` | `ok` | mean abs diff |
| `frame:12:reference_hash` | `ok` | reference hash |
| `frame:12:result_output_match` | `ok` | result output matches frame |
| `frame:12:target_match` | `ok` | output path matches adapter |
| `frame:12:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0012_backend_scene.json |
| `frame:12:scene_schema` | `ok` | scene schema |
| `frame:12:scene_match` | `ok` | scene path matches adapter |
| `frame:12:scene_output:image` | `ok` | scene output path |
| `frame:12:scene_output:metadata` | `ok` | scene output path |
| `frame:12:scene_output:validation` | `ok` | scene output path |
| `frame:12:metadata_schema` | `ok` | metadata schema |
| `frame:12:validation_schema` | `ok` | validation schema |
| `frame:12:validation_status` | `ok` | validation status |
| `frame:12:validation_max_abs` | `ok` | validation max abs |
| `frame:12:validation_mean_abs` | `ok` | validation mean abs |
| `frame:13:status` | `ok` | frame status |
| `frame:13:returncode` | `ok` | process return code |
| `frame:13:elapsed` | `ok` | process elapsed |
| `frame:13:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0013_stdout.log |
| `frame:13:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0013_stderr.log |
| `frame:13:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0013_backend_process_result.json |
| `frame:13:result_schema` | `ok` | result schema |
| `frame:13:result_status` | `ok` | result status |
| `frame:13:result_max_abs` | `ok` | result max abs |
| `frame:13:result_mean_abs` | `ok` | result mean abs |
| `frame:13:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0013.png |
| `frame:13:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0013.json |
| `frame:13:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0013.json |
| `frame:13:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0013_backend_process_stub.png |
| `frame:13:max_abs` | `ok` | max abs diff |
| `frame:13:mean_abs` | `ok` | mean abs diff |
| `frame:13:reference_hash` | `ok` | reference hash |
| `frame:13:result_output_match` | `ok` | result output matches frame |
| `frame:13:target_match` | `ok` | output path matches adapter |
| `frame:13:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0013_backend_scene.json |
| `frame:13:scene_schema` | `ok` | scene schema |
| `frame:13:scene_match` | `ok` | scene path matches adapter |
| `frame:13:scene_output:image` | `ok` | scene output path |
| `frame:13:scene_output:metadata` | `ok` | scene output path |
| `frame:13:scene_output:validation` | `ok` | scene output path |
| `frame:13:metadata_schema` | `ok` | metadata schema |
| `frame:13:validation_schema` | `ok` | validation schema |
| `frame:13:validation_status` | `ok` | validation status |
| `frame:13:validation_max_abs` | `ok` | validation max abs |
| `frame:13:validation_mean_abs` | `ok` | validation mean abs |
| `frame:14:status` | `ok` | frame status |
| `frame:14:returncode` | `ok` | process return code |
| `frame:14:elapsed` | `ok` | process elapsed |
| `frame:14:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0014_stdout.log |
| `frame:14:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0014_stderr.log |
| `frame:14:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0014_backend_process_result.json |
| `frame:14:result_schema` | `ok` | result schema |
| `frame:14:result_status` | `ok` | result status |
| `frame:14:result_max_abs` | `ok` | result max abs |
| `frame:14:result_mean_abs` | `ok` | result mean abs |
| `frame:14:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0014.png |
| `frame:14:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0014.json |
| `frame:14:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0014.json |
| `frame:14:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0014_backend_process_stub.png |
| `frame:14:max_abs` | `ok` | max abs diff |
| `frame:14:mean_abs` | `ok` | mean abs diff |
| `frame:14:reference_hash` | `ok` | reference hash |
| `frame:14:result_output_match` | `ok` | result output matches frame |
| `frame:14:target_match` | `ok` | output path matches adapter |
| `frame:14:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0014_backend_scene.json |
| `frame:14:scene_schema` | `ok` | scene schema |
| `frame:14:scene_match` | `ok` | scene path matches adapter |
| `frame:14:scene_output:image` | `ok` | scene output path |
| `frame:14:scene_output:metadata` | `ok` | scene output path |
| `frame:14:scene_output:validation` | `ok` | scene output path |
| `frame:14:metadata_schema` | `ok` | metadata schema |
| `frame:14:validation_schema` | `ok` | validation schema |
| `frame:14:validation_status` | `ok` | validation status |
| `frame:14:validation_max_abs` | `ok` | validation max abs |
| `frame:14:validation_mean_abs` | `ok` | validation mean abs |
| `frame:15:status` | `ok` | frame status |
| `frame:15:returncode` | `ok` | process return code |
| `frame:15:elapsed` | `ok` | process elapsed |
| `frame:15:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0015_stdout.log |
| `frame:15:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0015_stderr.log |
| `frame:15:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0015_backend_process_result.json |
| `frame:15:result_schema` | `ok` | result schema |
| `frame:15:result_status` | `ok` | result status |
| `frame:15:result_max_abs` | `ok` | result max abs |
| `frame:15:result_mean_abs` | `ok` | result mean abs |
| `frame:15:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0015.png |
| `frame:15:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0015.json |
| `frame:15:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0015.json |
| `frame:15:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0015_backend_process_stub.png |
| `frame:15:max_abs` | `ok` | max abs diff |
| `frame:15:mean_abs` | `ok` | mean abs diff |
| `frame:15:reference_hash` | `ok` | reference hash |
| `frame:15:result_output_match` | `ok` | result output matches frame |
| `frame:15:target_match` | `ok` | output path matches adapter |
| `frame:15:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0015_backend_scene.json |
| `frame:15:scene_schema` | `ok` | scene schema |
| `frame:15:scene_match` | `ok` | scene path matches adapter |
| `frame:15:scene_output:image` | `ok` | scene output path |
| `frame:15:scene_output:metadata` | `ok` | scene output path |
| `frame:15:scene_output:validation` | `ok` | scene output path |
| `frame:15:metadata_schema` | `ok` | metadata schema |
| `frame:15:validation_schema` | `ok` | validation schema |
| `frame:15:validation_status` | `ok` | validation status |
| `frame:15:validation_max_abs` | `ok` | validation max abs |
| `frame:15:validation_mean_abs` | `ok` | validation mean abs |
| `frame:16:status` | `ok` | frame status |
| `frame:16:returncode` | `ok` | process return code |
| `frame:16:elapsed` | `ok` | process elapsed |
| `frame:16:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0016_stdout.log |
| `frame:16:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0016_stderr.log |
| `frame:16:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0016_backend_process_result.json |
| `frame:16:result_schema` | `ok` | result schema |
| `frame:16:result_status` | `ok` | result status |
| `frame:16:result_max_abs` | `ok` | result max abs |
| `frame:16:result_mean_abs` | `ok` | result mean abs |
| `frame:16:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0016.png |
| `frame:16:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0016.json |
| `frame:16:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0016.json |
| `frame:16:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0016_backend_process_stub.png |
| `frame:16:max_abs` | `ok` | max abs diff |
| `frame:16:mean_abs` | `ok` | mean abs diff |
| `frame:16:reference_hash` | `ok` | reference hash |
| `frame:16:result_output_match` | `ok` | result output matches frame |
| `frame:16:target_match` | `ok` | output path matches adapter |
| `frame:16:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0016_backend_scene.json |
| `frame:16:scene_schema` | `ok` | scene schema |
| `frame:16:scene_match` | `ok` | scene path matches adapter |
| `frame:16:scene_output:image` | `ok` | scene output path |
| `frame:16:scene_output:metadata` | `ok` | scene output path |
| `frame:16:scene_output:validation` | `ok` | scene output path |
| `frame:16:metadata_schema` | `ok` | metadata schema |
| `frame:16:validation_schema` | `ok` | validation schema |
| `frame:16:validation_status` | `ok` | validation status |
| `frame:16:validation_max_abs` | `ok` | validation max abs |
| `frame:16:validation_mean_abs` | `ok` | validation mean abs |
| `frame:17:status` | `ok` | frame status |
| `frame:17:returncode` | `ok` | process return code |
| `frame:17:elapsed` | `ok` | process elapsed |
| `frame:17:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0017_stdout.log |
| `frame:17:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0017_stderr.log |
| `frame:17:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0017_backend_process_result.json |
| `frame:17:result_schema` | `ok` | result schema |
| `frame:17:result_status` | `ok` | result status |
| `frame:17:result_max_abs` | `ok` | result max abs |
| `frame:17:result_mean_abs` | `ok` | result mean abs |
| `frame:17:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0017.png |
| `frame:17:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0017.json |
| `frame:17:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0017.json |
| `frame:17:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0017_backend_process_stub.png |
| `frame:17:max_abs` | `ok` | max abs diff |
| `frame:17:mean_abs` | `ok` | mean abs diff |
| `frame:17:reference_hash` | `ok` | reference hash |
| `frame:17:result_output_match` | `ok` | result output matches frame |
| `frame:17:target_match` | `ok` | output path matches adapter |
| `frame:17:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0017_backend_scene.json |
| `frame:17:scene_schema` | `ok` | scene schema |
| `frame:17:scene_match` | `ok` | scene path matches adapter |
| `frame:17:scene_output:image` | `ok` | scene output path |
| `frame:17:scene_output:metadata` | `ok` | scene output path |
| `frame:17:scene_output:validation` | `ok` | scene output path |
| `frame:17:metadata_schema` | `ok` | metadata schema |
| `frame:17:validation_schema` | `ok` | validation schema |
| `frame:17:validation_status` | `ok` | validation status |
| `frame:17:validation_max_abs` | `ok` | validation max abs |
| `frame:17:validation_mean_abs` | `ok` | validation mean abs |
| `frame:18:status` | `ok` | frame status |
| `frame:18:returncode` | `ok` | process return code |
| `frame:18:elapsed` | `ok` | process elapsed |
| `frame:18:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0018_stdout.log |
| `frame:18:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0018_stderr.log |
| `frame:18:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0018_backend_process_result.json |
| `frame:18:result_schema` | `ok` | result schema |
| `frame:18:result_status` | `ok` | result status |
| `frame:18:result_max_abs` | `ok` | result max abs |
| `frame:18:result_mean_abs` | `ok` | result mean abs |
| `frame:18:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0018.png |
| `frame:18:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0018.json |
| `frame:18:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0018.json |
| `frame:18:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0018_backend_process_stub.png |
| `frame:18:max_abs` | `ok` | max abs diff |
| `frame:18:mean_abs` | `ok` | mean abs diff |
| `frame:18:reference_hash` | `ok` | reference hash |
| `frame:18:result_output_match` | `ok` | result output matches frame |
| `frame:18:target_match` | `ok` | output path matches adapter |
| `frame:18:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0018_backend_scene.json |
| `frame:18:scene_schema` | `ok` | scene schema |
| `frame:18:scene_match` | `ok` | scene path matches adapter |
| `frame:18:scene_output:image` | `ok` | scene output path |
| `frame:18:scene_output:metadata` | `ok` | scene output path |
| `frame:18:scene_output:validation` | `ok` | scene output path |
| `frame:18:metadata_schema` | `ok` | metadata schema |
| `frame:18:validation_schema` | `ok` | validation schema |
| `frame:18:validation_status` | `ok` | validation status |
| `frame:18:validation_max_abs` | `ok` | validation max abs |
| `frame:18:validation_mean_abs` | `ok` | validation mean abs |
| `frame:19:status` | `ok` | frame status |
| `frame:19:returncode` | `ok` | process return code |
| `frame:19:elapsed` | `ok` | process elapsed |
| `frame:19:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0019_stdout.log |
| `frame:19:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0019_stderr.log |
| `frame:19:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0019_backend_process_result.json |
| `frame:19:result_schema` | `ok` | result schema |
| `frame:19:result_status` | `ok` | result status |
| `frame:19:result_max_abs` | `ok` | result max abs |
| `frame:19:result_mean_abs` | `ok` | result mean abs |
| `frame:19:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0019.png |
| `frame:19:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0019.json |
| `frame:19:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0019.json |
| `frame:19:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0019_backend_process_stub.png |
| `frame:19:max_abs` | `ok` | max abs diff |
| `frame:19:mean_abs` | `ok` | mean abs diff |
| `frame:19:reference_hash` | `ok` | reference hash |
| `frame:19:result_output_match` | `ok` | result output matches frame |
| `frame:19:target_match` | `ok` | output path matches adapter |
| `frame:19:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0019_backend_scene.json |
| `frame:19:scene_schema` | `ok` | scene schema |
| `frame:19:scene_match` | `ok` | scene path matches adapter |
| `frame:19:scene_output:image` | `ok` | scene output path |
| `frame:19:scene_output:metadata` | `ok` | scene output path |
| `frame:19:scene_output:validation` | `ok` | scene output path |
| `frame:19:metadata_schema` | `ok` | metadata schema |
| `frame:19:validation_schema` | `ok` | validation schema |
| `frame:19:validation_status` | `ok` | validation status |
| `frame:19:validation_max_abs` | `ok` | validation max abs |
| `frame:19:validation_mean_abs` | `ok` | validation mean abs |
| `frame:20:status` | `ok` | frame status |
| `frame:20:returncode` | `ok` | process return code |
| `frame:20:elapsed` | `ok` | process elapsed |
| `frame:20:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0020_stdout.log |
| `frame:20:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0020_stderr.log |
| `frame:20:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0020_backend_process_result.json |
| `frame:20:result_schema` | `ok` | result schema |
| `frame:20:result_status` | `ok` | result status |
| `frame:20:result_max_abs` | `ok` | result max abs |
| `frame:20:result_mean_abs` | `ok` | result mean abs |
| `frame:20:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0020.png |
| `frame:20:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0020.json |
| `frame:20:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0020.json |
| `frame:20:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0020_backend_process_stub.png |
| `frame:20:max_abs` | `ok` | max abs diff |
| `frame:20:mean_abs` | `ok` | mean abs diff |
| `frame:20:reference_hash` | `ok` | reference hash |
| `frame:20:result_output_match` | `ok` | result output matches frame |
| `frame:20:target_match` | `ok` | output path matches adapter |
| `frame:20:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0020_backend_scene.json |
| `frame:20:scene_schema` | `ok` | scene schema |
| `frame:20:scene_match` | `ok` | scene path matches adapter |
| `frame:20:scene_output:image` | `ok` | scene output path |
| `frame:20:scene_output:metadata` | `ok` | scene output path |
| `frame:20:scene_output:validation` | `ok` | scene output path |
| `frame:20:metadata_schema` | `ok` | metadata schema |
| `frame:20:validation_schema` | `ok` | validation schema |
| `frame:20:validation_status` | `ok` | validation status |
| `frame:20:validation_max_abs` | `ok` | validation max abs |
| `frame:20:validation_mean_abs` | `ok` | validation mean abs |
| `frame:21:status` | `ok` | frame status |
| `frame:21:returncode` | `ok` | process return code |
| `frame:21:elapsed` | `ok` | process elapsed |
| `frame:21:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0021_stdout.log |
| `frame:21:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0021_stderr.log |
| `frame:21:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0021_backend_process_result.json |
| `frame:21:result_schema` | `ok` | result schema |
| `frame:21:result_status` | `ok` | result status |
| `frame:21:result_max_abs` | `ok` | result max abs |
| `frame:21:result_mean_abs` | `ok` | result mean abs |
| `frame:21:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0021.png |
| `frame:21:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0021.json |
| `frame:21:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0021.json |
| `frame:21:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0021_backend_process_stub.png |
| `frame:21:max_abs` | `ok` | max abs diff |
| `frame:21:mean_abs` | `ok` | mean abs diff |
| `frame:21:reference_hash` | `ok` | reference hash |
| `frame:21:result_output_match` | `ok` | result output matches frame |
| `frame:21:target_match` | `ok` | output path matches adapter |
| `frame:21:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0021_backend_scene.json |
| `frame:21:scene_schema` | `ok` | scene schema |
| `frame:21:scene_match` | `ok` | scene path matches adapter |
| `frame:21:scene_output:image` | `ok` | scene output path |
| `frame:21:scene_output:metadata` | `ok` | scene output path |
| `frame:21:scene_output:validation` | `ok` | scene output path |
| `frame:21:metadata_schema` | `ok` | metadata schema |
| `frame:21:validation_schema` | `ok` | validation schema |
| `frame:21:validation_status` | `ok` | validation status |
| `frame:21:validation_max_abs` | `ok` | validation max abs |
| `frame:21:validation_mean_abs` | `ok` | validation mean abs |
| `frame:22:status` | `ok` | frame status |
| `frame:22:returncode` | `ok` | process return code |
| `frame:22:elapsed` | `ok` | process elapsed |
| `frame:22:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0022_stdout.log |
| `frame:22:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0022_stderr.log |
| `frame:22:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0022_backend_process_result.json |
| `frame:22:result_schema` | `ok` | result schema |
| `frame:22:result_status` | `ok` | result status |
| `frame:22:result_max_abs` | `ok` | result max abs |
| `frame:22:result_mean_abs` | `ok` | result mean abs |
| `frame:22:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0022.png |
| `frame:22:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0022.json |
| `frame:22:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0022.json |
| `frame:22:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0022_backend_process_stub.png |
| `frame:22:max_abs` | `ok` | max abs diff |
| `frame:22:mean_abs` | `ok` | mean abs diff |
| `frame:22:reference_hash` | `ok` | reference hash |
| `frame:22:result_output_match` | `ok` | result output matches frame |
| `frame:22:target_match` | `ok` | output path matches adapter |
| `frame:22:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0022_backend_scene.json |
| `frame:22:scene_schema` | `ok` | scene schema |
| `frame:22:scene_match` | `ok` | scene path matches adapter |
| `frame:22:scene_output:image` | `ok` | scene output path |
| `frame:22:scene_output:metadata` | `ok` | scene output path |
| `frame:22:scene_output:validation` | `ok` | scene output path |
| `frame:22:metadata_schema` | `ok` | metadata schema |
| `frame:22:validation_schema` | `ok` | validation schema |
| `frame:22:validation_status` | `ok` | validation status |
| `frame:22:validation_max_abs` | `ok` | validation max abs |
| `frame:22:validation_mean_abs` | `ok` | validation mean abs |
| `frame:23:status` | `ok` | frame status |
| `frame:23:returncode` | `ok` | process return code |
| `frame:23:elapsed` | `ok` | process elapsed |
| `frame:23:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0023_stdout.log |
| `frame:23:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0023_stderr.log |
| `frame:23:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0023_backend_process_result.json |
| `frame:23:result_schema` | `ok` | result schema |
| `frame:23:result_status` | `ok` | result status |
| `frame:23:result_max_abs` | `ok` | result max abs |
| `frame:23:result_mean_abs` | `ok` | result mean abs |
| `frame:23:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0023.png |
| `frame:23:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0023.json |
| `frame:23:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0023.json |
| `frame:23:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0023_backend_process_stub.png |
| `frame:23:max_abs` | `ok` | max abs diff |
| `frame:23:mean_abs` | `ok` | mean abs diff |
| `frame:23:reference_hash` | `ok` | reference hash |
| `frame:23:result_output_match` | `ok` | result output matches frame |
| `frame:23:target_match` | `ok` | output path matches adapter |
| `frame:23:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0023_backend_scene.json |
| `frame:23:scene_schema` | `ok` | scene schema |
| `frame:23:scene_match` | `ok` | scene path matches adapter |
| `frame:23:scene_output:image` | `ok` | scene output path |
| `frame:23:scene_output:metadata` | `ok` | scene output path |
| `frame:23:scene_output:validation` | `ok` | scene output path |
| `frame:23:metadata_schema` | `ok` | metadata schema |
| `frame:23:validation_schema` | `ok` | validation schema |
| `frame:23:validation_status` | `ok` | validation status |
| `frame:23:validation_max_abs` | `ok` | validation max abs |
| `frame:23:validation_mean_abs` | `ok` | validation mean abs |
| `frame:24:status` | `ok` | frame status |
| `frame:24:returncode` | `ok` | process return code |
| `frame:24:elapsed` | `ok` | process elapsed |
| `frame:24:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0024_stdout.log |
| `frame:24:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0024_stderr.log |
| `frame:24:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0024_backend_process_result.json |
| `frame:24:result_schema` | `ok` | result schema |
| `frame:24:result_status` | `ok` | result status |
| `frame:24:result_max_abs` | `ok` | result max abs |
| `frame:24:result_mean_abs` | `ok` | result mean abs |
| `frame:24:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0024.png |
| `frame:24:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0024.json |
| `frame:24:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0024.json |
| `frame:24:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0024_backend_process_stub.png |
| `frame:24:max_abs` | `ok` | max abs diff |
| `frame:24:mean_abs` | `ok` | mean abs diff |
| `frame:24:reference_hash` | `ok` | reference hash |
| `frame:24:result_output_match` | `ok` | result output matches frame |
| `frame:24:target_match` | `ok` | output path matches adapter |
| `frame:24:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0024_backend_scene.json |
| `frame:24:scene_schema` | `ok` | scene schema |
| `frame:24:scene_match` | `ok` | scene path matches adapter |
| `frame:24:scene_output:image` | `ok` | scene output path |
| `frame:24:scene_output:metadata` | `ok` | scene output path |
| `frame:24:scene_output:validation` | `ok` | scene output path |
| `frame:24:metadata_schema` | `ok` | metadata schema |
| `frame:24:validation_schema` | `ok` | validation schema |
| `frame:24:validation_status` | `ok` | validation status |
| `frame:24:validation_max_abs` | `ok` | validation max abs |
| `frame:24:validation_mean_abs` | `ok` | validation mean abs |
| `frame:25:status` | `ok` | frame status |
| `frame:25:returncode` | `ok` | process return code |
| `frame:25:elapsed` | `ok` | process elapsed |
| `frame:25:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0025_stdout.log |
| `frame:25:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0025_stderr.log |
| `frame:25:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0025_backend_process_result.json |
| `frame:25:result_schema` | `ok` | result schema |
| `frame:25:result_status` | `ok` | result status |
| `frame:25:result_max_abs` | `ok` | result max abs |
| `frame:25:result_mean_abs` | `ok` | result mean abs |
| `frame:25:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0025.png |
| `frame:25:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0025.json |
| `frame:25:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0025.json |
| `frame:25:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0025_backend_process_stub.png |
| `frame:25:max_abs` | `ok` | max abs diff |
| `frame:25:mean_abs` | `ok` | mean abs diff |
| `frame:25:reference_hash` | `ok` | reference hash |
| `frame:25:result_output_match` | `ok` | result output matches frame |
| `frame:25:target_match` | `ok` | output path matches adapter |
| `frame:25:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0025_backend_scene.json |
| `frame:25:scene_schema` | `ok` | scene schema |
| `frame:25:scene_match` | `ok` | scene path matches adapter |
| `frame:25:scene_output:image` | `ok` | scene output path |
| `frame:25:scene_output:metadata` | `ok` | scene output path |
| `frame:25:scene_output:validation` | `ok` | scene output path |
| `frame:25:metadata_schema` | `ok` | metadata schema |
| `frame:25:validation_schema` | `ok` | validation schema |
| `frame:25:validation_status` | `ok` | validation status |
| `frame:25:validation_max_abs` | `ok` | validation max abs |
| `frame:25:validation_mean_abs` | `ok` | validation mean abs |
| `frame:26:status` | `ok` | frame status |
| `frame:26:returncode` | `ok` | process return code |
| `frame:26:elapsed` | `ok` | process elapsed |
| `frame:26:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0026_stdout.log |
| `frame:26:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0026_stderr.log |
| `frame:26:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0026_backend_process_result.json |
| `frame:26:result_schema` | `ok` | result schema |
| `frame:26:result_status` | `ok` | result status |
| `frame:26:result_max_abs` | `ok` | result max abs |
| `frame:26:result_mean_abs` | `ok` | result mean abs |
| `frame:26:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0026.png |
| `frame:26:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0026.json |
| `frame:26:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0026.json |
| `frame:26:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0026_backend_process_stub.png |
| `frame:26:max_abs` | `ok` | max abs diff |
| `frame:26:mean_abs` | `ok` | mean abs diff |
| `frame:26:reference_hash` | `ok` | reference hash |
| `frame:26:result_output_match` | `ok` | result output matches frame |
| `frame:26:target_match` | `ok` | output path matches adapter |
| `frame:26:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0026_backend_scene.json |
| `frame:26:scene_schema` | `ok` | scene schema |
| `frame:26:scene_match` | `ok` | scene path matches adapter |
| `frame:26:scene_output:image` | `ok` | scene output path |
| `frame:26:scene_output:metadata` | `ok` | scene output path |
| `frame:26:scene_output:validation` | `ok` | scene output path |
| `frame:26:metadata_schema` | `ok` | metadata schema |
| `frame:26:validation_schema` | `ok` | validation schema |
| `frame:26:validation_status` | `ok` | validation status |
| `frame:26:validation_max_abs` | `ok` | validation max abs |
| `frame:26:validation_mean_abs` | `ok` | validation mean abs |
| `frame:27:status` | `ok` | frame status |
| `frame:27:returncode` | `ok` | process return code |
| `frame:27:elapsed` | `ok` | process elapsed |
| `frame:27:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0027_stdout.log |
| `frame:27:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0027_stderr.log |
| `frame:27:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0027_backend_process_result.json |
| `frame:27:result_schema` | `ok` | result schema |
| `frame:27:result_status` | `ok` | result status |
| `frame:27:result_max_abs` | `ok` | result max abs |
| `frame:27:result_mean_abs` | `ok` | result mean abs |
| `frame:27:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0027.png |
| `frame:27:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0027.json |
| `frame:27:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0027.json |
| `frame:27:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0027_backend_process_stub.png |
| `frame:27:max_abs` | `ok` | max abs diff |
| `frame:27:mean_abs` | `ok` | mean abs diff |
| `frame:27:reference_hash` | `ok` | reference hash |
| `frame:27:result_output_match` | `ok` | result output matches frame |
| `frame:27:target_match` | `ok` | output path matches adapter |
| `frame:27:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0027_backend_scene.json |
| `frame:27:scene_schema` | `ok` | scene schema |
| `frame:27:scene_match` | `ok` | scene path matches adapter |
| `frame:27:scene_output:image` | `ok` | scene output path |
| `frame:27:scene_output:metadata` | `ok` | scene output path |
| `frame:27:scene_output:validation` | `ok` | scene output path |
| `frame:27:metadata_schema` | `ok` | metadata schema |
| `frame:27:validation_schema` | `ok` | validation schema |
| `frame:27:validation_status` | `ok` | validation status |
| `frame:27:validation_max_abs` | `ok` | validation max abs |
| `frame:27:validation_mean_abs` | `ok` | validation mean abs |
| `frame:28:status` | `ok` | frame status |
| `frame:28:returncode` | `ok` | process return code |
| `frame:28:elapsed` | `ok` | process elapsed |
| `frame:28:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0028_stdout.log |
| `frame:28:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0028_stderr.log |
| `frame:28:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0028_backend_process_result.json |
| `frame:28:result_schema` | `ok` | result schema |
| `frame:28:result_status` | `ok` | result status |
| `frame:28:result_max_abs` | `ok` | result max abs |
| `frame:28:result_mean_abs` | `ok` | result mean abs |
| `frame:28:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0028.png |
| `frame:28:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0028.json |
| `frame:28:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0028.json |
| `frame:28:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0028_backend_process_stub.png |
| `frame:28:max_abs` | `ok` | max abs diff |
| `frame:28:mean_abs` | `ok` | mean abs diff |
| `frame:28:reference_hash` | `ok` | reference hash |
| `frame:28:result_output_match` | `ok` | result output matches frame |
| `frame:28:target_match` | `ok` | output path matches adapter |
| `frame:28:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0028_backend_scene.json |
| `frame:28:scene_schema` | `ok` | scene schema |
| `frame:28:scene_match` | `ok` | scene path matches adapter |
| `frame:28:scene_output:image` | `ok` | scene output path |
| `frame:28:scene_output:metadata` | `ok` | scene output path |
| `frame:28:scene_output:validation` | `ok` | scene output path |
| `frame:28:metadata_schema` | `ok` | metadata schema |
| `frame:28:validation_schema` | `ok` | validation schema |
| `frame:28:validation_status` | `ok` | validation status |
| `frame:28:validation_max_abs` | `ok` | validation max abs |
| `frame:28:validation_mean_abs` | `ok` | validation mean abs |
| `frame:29:status` | `ok` | frame status |
| `frame:29:returncode` | `ok` | process return code |
| `frame:29:elapsed` | `ok` | process elapsed |
| `frame:29:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0029_stdout.log |
| `frame:29:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0029_stderr.log |
| `frame:29:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0029_backend_process_result.json |
| `frame:29:result_schema` | `ok` | result schema |
| `frame:29:result_status` | `ok` | result status |
| `frame:29:result_max_abs` | `ok` | result max abs |
| `frame:29:result_mean_abs` | `ok` | result mean abs |
| `frame:29:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0029.png |
| `frame:29:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0029.json |
| `frame:29:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0029.json |
| `frame:29:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0029_backend_process_stub.png |
| `frame:29:max_abs` | `ok` | max abs diff |
| `frame:29:mean_abs` | `ok` | mean abs diff |
| `frame:29:reference_hash` | `ok` | reference hash |
| `frame:29:result_output_match` | `ok` | result output matches frame |
| `frame:29:target_match` | `ok` | output path matches adapter |
| `frame:29:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0029_backend_scene.json |
| `frame:29:scene_schema` | `ok` | scene schema |
| `frame:29:scene_match` | `ok` | scene path matches adapter |
| `frame:29:scene_output:image` | `ok` | scene output path |
| `frame:29:scene_output:metadata` | `ok` | scene output path |
| `frame:29:scene_output:validation` | `ok` | scene output path |
| `frame:29:metadata_schema` | `ok` | metadata schema |
| `frame:29:validation_schema` | `ok` | validation schema |
| `frame:29:validation_status` | `ok` | validation status |
| `frame:29:validation_max_abs` | `ok` | validation max abs |
| `frame:29:validation_mean_abs` | `ok` | validation mean abs |
| `frame:30:status` | `ok` | frame status |
| `frame:30:returncode` | `ok` | process return code |
| `frame:30:elapsed` | `ok` | process elapsed |
| `frame:30:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0030_stdout.log |
| `frame:30:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0030_stderr.log |
| `frame:30:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0030_backend_process_result.json |
| `frame:30:result_schema` | `ok` | result schema |
| `frame:30:result_status` | `ok` | result status |
| `frame:30:result_max_abs` | `ok` | result max abs |
| `frame:30:result_mean_abs` | `ok` | result mean abs |
| `frame:30:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0030.png |
| `frame:30:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0030.json |
| `frame:30:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0030.json |
| `frame:30:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0030_backend_process_stub.png |
| `frame:30:max_abs` | `ok` | max abs diff |
| `frame:30:mean_abs` | `ok` | mean abs diff |
| `frame:30:reference_hash` | `ok` | reference hash |
| `frame:30:result_output_match` | `ok` | result output matches frame |
| `frame:30:target_match` | `ok` | output path matches adapter |
| `frame:30:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0030_backend_scene.json |
| `frame:30:scene_schema` | `ok` | scene schema |
| `frame:30:scene_match` | `ok` | scene path matches adapter |
| `frame:30:scene_output:image` | `ok` | scene output path |
| `frame:30:scene_output:metadata` | `ok` | scene output path |
| `frame:30:scene_output:validation` | `ok` | scene output path |
| `frame:30:metadata_schema` | `ok` | metadata schema |
| `frame:30:validation_schema` | `ok` | validation schema |
| `frame:30:validation_status` | `ok` | validation status |
| `frame:30:validation_max_abs` | `ok` | validation max abs |
| `frame:30:validation_mean_abs` | `ok` | validation mean abs |
| `frame:31:status` | `ok` | frame status |
| `frame:31:returncode` | `ok` | process return code |
| `frame:31:elapsed` | `ok` | process elapsed |
| `frame:31:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0031_stdout.log |
| `frame:31:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0031_stderr.log |
| `frame:31:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0031_backend_process_result.json |
| `frame:31:result_schema` | `ok` | result schema |
| `frame:31:result_status` | `ok` | result status |
| `frame:31:result_max_abs` | `ok` | result max abs |
| `frame:31:result_mean_abs` | `ok` | result mean abs |
| `frame:31:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0031.png |
| `frame:31:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0031.json |
| `frame:31:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0031.json |
| `frame:31:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0031_backend_process_stub.png |
| `frame:31:max_abs` | `ok` | max abs diff |
| `frame:31:mean_abs` | `ok` | mean abs diff |
| `frame:31:reference_hash` | `ok` | reference hash |
| `frame:31:result_output_match` | `ok` | result output matches frame |
| `frame:31:target_match` | `ok` | output path matches adapter |
| `frame:31:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0031_backend_scene.json |
| `frame:31:scene_schema` | `ok` | scene schema |
| `frame:31:scene_match` | `ok` | scene path matches adapter |
| `frame:31:scene_output:image` | `ok` | scene output path |
| `frame:31:scene_output:metadata` | `ok` | scene output path |
| `frame:31:scene_output:validation` | `ok` | scene output path |
| `frame:31:metadata_schema` | `ok` | metadata schema |
| `frame:31:validation_schema` | `ok` | validation schema |
| `frame:31:validation_status` | `ok` | validation status |
| `frame:31:validation_max_abs` | `ok` | validation max abs |
| `frame:31:validation_mean_abs` | `ok` | validation mean abs |
| `frame:32:status` | `ok` | frame status |
| `frame:32:returncode` | `ok` | process return code |
| `frame:32:elapsed` | `ok` | process elapsed |
| `frame:32:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0032_stdout.log |
| `frame:32:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0032_stderr.log |
| `frame:32:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0032_backend_process_result.json |
| `frame:32:result_schema` | `ok` | result schema |
| `frame:32:result_status` | `ok` | result status |
| `frame:32:result_max_abs` | `ok` | result max abs |
| `frame:32:result_mean_abs` | `ok` | result mean abs |
| `frame:32:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0032.png |
| `frame:32:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0032.json |
| `frame:32:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0032.json |
| `frame:32:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0032_backend_process_stub.png |
| `frame:32:max_abs` | `ok` | max abs diff |
| `frame:32:mean_abs` | `ok` | mean abs diff |
| `frame:32:reference_hash` | `ok` | reference hash |
| `frame:32:result_output_match` | `ok` | result output matches frame |
| `frame:32:target_match` | `ok` | output path matches adapter |
| `frame:32:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0032_backend_scene.json |
| `frame:32:scene_schema` | `ok` | scene schema |
| `frame:32:scene_match` | `ok` | scene path matches adapter |
| `frame:32:scene_output:image` | `ok` | scene output path |
| `frame:32:scene_output:metadata` | `ok` | scene output path |
| `frame:32:scene_output:validation` | `ok` | scene output path |
| `frame:32:metadata_schema` | `ok` | metadata schema |
| `frame:32:validation_schema` | `ok` | validation schema |
| `frame:32:validation_status` | `ok` | validation status |
| `frame:32:validation_max_abs` | `ok` | validation max abs |
| `frame:32:validation_mean_abs` | `ok` | validation mean abs |
| `frame:33:status` | `ok` | frame status |
| `frame:33:returncode` | `ok` | process return code |
| `frame:33:elapsed` | `ok` | process elapsed |
| `frame:33:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0033_stdout.log |
| `frame:33:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0033_stderr.log |
| `frame:33:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0033_backend_process_result.json |
| `frame:33:result_schema` | `ok` | result schema |
| `frame:33:result_status` | `ok` | result status |
| `frame:33:result_max_abs` | `ok` | result max abs |
| `frame:33:result_mean_abs` | `ok` | result mean abs |
| `frame:33:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0033.png |
| `frame:33:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0033.json |
| `frame:33:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0033.json |
| `frame:33:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0033_backend_process_stub.png |
| `frame:33:max_abs` | `ok` | max abs diff |
| `frame:33:mean_abs` | `ok` | mean abs diff |
| `frame:33:reference_hash` | `ok` | reference hash |
| `frame:33:result_output_match` | `ok` | result output matches frame |
| `frame:33:target_match` | `ok` | output path matches adapter |
| `frame:33:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0033_backend_scene.json |
| `frame:33:scene_schema` | `ok` | scene schema |
| `frame:33:scene_match` | `ok` | scene path matches adapter |
| `frame:33:scene_output:image` | `ok` | scene output path |
| `frame:33:scene_output:metadata` | `ok` | scene output path |
| `frame:33:scene_output:validation` | `ok` | scene output path |
| `frame:33:metadata_schema` | `ok` | metadata schema |
| `frame:33:validation_schema` | `ok` | validation schema |
| `frame:33:validation_status` | `ok` | validation status |
| `frame:33:validation_max_abs` | `ok` | validation max abs |
| `frame:33:validation_mean_abs` | `ok` | validation mean abs |
| `frame:34:status` | `ok` | frame status |
| `frame:34:returncode` | `ok` | process return code |
| `frame:34:elapsed` | `ok` | process elapsed |
| `frame:34:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0034_stdout.log |
| `frame:34:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0034_stderr.log |
| `frame:34:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0034_backend_process_result.json |
| `frame:34:result_schema` | `ok` | result schema |
| `frame:34:result_status` | `ok` | result status |
| `frame:34:result_max_abs` | `ok` | result max abs |
| `frame:34:result_mean_abs` | `ok` | result mean abs |
| `frame:34:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0034.png |
| `frame:34:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0034.json |
| `frame:34:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0034.json |
| `frame:34:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0034_backend_process_stub.png |
| `frame:34:max_abs` | `ok` | max abs diff |
| `frame:34:mean_abs` | `ok` | mean abs diff |
| `frame:34:reference_hash` | `ok` | reference hash |
| `frame:34:result_output_match` | `ok` | result output matches frame |
| `frame:34:target_match` | `ok` | output path matches adapter |
| `frame:34:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0034_backend_scene.json |
| `frame:34:scene_schema` | `ok` | scene schema |
| `frame:34:scene_match` | `ok` | scene path matches adapter |
| `frame:34:scene_output:image` | `ok` | scene output path |
| `frame:34:scene_output:metadata` | `ok` | scene output path |
| `frame:34:scene_output:validation` | `ok` | scene output path |
| `frame:34:metadata_schema` | `ok` | metadata schema |
| `frame:34:validation_schema` | `ok` | validation schema |
| `frame:34:validation_status` | `ok` | validation status |
| `frame:34:validation_max_abs` | `ok` | validation max abs |
| `frame:34:validation_mean_abs` | `ok` | validation mean abs |
| `frame:35:status` | `ok` | frame status |
| `frame:35:returncode` | `ok` | process return code |
| `frame:35:elapsed` | `ok` | process elapsed |
| `frame:35:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0035_stdout.log |
| `frame:35:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0035_stderr.log |
| `frame:35:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0035_backend_process_result.json |
| `frame:35:result_schema` | `ok` | result schema |
| `frame:35:result_status` | `ok` | result status |
| `frame:35:result_max_abs` | `ok` | result max abs |
| `frame:35:result_mean_abs` | `ok` | result mean abs |
| `frame:35:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0035.png |
| `frame:35:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0035.json |
| `frame:35:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0035.json |
| `frame:35:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0035_backend_process_stub.png |
| `frame:35:max_abs` | `ok` | max abs diff |
| `frame:35:mean_abs` | `ok` | mean abs diff |
| `frame:35:reference_hash` | `ok` | reference hash |
| `frame:35:result_output_match` | `ok` | result output matches frame |
| `frame:35:target_match` | `ok` | output path matches adapter |
| `frame:35:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0035_backend_scene.json |
| `frame:35:scene_schema` | `ok` | scene schema |
| `frame:35:scene_match` | `ok` | scene path matches adapter |
| `frame:35:scene_output:image` | `ok` | scene output path |
| `frame:35:scene_output:metadata` | `ok` | scene output path |
| `frame:35:scene_output:validation` | `ok` | scene output path |
| `frame:35:metadata_schema` | `ok` | metadata schema |
| `frame:35:validation_schema` | `ok` | validation schema |
| `frame:35:validation_status` | `ok` | validation status |
| `frame:35:validation_max_abs` | `ok` | validation max abs |
| `frame:35:validation_mean_abs` | `ok` | validation mean abs |
| `frame:36:status` | `ok` | frame status |
| `frame:36:returncode` | `ok` | process return code |
| `frame:36:elapsed` | `ok` | process elapsed |
| `frame:36:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0036_stdout.log |
| `frame:36:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0036_stderr.log |
| `frame:36:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0036_backend_process_result.json |
| `frame:36:result_schema` | `ok` | result schema |
| `frame:36:result_status` | `ok` | result status |
| `frame:36:result_max_abs` | `ok` | result max abs |
| `frame:36:result_mean_abs` | `ok` | result mean abs |
| `frame:36:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0036.png |
| `frame:36:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0036.json |
| `frame:36:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0036.json |
| `frame:36:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0036_backend_process_stub.png |
| `frame:36:max_abs` | `ok` | max abs diff |
| `frame:36:mean_abs` | `ok` | mean abs diff |
| `frame:36:reference_hash` | `ok` | reference hash |
| `frame:36:result_output_match` | `ok` | result output matches frame |
| `frame:36:target_match` | `ok` | output path matches adapter |
| `frame:36:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0036_backend_scene.json |
| `frame:36:scene_schema` | `ok` | scene schema |
| `frame:36:scene_match` | `ok` | scene path matches adapter |
| `frame:36:scene_output:image` | `ok` | scene output path |
| `frame:36:scene_output:metadata` | `ok` | scene output path |
| `frame:36:scene_output:validation` | `ok` | scene output path |
| `frame:36:metadata_schema` | `ok` | metadata schema |
| `frame:36:validation_schema` | `ok` | validation schema |
| `frame:36:validation_status` | `ok` | validation status |
| `frame:36:validation_max_abs` | `ok` | validation max abs |
| `frame:36:validation_mean_abs` | `ok` | validation mean abs |
| `frame:37:status` | `ok` | frame status |
| `frame:37:returncode` | `ok` | process return code |
| `frame:37:elapsed` | `ok` | process elapsed |
| `frame:37:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0037_stdout.log |
| `frame:37:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0037_stderr.log |
| `frame:37:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0037_backend_process_result.json |
| `frame:37:result_schema` | `ok` | result schema |
| `frame:37:result_status` | `ok` | result status |
| `frame:37:result_max_abs` | `ok` | result max abs |
| `frame:37:result_mean_abs` | `ok` | result mean abs |
| `frame:37:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0037.png |
| `frame:37:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0037.json |
| `frame:37:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0037.json |
| `frame:37:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0037_backend_process_stub.png |
| `frame:37:max_abs` | `ok` | max abs diff |
| `frame:37:mean_abs` | `ok` | mean abs diff |
| `frame:37:reference_hash` | `ok` | reference hash |
| `frame:37:result_output_match` | `ok` | result output matches frame |
| `frame:37:target_match` | `ok` | output path matches adapter |
| `frame:37:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0037_backend_scene.json |
| `frame:37:scene_schema` | `ok` | scene schema |
| `frame:37:scene_match` | `ok` | scene path matches adapter |
| `frame:37:scene_output:image` | `ok` | scene output path |
| `frame:37:scene_output:metadata` | `ok` | scene output path |
| `frame:37:scene_output:validation` | `ok` | scene output path |
| `frame:37:metadata_schema` | `ok` | metadata schema |
| `frame:37:validation_schema` | `ok` | validation schema |
| `frame:37:validation_status` | `ok` | validation status |
| `frame:37:validation_max_abs` | `ok` | validation max abs |
| `frame:37:validation_mean_abs` | `ok` | validation mean abs |
| `frame:38:status` | `ok` | frame status |
| `frame:38:returncode` | `ok` | process return code |
| `frame:38:elapsed` | `ok` | process elapsed |
| `frame:38:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0038_stdout.log |
| `frame:38:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0038_stderr.log |
| `frame:38:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0038_backend_process_result.json |
| `frame:38:result_schema` | `ok` | result schema |
| `frame:38:result_status` | `ok` | result status |
| `frame:38:result_max_abs` | `ok` | result max abs |
| `frame:38:result_mean_abs` | `ok` | result mean abs |
| `frame:38:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0038.png |
| `frame:38:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0038.json |
| `frame:38:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0038.json |
| `frame:38:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0038_backend_process_stub.png |
| `frame:38:max_abs` | `ok` | max abs diff |
| `frame:38:mean_abs` | `ok` | mean abs diff |
| `frame:38:reference_hash` | `ok` | reference hash |
| `frame:38:result_output_match` | `ok` | result output matches frame |
| `frame:38:target_match` | `ok` | output path matches adapter |
| `frame:38:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0038_backend_scene.json |
| `frame:38:scene_schema` | `ok` | scene schema |
| `frame:38:scene_match` | `ok` | scene path matches adapter |
| `frame:38:scene_output:image` | `ok` | scene output path |
| `frame:38:scene_output:metadata` | `ok` | scene output path |
| `frame:38:scene_output:validation` | `ok` | scene output path |
| `frame:38:metadata_schema` | `ok` | metadata schema |
| `frame:38:validation_schema` | `ok` | validation schema |
| `frame:38:validation_status` | `ok` | validation status |
| `frame:38:validation_max_abs` | `ok` | validation max abs |
| `frame:38:validation_mean_abs` | `ok` | validation mean abs |
| `frame:39:status` | `ok` | frame status |
| `frame:39:returncode` | `ok` | process return code |
| `frame:39:elapsed` | `ok` | process elapsed |
| `frame:39:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0039_stdout.log |
| `frame:39:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0039_stderr.log |
| `frame:39:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0039_backend_process_result.json |
| `frame:39:result_schema` | `ok` | result schema |
| `frame:39:result_status` | `ok` | result status |
| `frame:39:result_max_abs` | `ok` | result max abs |
| `frame:39:result_mean_abs` | `ok` | result mean abs |
| `frame:39:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0039.png |
| `frame:39:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0039.json |
| `frame:39:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0039.json |
| `frame:39:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0039_backend_process_stub.png |
| `frame:39:max_abs` | `ok` | max abs diff |
| `frame:39:mean_abs` | `ok` | mean abs diff |
| `frame:39:reference_hash` | `ok` | reference hash |
| `frame:39:result_output_match` | `ok` | result output matches frame |
| `frame:39:target_match` | `ok` | output path matches adapter |
| `frame:39:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0039_backend_scene.json |
| `frame:39:scene_schema` | `ok` | scene schema |
| `frame:39:scene_match` | `ok` | scene path matches adapter |
| `frame:39:scene_output:image` | `ok` | scene output path |
| `frame:39:scene_output:metadata` | `ok` | scene output path |
| `frame:39:scene_output:validation` | `ok` | scene output path |
| `frame:39:metadata_schema` | `ok` | metadata schema |
| `frame:39:validation_schema` | `ok` | validation schema |
| `frame:39:validation_status` | `ok` | validation status |
| `frame:39:validation_max_abs` | `ok` | validation max abs |
| `frame:39:validation_mean_abs` | `ok` | validation mean abs |
| `frame:40:status` | `ok` | frame status |
| `frame:40:returncode` | `ok` | process return code |
| `frame:40:elapsed` | `ok` | process elapsed |
| `frame:40:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0040_stdout.log |
| `frame:40:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0040_stderr.log |
| `frame:40:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0040_backend_process_result.json |
| `frame:40:result_schema` | `ok` | result schema |
| `frame:40:result_status` | `ok` | result status |
| `frame:40:result_max_abs` | `ok` | result max abs |
| `frame:40:result_mean_abs` | `ok` | result mean abs |
| `frame:40:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0040.png |
| `frame:40:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0040.json |
| `frame:40:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0040.json |
| `frame:40:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0040_backend_process_stub.png |
| `frame:40:max_abs` | `ok` | max abs diff |
| `frame:40:mean_abs` | `ok` | mean abs diff |
| `frame:40:reference_hash` | `ok` | reference hash |
| `frame:40:result_output_match` | `ok` | result output matches frame |
| `frame:40:target_match` | `ok` | output path matches adapter |
| `frame:40:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0040_backend_scene.json |
| `frame:40:scene_schema` | `ok` | scene schema |
| `frame:40:scene_match` | `ok` | scene path matches adapter |
| `frame:40:scene_output:image` | `ok` | scene output path |
| `frame:40:scene_output:metadata` | `ok` | scene output path |
| `frame:40:scene_output:validation` | `ok` | scene output path |
| `frame:40:metadata_schema` | `ok` | metadata schema |
| `frame:40:validation_schema` | `ok` | validation schema |
| `frame:40:validation_status` | `ok` | validation status |
| `frame:40:validation_max_abs` | `ok` | validation max abs |
| `frame:40:validation_mean_abs` | `ok` | validation mean abs |
| `frame:41:status` | `ok` | frame status |
| `frame:41:returncode` | `ok` | process return code |
| `frame:41:elapsed` | `ok` | process elapsed |
| `frame:41:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0041_stdout.log |
| `frame:41:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0041_stderr.log |
| `frame:41:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0041_backend_process_result.json |
| `frame:41:result_schema` | `ok` | result schema |
| `frame:41:result_status` | `ok` | result status |
| `frame:41:result_max_abs` | `ok` | result max abs |
| `frame:41:result_mean_abs` | `ok` | result mean abs |
| `frame:41:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0041.png |
| `frame:41:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0041.json |
| `frame:41:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0041.json |
| `frame:41:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0041_backend_process_stub.png |
| `frame:41:max_abs` | `ok` | max abs diff |
| `frame:41:mean_abs` | `ok` | mean abs diff |
| `frame:41:reference_hash` | `ok` | reference hash |
| `frame:41:result_output_match` | `ok` | result output matches frame |
| `frame:41:target_match` | `ok` | output path matches adapter |
| `frame:41:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0041_backend_scene.json |
| `frame:41:scene_schema` | `ok` | scene schema |
| `frame:41:scene_match` | `ok` | scene path matches adapter |
| `frame:41:scene_output:image` | `ok` | scene output path |
| `frame:41:scene_output:metadata` | `ok` | scene output path |
| `frame:41:scene_output:validation` | `ok` | scene output path |
| `frame:41:metadata_schema` | `ok` | metadata schema |
| `frame:41:validation_schema` | `ok` | validation schema |
| `frame:41:validation_status` | `ok` | validation status |
| `frame:41:validation_max_abs` | `ok` | validation max abs |
| `frame:41:validation_mean_abs` | `ok` | validation mean abs |
| `frame:42:status` | `ok` | frame status |
| `frame:42:returncode` | `ok` | process return code |
| `frame:42:elapsed` | `ok` | process elapsed |
| `frame:42:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0042_stdout.log |
| `frame:42:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0042_stderr.log |
| `frame:42:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0042_backend_process_result.json |
| `frame:42:result_schema` | `ok` | result schema |
| `frame:42:result_status` | `ok` | result status |
| `frame:42:result_max_abs` | `ok` | result max abs |
| `frame:42:result_mean_abs` | `ok` | result mean abs |
| `frame:42:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0042.png |
| `frame:42:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0042.json |
| `frame:42:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0042.json |
| `frame:42:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0042_backend_process_stub.png |
| `frame:42:max_abs` | `ok` | max abs diff |
| `frame:42:mean_abs` | `ok` | mean abs diff |
| `frame:42:reference_hash` | `ok` | reference hash |
| `frame:42:result_output_match` | `ok` | result output matches frame |
| `frame:42:target_match` | `ok` | output path matches adapter |
| `frame:42:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0042_backend_scene.json |
| `frame:42:scene_schema` | `ok` | scene schema |
| `frame:42:scene_match` | `ok` | scene path matches adapter |
| `frame:42:scene_output:image` | `ok` | scene output path |
| `frame:42:scene_output:metadata` | `ok` | scene output path |
| `frame:42:scene_output:validation` | `ok` | scene output path |
| `frame:42:metadata_schema` | `ok` | metadata schema |
| `frame:42:validation_schema` | `ok` | validation schema |
| `frame:42:validation_status` | `ok` | validation status |
| `frame:42:validation_max_abs` | `ok` | validation max abs |
| `frame:42:validation_mean_abs` | `ok` | validation mean abs |
| `frame:43:status` | `ok` | frame status |
| `frame:43:returncode` | `ok` | process return code |
| `frame:43:elapsed` | `ok` | process elapsed |
| `frame:43:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0043_stdout.log |
| `frame:43:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0043_stderr.log |
| `frame:43:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0043_backend_process_result.json |
| `frame:43:result_schema` | `ok` | result schema |
| `frame:43:result_status` | `ok` | result status |
| `frame:43:result_max_abs` | `ok` | result max abs |
| `frame:43:result_mean_abs` | `ok` | result mean abs |
| `frame:43:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0043.png |
| `frame:43:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0043.json |
| `frame:43:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0043.json |
| `frame:43:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0043_backend_process_stub.png |
| `frame:43:max_abs` | `ok` | max abs diff |
| `frame:43:mean_abs` | `ok` | mean abs diff |
| `frame:43:reference_hash` | `ok` | reference hash |
| `frame:43:result_output_match` | `ok` | result output matches frame |
| `frame:43:target_match` | `ok` | output path matches adapter |
| `frame:43:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0043_backend_scene.json |
| `frame:43:scene_schema` | `ok` | scene schema |
| `frame:43:scene_match` | `ok` | scene path matches adapter |
| `frame:43:scene_output:image` | `ok` | scene output path |
| `frame:43:scene_output:metadata` | `ok` | scene output path |
| `frame:43:scene_output:validation` | `ok` | scene output path |
| `frame:43:metadata_schema` | `ok` | metadata schema |
| `frame:43:validation_schema` | `ok` | validation schema |
| `frame:43:validation_status` | `ok` | validation status |
| `frame:43:validation_max_abs` | `ok` | validation max abs |
| `frame:43:validation_mean_abs` | `ok` | validation mean abs |
| `frame:44:status` | `ok` | frame status |
| `frame:44:returncode` | `ok` | process return code |
| `frame:44:elapsed` | `ok` | process elapsed |
| `frame:44:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0044_stdout.log |
| `frame:44:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0044_stderr.log |
| `frame:44:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0044_backend_process_result.json |
| `frame:44:result_schema` | `ok` | result schema |
| `frame:44:result_status` | `ok` | result status |
| `frame:44:result_max_abs` | `ok` | result max abs |
| `frame:44:result_mean_abs` | `ok` | result mean abs |
| `frame:44:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0044.png |
| `frame:44:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0044.json |
| `frame:44:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0044.json |
| `frame:44:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0044_backend_process_stub.png |
| `frame:44:max_abs` | `ok` | max abs diff |
| `frame:44:mean_abs` | `ok` | mean abs diff |
| `frame:44:reference_hash` | `ok` | reference hash |
| `frame:44:result_output_match` | `ok` | result output matches frame |
| `frame:44:target_match` | `ok` | output path matches adapter |
| `frame:44:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0044_backend_scene.json |
| `frame:44:scene_schema` | `ok` | scene schema |
| `frame:44:scene_match` | `ok` | scene path matches adapter |
| `frame:44:scene_output:image` | `ok` | scene output path |
| `frame:44:scene_output:metadata` | `ok` | scene output path |
| `frame:44:scene_output:validation` | `ok` | scene output path |
| `frame:44:metadata_schema` | `ok` | metadata schema |
| `frame:44:validation_schema` | `ok` | validation schema |
| `frame:44:validation_status` | `ok` | validation status |
| `frame:44:validation_max_abs` | `ok` | validation max abs |
| `frame:44:validation_mean_abs` | `ok` | validation mean abs |
| `frame:45:status` | `ok` | frame status |
| `frame:45:returncode` | `ok` | process return code |
| `frame:45:elapsed` | `ok` | process elapsed |
| `frame:45:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0045_stdout.log |
| `frame:45:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0045_stderr.log |
| `frame:45:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0045_backend_process_result.json |
| `frame:45:result_schema` | `ok` | result schema |
| `frame:45:result_status` | `ok` | result status |
| `frame:45:result_max_abs` | `ok` | result max abs |
| `frame:45:result_mean_abs` | `ok` | result mean abs |
| `frame:45:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0045.png |
| `frame:45:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0045.json |
| `frame:45:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0045.json |
| `frame:45:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0045_backend_process_stub.png |
| `frame:45:max_abs` | `ok` | max abs diff |
| `frame:45:mean_abs` | `ok` | mean abs diff |
| `frame:45:reference_hash` | `ok` | reference hash |
| `frame:45:result_output_match` | `ok` | result output matches frame |
| `frame:45:target_match` | `ok` | output path matches adapter |
| `frame:45:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0045_backend_scene.json |
| `frame:45:scene_schema` | `ok` | scene schema |
| `frame:45:scene_match` | `ok` | scene path matches adapter |
| `frame:45:scene_output:image` | `ok` | scene output path |
| `frame:45:scene_output:metadata` | `ok` | scene output path |
| `frame:45:scene_output:validation` | `ok` | scene output path |
| `frame:45:metadata_schema` | `ok` | metadata schema |
| `frame:45:validation_schema` | `ok` | validation schema |
| `frame:45:validation_status` | `ok` | validation status |
| `frame:45:validation_max_abs` | `ok` | validation max abs |
| `frame:45:validation_mean_abs` | `ok` | validation mean abs |
| `frame:46:status` | `ok` | frame status |
| `frame:46:returncode` | `ok` | process return code |
| `frame:46:elapsed` | `ok` | process elapsed |
| `frame:46:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0046_stdout.log |
| `frame:46:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0046_stderr.log |
| `frame:46:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0046_backend_process_result.json |
| `frame:46:result_schema` | `ok` | result schema |
| `frame:46:result_status` | `ok` | result status |
| `frame:46:result_max_abs` | `ok` | result max abs |
| `frame:46:result_mean_abs` | `ok` | result mean abs |
| `frame:46:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0046.png |
| `frame:46:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0046.json |
| `frame:46:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0046.json |
| `frame:46:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0046_backend_process_stub.png |
| `frame:46:max_abs` | `ok` | max abs diff |
| `frame:46:mean_abs` | `ok` | mean abs diff |
| `frame:46:reference_hash` | `ok` | reference hash |
| `frame:46:result_output_match` | `ok` | result output matches frame |
| `frame:46:target_match` | `ok` | output path matches adapter |
| `frame:46:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0046_backend_scene.json |
| `frame:46:scene_schema` | `ok` | scene schema |
| `frame:46:scene_match` | `ok` | scene path matches adapter |
| `frame:46:scene_output:image` | `ok` | scene output path |
| `frame:46:scene_output:metadata` | `ok` | scene output path |
| `frame:46:scene_output:validation` | `ok` | scene output path |
| `frame:46:metadata_schema` | `ok` | metadata schema |
| `frame:46:validation_schema` | `ok` | validation schema |
| `frame:46:validation_status` | `ok` | validation status |
| `frame:46:validation_max_abs` | `ok` | validation max abs |
| `frame:46:validation_mean_abs` | `ok` | validation mean abs |
| `frame:47:status` | `ok` | frame status |
| `frame:47:returncode` | `ok` | process return code |
| `frame:47:elapsed` | `ok` | process elapsed |
| `frame:47:stdout` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0047_stdout.log |
| `frame:47:stderr` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/logs/frame_0047_stderr.log |
| `frame:47:result_json` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/results/frame_0047_backend_process_result.json |
| `frame:47:result_schema` | `ok` | result schema |
| `frame:47:result_status` | `ok` | result status |
| `frame:47:result_max_abs` | `ok` | result max abs |
| `frame:47:result_mean_abs` | `ok` | result mean abs |
| `frame:47:output` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0047.png |
| `frame:47:metadata` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/metadata/frame_0047.json |
| `frame:47:validation` | `ok` | build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/validation/frame_0047.json |
| `frame:47:strip` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/strips/frame_0047_backend_process_stub.png |
| `frame:47:max_abs` | `ok` | max abs diff |
| `frame:47:mean_abs` | `ok` | mean abs diff |
| `frame:47:reference_hash` | `ok` | reference hash |
| `frame:47:result_output_match` | `ok` | result output matches frame |
| `frame:47:target_match` | `ok` | output path matches adapter |
| `frame:47:scene` | `ok` | build/shots/s560_mitsuba_s515_full48_t4_backend_adapter/scenes/frame_0047_backend_scene.json |
| `frame:47:scene_schema` | `ok` | scene schema |
| `frame:47:scene_match` | `ok` | scene path matches adapter |
| `frame:47:scene_output:image` | `ok` | scene output path |
| `frame:47:scene_output:metadata` | `ok` | scene output path |
| `frame:47:scene_output:validation` | `ok` | scene output path |
| `frame:47:metadata_schema` | `ok` | metadata schema |
| `frame:47:validation_schema` | `ok` | validation schema |
| `frame:47:validation_status` | `ok` | validation status |
| `frame:47:validation_max_abs` | `ok` | validation max abs |
| `frame:47:validation_mean_abs` | `ok` | validation mean abs |
| `gallery:index` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/index.html |
| `gallery:asset:Backend Process Stub GIF` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/shot.gif |
| `gallery:asset:Backend Process Stub Strip GIF` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strips.gif |
| `gallery:asset:Backend Process Stub Keyframe 1` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_00.png |
| `gallery:asset:Backend Process Stub Strip 1` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_00.png |
| `gallery:asset:Backend Process Stub Keyframe 2` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_01.png |
| `gallery:asset:Backend Process Stub Strip 2` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_01.png |
| `gallery:asset:Backend Process Stub Keyframe 3` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_02.png |
| `gallery:asset:Backend Process Stub Strip 3` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_02.png |
| `gallery:asset:Backend Process Stub Keyframe 4` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_03.png |
| `gallery:asset:Backend Process Stub Strip 4` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_03.png |
| `gallery:asset:Backend Process Stub Keyframe 5` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_04.png |
| `gallery:asset:Backend Process Stub Strip 5` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_04.png |
| `gallery:asset:Backend Process Stub Keyframe 6` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/keyframe_05.png |
| `gallery:asset:Backend Process Stub Strip 6` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_strip_05.png |
| `gallery:process_stub_gif` | `ok` | process stub GIF present |
| `gallery:process_stub_strip_gif` | `ok` | process stub strip GIF present |
| `gallery:metadata:Backend Process Stub Summary` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_process_stub_summary.json |
| `gallery:metadata:Backend Adapter Manifest` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/backend_adapter_manifest.json |
| `gallery:metadata:Backend Process Stub Script` | `ok` | build/shots/s562_mitsuba_s515_full48_t4_backend_process_stub/gallery/assets/mitsuba_low_frequency_backend_stub.py |
