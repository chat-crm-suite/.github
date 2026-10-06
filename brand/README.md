# ChatCRM — brand package

Final identity for **ChatCRM** (GitHub organization `chat-crm-suite`). Open `index.html` for a visual
sheet. Everything here is generated from the brand sources (`build_final.py`); do not edit these files by hand.

## The pieces

| Piece | What it is | Use it for |
| --- | --- | --- |
| **Wordmark** | `Chat` (Outfit 600, ink) + `CRM` (Outfit 800, green), rounded and hand-spaced | README headers, documents, anywhere the name must lead |
| **Symbol** | Two C's (Chat and CRM), one turned 180°, closing a circle | Next to the name, small UI spots, watermarks |
| **Badge** | The symbol on a deep-green rounded square | GitHub avatar, favicon, app icon, social avatars |
| **Lockup** | Symbol + wordmark | Main logo: app header, website, presentations |
| **Lockup with badge** | Badge + wordmark | When the logo sits on busy backgrounds or next to other app icons |

File names: `-light` = for light backgrounds, `-dark` = for dark backgrounds, `-mono` = one ink
(`currentColor`: set the colour with CSS `color:`). The badge has a single version because it carries
its own background.

## Folders

- `svg/` — vector masters (use these whenever possible).
- `png/` — transparent PNGs at 512/1024/2048 px wide (logo pieces) and 64–1024 px (badge).
- `favicon/` — `favicon.ico` (16/32/48), `favicon.svg`, `apple-touch-icon.png` (180), `icon-192.png`,
  `icon-512.png`, `icon-maskable-512.png` (full bleed, for PWA `purpose: "maskable"`). The favicon uses a
  larger symbol than the regular badge so it still reads at 16 px.
- `github/` — `avatar-500.png` / `avatar-1024.png` (full bleed: GitHub rounds the corners itself) and
  `social-preview-1280x640.png` for each repository (Settings → General → Social preview).
- `animated/` — `chatcrm-typing-{light,dark}.svg`: the name types itself, the caret blinks twice and
  leaves. Plays once; with `prefers-reduced-motion` it shows the static logo. Embed with `<img>` or
  `<object>` (inline `<svg>` also works).

## Colour

| Name | Hex | Role |
| --- | --- | --- |
| Deep green | `#006239` | `CRM` and symbol on light, badge background |
| Mint | `#72E3AD` | `CRM` and symbol on dark, badge accent (the frontend's `--primary`) |
| Ink | `#171717` | `Chat` on light |
| Frost | `#E2E8F0` | `Chat` on dark |
| Paper | `#FAFAFA` | Light background |
| Night | `#121212` | Dark background |
| Mid green | `#2FA36B` | Second arc of the symbol on dark only |

All taken from `chat-crm-app/src/styles/theme.css`. No gradients.

## Rules

- **Clear space:** keep at least the height of the `C` × 0.5 empty around the logo.
- **Minimum size:** wordmark 80 px wide · lockup 110 px wide · badge 16 px (use the favicon files below 32 px).
- **Don't:** recolour `Chat` and `CRM` the same, add a caret between the words, stretch, rotate,
  outline, add shadows or gradients, or set the name in live text instead of using the files.
- **The caret** belongs to motion, not to the static logo: the typing animation, the social preview
  tagline, typing indicators inside the product.

## Type

Built from **Outfit** (SIL Open Font License, the frontend's typeface): weights 600 and 800, corners
rounded at 38 % of the stem, inner corners filleted, Outfit's ink-trap notches filled, the M's inner
spurs removed, one top line at the cap height, optical spacing per pair. For text set next to the logo,
use Outfit from Google Fonts.
