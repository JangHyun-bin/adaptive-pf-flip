# Mitsuba Visual Cache AOV Import Bridge

## Goal

Promote the signed-response visual-cache path from a compositor-compatible layer into a renderer/import AOV contract that downstream tools can consume deterministically.

## Current Decision

The current promoted bridge is:

`lsfs_mitsuba_visual_cache_aov_package` -> `tools/apply_mitsuba_visual_cache_aov_package.py` -> `lsfs_mitsuba_secondary_composite`

This path keeps Mitsuba as the base render, stores the bounded signed response as importable AOV PNG channels, reconstructs the composite from AOVs with pixel-exact agreement, and remains compatible with the existing target-gap harness.

## Completed Chain

### S467 Signed Response Layer

- Tool: `tools/build_mitsuba_signed_response_layer.py`
- Reports:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_response_layer_s467.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_response_layer_target_gap_s467.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_response_layer_decision_s467.md`
- Result:
  - Frames: `8`
  - Applied requests: `12`
  - Target-gap mean MAD: `19.10240579989712`
  - Target-gap max MAD: `23.950307355967077`
  - Target-gap max abs gap: `176`

### S468-S471 Visual Cache Bundle And Consumer

- Tools:
  - `tools/build_mitsuba_visual_cache_bundle.py`
  - `tools/validate_mitsuba_visual_cache_bundle.py`
  - `tools/apply_mitsuba_visual_cache_bundle.py`
- Reports:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_bundle_s468.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_bundle_publish_s469.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_bundle_validation_s470.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_bundle_consumer_s471.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_bundle_consumer_target_gap_s471.md`
- Public review:
  - `https://refresh-oscar-values-complex.trycloudflare.com/index.html`
- Result:
  - Bundle frames: `8`
  - Copied files: `77`
  - Missing references: `0`
  - Hash failures: `0`
  - Consumer max pixel diff: `0`
  - Target-gap mean MAD: `19.10240579989712`
  - Target-gap max MAD: `23.950307355967077`
  - Target-gap max abs gap: `176`

### S472-S474 Visual Cache AOV Import

- Tools:
  - `tools/build_mitsuba_visual_cache_aov_package.py`
  - `tools/apply_mitsuba_visual_cache_aov_package.py`
- Reports:
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_aov_package_s472.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_aov_import_package_s473.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_aov_import_consumer_s473.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_aov_import_consumer_target_gap_s473.md`
  - `docs/reports/cinematic_larger_external_renderer_mitsuba_visual_cache_aov_import_publish_s474.md`
- Public review:
  - `https://wanted-simulations-editing-republican.trycloudflare.com/index.html`
- Result:
  - Frames: `8`
  - AOVs per frame: `12`
  - Max response mask coverage: `0.019110725308641975`
  - Max response alpha: `255`
  - Max response luma: `29`
  - AOV import max pixel diff: `0`
  - Target-gap mean MAD: `19.10240579989712`
  - Target-gap max MAD: `23.950307355967077`
  - Target-gap max abs gap: `176`

## AOV Contract

The S473 package exports these channels per frame:

- `base_rgb`
- `target_rgb`
- `composite_rgb`
- `base_luma`
- `target_luma`
- `composite_luma`
- `response_rgb`
- `response_alpha`
- `response_luma`
- `response_mask`
- `target_gap_diff`
- `response_overlay`

The exact reconstruction rule is:

`composite_rgb = clamp(base_rgb + response_rgb)`

The `response_alpha` and `response_mask` channels are import guidance and localization evidence. They are not required for exact reconstruction of the current brighten-only signed response, but they should drive future renderer-native material, light, or volume controls.

## Interpretation

The native residual-patch work proved placement was not the main issue: screen footprints were correct, but visible energy transfer through Mitsuba material/visibility was too weak. The visual-cache path therefore becomes the stable bridge while renderer-native work continues.

This is not the final photoreal renderer. It is a stable interchange layer that makes the current best bounded response reproducible, inspectable, and importable.

## Next

S475 should use the S473 AOV contract as the input to renderer-native control work:

1. Fit a renderer-native material/light/volume response from `response_mask`, `response_luma`, and `target_gap_diff`.
2. Keep the AOV importer as the hard compatibility gate: native candidates should be compared against the S473 imported composite and the target preview.
3. Avoid more discrete emitter patches unless they beat the S473 target-gap and visual review gates.
