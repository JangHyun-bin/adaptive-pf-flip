# S226 Cinematic Gallery Publish Tool Hardening

## Status

Passed.

## Bug

S225 exposed two publish stability issues:

- Existing `publish_logs` could contain an older trycloudflare URL, and the URL scanner returned that stale URL before the new quick tunnel URL appeared.
- On Windows, the port probe used `SO_REUSEADDR`, which allowed multiple local gallery servers to listen on the same port and made HTTP verification hit the wrong gallery.

## Fix

- `tools/publish_cinematic_gallery.py` now truncates stdout/stderr logs for each new started process.
- `choose_port` now accepts the requested bind address and avoids `SO_REUSEADDR` on Windows.

## Validation

```powershell
python -m py_compile tools\publish_cinematic_gallery.py
```

Inline regression smoke:

- occupied-port probe: passed, `choose_port` skipped the occupied port.
- stale-log probe: passed, `start_process` removed stale trycloudflare URLs before writing fresh process output.

Actual local publish smoke while S225 was serving on `18899`:

```powershell
python tools\publish_cinematic_gallery.py build\shots\s224_wide_accepted_review\gallery --port 18899 --manifest build\shots\s226_publish_tool_regression\local_publish_manifest.json --report build\shots\s226_publish_tool_regression\local_publish_report.md --timeout-seconds 30
python tools\publish_cinematic_gallery.py --stop-manifest build\shots\s226_publish_tool_regression\local_publish_manifest.json
```

Result: the test publish selected `http://127.0.0.1:18900`, verified the gallery, then stopped PID `150608` from its manifest.

## Decision

Keep the S225 public tunnel running, but use the hardened publisher for all future gallery refreshes.
