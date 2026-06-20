# S501 Mitsuba Low Frequency Renderer Job Dry Run Publish Decision

Generated UTC: `2026-06-20T18:54:00Z`

## Decision

Promote S501 as the current public execution proof for the Mitsuba low-frequency renderer job manifest path.

S500 proved the S499 job manifest can execute locally from the manifest alone. S501 exposes that dry-run gallery through a verified Cloudflare quick tunnel so the execution proof is inspectable outside the local machine.

## Evidence

- Publish report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_renderer_job_dry_run_publish_s501.md`
- Publish manifest: `build/shots/s501_mitsuba_low_frequency_renderer_job_dry_run_publish/publish_manifest.json`
- Source gallery: `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/index.html`
- Public URL: `https://chassis-yorkshire-email-retirement.trycloudflare.com`

## Key Checks

- Publish status: `running`
- Local index HTTP: `200`
- Local GIF HTTP: `200`
- Public index HTTP: `200`
- Public GIF HTTP: `200`
- Public index bytes: `3298`
- Public GIF bytes: `1191221`
- Public index contains S500 title: `true`
- HTTP server PID: `57872`
- Cloudflared PID: `156448`

## Interpretation

S501 is the visible proof for the production-job path, not just the earlier runtime gallery. The public page shows the dry-run execution output generated from `renderer_job_manifest.json`, which is closer to the final renderer/export workflow than the S496 static import preview.

The running tunnel remains a temporary quick-tunnel endpoint. The durable evidence is the publish manifest and report, plus the S500 dry-run summary and validation.

## Next Step

S502 should add a backend-adapter skeleton that consumes `renderer_job_manifest.json`, emits backend-specific scene/job descriptors, and preserves the S500 output/validation contract.
