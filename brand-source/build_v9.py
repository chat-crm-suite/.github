"""Brand draft 09 — ChatCRM custom lettering on Outfit (the product typeface).

    python brand-source/build_v9.py

Outfit 700 shaped with HarfBuzz, then edited glyph by glyph with boolean path operations
(skia-pathops): no masks, every output is a clean single path per colour. Three levels of
customisation; each produces wordmark (Chat│CRM, C + caret in green), symbol and badge.
Needs: fonttools, uharfbuzz, skia-pathops; Outfit.ttf in brand/fonts/.
"""
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER, SVGPathPen, _font

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v9"
FONT = ("Outfit.ttf", {"wght": 700})

STEM = 153                       # Outfit 700 vertical stem (h, l, t)
CARET_W, CARET_TOP, CARET_BOT, CARET_GAP = 84, 762, -118, 84
CUT = 0.8                        # 45° cut height as a fraction of the stem width


# ---------------------------------------------------------------- geometry helpers (font units, y up)

def poly(*pts):
    p = pathops.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def union(*paths):
    out = pathops.Path()
    for p in paths:
        out = pathops.op(out, p, pathops.PathOp.UNION)
    return out


def minus(a, b):
    return pathops.op(a, b, pathops.PathOp.DIFFERENCE)


def glyph(name, dx):
    static, _ = _font(*FONT)
    p = pathops.Path()
    static.getGlyphSet()[name].draw(TransformPen(p.getPen(), (1, 0, 0, 1, dx, 0)))
    return union(p)              # normalise winding / overlaps


def shape(text, track=-0.012):
    """[(glyph_name, x)] and the advance, using real kerning."""
    static, hbfont = _font(*FONT)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    order, x, out = static.getGlyphOrder(), 0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((order[info.codepoint], x + pos.x_offset))
        x += pos.x_advance + track * 1000
    return out, x


def top_cut(x0, top, w=STEM, k=CUT):
    """Triangle that slices the top-left corner of a stem at 45 degrees."""
    h = w * k
    return poly((x0 - 2, top - h), (x0 - 2, top + 2), (x0 + h, top + 2))


def caret(x, cut, w=CARET_W):
    if not cut:
        return poly((x, CARET_BOT), (x + w, CARET_BOT), (x + w, CARET_TOP), (x, CARET_TOP))
    return poly((x, CARET_BOT), (x + w, CARET_BOT), (x + w, CARET_TOP), (x, CARET_TOP - w))


# ---------------------------------------------------------------- lettering variants

def build(level):
    """Returns dict with 'c' (green C), 'caret', 'rest' (ink letters) as pathops paths + advance.

    level 1 = Outfit tuned · 2 = + 45° cuts on ascenders and caret · 3 = + 'at' ligature.
    """
    cut, lig = level >= 2, level >= 3
    chat, chat_adv = shape("Chat")
    cx = chat_adv + CARET_GAP
    crm, _ = shape("CRM", -0.006)
    crm_dx = cx + CARET_W + CARET_GAP

    c_path = glyph(chat[0][0], chat[0][1])
    rest = []
    a_x = t_x = None
    for name, x in chat[1:]:
        g = glyph(name, x)
        if name == "h" and cut:
            g = minus(g, top_cut(x + 54, 726))
        if name == "a":
            a_x = x
        if name == "t":
            t_x = x
            if cut:
                g = minus(g, top_cut(x + 123, 687))
        rest.append(g)
    if lig and a_x is not None:
        # the t crossbar runs back into the a's stem: one continuous stroke at x-height
        rest.append(poly((a_x + 470, 356), (t_x + 20, 356), (t_x + 20, 486), (a_x + 470, 486)))
        # drop the crossbar's left spur so the join reads as one bar
    for name, x in crm:
        rest.append(glyph(name, x + crm_dx))
    rest_path = union(*rest)
    if lig:
        rest_path = union(rest_path)
    return {"c": c_path, "caret": caret(cx, cut), "rest": rest_path, "cx": cx}


def d(path):
    pen = SVGPathPen()
    path.draw(pen)
    return pen.getCommands()


def bounds(*paths):
    bs = [p.bounds for p in paths if p.bounds and p.bounds[2] > p.bounds[0]]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


# surfaces: (ink letters, green parts, badge fill, badge letters, badge caret)
SURF = {
    "paper": (INK, DEEP, DEEP, PAPER, MINT),
    "night": (FROST, MINT, DEEP, PAPER, MINT),
    "deep":  (PAPER, MINT, PAPER, DEEP, DEEP),
    "mono":  ("currentColor",) * 5,
}


