"""ChatCRM brand — final package (from draft 15).

    python brand-source/build_final.py

Writes ../brand/ (the published package; its README.md is hand-written):
  svg/        wordmark, symbol, badge, lockup, lockup-badge · light / dark / mono
  png/        transparent renders at several sizes
  favicon/    favicon.ico (16/32/48), favicon.svg, apple-touch-icon, PWA icons
  github/     org avatar (500, 1024) and social preview (1280x640)
  animated/   typing wordmark (SVG + CSS, plays once, respects reduced motion)
  index.html  brand sheet · README.md usage guide
Needs: fonttools, uharfbuzz, skia-pathops, pyclipper, resvg-py, Pillow.
"""
import io
from pathlib import Path

import resvg_py
from PIL import Image

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER
from build_v9 import d as path_d
from build_v11 import s_link
from build_v15 import (CAP, CRM_SCALE, INNER, NOTCH_R, PAIRS, ROUND, STEMS, WC, WR, lockup_svg, parts, set_word, soften,
                       wordmark_svg)

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "brand"  # the published package, served from raw.githubusercontent
NS = 'xmlns="http://www.w3.org/2000/svg"'
SURFACES = {"light": "paper", "dark": "night", "mono": "mono"}


def label(name):
    return f'{NS} role="img" aria-label="ChatCRM{name}"'


# ---------------------------------------------------------------- vector pieces

def symbol(surface, attrs):
    a, b = {"paper": (DEEP, MINT), "night": (MINT, "#2FA36B"), "mono": ("currentColor", "currentColor")}[surface]
    _, body = s_link(a, b, "s")
    # the ring spans 15..85 of its 100 box: crop to it with a little air
    return f'<svg viewBox="10 10 80 80" {attrs}>{body}</svg>'


def badge(surface, attrs, full_bleed=False, small=False):
    if surface == "mono":
        _, body = s_link("#000", "#000", "b")
        return (f'<svg viewBox="0 0 100 100" {attrs}><defs><mask id="m"><rect width="100" height="100" fill="#fff"/>'
                f'<g transform="translate(18 18) scale(.64)">{body}</g></mask></defs>'
                f'<rect width="100" height="100" rx="23" fill="currentColor" mask="url(#m)"/></svg>')
    _, body = s_link(PAPER, MINT, "b")
    rx = 0 if full_bleed else 23
    # favicon sizes: bigger symbol (ring fills ~62 % instead of 45 %) so it still reads at 16 px
    fit = "translate(5 5) scale(.9)" if small else "translate(18 18) scale(.64)"
    return (f'<svg viewBox="0 0 100 100" {attrs}><rect width="100" height="100" rx="{rx}" fill="{DEEP}"/>'
            f'<g transform="{fit}">{body}</g></svg>')


def padded(svg, frac=0.06):
    """Grow the root viewBox by `frac` of its height on every side (air around PNG exports)."""
    import re
    m = re.search(r'viewBox="([^"]+)"', svg)
    x, y, w, h = (float(v) for v in m.group(1).split())
    p = h * frac
    return svg.replace(m.group(0), f'viewBox="{x - p:.1f} {y - p:.1f} {w + 2 * p:.1f} {h + 2 * p:.1f}"', 1)


def png(svg, width=None, height=None, background=None):
    return resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height, background=background)


def save_png(path, svg, **kw):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png(svg, **kw))


# ---------------------------------------------------------------- glyph list (for the animation)

def glyphs():
    """[(d, colour_role, right_edge)] for C h a t C R M, exactly as draft 15 sets them."""
    chat, x = set_word("Chat", WC, 0, align_tops=True, pairs=PAIRS)
    x += PAIRS[("t", "C")]
    crm, _ = set_word("CRM", WR, x, scale=CRM_SCALE, pairs=PAIRS)
    out = [(soften(p, STEMS[WC] * ROUND, STEMS[WC] * INNER[n], STEMS[WC] * NOTCH_R), "ink", p.bounds[2])
           for n, p in chat]
    out += [(soften(p, STEMS[WR] * ROUND * CRM_SCALE, STEMS[WR] * INNER[n] * CRM_SCALE,
                    STEMS[WR] * NOTCH_R * CRM_SCALE), "green", p.bounds[2]) for n, p in crm]
    return out


