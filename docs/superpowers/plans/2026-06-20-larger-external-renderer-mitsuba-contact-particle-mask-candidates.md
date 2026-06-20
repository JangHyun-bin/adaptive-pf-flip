# S381 Larger External Renderer Mitsuba Contact Particle Mask Candidates

## Goal

Test whether the explicit contact foam and impact ripple particles used by the
Blender bridge can provide a better target-free dark-secondary mask than DS6.

## Inputs

- Target preview:
  `build/shots/s328_mitsuba_renderer_target_preview/renderer_target_preview_summary.json`
- Active SV1-cache composite:
  `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1/secondary_composite_summary.json`
- Active Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Bridge contact/ripple settings:
  `build/shots/s305_larger_external_renderer_job_blender_full48/bridge_summary.json`

## Work

- Add `tools/analyze_mitsuba_contact_particle_masks.py`.
- Reproduce the Blender bridge contact selection:
  - contact foam: foam-channel secondary particles, max/keep-ratio filtered
  - impact ripples: foam/spray secondary particles, max-count filtered
- Project contact ellipses and ripple arcs through the Mitsuba camera.
- Cross contact/ripple masks with secondary alpha and source-luma bands.
- Run a small radius sensitivity sweep.

## Results

- DS6-equivalent baseline:
  `secondary_source_luma_0_75` F1 `0.612175`.
- Default best contact mask:
  `contact_foam_or_ripple_secondary_source_luma_0_85`.
  - Precision: `0.632975`
  - Recall: `0.172661`
  - F1: `0.271314`
- Radius sweep:
  - `r150`: F1 `0.311431`
  - `r250`: F1 `0.359728`
  - `r400`: F1 `0.402618`
- Contact/ripple masks are very weak highlight evidence; best contact highlight
  F1 is `0.005742`.

## Decision

Do not promote contact/ripple masks to a dark-secondary response candidate. They
are physically meaningful, but too local for the current remaining target-dark
secondary region. Even aggressive radius inflation stays below DS6.

## Artifacts

- New tool:
  `tools/analyze_mitsuba_contact_particle_masks.py`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_contact_particle_mask_candidates_sv1_s381.md`
- Main gallery:
  `build/shots/s381_mitsuba_contact_particle_mask_candidates_sv1/gallery/index.html`
- Public quick-tunnel review:
  `https://motivation-asthma-gilbert-gabriel.trycloudflare.com/index.html`

## Next

Stop searching for a better target-free mask in existing secondary/contact
geometry. The next practical visual step is a bounded material/response pass
using the proven DS6 mask, or a renderer AOV export that exposes richer
screen-space shading state.
