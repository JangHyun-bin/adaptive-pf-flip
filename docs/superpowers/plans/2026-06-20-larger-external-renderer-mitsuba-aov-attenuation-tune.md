# Larger External Renderer: Mitsuba AOV Attenuation Tune

Status: complete

## Goal

Tune the S407 spray/foam attenuation probe around `SF18` and choose the best
bounded target-free AOV response.

## Result

`SF12_SprayFoam` is the best tuned probe:

- SS1 max target MAD: `23.951853137860084`
- SF18 max target MAD: `23.77382137345679`
- SF12 max target MAD: `23.755951646090534`
- S401 CR21 max target MAD: `23.552905092592592`

## Decision

Promote `SF12_SprayFoam` as the current AOV attenuation baseline. It improves
over SS1 and over SF18, but it does not solve source highlights.

## Next

S409 should keep SF12 for dark-secondary attenuation and work on target-free
source-highlight response separately.
