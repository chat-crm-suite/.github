"""Brand draft 07 — ChatCRM: flat, serious marks with a concept + outlined wordmarks.

    python brand-source/build_v7.py [FONTS_DIR]

FONTS_DIR holds the OFL variable fonts from github.com/google/fonts (Fraunces, InstrumentSans,
Manrope, Sora). Wordmarks are shaped with HarfBuzz (real kerning) and converted to outlines, so the
SVGs in v7/ need no font installed. Needs: fonttools, uharfbuzz.
"""
import io
import math
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.basePen import BasePen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v7"
FONTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "fonts"

# Flat palette from chat-crm-app/src/styles/theme.css. No gradients.
DEEP, MINT, INK, NIGHT, PAPER, FROST = "#006239", "#72E3AD", "#171717", "#121212", "#FAFAFA", "#E2E8F0"

# ---------------------------------------------------------------- type

_cache = {}


class SVGPathPen(BasePen):
    """SVG path pen that emits cubic curves rounded to 2 decimals (quadratics -> cubics)."""

    def __init__(self, glyphSet=None):
        super().__init__(glyphSet)
        self._d = []

    def _f(self, *pts):
        return " ".join(f"{round(x, 2):g} {round(y, 2):g}" for x, y in pts)

    def _moveTo(self, p):
        self._d.append(f"M{self._f(p)}")

    def _lineTo(self, p):
        self._d.append(f"L{self._f(p)}")

    def _curveToOne(self, p1, p2, p3):
        self._d.append(f"C{self._f(p1, p2, p3)}")

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        c1 = (p0[0] + 2 / 3 * (p1[0] - p0[0]), p0[1] + 2 / 3 * (p1[1] - p0[1]))
        c2 = (p2[0] + 2 / 3 * (p1[0] - p2[0]), p2[1] + 2 / 3 * (p1[1] - p2[1]))
        self._curveToOne(c1, c2, p2)

    def _closePath(self):
        self._d.append("Z")

    def getCommands(self):
        return "".join(self._d)


def _font(file, axes):
    key = (file, tuple(sorted(axes.items())))
    if key not in _cache:
        static = instancer.instantiateVariableFont(TTFont(FONTS / file), axes)
        buf = io.BytesIO()
        static.save(buf)
        data = buf.getvalue()
        static = TTFont(io.BytesIO(data))
        _cache[key] = (static, hb.Font(hb.Face(data)))
    return _cache[key]


def set_type(runs, cap=60):
    """Shape and outline `runs` = [(file, axes, text, paint, tracking_em)] on one baseline.

    Returns (svg_body, (xmin, ymin, xmax, ymax), cap_height, x_cursor_end). Baseline is y=0,
    cap height of the first run is scaled to `cap` units.
    """
    first, _ = _font(runs[0][0], runs[0][1])
    k = cap / first["OS/2"].sCapHeight
    x, parts, bounds = 0.0, [], [math.inf, math.inf, -math.inf, -math.inf]
    for file, axes, text, paint, track in runs:
        static, hbfont = _font(file, axes)
        upm = static["head"].unitsPerEm
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hbfont, buf, {"kern": True, "liga": False})
        order, gs = static.getGlyphOrder(), static.getGlyphSet()
        pen, bpen = SVGPathPen(gs), BoundsPen(gs)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            g = order[info.codepoint]
            t = (k, 0, 0, -k, x + pos.x_offset * k, -pos.y_offset * k)
            gs[g].draw(TransformPen(pen, t))
            gs[g].draw(TransformPen(bpen, t))
            x += (pos.x_advance + track * upm) * k
        if bpen.bounds:
            b = bpen.bounds
            bounds = [min(bounds[0], b[0]), min(bounds[1], b[1]), max(bounds[2], b[2]), max(bounds[3], b[3])]
        parts.append(f'<path fill="{paint}" d="{pen.getCommands()}"/>')
    return "".join(parts), bounds, cap, x


# Each wordmark: runs + optional extra shapes drawn in its own coordinates (baseline y=0, cap 60).
def wm_fraunces(ink, acc):
    ax = {"opsz": 144, "wght": 560, "SOFT": 0, "WONK": 0}
    return set_type([("Fraunces.ttf", ax, "ChatCRM", ink, -0.012)]), ""


