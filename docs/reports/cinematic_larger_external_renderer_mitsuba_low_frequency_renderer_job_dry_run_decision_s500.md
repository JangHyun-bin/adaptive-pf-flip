# S500 Mitsuba Low Frequency Renderer Job Dry Run Decision

Generated UTC: `2026-06-20T18:52:00Z`

## Decision

Promote S500 as the execution smoke gate for the Mitsuba low-frequency renderer job manifest.

S499 emitted a production-style job manifest. S500 proves that manifest can be executed directly: the dry-run runner reads `renderer_job_manifest.json`, binds the declared texture inputs, writes the declared output images/metadata/validation files, and matches the accepted reference frames exactly.

## Evidence

- Dry-run report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_renderer_job_dry_run_s500.md`
- Dry-run validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_low_frequency_renderer_job_dry_run_validation_s500.md`
- Dry-run summary: `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/renderer_job_dry_run_summary.json`
- Dry-run validation JSON: `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/renderer_job_dry_run_validation.json`
- Dry-run gallery: `build/shots/s500_mitsuba_low_frequency_renderer_job_dry_run/gallery/index.html`
- Source job: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest.json`

## Key Checks

- Dry-run status: `passed`
- Validation status: `passed`
- Validation checks: `101`
- Validation failures: `0`
- Frames: `8`
- Passed frames: `8`
- Failed frames: `0`
- Missing frames: `0`
- Max abs diff: `0`
- Max mean abs diff: `0.0`
- Output bytes: `2027129`
- Dry-run GIF bytes: `1191221`
- Dry-run strip GIF bytes: `4414531`

## Interpretation

S500 is the first point where the low-frequency correction path is not only packaged or specified, but executed from the production-style job manifest. The output files are written to the manifest-declared paths under `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs`.

This is still a deterministic software dry run, not a native Mitsuba backend call. The next backend integration should preserve this exact input/output/validation shape while replacing the executor internals.

## Next Step

S501 should publish the S500 dry-run gallery as the current execution proof, then S502 should add the first backend-adapter skeleton that consumes the same S499 job manifest without changing the manifest contract.
