"""Brand draft 15 — polishing the ChatCRM wordmark (v14 "none": Chat 600 + CRM 800 green, rounded).

    python brand-source/build_v15.py

Four corrections, each shown before/after on the page:
  1. One top line: h and t raised/lowered to the cap height; CRM scaled so its caps match Chat's C.
  2. Optical spacing per pair (the t→C seam was 12 units, R→M 20) instead of one tracking value.
  3. Inner corners rounded too (morphological closing), so joins match the soft outer corners.
  4. CRM (weight 800) scaled 703/709 so both C's are perceived at the same size.
"""
from pathlib import Path

import pathops
import pyclipper
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER, _font
from build_v11 import s_link
from build_v12 import SCALE, _Flatten
from build_v13 import ROUND, STEMS
from build_v14 import lockup_svg as before_lockup, wordmark_svg as before_wordmark

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v15"

WC, WR = 600, 800
TRACK = -38                         # font units, baseline tracking before optical pairs
CAP = 703                           # the one top line (Chat's cap height)
CRM_SCALE = CAP / 709               # CRM 800 caps → 703
# Inner corners: Outfit has small ink-trap notches at joins (h shoulder, a, R bowl/leg). They are
# filled selectively: a closing with radius NOTCH_R × stem finds every concave region; only the small
# ones (< NOTCH_MAX units²) are kept, so real spaces such as the R's leg/bowl gap are never touched.
# Then every remaining inner corner gets a light fillet of INNER × stem.
INNER = {"h": 0.10, "a": 0.10, "t": 0.10, "C": 0.0, "R": 0.10, "M": 0.10}
NOTCH_R, NOTCH_MIN, NOTCH_MAX = 0.30, 20, 1100    # slivers along curves are < 5 units²
NOTCH_FLOOR = 20                    # regions touching the baseline are outer contour, not notches
# optical pair adjustments on top of TRACK (font units, + opens)
PAIRS = {("C", "h"): -4, ("h", "a"): 0, ("a", "t"): 2, ("t", "C"): 34, ("C", "R"): 4, ("R", "M"): 14}


class _TopPen(TransformPen):
    """Moves the flat top of a stem (every point within 2 units of the glyph's top) to `top`."""

    def __init__(self, pen, matrix, ymax, top):
        super().__init__(pen, matrix)
        self._ymax, self._top = ymax, top

    def _fix(self, pts):
        return [(x, self._top if y >= self._ymax - 2 else y) for x, y in pts]

    def moveTo(self, p):
        super().moveTo(*self._fix([p]))

    def lineTo(self, p):
        super().lineTo(*self._fix([p]))

    def curveTo(self, *pts):
        super().curveTo(*self._fix(pts))

    def qCurveTo(self, *pts):
        super().qCurveTo(*[q if q is None else self._fix([q])[0] for q in pts])


