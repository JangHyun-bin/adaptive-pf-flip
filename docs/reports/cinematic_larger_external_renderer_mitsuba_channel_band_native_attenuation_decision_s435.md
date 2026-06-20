# S435 Mitsuba Channel-Band Native Attenuation Decision

Generated UTC: `2026-06-20T12:34:00Z`

## Decision

Do not rerun a new S435 channel-band native attenuation sweep. S414 already implemented the intended experiment:

- Tool: `tools/localize_mitsuba_secondary_material_response.py`
- Input mask: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Channels: `spray,foam`
- Mechanism: projected-shape localized secondary BSDF reflectance/opacity scaling
- Best localized candidate: `S414_LR4_Luma85`

## Evidence

| Candidate | Mean target MAD | Max target MAD | Max gap | Notes |
| --- | ---: | ---: | ---: | --- |
| S401 CR21 profile | 18.657218 | 23.552905 | 182 | Score leader, upper-bound post response |
| S409 SF12 H18 | 18.756909 | 23.687432 | 170 | Best secondary/channel plus source-highlight reference |
| SF12 spray/foam | 19.120777 | 23.755952 | 170 | Best spray/foam AOV attenuation probe |
| SS1 native | 19.146412 | 23.951853 | 170 | Native baseline |
| S414 LR4 luma85 | 19.222742 | 23.989165 | 226 | Localized native channel-band attenuation, rejected |

S423 also showed that S409's channel-band is strongly explained by projected spray/foam, but S414 showed that simply localizing native secondary material does not recover the response. The gap is therefore not just "which secondary particles receive darker material"; it is likely a screen/transport/visibility mismatch.

## Next

Move to S436 with a renderer-side decomposition target:

- Compare water, secondary, source-highlight, and dark-primary response buckets as separate evaluation masks.
- Avoid new additive geometry until the dominant missing bucket is known.
- Treat S401 highlight and dark-primary as non-native reference gates unless a real renderer-side mechanism is identified.