def typing_svg(surface="paper"):
    ink, green = {"paper": (INK, DEEP), "night": (FROST, MINT)}[surface]
    gl = glyphs()
    x0, y0, x1, y1 = parts()[2]
    cw, gap, top, bot = 60, 46, 742, -70
    pad = 40
    vb = f"{x0 - pad:.0f} {-y1 - pad - 40:.0f} {x1 - x0 + cw + gap + 2 * pad:.0f} {y1 - bot + 2 * pad + 40:.0f}"
    start, step = 0.35, 0.11                       # seconds
    end = start + step * len(gl)
    total = end + 1.6                              # two blinks, then the caret leaves
    css = [f".g{{opacity:0;animation:in .01s linear forwards}}",
           "@keyframes in{to{opacity:1}}",
           f".k{{animation:mv {total:.2f}s linear forwards}}"]
    for i in range(len(gl)):
        css.append(f".g{i}{{animation-delay:{start + step * i:.2f}s}}")
    # caret path: sits before C, jumps after each glyph, blinks twice, fades out
    pct = lambda t: f"{100 * t / total:.2f}%"
    kf = [f"0%{{transform:translateX({x0 - gap - cw:.0f}px);opacity:1}}"]
    for i, (_, _, right) in enumerate(gl):
        t = start + step * i
        kf.append(f"{pct(t)}{{transform:translateX({right + gap:.0f}px);opacity:1}}")
    last = gl[-1][2] + gap
    for j, (t, o) in enumerate([(end + .25, 0), (end + .5, 1), (end + .75, 0), (end + 1.0, 1), (end + 1.4, 0)]):
        kf.append(f"{pct(t)}{{transform:translateX({last:.0f}px);opacity:{o}}}")
    kf.append(f"100%{{transform:translateX({last:.0f}px);opacity:0}}")
    css.append("@keyframes mv{" + "".join(kf) + "}")
    css.append("@media (prefers-reduced-motion:reduce){.g{opacity:1;animation:none}.k{display:none}}")
    body = "".join(f'<path class="g g{i}" fill="{ink if role == "ink" else green}" d="{dd}"/>'
                   for i, (dd, role, _) in enumerate(gl))
    caret = (f'<g class="k"><rect x="0" y="{-top}" width="{cw}" height="{top - bot}" rx="{cw / 2}" '
             f'fill="{green}"/></g>')
    return (f'<svg viewBox="{vb}" {NS} role="img" aria-label="ChatCRM"><style>{"".join(css)}</style>'
            f'<g transform="scale(1 -1)">{body}</g>{caret}</svg>')


# ---------------------------------------------------------------- social preview

def tagline(text, weight=400):
    """Plain Outfit text (no wordmark tracking) as one outline."""
    import build_v15
    from build_v9 import union
    saved, build_v15.TRACK = build_v15.TRACK, 0
    try:
        words, _ = set_word(text, weight, 0)
    finally:
        build_v15.TRACK = saved
    u = union(*[p for _, p in words])
    return path_d(u), u.bounds


TAGLINE_EN = "WhatsApp conversations that turn into customers"
TAGLINE_ES = "Conversaciones de WhatsApp que se convierten en clientes"

# per-repo label shown on its social preview
REPO_LABELS = {"api": "API · NestJS", "app": "Web app · React", "ia": "AI · Sentiment analysis"}


def _text(text, weight, x_center, top, cap_px, fill, opacity=1.0):
    """Centred outlined Outfit text whose cap height is `cap_px`; returns (svg, width_px, x_left)."""
    td, (tx0, _, tx1, _) = tagline(text, weight)
    s = cap_px / 700
    w = (tx1 - tx0) * s
    x = x_center - w / 2 - tx0 * s
    return (f'<g transform="translate({x:.1f} {top + 742 * s:.1f}) scale({s:.4f} {-s:.4f})">'
            f'<path fill="{fill}" fill-opacity="{opacity}" d="{td}"/></g>'), w, x_center - w / 2


