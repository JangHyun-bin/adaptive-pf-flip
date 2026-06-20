# S505 Mitsuba Low Frequency Backend Process Stub Decision

## Decision

Keep S505 as the first process-level backend contract for the low-frequency renderer path.

## Evidence

- Process-stub summary: `build/shots/s505_mitsuba_low_frequency_backend_process_stub/backend_process_stub_summary.json`
- Validation JSON: `build/shots/s505_mitsuba_low_frequency_backend_process_stub/backend_process_stub_validation.json`
- Gallery: `build/shots/s505_mitsuba_low_frequency_backend_process_stub/gallery/index.html`
- Source adapter: `build/shots/s502_mitsuba_low_frequency_backend_adapter/backend_adapter_manifest.json`
- Backend stub script: `tools/mitsuba_low_frequency_backend_stub.py`

## Metrics

- Process-stub status: `passed`
- Validation status: `passed`
- Frames: `8`
- Passed frames: `8`
- Failed frames: `0`
- Process failures: `0`
- Max abs diff: `0`
- Max mean abs diff: `0.0`
- Output bytes: `2027129`
- GIF bytes: `1191221`
- Strip GIF bytes: `4415132`
- Stdout bytes: `9541`
- Stderr bytes: `0`
- Result JSON bytes: `9541`
- Validation checks: `277`
- Failed validation checks: `0`

## Why This Matters

S503 proved the descriptor execution path in-process. S505 proves the same descriptors can be consumed by a separate executable-style backend with per-frame stdout, stderr, return code, result JSON, image output, metadata output, validation output, strips, GIFs, and gallery artifacts.

This is still a stub, not real Mitsuba rendering. The useful contract is now the process boundary: the next backend can replace `tools/mitsuba_low_frequency_backend_stub.py` with a renderer-specific executable while keeping the runner, summary schema, report, and validation gates stable.

## Next

Proceed to a real backend command adapter: either invoke Mitsuba/Blender directly from the same scene descriptor contract, or add a command-template runner that records external executable availability, command expansion, stdout, stderr, return code, and output artifact checks.
