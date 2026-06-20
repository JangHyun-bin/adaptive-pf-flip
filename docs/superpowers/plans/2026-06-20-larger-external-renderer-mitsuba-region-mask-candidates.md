# S373 Larger External Renderer Mitsuba Region Mask Candidates

## Goal

Diagnose which target-free masks can explain the two remaining hard regions:
target highlights and target-dark secondary detail. This step does not change a
render. It selects the next renderer-native evidence path.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Depth-aware composite metadata:
  `build/shots/s341_mitsuba_depth_aware_composite_c3/depth_aware_secondary_composite_summary.json`

## Work

- Add `tools/analyze_mitsuba_region_mask_candidates.py`.
- Evaluate source-luma, secondary-alpha, native-weight, and combined masks
  against diagnostic target labels.
- Emit aggregate precision/recall/F1, CSV, and a mask-strip gallery.
- Publish the gallery through a Cloudflare quick tunnel.

## Results

- Best target-highlight mask: `source_highlight_120`.
  - Precision: `0.997656`
  - Recall: `0.800290`
  - F1: `0.888140`
- Best target-dark-secondary mask: `secondary_source_luma_20_105`.
  - Precision: `0.086989`
  - Recall: `0.965468`
  - F1: `0.159599`
- Highlight selection is well explained by source luminance, which supports the
  S372 SR6 direction.
- Dark-secondary selection is not well explained by the current alpha/luma/native
  weight evidence. The available masks have high recall only because they are
  too broad.

## Artifacts

- Mask candidate report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_region_mask_candidates_sv1_s373.md`
- Public quick-tunnel review:
  `https://bind-apps-continent-francisco.trycloudflare.com/index.html`

## Next

Do not keep strengthening broad screen-space darkening. The next useful step is
to add a richer secondary-dark evidence source: projected secondary channel
metadata, local layer density/shape, depth ordering, or surface/normal contact
signals.