def hero_svg(W, H, surface="night", text=TAGLINE_EN, label=None, lock_w=760, radius=0, rule=True):
    """Logo + tagline with the brand caret; optional repo label chip above the logo."""
    import re
    bg, fg = (NIGHT, FROST) if surface == "night" else (PAPER, INK)
    caret_c = MINT if surface == "night" else DEEP
    lock = lockup_svg(surface, "")
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', lock).group(1).split()]
    lh = lock_w * vb[3] / vb[2]
    cap = lock_w * 0.032                              # tagline cap height scales with the logo
    gap = cap * 1.5
    chip_h = cap * 2.1 if label else 0
    block = chip_h + (gap * 1.4 if label else 0) + lh + gap + cap * 1.25
    y0 = (H - block) / 2
    parts = []
    if label:
        lt, lw, lx = _text(label, 600, W / 2, y0 + (chip_h - cap * 0.9) / 2, cap * 0.9,
                           MINT if surface == "night" else DEEP)
        pad = cap * 1.1
        chip_bg = "#0d2a1c" if surface == "night" else "#e3f3ea"
        parts.append(f'<rect x="{lx - pad:.1f}" y="{y0:.1f}" width="{lw + 2 * pad:.1f}" height="{chip_h:.1f}" '
                     f'rx="{chip_h / 2:.1f}" fill="{chip_bg}"/>{lt}')
        y0 += chip_h + gap * 1.4
    parts.append(lock.replace('<svg ', f'<svg width="{lock_w:.0f}" height="{lh:.0f}" x="{(W - lock_w) / 2:.0f}" '
                                       f'y="{y0:.1f}" ', 1))
    ty = y0 + lh + gap
    cw = cap * 0.1 + 2
    tt, tw, tx = _text(text, 400, W / 2 - (cw + cap * 0.35) / 2, ty, cap, fg, .72)
    parts.append(tt)
    parts.append(f'<rect x="{tx + tw + cap * 0.35:.1f}" y="{ty - cap * 0.12:.1f}" width="{cw:.1f}" '
                 f'height="{cap * 1.24:.1f}" rx="{cw / 2:.1f}" fill="{caret_c}"/>')
    frame = f'<rect width="{W}" height="{H}" rx="{radius}" fill="{bg}"/>'
    if rule:
        frame += (f'<clipPath id="hc"><rect width="{W}" height="{H}" rx="{radius}"/></clipPath>'
                  f'<rect x="0" y="{H - 8}" width="{W}" height="8" fill="{DEEP}" clip-path="url(#hc)"/>')
    return f'<svg viewBox="0 0 {W} {H}" {NS} role="img" aria-label="ChatCRM — {text}">{frame}{"".join(parts)}</svg>'


def social_svg(label=None):
    return hero_svg(1280, 640, "night", TAGLINE_EN, label=label)


# ---------------------------------------------------------------- build

