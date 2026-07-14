# Team flags

Drop national flags (or franchise logos for league teams) in this directory
and the web UI will show them side by side when the two teams are selected.

## Filename convention

Same rule as player pics: lowercase the team name exactly as it appears in
`data/teams_*.json`, replace every run of non-alphanumeric characters with a
single underscore, and add an image extension:

| Team name in teams JSON | Filename              |
|-------------------------|-----------------------|
| `India`                 | `india.png`           |
| `NewZealand`            | `newzealand.png`      |
| `KingsXI-Punjab`        | `kingsxi_punjab.png`  |

Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp` (checked in that
order). Landscape images work best — the UI shows them at 84x56 (flag
aspect ratio), cropped to fit.

Watch out for spelling variants across roster files (e.g. `WestIndies` in
one file, `West-Indies` in another) — they resolve to different filenames,
so either save the flag under both names or normalize the JSONs.

If no flag is found for a team, the UI falls back to a badge with the first
three letters of the team name.
