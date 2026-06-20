# S518 Mitsuba Material Tone mt12_highlight_cut Export

Generated UTC: `2026-06-20T19:45:55.969134+00:00`
Export JSON: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt12_highlight_cut/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask source: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Material Response

- Secondary channels: `['foam', 'spray']`
- Secondary reflectance drop: `0.1`
- Secondary opacity drop: `0.05`
- Water alpha drop: `0.5`
- Water alpha min: `0.0025`
- Highlight key light max radiance: `[0.2, 0.25, 0.34]`

## Checks

- Frames exported: `8`
- Missing references: `0`
- XML scene bytes: `322.36 KB`
- Water alpha replacements: `8`
- Secondary reflectance replacements: `16`
- Secondary opacity replacements: `16`
- Key lights inserted: `8`

## Frame Samples

| Output | Channel Cov | Highlight Cov | Water Alpha | Secondary Scale | Opacity Scale | Key Radiance | XML Scene |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0.011321373456790124 | 0.0016859567901234569 | 0.023587953987333595 | 0.914520827264783 | 0.9572604136323914 | `[0.031629830683727544, 0.03953728835465943, 0.05377071216233683]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt12_highlight_cut/scenes/frame_0000.xml` |
| 27 | 0.005208333333333333 | 0.0010686728395061728 | 0.02410495023911077 | 0.9606757937663851 | 0.9803378968831925 | `[0.02004911464391883, 0.025061393304898538, 0.03408349489466201]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt12_highlight_cut/scenes/frame_0004.xml` |
| 47 | 0.0132445987654321 | 0.014924768518518518 | 0.0125 | 0.9 | 0.95 | `[0.27999999999999997, 0.35, 0.476]` | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt12_highlight_cut/scenes/frame_0007.xml` |

## Next

Validate, render, and compare S518 mt12_highlight_cut.