def build():
    svg_dir, png_dir = OUT / "svg", OUT / "png"
    for d_ in (svg_dir, png_dir, OUT / "favicon", OUT / "github", OUT / "animated"):
        d_.mkdir(parents=True, exist_ok=True)

    pieces = {
        "wordmark": lambda s, a: wordmark_svg(s, a),
        "lockup": lambda s, a: lockup_svg(s, a),
        "lockup-badge": lambda s, a: lockup_svg(s, a, badge=True),
        "symbol": lambda s, a: symbol(s, a),
        "badge": lambda s, a: badge(s, a),
    }
    for name, fn in pieces.items():
        for tone, surf in SURFACES.items():
            if name == "badge" and tone == "dark":
                continue                                    # the badge carries its own background
            fname = f"chatcrm-{name}.svg" if name == "badge" and tone == "light" else f"chatcrm-{name}-{tone}.svg"
            (svg_dir / fname).write_text(fn(surf, label("")) + "\n", encoding="utf-8")

    # transparent PNGs
    for tone in ("light", "dark"):
        surf = SURFACES[tone]
        for w in (512, 1024, 2048):
            save_png(png_dir / f"chatcrm-wordmark-{tone}-{w}.png", padded(wordmark_svg(surf, NS)), width=w)
            save_png(png_dir / f"chatcrm-lockup-{tone}-{w}.png", padded(lockup_svg(surf, NS)), width=w)
            save_png(png_dir / f"chatcrm-lockup-badge-{tone}-{w}.png", padded(lockup_svg(surf, NS, badge=True)), width=w)
        for w in (256, 512, 1024):
            save_png(png_dir / f"chatcrm-symbol-{tone}-{w}.png", symbol(surf, NS), width=w)
    for w in (64, 128, 256, 512, 1024):
        save_png(png_dir / f"chatcrm-badge-{w}.png", badge("paper", NS), width=w)

    # favicons
    fav = OUT / "favicon"
    (fav / "favicon.svg").write_text(badge("paper", NS, small=True) + "\n", encoding="utf-8")
    imgs = {s: Image.open(io.BytesIO(png(badge("paper", NS, small=True), width=s))).convert("RGBA")
            for s in (16, 32, 48)}
    imgs[48].save(fav / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=[imgs[16], imgs[32]])
    for s in (16, 32, 48):
        imgs[s].save(fav / f"favicon-{s}.png")
    save_png(fav / "apple-touch-icon.png", badge("paper", NS, full_bleed=True), width=180)
    save_png(fav / "icon-192.png", badge("paper", NS), width=192)
    save_png(fav / "icon-512.png", badge("paper", NS), width=512)
    save_png(fav / "icon-maskable-512.png", badge("paper", NS, full_bleed=True), width=512)

    # GitHub
    gh = OUT / "github"
    for s in (500, 1024):
        save_png(gh / f"avatar-{s}.png", badge("paper", NS, full_bleed=True), width=s)
    soc = social_svg()
    (gh / "social-preview.svg").write_text(soc + "\n", encoding="utf-8")
    save_png(gh / "social-preview-1280x640.png", soc, width=1280, height=640)
    for repo, lab in REPO_LABELS.items():
        save_png(gh / f"social-preview-{repo}.png", social_svg(lab), width=1280, height=640)
    # organization profile banner (GitHub README width ≈ 830 px; shipped as SVG, theme-aware via <picture>)
    for tone, surf in (("light", "paper"), ("dark", "night")):
        for lang, text in (("en", TAGLINE_EN), ("es", TAGLINE_ES)):
            ban = hero_svg(1280, 400, surf, text, lock_w=640, radius=24, rule=False)
            (gh / f"profile-banner-{lang}-{tone}.svg").write_text(ban + "\n", encoding="utf-8")

    # animation
    (OUT / "animated" / "chatcrm-typing-light.svg").write_text(typing_svg("paper") + "\n", encoding="utf-8")
    (OUT / "animated" / "chatcrm-typing-dark.svg").write_text(typing_svg("night") + "\n", encoding="utf-8")

    (OUT / "index.html").write_text(sheet(), encoding="utf-8")


def sheet():
    A = 'aria-hidden="true"'
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — marca</title>
<link rel="icon" href="favicon/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:#5f6360; --hair:rgba(23,23,23,.12); --card:#fff; --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d;
  --hair:rgba(226,232,240,.12); --card:#161616; --acc:{MINT}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d; --hair:rgba(226,232,240,.12); --card:#161616; --acc:{MINT}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:Outfit,system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1080px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; border-bottom:1px solid var(--hair);
  font-size:13px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:999px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }}