def wm_instrument(ink, acc):
    return set_type([("InstrumentSans.ttf", {"wdth": 100, "wght": 400}, "Chat", ink, -0.01),
                     ("InstrumentSans.ttf", {"wdth": 100, "wght": 700}, "CRM", ink, -0.005)]), ""


def wm_cursor(ink, acc):
    a = set_type([("Manrope.ttf", {"wght": 800}, "Chat", ink, -0.025)])
    # The composer caret between the two words: the moment you write to a customer.
    gap, w = 7.5, 6.5
    x0 = a[3] + gap
    b = set_type([("Manrope.ttf", {"wght": 800}, "CRM", ink, -0.02)])
    shift = x0 + w + gap
    body = (a[0] + f'<rect x="{x0:.2f}" y="-66" width="{w}" height="78" rx="1.2" fill="{acc}"/>'
            + f'<g transform="translate({shift:.2f} 0)">{b[0]}</g>')
    bounds = [a[1][0], min(a[1][1], -66), shift + b[1][2], max(a[1][3], 12)]
    return (body, bounds, 60, shift + b[3]), ""


def wm_sora(ink, acc):
    return set_type([("Sora.ttf", {"wght": 300}, "chat", ink, -0.02),
                     ("Sora.ttf", {"wght": 700}, "crm", acc, -0.02)]), ""


WORDMARKS = [
    ("serif", "Editorial", "Fraunces 560 · óptico 144", wm_fraunces,
     "Una serif de alto contraste con remates firmes. Seria y con oficio, como un estudio o una "
     "consultora. Es la que más «marca» transmite y la que mejor envejece."),
    ("weight", "Contraste", "Instrument Sans 400 + 700", wm_instrument,
     "«Chat» ligero y «CRM» en negrita: la conversación y el sistema que la ordena, en un mismo "
     "nombre. Una grotesca precisa, sobria, muy legible en pequeño."),
    ("caret", "Cursor", "Manrope 800 + cursor", wm_cursor,
     "El cursor del compositor separa las dos palabras: el instante en que escribes al cliente. "
     "Es la variante con más carácter y se lee de lejos."),
    ("lower", "Minúsculas", "Sora 300 + 700", wm_sora,
     "En minúsculas, «chat» fino y «crm» en verde y negrita. Más cercana y de producto, sin "
     "perder seriedad."),
]


# ---------------------------------------------------------------- symbols (100 x 100)

def rrect(x, y, w, h, r):
    return (f"M {x+r} {y} H {x+w-r} A {r} {r} 0 0 1 {x+w} {y+r} V {y+h-r} "
            f"A {r} {r} 0 0 1 {x+w-r} {y+h} H {x+r} A {r} {r} 0 0 1 {x} {y+h-r} "
            f"V {y+r} A {r} {r} 0 0 1 {x+r} {y} Z")


def pt(cx, cy, r, ang):
    a = math.radians(ang)
    return round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2)


def mask(mid, content):
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<rect width="100" height="100" fill="#fff"/>{content}</mask>')


GAP = 3.4


def s_record(a, b, u):
    """Doble C — the CRM (outer C, with the speech tail) holding the chat (inner C)."""
    cx, cy = 53, 47
    outer, inner = (27.5, 37, 38), (13, 22.5, 50)       # (r_in, r_out, opening half-angle)

    def arc(r_in, r_out, half, paint):
        rm, sw = (r_in + r_out) / 2, r_out - r_in
        s, e = pt(cx, cy, rm, -half), pt(cx, cy, rm, half)
        return (f'<path d="M {s[0]} {s[1]} A {rm} {rm} 0 1 0 {e[0]} {e[1]}" fill="none" stroke="{paint}" '
                f'stroke-width="{sw}"/>')
    o1, o2 = pt(cx, cy, outer[1], 152), pt(cx, cy, outer[1], 116)
    i1 = pt(cx, cy, outer[0], 140)
    tail = f"M {o1[0]} {o1[1]} L 13 90 L {o2[0]} {o2[1]} L {i1[0]} {i1[1]} Z"
    return "", arc(*outer, a) + f'<path d="{tail}" fill="{a}"/>' + arc(*inner, b)


