# S158 S157 Gallery Refresh Publish

## Objective

Package and publish the S157 contact foam sheet continuity Blender review so the updated contact foam surface can be inspected externally before the next visual triage.

## Inputs

- Shot output: `build/shots/s157_contact_foam_sheet_continuity`
- Shot report: `docs/reports/cinematic_contact_foam_sheet_continuity_s157.md`
- Shot GIF: `build/shots/s157_contact_foam_sheet_continuity/shot.gif`
- Review manifest: `build/shots/s157_contact_foam_sheet_continuity/review/review_manifest.json`

## Scope

- Build an artifact package report for the S157 GIF and review sheets.
- Build a self-contained static gallery under the S157 shot directory.
- Publish the gallery with a Cloudflare quick tunnel.
- Verify local and public `index.html` plus `assets/shot.gif`.

## Non-Goals

- Do not re-render the S157 shot unless the existing artifacts fail validation.
- Do not stop existing public gallery tunnels.
- Do not select the next look-dev adjustment until the S157 gallery is verified.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s157_contact_foam_sheet_continuity --out docs\reports\cinematic_artifact_package_s158.md
python tools\build_cinematic_gallery.py build\shots\s157_contact_foam_sheet_continuity --package docs\reports\cinematic_artifact_package_s158.md --out build\shots\s157_contact_foam_sheet_continuity\gallery --report docs\reports\cinematic_static_gallery_s158.md
python tools\publish_cinematic_gallery.py build\shots\s157_contact_foam_sheet_continuity\gallery --port 8817 --cftunnel --manifest build\shots\s157_contact_foam_sheet_continuity\gallery\publish_manifest_s158.json --report docs\reports\cinematic_gallery_publish_s158.md --timeout-seconds 120
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
