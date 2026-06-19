# S161 S160 Gallery Refresh Publish

## Objective

Package and publish the S160 large-event cinematic scale gate so the current larger physical event can be inspected externally before the next composition pass.

## Inputs

- Shot output: `build/shots/s160_large_event_scale_gate`
- Shot report: `docs/reports/cinematic_large_event_scale_gate_s160.md`
- Shot GIF: `build/shots/s160_large_event_scale_gate/shot.gif`
- Review manifest: `build/shots/s160_large_event_scale_gate/review/review_manifest.json`

## Scope

- Build an artifact package report for the S160 GIF and review sheets.
- Build a self-contained static gallery under the S160 shot directory.
- Publish the gallery with a Cloudflare quick tunnel.
- Verify local and public `index.html` plus `assets/shot.gif`.

## Non-Goals

- Do not re-render S160 unless the existing artifacts fail validation.
- Do not stop existing public gallery tunnels.
- Do not start the S162 composition pass until S160 is publicly inspectable.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s160_large_event_scale_gate --out docs\reports\cinematic_artifact_package_s161.md
python tools\build_cinematic_gallery.py build\shots\s160_large_event_scale_gate --package docs\reports\cinematic_artifact_package_s161.md --out build\shots\s160_large_event_scale_gate\gallery --report docs\reports\cinematic_static_gallery_s161.md
python tools\publish_cinematic_gallery.py build\shots\s160_large_event_scale_gate\gallery --port 8818 --cftunnel --manifest build\shots\s160_large_event_scale_gate\gallery\publish_manifest_s161.json --report docs\reports\cinematic_gallery_publish_s161.md --timeout-seconds 120
```

## Acceptance Gate

- Artifact package report exists and marks required assets present.
- Static gallery has `index.html`, `gallery_manifest.json`, and copied review assets.
- Publish manifest records a local URL and a public Cloudflare URL.
- Local and public `index.html` return HTTP 200.
- Local and public `assets/shot.gif` return HTTP 200 and nonzero bytes.

## Verification

```powershell
git diff --check
```
