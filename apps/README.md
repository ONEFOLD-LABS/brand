# App icons and app colours

Icons and colour sets for every ONEFOLD LABS app, computed by `tools/make_app_icons.py` from
`tokens/tokens.json`. They follow "The app family" in the brand book; nothing is drawn by hand
or traced.

```sh
uv run --with shapely python tools/make_app_icons.py   # rewrites apps/<app>/*.svg and apps/palette.json
```

## Icons

| App | Motif | Colour (`app-<name>`) |
|---|---|---|
| StudioCraft | Decay: a struck tone that rises and rings out (the shipped icon, unchanged) | `#9e2343` wine |

Per app: `icon.svg` (30 px strokes, from 48 px) and `icon-small.svg` (44 px strokes, simplified
where needed, 16–32 px). Disc radius 226 on the 512 grid, gradient from the app colour one step
lighter (top left) to one step darker (bottom right), motif cut out as one real hole. The app
repositories copy these into `assets/app-icon/` and render the platform sizes from them.

## Colours

`palette.json` holds, per app and theme:

- `accent`, `on_accent`, `accent_strong` (hover, pressed), `accent_tint` (selection, callouts).
  Light theme: the app colour with white text. Dark theme: a lighter accent with near-black
  text (`on-petrol`), the same pattern as `petrol`.
- `domain`: colours for the app's own data (none for StudioCraft yet).

And for all apps, `semantic`: success, warning, danger, info, neutral.

Checks, recomputed on every run:

- Every text colour (semantic, domain) holds at least 4.6:1 on `paper`, `surface` and
  `surface-sunken` of its theme.
- `on_accent` on `accent` at least 4.5:1; `accent` against the grounds at least 3:1.

Not in the tokens yet: the semantic colours and the per-app UI and domain colours. Once they are
settled they can move into `tokens.json`.
