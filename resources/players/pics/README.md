# Player pictures

Drop player photos in this directory and the web UI's event pane will show
them when that player walks in to bat or comes on to bowl.

## Filename convention

Lowercase the player's name as it appears in `data/teams_*.json`, replace
every run of non-alphanumeric characters (spaces, dots, hyphens) with a
single underscore, and add an image extension:

| Name in teams JSON       | Filename                    |
|--------------------------|-----------------------------|
| `Virat Kohli`            | `virat_kohli.png`           |
| `K.L Rahul`              | `k_l_rahul.png`             |
| `Rassie van der dussen`  | `rassie_van_der_dussen.png` |

Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp` (checked in that
order). Square-ish images work best — the UI crops them into a 72px circle.

If no picture is found for a player, the UI falls back to an initials
avatar, so missing pictures are fine.
