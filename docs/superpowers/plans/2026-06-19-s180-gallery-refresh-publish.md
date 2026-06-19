# S181 S180 Gallery Refresh Publish

## Objective

Package and publish the S180 secondary mist de-beading render for public
inspection.

## Inputs

- Shot directory: `build/shots/s180_secondary_mist_debeading`
- Comparison sheet:
  `build/shots/s180_secondary_mist_debeading/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s180_secondary_mist_debeading/comparison/comparison_summary.json`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s180_secondary_mist_debeading --out build\shots\s180_secondary_mist_debeading\gallery --comparison-sheet build\shots\s180_secondary_mist_debeading\comparison\comparison_sheet.png --comparison-summary build\shots\s180_secondary_mist_debeading\comparison\comparison_summary.json --comparison-label "S177 vs S180 Comparison" --title "S180 Secondary Mist De-Beading" --keyframes 3 --report docs\reports\cinematic_secondary_mist_debeading_gallery_s181.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s180_secondary_mist_debeading\gallery --port 8824 --cftunnel --manifest build\shots\s180_secondary_mist_debeading\gallery_publish_s181_manifest.json --report docs\reports\cinematic_gallery_publish_s181.md --timeout-seconds 120
```

## Result

- Local URL: `http://127.0.0.1:8824`
- Public URL: `https://message-kernel-pizza-increase.trycloudflare.com`
- HTTP server PID: `82700`
- cloudflared PID: `66852`
- Gallery report: `docs/reports/cinematic_secondary_mist_debeading_gallery_s181.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s181.md`

Checks:

- `http://127.0.0.1:8824/index.html`: HTTP `200`, `5507` bytes
- `http://127.0.0.1:8824/assets/shot.gif`: HTTP `200`, `24004938` bytes
- `https://message-kernel-pizza-increase.trycloudflare.com/index.html`: HTTP `200`, `5507` bytes
- `https://message-kernel-pizza-increase.trycloudflare.com/assets/shot.gif`: HTTP `200`, `24004938` bytes

## Next

S182 should triage the public gallery and decide whether S180's de-beading amount
is acceptable or needs a visibility rebound.