def wordmark_svg(level, surf, attrs, pad=40):
    ink, acc, *_ = SURF[surf]
    b = build(level)
    x0, y0, x1, y1 = bounds(b["c"], b["caret"], b["rest"])
    vb = f"{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"
    return (f'<svg viewBox="{vb}" {attrs}><g transform="scale(1 -1)">'
            f'<path fill="{ink}" d="{d(b["rest"])}"/>'
            f'<path fill="{acc}" d="{d(union(b["c"], b["caret"]))}"/></g></svg>')


SYMBOL_CARET_W = 112             # optical correction: the caret must survive at 16 px


def symbol_parts(level):
    """The wordmark's own C, with the caret right after it at the wordmark's spacing."""
    chat, _ = shape("C")
    c = glyph(chat[0][0], 0)
    _, adv = shape("C")
    return c, caret(adv + CARET_GAP, level >= 2, SYMBOL_CARET_W)


def symbol_svg(level, surf, attrs, pad=40):
    _, acc, *_ = SURF[surf]
    c, k = symbol_parts(level)
    x0, y0, x1, y1 = bounds(c, k)
    vb = f"{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"
    return f'<svg viewBox="{vb}" {attrs}><g transform="scale(1 -1)"><path fill="{acc}" d="{d(union(c, k))}"/></g></svg>'


def badge_svg(level, surf, attrs, fill_ratio=0.62):
    _, _, bg, letters, car = SURF[surf]
    c, k = symbol_parts(level)
    x0, y0, x1, y1 = bounds(c, k)
    S = 1000
    s = min(S * fill_ratio / (x1 - x0), S * fill_ratio / (y1 - y0))
    tx = (S - (x1 - x0) * s) / 2 - x0 * s
    ty = (S - (y1 - y0) * s) / 2 + y1 * s          # y flipped
    sym = (f'<g transform="translate({tx:.1f} {ty:.1f}) scale({s:.4f} {-s:.4f})">'
           f'<path fill="{letters}" d="{d(c)}"/><path fill="{car}" d="{d(k)}"/></g>')
    if surf == "mono":
        return (f'<svg viewBox="0 0 {S} {S}" {attrs}><defs><mask id="bm"><rect width="{S}" height="{S}" fill="#fff"/>'
                f'{sym.replace("currentColor", "#000")}</mask></defs>'
                f'<rect width="{S}" height="{S}" rx="{S * .23:.0f}" fill="currentColor" mask="url(#bm)"/></svg>')
    return (f'<svg viewBox="0 0 {S} {S}" {attrs}><rect width="{S}" height="{S}" rx="{S * .23:.0f}" fill="{bg}"/>'
            f'{sym}</svg>')


