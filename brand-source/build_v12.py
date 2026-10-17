"""Brand draft 12 — rounded Outfit wordmark + CC monogram.

    python brand-source/build_v12.py

The symbol (two C's closing a circle) has round caps, so the lettering follows: Outfit 700 outlines
get their corners rounded by a morphological opening (shrink by r, grow back by r with round joins,
pyclipper). That rounds every convex corner with radius r and keeps Outfit's proportions intact.
The caret becomes a pill. Two levels: soft (r=28) and round (r=58, stem = 153).
Needs: fonttools, uharfbuzz, skia-pathops, pyclipper.
"""
import math
from pathlib import Path

import pyclipper
from fontTools.pens.basePen import BasePen

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER
from build_v11 import CARET_BOT, CARET_GAP, CARET_TOP, CARET_W, TRACK, s_link
from build_v9 import d, glyph, shape, union

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v12"
SCALE = 16                          # pyclipper works on integers: 1/16 font unit precision

LEVELS = [
    ("square", "Recto (v11)", 0, "Outfit 700 tal cual: esquinas rectas. Como referencia de partida."),
    ("soft", "Suave", 28, "Esquinas redondeadas con radio 28 (18 % del asta). Sigue siendo Outfit a primera "
     "vista, pero las terminaciones ya conversan con las puntas redondas del símbolo."),
    ("round", "Redondo", 58, "Radio 58 (38 % del asta): terminaciones claramente redondas, como las del "
     "símbolo. Más amigable, en la línea de Intercom o Notion, y sin perder el dibujo de Outfit."),
]


class _Flatten(BasePen):
    """Collects contours as point lists, sampling curves finely."""

    def __init__(self):
        super().__init__(None)
        self.contours, self._cur = [], []

    def _moveTo(self, p):
        self._cur = [p]

    def _lineTo(self, p):
        self._cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for i in range(1, 25):
            t = i / 24
            mt = 1 - t
            self._cur.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                              mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, 17):
            t = i / 16
            mt = 1 - t
            self._cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                              mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self._cur) > 2:
            self.contours.append(self._cur)
        self._cur = []

    _endPath = _closePath


def rounded(path, r):
    """Round convex corners of a pathops path with radius r (font units). Returns SVG path data."""
    pen = _Flatten()
    path.draw(pen)
    polys = [[(round(x * SCALE), round(y * SCALE)) for x, y in c] for c in pen.contours]
    if r > 0:
        off = pyclipper.PyclipperOffset(arc_tolerance=0.08 * SCALE)
        off.AddPaths(polys, pyclipper.JT_MITER, pyclipper.ET_CLOSEDPOLYGON)
        shrunk = off.Execute(-r * SCALE)
        off = pyclipper.PyclipperOffset(arc_tolerance=0.08 * SCALE)
        off.AddPaths(shrunk, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)
        polys = off.Execute(r * SCALE)
    out = []
    for poly_ in polys:
        pts = pyclipper.CleanPolygon(poly_, 0.3 * SCALE)
        out.append("M" + "L".join(f"{x / SCALE:.1f} {y / SCALE:.1f}" for x, y in pts) + "Z")
    return "".join(out)


def pill(x, y0, w, y1):
    r = w / 2
    return (f"M{x} {y0 + r}A{r} {r} 0 0 1 {x + w} {y0 + r}V{y1 - r}A{r} {r} 0 0 1 {x} {y1 - r}Z")


_cache = {}


def wordmark_parts(level):
    if level in _cache:
        return _cache[level]
    r = dict((k, rr) for k, _, rr, _ in LEVELS)[level]
    chat, chat_adv = shape("Chat", TRACK)
    letters = [glyph(n, x) for n, x in chat]
    cx = chat_adv + CARET_GAP
    crm, _ = shape("CRM", TRACK)
    dx = cx + CARET_W + CARET_GAP
    letters += [glyph(n, x + dx) for n, x in crm]
    u = union(*letters)
    if r:
        letters_d = rounded(u, r)
        caret_d = pill(cx, CARET_BOT, CARET_W, CARET_TOP)
    else:
        letters_d = d(u)
        caret_d = f"M{cx} {CARET_BOT}H{cx + CARET_W}V{CARET_TOP}H{cx}Z"
    b = u.bounds
    bounds = (b[0], min(b[1], CARET_BOT), max(b[2], cx + CARET_W), max(b[3], CARET_TOP))
    _cache[level] = (letters_d, caret_d, bounds)
    return _cache[level]


