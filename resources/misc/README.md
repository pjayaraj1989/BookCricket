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
| Declaration (Test)           | `declare.png`     | ✋             |
| Follow-on enforced (Test)    | `follow_on.png`   | 🔁             |
| Rain clouds (pre-match)      | `rain_clouds.png` | 🌥️             |
| Getting cloudy (Test)        | `rain_cloudy.png` | 🌥️             |
| Drizzle (Test)               | `rain_drizzle.png`| 🌦️             |
| Heavy rain (Test)            | `rain_heavy.png`  | 🌧️             |
| Rain stopped play (Test)     | `rain_stopped.png`| ☔             |

Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp` (checked in that
order). Images are shown at up to 150x95, cropped to fit.

Any image that's missing simply falls back to the emoji, so add only the
ones you care about.
