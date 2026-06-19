# S152 S151 Gallery Refresh Publish

## Objective

Package and publish the S151 source-edge cleanup framing Blender review so the tighter timing/framing pass can be inspected externally before the next visual triage.

## Inputs

- Shot output: `build/shots/s151_source_edge_cleanup_framing`
- Shot report: `docs/reports/cinematic_source_edge_cleanup_framing_s151.md`
- Shot GIF: `build/shots/s151_source_edge_cleanup_framing/shot.gif`
- Review manifest: `build/shots/s151_source_edge_cleanup_framing/review/review_manifest.json`

## Scope

- Build an artifact package report for the S151 GIF and review sheets.
- Build a self-contained static gallery under the S151 shot directory.
- Publish the gallery with a Cloudflare quick tunnel.
- Verify local and public `index.html` plus `assets/shot.gif`.

## Non-Goals

- Do not re-render the S151 shot unless the existing artifacts fail validation.
- Do not stop existing public gallery tunnels.
- Do not select the next look-dev adjustment until the S151 gallery is verified.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s151_source_edge_cleanup_framing --out docs\reports\cinematic_artifact_package_s152.md
python tools\build_cinematic_gallery.py build\shots\s151_source_edge_cleanup_framing --package docs\reports\cinematic_artifact_package_s152.md --out build\shots\s151_source_edge_cleanup_framing\gallery --report docs\reports\cinematic_static_gallery_s152.md
python tools\publish_cinematic_gallery.py build\shots\s151_source_edge_cleanup_framing\gallery --port 8805 --cftunnel --manifest build\shots\s151_source_edge_cleanup_framing\gallery\publish_manifest_s152.json --report docs\reports\cinematic_gallery_publish_s152.md --timeout-seconds 120
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