def s_half(a, b, u):
    """Mitad — one shape, two halves: the chat bubble on the left, the customer record on the right."""
    body = rrect(13, 16, 74, 60, 20)
    tail = "M 21 64 L 14.5 87.5 L 41 75 Z"
    rows = (f'<rect x="0" y="0" width="{50 + GAP / 2}" height="100" fill="#000"/>'
            f'<rect x="0" y="{16 + 60/3 - GAP/2:.2f}" width="100" height="{GAP}" fill="#000"/>'
            f'<rect x="0" y="{16 + 120/3 - GAP/2:.2f}" width="100" height="{GAP}" fill="#000"/>')
    left = f'<rect x="{50 - GAP / 2}" y="0" width="60" height="100" fill="#000"/>'
    return (mask(f"{u}l", left) + mask(f"{u}r", rows),
            f'<g mask="url(#{u}l)" fill="{a}"><path d="{body}"/><path d="{tail}"/></g>'
            f'<path d="{body}" fill="{b}" mask="url(#{u}r)"/>')


def s_link(a, b, u):
    """Enlace — the conversation and the customer record woven together."""
    ra, rb, sw = rrect(12, 17, 48, 44, 15), rrect(40, 37, 48, 44, 15), 11
    tail = "M 14 51 L 7.5 77 L 31 60 Z"
    over = sw + 2 * GAP
    return ((f'<clipPath id="{u}c1"><circle cx="60" cy="37" r="13"/></clipPath>'
             f'<clipPath id="{u}c2"><circle cx="40" cy="61" r="13"/></clipPath>'
             + mask(f"{u}mb", f'<g clip-path="url(#{u}c1)"><path d="{ra}" fill="none" stroke="#000" stroke-width="{over}"/></g>')
             + mask(f"{u}ma", f'<g clip-path="url(#{u}c2)"><path d="{rb}" fill="none" stroke="#000" stroke-width="{over}"/></g>')),
            f'<g mask="url(#{u}ma)"><path d="{ra}" fill="none" stroke="{a}" stroke-width="{sw}"/>'
            f'<path d="{tail}" fill="{a}"/></g>'
            f'<path d="{rb}" fill="none" stroke="{b}" stroke-width="{sw}" mask="url(#{u}mb)"/>')


def s_caret(a, b, u):
    """Cursor — the C of ChatCRM with the composer caret in its mouth: writing to your customer."""
    cx, cy, ro, ri = 46.5, 50, 34, 18
    rm, sw = (ro + ri) / 2, ro - ri
    s, e = pt(cx, cy, rm, -48), pt(cx, cy, rm, 48)
    return ("", f'<path d="M {s[0]} {s[1]} A {rm} {rm} 0 1 0 {e[0]} {e[1]}" fill="none" stroke="{a}" '
                f'stroke-width="{sw}"/><rect x="75" y="27" width="8" height="46" rx="1.5" fill="{b}"/>')


SYMBOLS = [
    ("record", "Doble C", s_record,
     "Dos «C», la de Chat y la de CRM, una dentro de la otra. La exterior (el CRM, con la cola del mensaje) "
     "envuelve a la interior (el chat): cada conversación queda contenida en la relación con el cliente."),
    ("half", "Mitad", s_half,
     "Una sola forma partida en dos: a la izquierda la burbuja del chat, a la derecha la ficha del "
     "cliente en filas. El producto entero en un vistazo: Chat | CRM."),
    ("link", "Enlace", s_link,
     "La conversación (con su cola) y la ficha del cliente entrelazadas: cada una pasa una vez por "
     "encima de la otra. Une el chat con el CRM, sin perder ninguno."),
    ("caret", "Cursor", s_caret,
     "La «C» de ChatCRM con el cursor del compositor en la boca: el momento de responder al cliente. "
     "Hace pareja exacta con el wordmark «Cursor»."),
]

# Paint pairs per surface: (symbol a, symbol b, wordmark ink, wordmark accent)
SURF = {
    "paper": (DEEP, INK, INK, DEEP),
    "night": (MINT, FROST, FROST, MINT),
    "deep":  (PAPER, MINT, PAPER, MINT),
    "mono":  ("currentColor",) * 4,
}

# ---------------------------------------------------------------- output

_n = 0


def uid():
    global _n
    _n += 1
    return f"k{_n}"


def symbol_svg(fn, surf, attrs='aria-hidden="true"', u=None):
    a, b, *_ = SURF[surf]
    defs, body = fn(a, b, u or uid())
    return f'<svg viewBox="0 0 100 100" {attrs}><defs>{defs}</defs>{body}</svg>'