# surface -> (symbol a, symbol b, word ink, caret, badge bg, badge a, badge b)
SURF = {
    "paper": (DEEP, MINT, INK, DEEP, DEEP, PAPER, MINT),
    "night": (MINT, "#2FA36B", FROST, MINT, DEEP, PAPER, MINT),
    "mono":  ("currentColor",) * 7,
}


def wordmark_g(level, ink, acc):
    letters, caret, _ = wordmark_parts(level)
    return f'<g transform="scale(1 -1)"><path fill="{ink}" d="{letters}"/><path fill="{acc}" d="{caret}"/></g>'


def wordmark_svg(level, surf, attrs='aria-hidden="true"', pad=40):
    _, _, ink, acc, *_ = SURF[surf]
    x0, y0, x1, y1 = wordmark_parts(level)[2]
    return (f'<svg viewBox="{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}" {attrs}>'
            f'{wordmark_g(level, ink, acc)}</svg>')


def symbol_svg(surf, attrs='aria-hidden="true"', mono=False):
    a, b = SURF[surf][:2]
    _, body = s_link(a, a if mono else b, "s")
    return f'<svg viewBox="0 0 100 100" {attrs}>{body}</svg>'


def badge_svg(surf, attrs='aria-hidden="true"'):
    *_, bg, a, b = SURF[surf]
    _, body = s_link(a, b, "b")
    return (f'<svg viewBox="0 0 100 100" {attrs}><rect width="100" height="100" rx="23" fill="{bg}"/>'
            f'<g transform="translate(18 18) scale(.64)">{body}</g></svg>')


