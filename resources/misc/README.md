# Miscellaneous event images

Images shown by the web UI's event pane at fixed moments in a match. Unlike
player pics and team flags, these use **fixed filenames** — one image per
event kind:

| Event                        | Filename          | Emoji fallback |
|------------------------------|-------------------|----------------|
| Lunch break (Test session)   | `lunch.png`       | 🍽️             |
| Tea break (Test session)     | `tea.png`         | ☕             |
| Innings over                 | `innings_over.png`| 🏏             |
| Match won                    | `victory.png`     | 🏆             |
| Run out                      | `runout.png`      | 🏃             |

Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp` (checked in that
order). Images are shown at up to 150x95, cropped to fit.

Any image that's missing simply falls back to the emoji, so add only the
ones you care about.
