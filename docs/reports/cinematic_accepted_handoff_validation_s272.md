# S271 Accepted Bridge Handoff Manifest Validation

Generated UTC: `2026-06-19T19:43:55.838355+00:00`
Validation JSON: `build/shots/s272_handoff_validation/validation.json`
Status: `passed`
Accepted preset: `dam_break_water_mesh_smoothing`
Checks: `23`
Failures: `0`
Warnings: `0`

## Checks

| Check | Status | Detail | Path |
| --- | --- | --- | --- |
| schema | `passed` | schema check | `` |
| version | `passed` | version check | `` |
| accepted_preset | `passed` | accepted preset recorded | `` |
| source:preset_config | `passed` | sha256 matched | `configs/cinematic_presets.json` |
| source:publish_manifest | `passed` | sha256 matched | `build/shots/s270_s269_gallery_publish/publish_manifest.json` |
| source:render_data_summary | `passed` | sha256 matched | `build/shots/s168_water_depth_foreground_separation/converted/render_data_summary.json` |
| source:review_package | `passed` | sha256 matched | `build/shots/s270_accepted_review_package/review_package.json` |
| source:sequence | `passed` | sha256 matched | `build/shots/s205_surface_quality_annotation/converted/sequence.json` |
| artifact:Shot GIF | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/shot.gif` |
| artifact:S264 Accepted vs S269 Secondary Dewarm Accepted | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/comparison.png` |
| artifact:Keyframe 1 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_00.png` |
| artifact:Keyframe 2 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_01.png` |
| artifact:Keyframe 3 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_02.png` |
| artifact:Keyframe 4 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_03.png` |
| artifact:Keyframe 5 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_04.png` |
| artifact:Keyframe 6 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_05.png` |
| artifact:Keyframe 7 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_06.png` |
| artifact:Keyframe 8 | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/keyframe_07.png` |
| artifact:Bridge summary | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/bridge_summary.json` |
| artifact:Comparison summary | `passed` | sha256 matched | `build/shots/s269_secondary_dewarm_acceptance/gallery/assets/comparison_summary.json` |
| publish_status | `passed` | publish manifest status | `` |
| public:index | `passed` | HTTP 200 | `https://rfc-empirical-match-outstanding.trycloudflare.com/index.html` |
| public:shot_gif | `passed` | HTTP 200, 5118717 bytes | `https://rfc-empirical-match-outstanding.trycloudflare.com/assets/shot.gif` |

## Next

Use this validation before treating the handoff manifest as an external-render or large-benchmark baseline.
