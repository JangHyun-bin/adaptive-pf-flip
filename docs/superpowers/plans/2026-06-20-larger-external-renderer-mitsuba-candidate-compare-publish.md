# Larger External Renderer: Mitsuba Candidate Compare Publish

Status: complete

## Goal

Create and publish a side-by-side review page for the current renderer decision
point: target reference, C1E bridge, SS1 native baseline, S400 KL1, and S401
CR21 profile.

## Artifact

- Compare gallery: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/gallery/index.html`
- Compare summary: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21/candidate_compare_gallery.json`
- Compare report: `docs/reports/cinematic_larger_external_renderer_mitsuba_candidate_compare_ss1_kl1_cr21_s403.md`
- Publish manifest: `build/shots/s403_mitsuba_candidate_compare_ss1_kl1_cr21_publish/publish_manifest.json`
- Publish report: `docs/reports/cinematic_larger_external_renderer_mitsuba_candidate_compare_ss1_kl1_cr21_publish_s403.md`
- Public URL: `https://scholar-page-wednesday-soviet.trycloudflare.com/index.html`

## Validation

- Compare gallery generation: `ready`
- Frames: `8`
- Columns: `5`
- Columns: `Target`, `C1E`, `SS1_Native`, `KL1`, `S401_CR21_Profile`
- Strip/GIF dimensions: `4824 x 574`
- GIF frames: `8`
- Local `index.html`: HTTP `200`
- Local `assets/comparison.gif`: HTTP `200`
- Public `index.html`: HTTP `200`
- Public `assets/comparison.gif`: HTTP `200`

## Decision

Use S403 as the current renderer decision board. Broad scalar water/light
tuning did not beat SS1, while CR21 remains the strongest target-free visual
response profile. The next useful renderer branch should either move CR21-like
source response into a more renderer-native material/light model or build a
new native secondary/water transport pass that reduces the remaining source and
secondary mismatch without target-image input.

## Notes

The quick-tunnel URL is session-scoped. Refresh the publish step if the recorded
HTTP server or `cloudflared` process exits.
