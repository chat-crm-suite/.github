# ChatCRM — brand directions (draft 04)

Brand name: **ChatCRM** · GitHub organization: `chat-crm-suite`

Eight directions for the mark, rebuilt around what the product does: messages arrive, get handled
and go out at scale. All of them share the palette (mapped 1:1 from the product theme,
`chat-crm-app/src/styles/theme.css`), one weight language, and one habit — **removing shapes
instead of drawing lines.**

Open `showcase.html` to compare them, with a light/night toggle for the whole page.

## The palette

| Token | Hex       | Role                                                        |
| ----- | --------- | ----------------------------------------------------------- |
| Deep  | `#00623A` | The mark on paper (light surfaces)                          |
| Mint  | `#72E3AD` | Accent surface; same green as the product's primary buttons |
| Vivid | `#4ADE80` | The mark on night (dark surfaces)                           |
| Ink   | `#171717` | Text and mono usage                                         |
| Night | `#121212` | Dark surface                                                |
| Paper | `#FAFAFA` | Light surface                                               |

Every SVG is single-colour via `currentColor`: one file per direction covers both themes.

## Directions (`variants/`)

| File                    | Idea                                                        | Best for                        |
| ----------------------- | ----------------------------------------------------------- | ------------------------------- |
| `wordmark.svg`          | Outfit 700 → curves, speech tail in the first C             | Website header · README         |
| `wordmark-stacked.svg`  | Same lettering stacked, tail anchoring the bottom-left      | Avatar · tight frames           |
| `message-note.svg`      | Fold's folded corner plus a message tail                    | Docs · marketing · stamps       |
| `inbox-stack.svg`       | Conversation cards stacked, front chat card with tail       | Org avatar · product UI         |
| `bubble-check.svg`      | Bubble plus a bold check cut into it                        | Product · notifications         |
| `broadcast.svg`         | Bubble pulling two ripples: one message to many             | Campaigns · mass messaging      |
| `composer.svg`          | The input bar with its cursor, tapering like a tail         | Product · typing states         |
| `spark.svg`             | Bubble with a four-point star cut: the AI inside            | AI features · suite storytelling|

## Usage rules

- Keep ≥ 14 units padding (of 100) around the symbols.
- At 16 px, the safest marks are Message note, Inbox stack, Bubble check and Spark. Give
  Broadcast and Composer 24 px or more. The single-line wordmark needs 120 px of width;
  the stacked wordmark holds from about 56 px.
- On light surfaces set `color: #00623A`; on dark surfaces `color: #4ADE80`; mono use `#171717`.
- The wordmarks are pure vector outlines (no live text): they render identically everywhere,
  font or no font. Outfit is licensed under the SIL Open Font License (Rodrigo Fuenzalida /
  On Brand Investments); the outlined letterforms are embedded in the SVGs.

## Next steps

1. Pick one or two directions (via `showcase.html` or by name).
2. Refinements: weight, roundness, the cut, spacing.
3. Optional phase: PNG exports at 1024 px (transparent, paper + night) and favicon sizes.

---

# Draft 05 — `chat-crm suite` (2026-10-06)

Six new directions, each with a name lockup (`chat-crm` + `suite`), a GitHub avatar and favicon
sizes. Open `showcase-v5.html` (serve the folder, e.g. `python -m http.server`, so fonts load).
Regenerate everything with `python build_v5.py`; the SVGs land in `v5/`.

| # | File               | Idea                                                              |
| - | ------------------ | ----------------------------------------------------------------- |
| 1 | `pulse.svg`        | Typing dots rising like a bar chart: chat + metrics               |
| 2 | `funnel.svg`       | Message lines narrowing into a sales funnel                       |
| 3 | `contact.svg`      | A contact (person) cut out of the bubble                          |
| 4 | `dialogue.svg`     | Business and customer bubbles; `dialogue-duo.svg` in Deep + Mint  |
| 5 | `monogram.svg`     | A heavy "c" whose base becomes the tail, plus an outgoing dot     |
| 6 | `suite.svg`        | Four suite modules, the chat one with a sharp corner; `suite-color*.svg` use chart-2/chart-4 |

Mono files use `currentColor`; `*-duo` / `*-color*` files carry fixed hex values from the theme.
The lockup text in the showcase is live Outfit; it gets outlined once a direction is chosen.

---

# Draft 06 — marks with depth (2026-10-06)

Feedback on 05: too generic and too simple. Draft 06 moves to marks with volume (weave, fold,
extrusion, orbit), the theme gradient (Vivid → Deep on light, Mint → Emerald on dark) and a heavier
wordmark (`chat·crm` Outfit 800 + `SUITE` tracked). Page: `showcase-v6.html`; build: `python build_v6.py`.

| # | Mark      | Files (`v6/`)                                   | Idea                                         |
| - | --------- | ----------------------------------------------- | -------------------------------------------- |
| 1 | Pliegue   | `fold{,-light,-dark,-app}.svg`                  | "c" ribbon folding under into the tail       |
| 2 | Enlace    | `link{,-light,-dark,-app}.svg`                  | Chat and customer record woven together      |
| 3 | Infinito  | `loop{,-light,-dark,-app}.svg`                  | Endless customer loop with a message tail    |
| 4 | Bloque    | `block{,-light,-dark,-app}.svg`                 | Extruded bubble, "c" carved in its face      |
| 5 | Órbita    | `orbit{,-light,-dark,-app}.svg`                 | The suite orbiting the conversation          |