def lockup_svg(level, surf, attrs='aria-hidden="true"', badge=False):
    a, b, ink, acc, bg, ba, bb = SURF[surf]
    cap = 706
    x0, y0, x1, y1 = wordmark_parts(level)[2]
    size = cap * (1.42 if badge else 1.36)
    sy = -cap / 2 - size / 2
    if badge:
        _, body = s_link(ba, bb, "l")
        sym = (f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})"><rect width="100" height="100" rx="23" '
               f'fill="{bg}"/><g transform="translate(18 18) scale(.64)">{body}</g></g>')
        lead, left = 0, 0
    else:
        _, body = s_link(a, b, "l")
        sym = f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})">{body}</g>'
        left = size * 0.15                     # the ring spans 15..85 of its 100 box
        lead = -left
    gx = size + cap * 0.34 - x0 + lead
    vx0, vy0 = left - 30, min(sy, -y1) - 30
    w, h = gx + x1 + 30 - vx0, max(sy + size, -y0) - vy0 + 30
    return (f'<svg viewBox="{vx0:.0f} {vy0:.0f} {w:.0f} {h:.0f}" {attrs}>{sym}'
            f'<g transform="translate({gx:.1f} 0)">{wordmark_g(level, ink, acc)}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for surf in ("paper", "night", "mono"):
        sfx = "" if surf == "mono" else f"-{surf}"
        (OUT / f"symbol{sfx}.svg").write_text(symbol_svg(surf, x, mono=surf == "mono") + "\n", encoding="utf-8")
        (OUT / f"badge{sfx}.svg").write_text(badge_svg(surf, x) + "\n", encoding="utf-8")
        for key, *_ in LEVELS[1:]:
            (OUT / f"wordmark-{key}{sfx}.svg").write_text(wordmark_svg(key, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-{key}{sfx}.svg").write_text(lockup_svg(key, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-badge-{key}{sfx}.svg").write_text(lockup_svg(key, surf, x, badge=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def page():
    compare = "".join(f"""
    <article class="lv" id="{k}">
      <div class="cap"><span class="idx">{t}</span><span class="r">{'radio ' + str(r) if r else 'sin redondeo'}</span></div>
      <p>{desc}</p>
      <div class="stage paper">{lockup_svg(k, "paper")}</div>
      <div class="pair"><div class="night">{lockup_svg(k, "night")}</div><div class="paper">{lockup_svg(k, "paper", badge=True)}</div></div>
      <div class="zoom paper">{wordmark_svg(k, "paper")}</div>
    </article>""" for k, t, r, desc in LEVELS)
    sizes = "".join(f'<span style="width:{s}px;height:{s}px">{badge_svg("paper")}</span>' for s in (16, 24, 32, 48, 64, 96))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — draft 12</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:#5f6360; --hair:rgba(23,23,23,.12); --card:#fff; --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d;
  --hair:rgba(226,232,240,.12); --card:#161616; --acc:{MINT}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d; --hair:rgba(226,232,240,.12); --card:#161616;
  --acc:{MINT}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:Outfit,system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1080px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; border-bottom:1px solid var(--hair);
  font-size:13px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:999px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }}
.intro {{ padding:56px 0 12px; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:700; letter-spacing:-.03em; line-height:1.05; }}
.intro p {{ margin-top:16px; color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; max-width:66ch; }}
.lv {{ border-top:1px solid var(--hair); margin-top:44px; padding-top:40px; }}
.cap {{ display:flex; gap:14px; align-items:baseline; }}
.idx {{ font-size:28px; font-weight:700; letter-spacing:-.02em; }} .r {{ color:var(--muted); font-size:14px; }}
.lv > p {{ color:var(--muted); line-height:1.6; max-width:70ch; margin:8px 0 18px; font-size:16px; }}
.stage {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:clamp(40px,7vw,80px) 20px; }}
.stage svg {{ width:min(540px,88%); height:auto; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }}
@media (max-width:640px) {{ .pair {{ grid-template-columns:1fr; }} }}
.pair div {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:30px 16px; }}
.pair svg {{ width:min(290px,86%); height:auto; }}
.zoom {{ border:1px solid var(--hair); border-radius:18px; margin-top:10px; overflow:hidden; height:clamp(160px,26vw,260px); position:relative; }}
.zoom svg {{ position:absolute; height:118%; width:auto; left:3%; top:-9%; }}
.kit {{ border-top:1px solid var(--hair); margin-top:44px; padding-top:40px; }}
h2 {{ font-size:28px; font-weight:700; letter-spacing:-.02em; }}
.kit > p {{ color:var(--muted); line-height:1.6; max-width:70ch; margin:8px 0 18px; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; }}
.tile {{ position:relative; aspect-ratio:1; border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; }}
.tile svg {{ width:54%; height:54%; }} .tile span {{ position:absolute; left:12px; bottom:10px; font-size:11px; color:#8a8f8c; }}
.sizes {{ display:flex; gap:18px; align-items:flex-end; flex-wrap:wrap; border:1px solid var(--hair); border-radius:18px;
  padding:20px; margin-top:10px; background:var(--card); }}
.sizes > span svg {{ width:100%; height:100%; display:block; }}
.gh {{ margin-left:auto; display:flex; gap:12px; align-items:center; }} .gh .av {{ width:56px; height:56px; }}
.gh .av svg {{ width:100%; height:100%; display:block; }} .gh b {{ font-size:19px; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · draft 12</span><button id="t">Claro / oscuro</button></div>
  <section class="intro">
    <h1>Todo redondo,<br>como el símbolo</h1>
    <p>El monograma CC termina en puntas redondas, así que el resto lo sigue: el cursor es ahora una píldora y
    las letras de Outfit tienen las esquinas redondeadas (R, M, t, h, C…) sin cambiar su dibujo ni sus
    proporciones. Compara tres niveles; el recto es la referencia de v11. Abajo de cada uno, un acercamiento
    para ver las terminaciones.</p>
  </section>
  {compare}
  <section class="kit"><h2>Símbolo e insignia</h2>
    <p>Las dos «C» con las mismas puntas redondas que ahora tienen las letras y el cursor.</p>
    <div class="tiles">
      <div class="tile paper">{symbol_svg("paper")}<span>símbolo</span></div>
      <div class="tile paper">{badge_svg("paper")}<span>insignia · GitHub</span></div>
      <div class="tile night">{badge_svg("night")}<span>insignia · oscuro</span></div>
      <div class="tile paper">{symbol_svg("paper", mono=True)}<span>una tinta</span></div>
    </div>
    <div class="sizes">{sizes}<div class="gh"><span class="av">{badge_svg("paper")}</span><b>chat-crm-suite</b></div></div>
    <code>v12/symbol*.svg · badge*.svg · wordmark-soft*.svg · wordmark-round*.svg · lockup-*.svg</code>
  </section>
  <p class="foot">Dime qué nivel de redondeo quieres (suave o redondo, o un punto intermedio) y cierro los archivos finales.</p>
</div>
<script>
const r=document.documentElement;
document.getElementById('t').onclick=()=>{{const dk=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;r.dataset.theme=dk?'light':'dark';}};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    write_files()
    (ROOT / "showcase-v12.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
