# Larger External Renderer: Mitsuba CR21 Mask Channel Join

Status: complete

## Goal

Join S405 CR21 response masks with projected secondary-channel AOVs so S407 can
choose a material/AOV direction from evidence instead of broad scalar sweeps.

## Scope

- Add `tools/analyze_mitsuba_source_response_mask_channels.py`.
- Analyze highlight, dark-secondary, and response-union mask sources.
- Score spray, foam, bubble, droplet, grouped-channel, and density candidates.
- Publish the AOV gallery through a Cloudflare quick tunnel.

## Result

Highlight is not explained by secondary channels. Dark-secondary and
response-union are loosely explained by all-channel or spray/foam density, but
with low precision.

## Decision

Do not solve source highlights through secondary material. For S407, test local
spray/foam-density attenuation only as a bounded diagnostic candidate.