`*.svg` = one ink (`currentColor`), `-light` / `-dark` = gradient colour, `-app` = app icon / avatar.

---

# Draft 07 — ChatCRM, flat and serious (2026-10-06)

Feedback on 06: no gradients, serious and elegant, a mark with a concept, proper typography, name
**ChatCRM** (no "suite"), plus a wordmark-only option. Page: `showcase-v7.html`.
Build: `python build_v7.py` (needs `fonttools` + `uharfbuzz`; OFL fonts in `fonts/` from
github.com/google/fonts). Wordmarks are HarfBuzz-shaped (real kerning) and outlined: no font needed.

Wordmarks (`v7/wordmark-<key>[-paper|-night].svg`):
W1 `serif` Fraunces 560 · W2 `weight` Instrument Sans 400+700 · W3 `caret` Manrope 800 + caret ·
W4 `lower` Sora 300+700.

Symbols (`v7/symbol-<key>[-paper|-night].svg`):
S1 `record` Doble C (CRM wraps the chat) · S2 `half` Mitad (bubble | record rows) ·
S3 `link` Enlace (chat and record woven) · S4 `caret` Cursor (C + composer caret).

Every symbol × wordmark lockup: `v7/lockup-<symbol>-<wordmark>.svg`. Palette: Deep `#006239`,
Ink `#171717`, Mint `#72E3AD` (dark surfaces only), Paper, Night.

---

# Draft 08 — "Cursor" system (W3 + S4), 2026-10-06

Chosen direction: W3 wordmark (`Chat│CRM`, Manrope 800) + S4 symbol. The v7 lockup failed because
the C and the caret appeared twice and the symbol was drawn separately (different weight/curve).
Now the symbol is the wordmark's own Manrope 800 "C" + the same caret at the same spacing.

**Rule:** the caret appears once per composition. With the symbol present, the name drops its caret.

Files in `v8/` (each as `<name>.svg` one ink, `-paper`, `-night`): `wordmark`, `symbol`, `badge`,
`horizontal` (L1, badge + name), `open` (L2, bare symbol + hairline + name), `stacked` (L3),
`fusion` (L4, wordmark with green C + caret). Page: `showcase-v8.html`; build: `python build_v8.py`.

---

# Draft 09 — custom lettering on Outfit (2026-10-06)

Feedback on 08: the typeface felt basic; wanted custom lettering in the spirit of the frontend font
(Outfit), the L4 "fusion" wordmark, plus symbol and badge for GitHub.