LEVELS = [
    (1, "afinada", "Outfit afinada",
     "Outfit 700 tal cual la usa el frontend, con espaciado ajustado a mano y el cursor con el grosor "
     "proporcional a las astas. Máxima coherencia con la app; personalización mínima."),
    (2, "corte", "Corte 45°",
     "Las terminales de la «C» de Outfit ya están cortadas a 45°. Ese corte se repite en la parte alta "
     "de la «h», de la «t» y del cursor: un solo gesto que recorre todo el nombre y lo vuelve propio."),
    (3, "ligadura", "Corte 45° + ligadura",
     "Lo anterior y además la barra de la «t» se une con la «a» en una sola línea a la altura de las "
     "minúsculas: «at» como una pieza. Es el nivel más personalizado y el más reconocible."),
]


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for lvl, key, *_ in LEVELS:
        for surf in ("paper", "night", "mono"):
            sfx = "" if surf == "mono" else f"-{surf}"
            (OUT / f"{key}-wordmark{sfx}.svg").write_text(wordmark_svg(lvl, surf, x) + "\n", encoding="utf-8")
            (OUT / f"{key}-symbol{sfx}.svg").write_text(symbol_svg(lvl, surf, x) + "\n", encoding="utf-8")
            (OUT / f"{key}-badge{sfx}.svg").write_text(badge_svg(lvl, surf, x) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def page():
    A = 'aria-hidden="true"'

    def block(lvl, key, title, desc):
        sizes = "".join(f'<span style="width:{s}px;height:{s}px">{badge_svg(lvl, "paper", A)}</span>'
                        for s in (16, 24, 32, 48, 64))
        return f"""
    <article class="lv" id="{key}">
      <div class="cap"><span class="idx">0{lvl}</span><h3>{title}</h3></div>
      <p>{desc}</p>
      <div class="stage paper">{wordmark_svg(lvl, "paper", 'class="wm" ' + A)}</div>
      <div class="pair">
        <div class="night">{wordmark_svg(lvl, "night", A)}</div>
        <div class="deep">{wordmark_svg(lvl, "deep", A)}</div>
      </div>
      <div class="kit">
        <figure><div class="box paper">{symbol_svg(lvl, "paper", A)}</div><figcaption><b>Símbolo</b>«C» + cursor del wordmark</figcaption></figure>
        <figure><div class="box paper">{badge_svg(lvl, "paper", 'class="bd" ' + A)}</div><figcaption><b>Insignia</b>Avatar de GitHub · ícono de app</figcaption></figure>
        <figure><div class="box night">{badge_svg(lvl, "night", 'class="bd" ' + A)}</div><figcaption><b>Insignia sobre oscuro</b>Misma pieza</figcaption></figure>
        <figure><div class="box paper sz">{sizes}</div><figcaption><b>Tamaños</b>16 · 24 · 32 · 48 · 64 px</figcaption></figure>
      </div>
      <div class="gh"><span class="av">{badge_svg(lvl, "paper", A)}</span>
        <div><b>chat-crm-suite</b><small>{wordmark_svg(lvl, "paper", 'class="ghwm" ' + A)}</small></div></div>
      <code>v9/{key}-wordmark.svg · {key}-symbol.svg · {key}-badge.svg (+ -paper / -night)</code>
    </article>"""

    blocks = "".join(block(l, k, t, d_) for l, k, t, d_ in LEVELS)
    detail = "".join(f'<figure><div class="box paper zoom">{wordmark_svg(l, "paper", A)}</div>'
                     f'<figcaption><b>0{l} · {t}</b></figcaption></figure>' for l, _, t, _ in LEVELS)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — lettering</title>
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
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:6px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.intro {{ padding:64px 0 40px; }}
h1 {{ font-size:clamp(36px,6vw,64px); font-weight:700; letter-spacing:-.03em; line-height:1; }}
.intro p {{ margin-top:20px; color:var(--muted); font-size:18px; font-weight:300; line-height:1.6; max-width:64ch; }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }} .deep {{ background:{DEEP}; }}
.detail {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:36px; }}
@media (max-width:760px) {{ .detail {{ grid-template-columns:1fr; }} }}
figure {{ border:1px solid var(--hair); }}
figcaption {{ padding:10px 14px; font-size:13px; color:var(--muted); border-top:1px solid var(--hair); background:var(--card); line-height:1.45; }}
figcaption b {{ display:block; color:var(--fg); font-weight:600; }}
.box {{ display:grid; place-items:center; aspect-ratio:4/3; }}
.box svg {{ width:auto; height:48%; max-width:80%; }}
.box svg.bd {{ height:58%; }}
.zoom {{ overflow:hidden; aspect-ratio:16/10; }}
.zoom svg {{ height:auto; width:260%; max-width:none; transform:translateX(13%); }}
.lvs {{ display:grid; gap:80px; border-top:1px solid var(--hair); padding-top:56px; margin-top:56px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; }}
.idx {{ font-size:13px; color:var(--muted); font-weight:600; }}
h3 {{ font-size:30px; font-weight:700; letter-spacing:-.02em; }}
.lv > p {{ color:var(--muted); line-height:1.6; max-width:68ch; margin:8px 0 20px; font-size:16.5px; }}
.stage {{ border:1px solid var(--hair); display:grid; place-items:center; padding:clamp(40px,8vw,90px) 20px; }}
.stage svg.wm {{ width:min(600px,88%); height:auto; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; }}
.pair div {{ display:grid; place-items:center; padding:30px 16px; }} .pair svg {{ width:min(270px,84%); height:auto; }}
.kit {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin-top:12px; }}
.sz {{ display:flex; gap:14px; align-items:flex-end; justify-content:center; padding:16px; }}
.sz span svg {{ width:100%; height:100%; max-width:none; display:block; }}
.gh {{ margin-top:12px; display:flex; gap:14px; align-items:center; border:1px solid var(--hair); padding:16px; background:var(--card); }}
.gh .av {{ width:60px; height:60px; flex:none; }} .gh .av svg {{ width:100%; height:100%; display:block; }}
.gh b {{ display:block; font-size:19px; font-weight:700; }} .ghwm {{ height:16px; width:auto; margin-top:6px; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:64px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · lettering propio</span><button id="t">Claro / oscuro</button></div>
  <section class="intro">
    <h1>Letras propias,<br>sobre Outfit</h1>
    <p>Partimos de Outfit, la tipografía del frontend, y la modificamos letra por letra: espaciado,
    cortes a 45° que salen de la propia «C», y una ligadura. Tres niveles para elegir. Cada uno trae el
    juego completo: wordmark (estilo L4, con la «C» y el cursor en verde), símbolo e insignia.</p>
    <div class="detail">{detail}</div>
  </section>
  <div class="lvs">{blocks}</div>
  <p class="foot">Elige el nivel (01, 02 o 03). Después cierro: PNG 1024 px, favicon.ico, avatar 500×500
  para chat-crm-suite y banner social 1280×640.</p>
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
    (ROOT / "showcase-v9.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
