# S175 S173 Gallery Refresh Publish

## Objective

Package the S173 metadata-depth render and S174 comparison artifact into a
static gallery, then publish it through Cloudflare Tunnel for external review.

## Inputs

- Shot directory: `build/shots/s173_metadata_depth_attenuation`
- S174 comparison sheet:
  `build/shots/s174_metadata_depth_comparison/comparison_sheet.png`
- S174 comparison summary:
  `build/shots/s174_metadata_depth_comparison/comparison_summary.json`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s173_metadata_depth_attenuation --out build\shots\s173_metadata_depth_attenuation\gallery --comparison-sheet build\shots\s174_metadata_depth_comparison\comparison_sheet.png --comparison-summary build\shots\s174_metadata_depth_comparison\comparison_summary.json --title "S173 Metadata Depth Attenuation" --keyframes 3 --report docs\reports\cinematic_metadata_depth_gallery_s175.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s173_metadata_depth_attenuation\gallery --port 8822 --cftunnel --manifest build\shots\s173_metadata_depth_attenuation\gallery_publish_s175_manifest.json --report docs\reports\cinematic_gallery_publish_s175.md --timeout-seconds 120
```

## Result

- Local URL: `http://127.0.0.1:8822`
- Public URL: `https://yearly-whereas-generated-alfred.trycloudflare.com`
- HTTP server PID: `96440`
- cloudflared PID: `54920`
- Gallery report: `docs/reports/cinematic_metadata_depth_gallery_s175.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s175.md`

Checks:

- `http://127.0.0.1:8822/index.html`: HTTP `200`, `5536` bytes
- `http://127.0.0.1:8822/assets/shot.gif`: HTTP `200`, `23891985` bytes
- `https://yearly-whereas-generated-alfred.trycloudflare.com/index.html`: HTTP `200`, `5536` bytes
- `https://yearly-whereas-generated-alfred.trycloudflare.com/assets/shot.gif`: HTTP `200`, `23891985` bytes

## Next

S176 should triage the public gallery and choose one concrete visual pass to
improve next.