Outfit 700 (the app's font) shaped with HarfBuzz and edited per glyph with boolean ops
(skia-pathops), so each colour is one clean path. Three levels, each with wordmark / symbol / badge:

| Level | Key        | Changes                                                              |
| ----- | ---------- | -------------------------------------------------------------------- |
| 01    | `afinada`  | Outfit 700, hand-tuned spacing, caret proportional to the stems      |
| 02    | `corte`    | + 45° cuts (taken from Outfit's C terminals) on h, t and the caret    |
| 03    | `ligadura` | + the t crossbar joins the a stem: "at" as one piece                 |

Files: `v9/<key>-{wordmark,symbol,badge}{,-paper,-night}.svg`. Page `showcase-v9.html`;
build `python build_v9.py` (needs `skia-pathops`, `uharfbuzz`, `fonttools`; Outfit.ttf in `fonts/`).
The symbol's caret is slightly thicker (112 vs 84 units) so it survives at 16 px.
SVG paths are cubic curves rounded to 0.01.

---

# Draft 10 — the C as hero (2026-10-06)

Feedback on 09: CRM was still stock Outfit, and the C is the main element. One rule now: **every cut
and diagonal is 45°** (the angle of Outfit's own C terminals).

- **Hero C** (green, also the symbol): geometric ring, stroke 180, opening cut by two exact 45°
  lines, speech tail pointing down-left at 45°.
- **C of CRM**: the same ring without tail, stroke 162 (optical match to the 153 stems).
- **R / M**: 45° cuts on the outer top corners (M symmetric). **h / t / caret**: 45° top cut.
- Optional "at" ligature: `wordmark-lig*.svg`.

Files `v10/{wordmark,wordmark-lig,symbol,badge}{,-paper,-night}.svg`; page `showcase-v10.html`;
build `python build_v10.py` (reuses `build_v9.py` / `build_v7.py` helpers).

---

# Draft 11 — compact Outfit + abstract symbols (2026-10-06)

Feedback on 10: the tail and the 45° cuts were decoration, not design. Answers: start from v8
(Chat│CRM + caret); geometric type like Outfit but compact and matched to symbol/badge; references
Notion/Slack/Intercom + HubSpot/Salesforce/Zendesk; symbol: abstract (main), CC monogram (variant).

- Wordmark: Outfit 700 untouched letterforms, tracking −0.03 em, green caret (`v11/wordmark*.svg`).
- Symbols (`v11/<key>-{symbol,badge,lockup}{,-paper,-night}.svg`): `dialogue` (two overlapping forms,
  one sharp corner each), `converge` (four forms pointing to the centre), `flow` (rounded square split
  by a soft curve), `link` (two C's turned 180° closing a circle).
- Lockup: symbol = 1.3× cap height, gap 0.36 cap. Page `showcase-v11.html`; build `python build_v11.py`.

---

# Draft 12 — rounded Outfit + CC monogram (2026-10-06)

Feedback on 11: Flujo looks like B Capital's logo (dropped). CC monogram liked, but its round caps
clashed with the square caret and square letter ends. Now everything is round:

- Letters: Outfit 700 outlines with every convex corner rounded by a morphological opening
  (pyclipper: shrink by r, grow by r with round joins); proportions untouched. Levels: `soft` r=28,
  `round` r=58 (stem 153).
- Caret: a pill. Symbol/badge: the v11 CC monogram (two round-capped C's closing a circle).

Files `v12/{symbol,badge}*.svg`, `wordmark-{soft,round}*.svg`, `lockup-{soft,round}*.svg`,
`lockup-badge-{soft,round}*.svg`. Page `showcase-v12.html`; build `python build_v12.py`
(needs `pyclipper` too). Rounded letters are exported as fine polylines (0.1 unit precision).

---

# Draft 13 — Chat vs CRM, tighter (2026-10-06)

Chosen: draft 12 "round". Asked: tell Chat and CRM apart, set them closer, try a heavier CRM.
Tracking −0.038 em (was −0.03), caret gap 40 (was 62). Corner radius = 38 % of the stem of each
weight (stems: 400→90, 600→131, 700→153, 800→174), so mixed weights look equally soft.

| Key        | Chat | CRM | Note                          |
| ---------- | ---- | --- | ----------------------------- |
| `base`     | 700  | 700 | v12 round, just tighter       |
| `weight`   | 600  | 800 | the suggested heavier CRM     |
| `contrast` | 400  | 800 | strongest contrast            |
| `color`    | 600  | 800 | CRM also in Deep green        |

Files `v13/{wordmark,lockup,lockup-badge}-<key>{,-paper,-night}.svg`. Symbol/badge unchanged (v12).
Page `showcase-v13.html`; build `python build_v13.py`.

---

# Draft 14 — variant 04, caret options (2026-10-06)

Chosen: v13 variant 04 (Chat 600 ink + CRM 800 Deep green, rounded r = 38 % stem), light/dark
surfaces as shown. Problem: with CRM split by weight and colour, the green caret between the words
read as an extra letter. Options (`v14/{wordmark,lockup,lockup-badge}-<mode>{,-paper,-night}.svg`):

- `none` — no caret: ChatCRM, words set with normal t→C spacing.
- `end` — caret after CRM (typing): ChatCRM│.
- `thin` — thinner (40), cap-height, light-green caret between the words.

Page `showcase-v14.html`; build `python build_v14.py`.

---

# Draft 15 — wordmark polish (2026-10-06)

Chosen: v14 `none` (ChatCRM, no caret; Chat 600 ink + CRM 800 Deep green, rounded). Polish:

1. **One top line at 703** (Chat's cap height): h (was 723) and t (was 684) moved to it.
2. **Optical pair spacing** on top of −38 tracking: t→C +34 (the seam was 12 units), R→M +14,
   C→h −4, a→t +2, C→R +4.
3. **Inner corners rounded** (closing): r = 0.30 × stem on h, a, t (fills Outfit's ink-trap notches
   into smooth fillets); light r on R (0.10) and M (0.08) whose inner spaces are narrow at 800.
4. **CRM scaled to 703/709** so both C's read the same size.

Files `v15/{wordmark,lockup,lockup-badge}{,-paper,-night}.svg`. Page `showcase-v15.html` shows each
step before/after; build `python build_v15.py`.

---

# FINAL — `final/` (2026-10-06)

Brand package built from draft 15 by `python build_final.py` (also needs `resvg-py` and `Pillow`).
See `final/README.md` for pieces, colours and usage rules, and `final/index.html` for the sheet.

Last fixes made while packaging (in `build_v15.py`, so drafts and final agree):
- Outfit's ink-trap notches filled selectively: a closing finds concave regions; only notch-sized ones
  (20–1100 units², not touching the baseline) are filled, so real spaces (R leg/bowl) stay intact.
- The M's inner stem spurs removed (inner stem tops moved to where the diagonals meet them).
- Favicons use a larger symbol inside the badge so they read at 16 px.

---

# Published (2026-10-06)

The package is published in **`chat-crm-suite/.github` → `brand/`** (local checkout: `../org-github/`).
After rebuilding with `python build_final.py`, copy `final/` over `../org-github/brand/` (keep its README
line about the generator) and commit there. Extra GitHub assets added for the organization:
`github/profile-banner-{en,es}-{light,dark}.svg` and `github/social-preview-{api,app,ia}.png`.