.hero {{ margin-top:32px; border:1px solid var(--hair); border-radius:20px; display:grid; place-items:center; padding:clamp(56px,10vw,110px) 20px; }}
.hero img {{ width:min(560px,86%); height:auto; }}
h2 {{ font-size:26px; font-weight:700; letter-spacing:-.02em; margin:56px 0 6px; }}
.lead {{ color:var(--muted); line-height:1.6; max-width:70ch; margin-bottom:18px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:10px; }}
figure {{ border:1px solid var(--hair); border-radius:18px; overflow:hidden; }}
figure > div {{ display:grid; place-items:center; padding:36px 18px; min-height:170px; }}
figure img {{ max-width:84%; max-height:110px; }}
figcaption {{ padding:10px 14px; font-size:13px; color:var(--muted); border-top:1px solid var(--hair); background:var(--card); }}
figcaption b {{ display:block; color:var(--fg); }} figcaption a {{ color:var(--acc); }}
.social img {{ width:100%; border-radius:14px; display:block; }}
.sw {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }}
.sw div {{ border:1px solid var(--hair); border-radius:14px; overflow:hidden; background:var(--card); }}
.sw i {{ display:block; height:72px; }} .sw p {{ padding:10px 12px; font-size:13px; color:var(--muted); }} .sw b {{ display:block; color:var(--fg); }}
.anim {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:48px 18px; }}
.anim object {{ width:min(460px,86%); }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · marca</span><button id="t">Claro / oscuro</button></div>
  <div class="hero paper"><img src="svg/chatcrm-lockup-light.svg" alt="ChatCRM"></div>

  <h2>Piezas</h2>
  <p class="lead">Todo en <code>svg/</code> (vectorial) y <code>png/</code> (transparente). «light» = para fondos claros,
  «dark» = para fondos oscuros, «mono» = una tinta con <code>currentColor</code>.</p>
  <div class="grid">
    <figure><div class="paper"><img src="svg/chatcrm-wordmark-light.svg" alt=""></div><figcaption><b>Wordmark</b><a href="svg/chatcrm-wordmark-light.svg">claro</a> · <a href="svg/chatcrm-wordmark-dark.svg">oscuro</a> · <a href="svg/chatcrm-wordmark-mono.svg">mono</a></figcaption></figure>
    <figure><div class="night"><img src="svg/chatcrm-wordmark-dark.svg" alt=""></div><figcaption><b>Wordmark sobre oscuro</b>chatcrm-wordmark-dark</figcaption></figure>
    <figure><div class="paper"><img src="svg/chatcrm-lockup-light.svg" alt=""></div><figcaption><b>Logo (símbolo + nombre)</b><a href="svg/chatcrm-lockup-light.svg">claro</a> · <a href="svg/chatcrm-lockup-dark.svg">oscuro</a></figcaption></figure>
    <figure><div class="night"><img src="svg/chatcrm-lockup-badge-dark.svg" alt=""></div><figcaption><b>Logo con insignia</b><a href="svg/chatcrm-lockup-badge-light.svg">claro</a> · <a href="svg/chatcrm-lockup-badge-dark.svg">oscuro</a></figcaption></figure>
    <figure><div class="paper"><img src="svg/chatcrm-symbol-light.svg" alt=""></div><figcaption><b>Símbolo</b><a href="svg/chatcrm-symbol-light.svg">claro</a> · <a href="svg/chatcrm-symbol-dark.svg">oscuro</a></figcaption></figure>
    <figure><div class="paper"><img src="svg/chatcrm-badge.svg" alt=""></div><figcaption><b>Insignia</b><a href="svg/chatcrm-badge.svg">svg</a> · <a href="png/chatcrm-badge-1024.png">png 1024</a></figcaption></figure>
  </div>

  <h2>GitHub</h2>
  <p class="lead">Avatar de la organización (<code>github/avatar-500.png</code>, GitHub redondea las esquinas) y la imagen
  para compartir del repositorio (Settings → Social preview).</p>
  <div class="grid">
    <figure><div class="paper"><img src="github/avatar-500.png" alt="" style="border-radius:16px;max-height:140px"></div><figcaption><b>Avatar</b>avatar-500.png · avatar-1024.png</figcaption></figure>
  </div>
  <div class="social" style="margin-top:10px"><img src="github/social-preview-1280x640.png" alt="ChatCRM — vista previa social"></div>

  <h2>Animación</h2>
  <p class="lead">Para la carga o el login: el nombre se escribe, el cursor parpadea dos veces y se va. Se reproduce
  una vez y respeta «reducir movimiento». Recarga la página para verla otra vez.</p>
  <div class="anim paper"><object data="animated/chatcrm-typing-light.svg" type="image/svg+xml" aria-label="ChatCRM"></object></div>

  <h2>Color</h2>
  <div class="sw">
    <div><i style="background:{DEEP}"></i><p><b>Verde profundo</b>{DEEP} · CRM, insignia</p></div>
    <div><i style="background:{MINT}"></i><p><b>Menta</b>{MINT} · CRM en oscuro</p></div>
    <div><i style="background:{INK}"></i><p><b>Tinta</b>{INK} · Chat en claro</p></div>
    <div><i style="background:{FROST}"></i><p><b>Escarcha</b>{FROST} · Chat en oscuro</p></div>
    <div><i style="background:{PAPER};border-bottom:1px solid var(--hair)"></i><p><b>Papel</b>{PAPER} · fondo claro</p></div>
    <div><i style="background:{NIGHT}"></i><p><b>Noche</b>{NIGHT} · fondo oscuro</p></div>
  </div>
</div>
<script>
const r=document.documentElement;
document.getElementById('t').onclick=()=>{{const dk=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;r.dataset.theme=dk?'light':'dark';}};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
    n = sum(1 for p in OUT.rglob("*") if p.is_file())
    print("ok:", n, "files in", OUT)