def _draw_m(glyph, pen):
    """Outfit's M: the inner stem edges rise past the diagonals (a small spur). Move each inner stem top
    to where the diagonal actually meets the stem, so the join is clean."""
    from fontTools.pens.recordingPen import RecordingPen
    rec = RecordingPen()
    glyph.draw(rec)
    ops = rec.value
    pts = [a[0] if a else None for _, a in ops]
    out, skip = [], set()
    for i, (op, args) in enumerate(ops):
        if i in skip or op != "lineTo" or i + 2 >= len(ops) or ops[i + 1][0] != "lineTo" or ops[i + 2][0] != "lineTo":
            continue
        (x0, y0), (x1, y1), (x2, y2) = pts[i], pts[i + 1], pts[i + 2]
        prev = pts[i - 1]
        # right inner stem: vertical edge up to (x0,y0), spur to (x1,y1), diagonal down to (x2,y2)
        if prev and prev[0] == x0 and y0 > prev[1] and x1 > x0 and y1 < y0 and y2 < y1:
            yi = y1 - (x1 - x0) * (y1 - y2) / (x1 - x2)
            ops[i] = ("lineTo", ((x0, yi),))
            skip.add(i + 1)
    # left inner stem (mirror): diagonal up to (x0,y0), spur to (x1,y1), vertical edge down from x1
    for i, (op, args) in enumerate(ops):
        if op != "lineTo" or i + 2 >= len(ops) or i in skip:
            continue
        nxt = ops[i + 1]
        if nxt[0] != "lineTo" or ops[i + 2][0] != "lineTo":
            continue
        (x0, y0), (x1, y1), (x2, y2) = pts[i], pts[i + 1], pts[i + 2]
        prev = pts[i - 1]
        if prev and x2 == x1 and y2 < y1 and x1 > x0 and y1 > y0 and prev[1] < y0 and prev[0] > x0:
            yi = y0 + (x1 - x0) * (y0 - prev[1]) / (x0 - prev[0])
            ops[i] = ("lineTo", ((x1, yi),))
            skip.add(i + 1)
    ops = [o for j, o in enumerate(ops) if j not in skip]
    from fontTools.pens.recordingPen import replayRecording
    replayRecording(ops, pen)


def set_word(text, weight, x0, scale=1.0, align_tops=False, pairs=None):
    """Shape `text`; returns [(name, pathops path)] and the x after the last glyph's advance."""
    static, hbfont = _font("Outfit.ttf", {"wght": weight})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    order, gs = static.getGlyphOrder(), static.getGlyphSet()
    x, out, prev = x0, [], None
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        if prev and pairs:
            x += pairs.get((prev, name), 0)
        p = pathops.Path()
        m = (scale, 0, 0, scale, x + pos.x_offset * scale, 0)
        if name == "M":
            _draw_m(gs[name], TransformPen(p.getPen(glyphSet=gs), m))
        elif align_tops and name in ("h", "t"):
            from fontTools.pens.boundsPen import BoundsPen
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            gs[name].draw(_TopPen(p.getPen(glyphSet=gs), m, bp.bounds[3], CAP / scale))
        else:
            gs[name].draw(TransformPen(p.getPen(glyphSet=gs), m))
        out.append((name, pathops.op(p, pathops.Path(), pathops.PathOp.UNION)))
        x += pos.x_advance * scale + TRACK
        prev = name
    return out, x


def soften(path, r_out, r_in, notch_r=0.0):
    """Fill small notches (closing with notch_r, small regions only), then round convex corners with
    r_out and concave corners with r_in. Returns SVG path data."""
    pen = _Flatten()
    path.draw(pen)
    polys = [[(round(x * SCALE), round(y * SCALE)) for x, y in c] for c in pen.contours]

    def offset(paths, delta, join):
        o = pyclipper.PyclipperOffset(arc_tolerance=0.08 * SCALE)
        o.AddPaths(paths, join, pyclipper.ET_CLOSEDPOLYGON)
        return o.Execute(delta * SCALE)

    def boolean(a, b, op):
        c = pyclipper.Pyclipper()
        c.AddPaths(a, pyclipper.PT_SUBJECT, True)
        c.AddPaths(b, pyclipper.PT_CLIP, True)
        return c.Execute(op, pyclipper.PFT_NONZERO, pyclipper.PFT_NONZERO)
    if notch_r:
        closed = offset(offset(polys, notch_r, pyclipper.JT_ROUND), -notch_r, pyclipper.JT_ROUND)
        extra = [q for q in boolean(closed, polys, pyclipper.CT_DIFFERENCE)
                 if NOTCH_MIN < abs(pyclipper.Area(q)) / SCALE ** 2 < NOTCH_MAX
                 and min(y for _, y in q) > NOTCH_FLOOR * SCALE]
        if extra:
            polys = boolean(polys, extra, pyclipper.CT_UNION)
    polys = offset(polys, -r_out, pyclipper.JT_MITER)
    polys = offset(polys, r_out + r_in, pyclipper.JT_ROUND)
    if r_in:
        polys = offset(polys, -r_in, pyclipper.JT_ROUND)
    return "".join("M" + "L".join(f"{x / SCALE:.1f} {y / SCALE:.1f}" for x, y in pyclipper.CleanPolygon(p, 0.3 * SCALE)) + "Z"
                   for p in polys)