def wordmark_svg(fn, surf, attrs='aria-hidden="true"', pad=4):
    _, _, ink, acc = SURF[surf]
    (body, (x0, y0, x1, y1), *_), _ = fn(ink, acc)
    vb = f"{x0 - pad:.1f} {y0 - pad:.1f} {x1 - x0 + 2 * pad:.1f} {y1 - y0 + 2 * pad:.1f}"
    return f'<svg viewBox="{vb}" {attrs}>{body}</svg>'


def lockup_svg(sfn, wfn, surf, attrs='aria-hidden="true"', u=None):
    a, b, ink, acc = SURF[surf]
    defs, sym = sfn(a, b, u or uid())
    (body, (x0, y0, x1, y1), cap, _), _ = wfn(ink, acc)
    size = cap * 1.55                         # symbol box relative to cap height
    sy = -cap / 2 - size / 2                  # centre symbol on the cap height
    gx = size + cap * 0.32 - x0
    vb_x0, vb_y0 = -2, min(sy, y0) - 2
    w = gx + x1 + 4
    h = max(sy + size, y1) - vb_y0 + 2
    return (f'<svg viewBox="{vb_x0} {vb_y0:.1f} {w:.1f} {h:.1f}" {attrs}><defs>{defs}</defs>'
            f'<g transform="translate(0 {sy:.2f}) scale({size / 100:.4f})">{sym}</g>'
            f'<g transform="translate({gx:.2f} 0)">{body}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img"'
    for key, title, fn, _ in SYMBOLS:
        for surf in ("mono", "paper", "night"):
            name = key if surf == "mono" else f"{key}-{surf}"
            (OUT / f"symbol-{name}.svg").write_text(
                symbol_svg(fn, surf, f'{x} aria-label="ChatCRM — {title}"', u=key) + "\n", encoding="utf-8")
    for key, title, _, fn, _ in WORDMARKS:
        for surf in ("mono", "paper", "night"):
            name = key if surf == "mono" else f"{key}-{surf}"
            (OUT / f"wordmark-{name}.svg").write_text(
                wordmark_svg(fn, surf, f'{x} aria-label="ChatCRM"') + "\n", encoding="utf-8")
    for skey, _, sfn, _ in SYMBOLS:
        for wkey, _, _, wfn, _ in WORDMARKS:
            (OUT / f"lockup-{skey}-{wkey}.svg").write_text(
                lockup_svg(sfn, wfn, "paper", f'{x} aria-label="ChatCRM"', u=skey) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

PAIRS = {"record": "serif", "half": "weight", "link": "weight", "caret": "caret"}


def page():
    wm_secs = "".join(f"""
    <article class="wm" id="w-{k}">
      <div class="wm-stage paper">{wordmark_svg(fn, "paper", 'class="wm-big" aria-hidden="true"')}</div>
      <div class="wm-pair">
        <div class="night">{wordmark_svg(fn, "night", 'aria-hidden="true"')}</div>
        <div class="deep">{wordmark_svg(fn, "deep", 'aria-hidden="true"')}</div>
      </div>
      <div class="cap"><span class="idx">W{i + 1}</span><h3>{t}</h3><span class="spec">{spec}</span></div>
      <p>{d}</p>
      <code>v7/wordmark-{k}.svg</code>
    </article>""" for i, (k, t, spec, fn, d) in enumerate(WORDMARKS))

    def sizes(fn):
        return "".join(f'<span style="width:{s}px;height:{s}px">{symbol_svg(fn, "paper")}</span>' for s in (16, 24, 32, 48))

    sym_secs = "".join(f"""
    <article class="sym" id="s-{k}">
      <div class="sym-tiles">
        <div class="tile paper big">{symbol_svg(fn, "paper")}</div>
        <div class="tile night">{symbol_svg(fn, "night")}</div>
        <div class="tile deep">{symbol_svg(fn, "deep")}</div>
        <div class="tile paper sizes">{sizes(fn)}</div>
      </div>
      <div class="sym-text">
        <div class="cap"><span class="idx">S{i + 1}</span><h3>{t}</h3></div>
        <p>{d}</p>
        <div class="lock paper">{lockup_svg(fn, dict((w[0], w[3]) for w in WORDMARKS)[PAIRS[k]], "paper")}</div>
        <div class="lock night">{lockup_svg(fn, dict((w[0], w[3]) for w in WORDMARKS)[PAIRS[k]], "night")}</div>
        <div class="apps">
          <span class="av">{symbol_svg(fn, "deep")}</span>
          <span class="gh"><span class="av sm">{symbol_svg(fn, "deep")}</span><b>chat-crm-suite</b></span>
        </div>
        <code>v7/symbol-{k}.svg · lockup-{k}-*.svg</code>
      </div>
    </article>""" for i, (k, t, fn, d) in enumerate(SYMBOLS))

    wm_by = {w[0]: w[3] for w in WORDMARKS}
    matrix = "".join(
        f'<tr><th>{st}</th>' + "".join(f'<td>{lockup_svg(sfn, wm_by[wk], "paper")}</td>' for wk, *_ in WORDMARKS) + "</tr>"
        for sk, st, sfn, _ in SYMBOLS)
    heads = "".join(f"<th>{t}</th>" for _, t, *_ in WORDMARKS)
    sw = "".join(f'<div class="swatch"><i style="background:{h}"></i><b>{n}</b><small>{h}<br>{r}</small></div>'
                 for n, h, r in [("Verde profundo", DEEP, "marca sobre claro"), ("Tinta", INK, "texto, wordmark"),
                                 ("Menta", MINT, "marca sobre oscuro"), ("Papel", PAPER, "fondo claro"),
                                 ("Noche", NIGHT, "fondo oscuro")])

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — draft 07</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,560&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:#5f6360; --hair:rgba(23,23,23,.12); --card:#fff; --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d;
  --hair:rgba(226,232,240,.12); --card:#161616; --acc:{MINT}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d; --hair:rgba(226,232,240,.12); --card:#161616;
  --acc:{MINT}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:'Instrument Sans',system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1120px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; border-bottom:1px solid var(--hair);
  font-size:13px; letter-spacing:.08em; text-transform:uppercase; }}
