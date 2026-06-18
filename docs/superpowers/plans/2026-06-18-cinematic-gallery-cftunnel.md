# S122 Cinematic Gallery Cftunnel Publisher

## Objective

Expose the S121 static gallery through a local HTTP server and an optional Cloudflare quick tunnel, then verify that the HTML and copied GIF asset are reachable over HTTP.

## Command

```powershell
python tools\publish_cinematic_gallery.py build\shots\s119_blender_quality_baseline_comparison\gallery --port 8899 --cftunnel --manifest build\shots\s119_blender_quality_baseline_comparison\gallery\publish_manifest_s122.json --report build\shots\s119_blender_quality_baseline_comparison\gallery\publish_report_s122.md --timeout-seconds 90
```

Run-specific tunnel URLs, process IDs, logs, and publish reports stay under `build/` and are not committed.

## Result

S122 passed. The publisher started a local static server and a Cloudflare quick tunnel, then verified:

- local `index.html`: HTTP 200, 8161 bytes
- local `assets/shot.gif`: HTTP 200, 25268927 bytes
- public `index.html`: HTTP 200, 8161 bytes
- public `assets/shot.gif`: HTTP 200, 25268927 bytes

The tool writes:

- `publish_manifest_s122.json`
- `publish_report_s122.md`
- `publish_logs/http_stdout.log`
- `publish_logs/http_stderr.log`
- `publish_logs/cloudflared_stdout.log`
- `publish_logs/cloudflared_stderr.log`

It also supports cleanup through:

```powershell
python tools\publish_cinematic_gallery.py --stop-manifest build\shots\s119_blender_quality_baseline_comparison\gallery\publish_manifest_s122.json
```

## Verification

```powershell
python -m py_compile tools\publish_cinematic_gallery.py
python tools\publish_cinematic_gallery.py build\shots\s119_blender_quality_baseline_comparison\gallery --port 8899 --cftunnel --manifest build\shots\s119_blender_quality_baseline_comparison\gallery\publish_manifest_s122.json --report build\shots\s119_blender_quality_baseline_comparison\gallery\publish_report_s122.md --timeout-seconds 90
git diff --check
ctest --test-dir build -C Release --output-on-failure
```

## Next

S123 should capture a visual review triage report from the published gallery and choose the next look-dev adjustment.