_cache = {}


def parts(steps=(1, 2, 3, 4)):
    """Wordmark with the given corrections applied. Returns (chat_d, crm_d, bounds)."""
    key = tuple(steps)
    if key in _cache:
        return _cache[key]
    pairs = PAIRS if 2 in steps else {("t", "C"): 6 + 38 - 38}     # v14 seam: adv + 6
    chat, x = set_word("Chat", WC, 0, align_tops=1 in steps, pairs=pairs)
    if 2 in steps:
        x += pairs[("t", "C")]
    else:
        x += 6
    sc = CRM_SCALE if 4 in steps else 1.0
    crm, _ = set_word("CRM", WR, x, scale=sc, pairs=pairs if 2 in steps else None)
    k = 1 if 3 in steps else 0
    chat_d = "".join(soften(p, STEMS[WC] * ROUND, STEMS[WC] * INNER[n] * k, STEMS[WC] * NOTCH_R * k)
                     for n, p in chat)
    crm_d = "".join(soften(p, STEMS[WR] * ROUND * sc, STEMS[WR] * INNER[n] * sc * k, STEMS[WR] * NOTCH_R * sc * k)
                    for n, p in crm)
    bs = [p.bounds for _, p in chat + crm]
    bounds = (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
    _cache[key] = (chat_d, crm_d, bounds, [(n, p.bounds) for n, p in chat + crm])
    return _cache[key]


SURF = {
    "paper": (INK, DEEP, DEEP, MINT, DEEP, PAPER, MINT),
    "night": (FROST, MINT, MINT, "#2FA36B", DEEP, PAPER, MINT),
    "mono":  ("currentColor",) * 7,
}


def word_g(surf, steps=(1, 2, 3, 4)):
    ink, green = SURF[surf][:2]
    chat, crm, *_ = parts(steps)
    return f'<g transform="scale(1 -1)"><path fill="{ink}" d="{chat}"/><path fill="{green}" d="{crm}"/></g>'


def wordmark_svg(surf, attrs='aria-hidden="true"', pad=40, steps=(1, 2, 3, 4), extra="", vb=None):
    x0, y0, x1, y1 = parts(steps)[2]
    view = vb or (x0 - pad, -y1 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    return (f'<svg viewBox="{view[0]:.0f} {view[1]:.0f} {view[2]:.0f} {view[3]:.0f}" {attrs}>'
            f'{word_g(surf, steps)}{extra}</svg>')


def detail(n, steps):
    """Before/after crop for correction n, in font units (y down in the SVG)."""
    _, _, (x0, y0, x1, y1), gl = parts(steps)
    g = lambda i: gl[i][1]                      # glyph bounds: 0 C 1 h 2 a 3 t 4 C 5 R 6 M
    line = lambda y, c="#E5484D": (f'<line x1="{x0 - 200}" x2="{x1 + 200}" y1="{-y}" y2="{-y}" stroke="{c}" '
                                   f'stroke-width="4" stroke-dasharray="18 10"/>')
    if n == 1:
        tops = sorted({round(g(i)[3]) for i in (1, 3, 5)})
        return (x0 - 30, -790, x1 - x0 + 60, 380), "".join(line(t) for t in tops)
    if n == 2:
        a, b = g(2)[0] - 40, g(5)[2] + 40
        seam = (f'<rect x="{g(3)[2]:.0f}" y="-760" width="{g(4)[0] - g(3)[2]:.0f}" height="790" fill="#E5484D" '
                f'fill-opacity=".18"/>')
        return (a, -790, b - a, 840), seam
    if n == 3:
        a, b = g(1)[0] - 30, g(3)[2] + 30
        return (a, -560, b - a, 600), ""
    a, b = g(3)[0] - 20, g(4)[2] + 30
    return (a, -760, b - a, 800), line(g(0)[3], "#E5484D") + line(g(4)[3], "#3B82F6")


def lockup_svg(surf, attrs='aria-hidden="true"', badge=False):
    _, _, a, b, bg, ba, bb = SURF[surf]
    x0, y0, x1, y1 = parts()[2]
    size = CAP * (1.42 if badge else 1.36)
    sy = -CAP / 2 - size / 2
    if badge:
        _, body = s_link(ba, bb, "l")
        sym = (f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})"><rect width="100" height="100" rx="23" '
               f'fill="{bg}"/><g transform="translate(18 18) scale(.64)">{body}</g></g>')
        left = 0
    else:
        _, body = s_link(a, b, "l")
        sym = f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})">{body}</g>'
        left = size * 0.15
    gx = size - left + CAP * 0.32 - x0
    vx0, vy0 = left - 30, min(sy, -y1) - 30
    w, h = gx + x1 + 30 - vx0, max(sy + size, -y0) - vy0 + 30
    return (f'<svg viewBox="{vx0:.0f} {vy0:.0f} {w:.0f} {h:.0f}" {attrs}>{sym}'
            f'<g transform="translate({gx:.1f} 0)">{word_g(surf)}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for surf in ("paper", "night", "mono"):
        sfx = "" if surf == "mono" else f"-{surf}"
        (OUT / f"wordmark{sfx}.svg").write_text(wordmark_svg(surf, x) + "\n", encoding="utf-8")
        (OUT / f"lockup{sfx}.svg").write_text(lockup_svg(surf, x) + "\n", encoding="utf-8")
        (OUT / f"lockup-badge{sfx}.svg").write_text(lockup_svg(surf, x, badge=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def guides(steps):
    x0, y0, x1, y1 = parts(steps)[2]
    lines = "".join(f'<line x1="{x0 - 40}" x2="{x1 + 40}" y1="{-y}" y2="{-y}" stroke="#E5484D" stroke-width="3"/>'
                    for y in sorted({723, 684, 709, CAP} if steps == () else {CAP}))
    return lines


def _crop(n, steps):
    vb, extra = detail(n, steps)
    return wordmark_svg("paper", 'aria-hidden="true"', steps=steps, extra=extra, vb=vb)


def page():
    A = 'aria-hidden="true"'
    before = (lambda: before_wordmark("none", "paper"))
    steps_desc = [
        (1, "Una sola línea superior", "Antes la «h» (723), la «t» (684) y las mayúsculas de CRM (709) tenían tres "
         "alturas distintas. Ahora todas terminan en la misma línea (703, la altura de mayúscula de «Chat»): el "
         "nombre tiene un borde superior limpio, como un bloque."),
        (2, "Espaciado óptico por pares", "Antes todas las letras usaban la misma regla. El par «tC», justo donde se "
         "unen las dos palabras, quedaba a 12 unidades (casi se tocaban) y «RM» a 20. Ahora cada par está ajustado "
         "a ojo: «tC» +34, «RM» +14, ajustes finos en «Ch», «at» y «CR»."),
        (3, "Esquinas interiores redondeadas", "Las puntas exteriores ya eran redondas, pero las uniones interiores "
         "(el arco de la «h», la pierna de la R, el vértice de la M, la barra de la «t») seguían en ángulo vivo. "
         "Ahora también tienen un radio suave: todo el nombre parece del mismo material que el símbolo."),
        (4, "Las dos «C» del mismo tamaño", "En peso 800 la «C» de CRM medía 721 contra 714 de la «C» de Chat y se "
         "veía más grande. CRM se ajusta al 99,2 % para que ambas se perciban iguales."),
    ]
    rows = "".join(f"""
    <article class="fix">
      <div class="cap"><span class="idx">{n}</span><h3>{t}</h3></div><p>{d}</p>
      <div class="ba">
        <figure><div class="zoom">{_crop(n, tuple(s for s in (1, 2, 3, 4) if s < n))}</div><figcaption>Antes</figcaption></figure>
        <figure><div class="zoom">{_crop(n, tuple(s for s in (1, 2, 3, 4) if s <= n))}</div><figcaption>Después</figcaption></figure>
      </div>
    </article>""" for n, t, d in steps_desc)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — pulido</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:#5f6360; --hair:rgba(23,23,23,.12); --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d;
  --hair:rgba(226,232,240,.12); --acc:{MINT}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d; --hair:rgba(226,232,240,.12); --acc:{MINT}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:Outfit,system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1080px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; border-bottom:1px solid var(--hair);
  font-size:13px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:999px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:700; letter-spacing:-.03em; line-height:1.05; margin-top:56px; }}
.lede {{ margin-top:16px; color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; max-width:66ch; }}
.ba {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
@media (max-width:640px) {{ .ba {{ grid-template-columns:1fr; }} }}
figure {{ border:1px solid var(--hair); border-radius:18px; overflow:hidden; background:{PAPER}; }}
figcaption {{ padding:10px 14px; font-size:13px; color:#5f6360; border-top:1px solid rgba(23,23,23,.1); background:#fff; font-weight:600; }}
.hero figure > div {{ display:grid; place-items:center; padding:clamp(40px,6vw,70px) 16px; }}
.hero svg {{ width:88%; height:auto; }}
.hero {{ margin-top:28px; }}
.fix {{ border-top:1px solid var(--hair); margin-top:44px; padding-top:36px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; }}
.idx {{ font-size:13px; color:var(--muted); font-weight:600; }}
h3 {{ font-size:26px; font-weight:700; letter-spacing:-.02em; }}
.fix > p {{ color:var(--muted); line-height:1.6; max-width:72ch; margin:8px 0 16px; }}
.zoom {{ display:grid; place-items:center; padding:18px; height:clamp(170px,24vw,240px); }}
.zoom svg {{ width:100%; height:100%; }}
.final {{ border-top:1px solid var(--hair); margin-top:44px; padding-top:36px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:16px; }}
@media (max-width:640px) {{ .grid {{ grid-template-columns:1fr; }} }}
.grid div {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:40px 16px; }}
.grid svg {{ width:min(360px,88%); height:auto; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · pulido del wordmark</span><button id="t">Claro / oscuro</button></div>
  <h1>Mismo logo,<br>dibujado a mano</h1>
  <p class="lede">Cuatro correcciones finas sobre la versión sin cursor. Cada una se muestra antes y después con un
  acercamiento; los cambios se van acumulando de una a la siguiente.</p>
  <div class="ba hero">
    <figure><div>{before()}</div><figcaption>Antes (v14)</figcaption></figure>
    <figure><div>{wordmark_svg("paper", A)}</div><figcaption>Después (v15)</figcaption></figure>
  </div>
  {rows}
  <section class="final"><h3>Resultado</h3>
    <div class="grid">
      <div class="paper">{lockup_svg("paper")}</div>
      <div class="night">{lockup_svg("night")}</div>
      <div class="paper">{lockup_svg("paper", badge=True)}</div>
      <div class="night">{lockup_svg("night", badge=True)}</div>
      <div class="paper">{wordmark_svg("paper")}</div>
      <div class="night">{wordmark_svg("night")}</div>
    </div>
    <code>v15/wordmark.svg · lockup.svg · lockup-badge.svg (+ -paper / -night)</code>
  </section>
  <p class="foot">Si te convence, el siguiente paso es el paquete final.</p>
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
    (ROOT / "showcase-v15.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