button {{ font:inherit; font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--fg); background:none;
  border:1px solid var(--hair); border-radius:2px; padding:7px 14px; cursor:pointer; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
header.intro {{ padding:72px 0 56px; display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:40px; align-items:end; }}
@media (max-width:820px) {{ header.intro {{ grid-template-columns:1fr; padding-top:48px; }} }}
h1 {{ font-family:Fraunces,serif; font-weight:400; font-size:clamp(44px,7vw,84px); line-height:.95; letter-spacing:-.025em; }}
h1 em {{ font-style:normal; color:var(--acc); }}
.intro p {{ color:var(--muted); font-size:17px; line-height:1.65; max-width:52ch; }}
h2 {{ font-family:Fraunces,serif; font-weight:400; font-size:clamp(30px,4vw,42px); letter-spacing:-.02em; margin:0 0 6px; }}
.part {{ border-top:1px solid var(--hair); padding:56px 0 24px; }}
.part > p.lead {{ color:var(--muted); max-width:66ch; line-height:1.6; margin-bottom:36px; }}
.eyebrow {{ font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--acc); margin-bottom:14px; }}
h3 {{ font-family:Fraunces,serif; font-weight:560; font-size:26px; letter-spacing:-.01em; }}
.cap {{ display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin:18px 0 6px; }}
.idx {{ font-size:12px; letter-spacing:.1em; color:var(--muted); }}
.spec {{ margin-left:auto; font-size:12px; color:var(--muted); letter-spacing:.04em; }}
article p {{ color:var(--muted); line-height:1.6; max-width:64ch; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }} .deep {{ background:{DEEP}; }}
.wms {{ display:grid; gap:64px; }}
.wm-stage {{ border:1px solid var(--hair); display:grid; place-items:center; padding:clamp(40px,8vw,88px) 20px; }}
.wm-big {{ width:min(560px,86%); height:auto; }}
.wm-pair {{ display:grid; grid-template-columns:1fr 1fr; gap:1px; }}
.wm-pair div {{ display:grid; place-items:center; padding:28px 16px; }} .wm-pair svg {{ width:min(230px,80%); height:auto; }}
.syms {{ display:grid; gap:72px; }}
.sym {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:36px; }}
@media (max-width:820px) {{ .sym {{ grid-template-columns:1fr; }} }}
.sym-tiles {{ display:grid; grid-template-columns:1fr 1fr; gap:1px; align-content:start; }}
.tile {{ aspect-ratio:1; display:grid; place-items:center; border:1px solid var(--hair); }}
.tile.big {{ grid-column:1 / -1; aspect-ratio:2 / 1.15; }}
.tile svg {{ width:46%; height:auto; }} .tile.big svg {{ width:34%; }}
.tile.sizes {{ grid-column:1 / -1; aspect-ratio:auto; display:flex; gap:22px; align-items:flex-end; justify-content:center; padding:22px; }}
.tile.sizes span svg {{ width:100%; height:100%; display:block; }}
.sym-text .cap {{ margin-top:0; }}
.lock {{ display:flex; align-items:center; padding:30px 26px; border:1px solid var(--hair); margin-top:12px; }}
.lock svg {{ width:min(300px,90%); height:auto; }}
.apps {{ display:flex; gap:16px; align-items:center; margin-top:16px; flex-wrap:wrap; }}
.av {{ width:72px; height:72px; background:{DEEP}; border-radius:50%; display:grid; place-items:center; flex:none; }}
.av svg {{ width:60%; height:60%; }} .av.sm {{ width:32px; height:32px; border-radius:6px; }}
.gh {{ display:flex; gap:10px; align-items:center; border:1px solid var(--hair); padding:10px 14px; font-size:15px; background:var(--card); }}
.matrix-wrap {{ overflow-x:auto; border:1px solid var(--hair); }}
table {{ border-collapse:collapse; width:100%; min-width:760px; background:{PAPER}; color:{INK}; }}
th, td {{ border:1px solid rgba(23,23,23,.1); padding:18px 14px; text-align:left; font-weight:500; font-size:13px; }}
thead th {{ font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:#5f6360; }}
td svg {{ width:100%; max-width:210px; height:auto; display:block; }}
.swatches {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }}
.swatch i {{ display:block; height:84px; border:1px solid var(--hair); margin-bottom:10px; }}
.swatch b {{ display:block; font-weight:600; }} .swatch small {{ color:var(--muted); font-size:12px; line-height:1.5; }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · Identidad</span><button id="t">Claro / oscuro</button></div>
  <header class="intro">
    <h1>Chat<em>CRM</em><br>draft 07</h1>
    <p>Tinta plana, sin degradados. Cuatro wordmarks para que el nombre se sostenga solo, y cuatro
    símbolos que explican el producto: conversaciones de WhatsApp que se convierten en relación con el
    cliente. Todo el texto está convertido a curvas desde tipografías con licencia libre (OFL).</p>
  </header>

  <section class="part"><div class="eyebrow">Parte 1</div><h2>Wordmarks: solo el nombre</h2>
    <p class="lead">Para cabeceras, documentos, README y firma. Cada uno en papel, noche y sobre verde profundo.</p>
    <div class="wms">{wm_secs}</div></section>

  <section class="part"><div class="eyebrow">Parte 2</div><h2>Símbolos con concepto</h2>
    <p class="lead">Para avatar de GitHub, favicon e ícono de la app. Cada uno se muestra con el wordmark que mejor le acompaña.</p>
    <div class="syms">{sym_secs}</div></section>

  <section class="part"><div class="eyebrow">Parte 3</div><h2>Todas las combinaciones</h2>
    <p class="lead">Cualquier símbolo funciona con cualquier wordmark. Todos estos archivos están en <code style="display:inline">v7/lockup-*.svg</code>.</p>
    <div class="matrix-wrap"><table><thead><tr><th></th>{heads}</tr></thead><tbody>{matrix}</tbody></table></div></section>

  <section class="part"><div class="eyebrow">Parte 4</div><h2>Color</h2>
    <p class="lead">Los mismos verdes del frontend, usados en tinta plana. El verde profundo es la firma; la menta solo aparece sobre fondos oscuros.</p>
    <div class="swatches">{sw}</div></section>

  <p class="foot">Elige un wordmark y un símbolo (por ejemplo «W1 + S1»). Después: ajuste óptico, versión final de
  cada archivo, PNG, favicon.ico, avatar 500×500 y banner social para GitHub.</p>
</div>
<script>
const r=document.documentElement;
document.getElementById('t').onclick=()=>{{const d=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;r.dataset.theme=d?'light':'dark';}};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    write_files()
    (ROOT / "showcase-v7.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
