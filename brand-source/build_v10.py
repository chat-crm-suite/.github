"""Brand draft 10 — ChatCRM custom lettering, the C as hero.

    python brand-source/build_v10.py

System: every cut and diagonal is 45°, taken from the terminals of Outfit's C.
  · Hero C: geometric ring (stroke 180) with 45° cuts and a 45° speech tail. Also the symbol.
  · CRM: the same ring C without tail; R and M with 45° cuts on their outer top corners.
  · h, t and the caret keep the 45° cut. Optional "at" ligature.
Outputs v10/{wordmark,wordmark-lig,symbol,badge}{,-paper,-night}.svg + showcase-v10.html.
"""
import math
from pathlib import Path

import pathops

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER
from build_v9 import (CARET_BOT, CARET_GAP, CARET_TOP, CARET_W, STEM, d, glyph, minus, poly, shape,
                      union)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v10"

RING_STROKE, RING_R, RING_CY, RING_GAP = 180, 364, 353, 40
TEXT_C_STROKE = 162             # the C inside CRM: optical match to the 153 stems
LSB = 32                        # Outfit C left side bearing
CUT_H = STEM * 0.8              # 45° corner cut on h, t, R
CUT_M = 100                     # M's flat top is narrower
TRACK = -12                     # font units between glyphs (on top of kerning)
SYMBOL_CARET_W = 112


def circle(cx, cy, r):
    k = 0.5522847498 * r
    p = pathops.Path()
    p.moveTo(cx + r, cy)
    p.cubicTo(cx + r, cy + k, cx + k, cy + r, cx, cy + r)
    p.cubicTo(cx - k, cy + r, cx - r, cy + k, cx - r, cy)
    p.cubicTo(cx - r, cy - k, cx - k, cy - r, cx, cy - r)
    p.cubicTo(cx + k, cy - r, cx + r, cy - k, cx + r, cy)
    p.close()
    return p


def ring_c(x0, tail=False, stroke=RING_STROKE):
    """Geometric C whose left edge sits at x0 + LSB. Returns (path, advance)."""
    cx, cy, R = x0 + LSB + RING_R, RING_CY, RING_R
    ring = minus(circle(cx, cy, R), circle(cx, cy, R - stroke))
    g = cx + RING_GAP                                         # opening: two exact 45° cuts
    ring = minus(ring, poly((g, cy), (g + 900, cy + 900), (g + 900, cy - 900)))
    if tail:
        pt = lambda a, r: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        ang, spread = 225, 24                                 # tail points down-left at 45°
        ring = union(ring, poly(pt(ang - spread, R - 60), pt(ang, R * 1.55), pt(ang + spread, R - 60),
                                pt(ang, R - RING_STROKE + 10)))
    right = ring.bounds[2]
    return ring, right + 18 - x0                              # Outfit C right side bearing


def corner_cut(x, top, h, side="left"):
    if side == "left":
        return poly((x - 2, top - h), (x - 2, top + 2), (x + h, top + 2))
    return poly((x + 2, top - h), (x + 2, top + 2), (x - h, top + 2))


def caret(x, w=CARET_W):
    return poly((x, CARET_BOT), (x + w, CARET_BOT), (x + w, CARET_TOP), (x, CARET_TOP - w))


def letters(text, x0, hero=False, lig=False):
    """Custom-set `text`; returns (green_path or None, ink_path, advance)."""
    glyphs, _ = shape(text, TRACK / 1000)
    green, ink, x = None, [], x0
    prev_end = None
    a_x = t_x = None
    for i, (name, gx) in enumerate(glyphs):
        if name == "C":
            main = hero and i == 0
            c, adv = ring_c(x, tail=main, stroke=RING_STROKE if main else TEXT_C_STROKE)
            if hero and i == 0:
                green = c
            else:
                ink.append(c)
            x += adv + TRACK
            continue
        # following glyphs keep their kerning relative to the previous one
        static_adv = glyphs[i + 1][1] - gx if i + 1 < len(glyphs) else None
        g = glyph(name, x)
        if name == "h":
            g = minus(g, corner_cut(x + 54, 726, CUT_H))
        elif name == "t":
            g = minus(g, corner_cut(x + 123, 687, CUT_H))
            t_x = x
        elif name == "a":
            a_x = x
        elif name == "R":
            g = minus(g, corner_cut(x + 68, 706, CUT_H))
        elif name == "M":
            g = minus(minus(g, corner_cut(x + 68, 706, CUT_M)), corner_cut(x + 791, 706, CUT_M, "right"))
        ink.append(g)
        x += static_adv if static_adv is not None else _width(name) + TRACK
    if lig and a_x is not None and t_x is not None:
        ink.append(poly((a_x + 470, 356), (t_x + 20, 356), (t_x + 20, 486), (a_x + 470, 486)))
    return green, union(*ink), x - x0


def _width(name):
    from build_v7 import _font
    from build_v9 import FONT
    return _font(*FONT)[0]["hmtx"][name][0]


def build(lig=False):
    green, chat, chat_adv = letters("Chat", 0, hero=True, lig=lig)
    cx = chat_adv + CARET_GAP
    _, crm, _ = letters("CRM", cx + CARET_W + CARET_GAP)
    return {"c": green, "caret": caret(cx), "rest": union(chat, crm)}


def symbol_parts():
    c, adv = ring_c(0, tail=True)
    return c, caret(adv + CARET_GAP, SYMBOL_CARET_W)


def bounds(*paths):
    bs = [p.bounds for p in paths]
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


SURF = {  # letters, green, badge bg, badge C, badge caret
    "paper": (INK, DEEP, DEEP, PAPER, MINT),
    "night": (FROST, MINT, DEEP, PAPER, MINT),
    "deep":  (PAPER, MINT, PAPER, DEEP, DEEP),
    "mono":  ("currentColor",) * 5,
}


def _vb(b, pad):
    x0, y0, x1, y1 = b
    return f"{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}"


def wordmark_svg(surf, attrs, lig=False, pad=40):
    ink, acc, *_ = SURF[surf]
    b = build(lig)
    return (f'<svg viewBox="{_vb(bounds(b["c"], b["caret"], b["rest"]), pad)}" {attrs}><g transform="scale(1 -1)">'
            f'<path fill="{ink}" d="{d(b["rest"])}"/><path fill="{acc}" d="{d(union(b["c"], b["caret"]))}"/></g></svg>')


def symbol_svg(surf, attrs, pad=40):
    _, acc, *_ = SURF[surf]
    c, k = symbol_parts()
    return (f'<svg viewBox="{_vb(bounds(c, k), pad)}" {attrs}><g transform="scale(1 -1)">'
            f'<path fill="{acc}" d="{d(union(c, k))}"/></g></svg>')


def badge_svg(surf, attrs, ratio=0.64):
    _, _, bg, cfill, kfill = SURF[surf]
    c, k = symbol_parts()
    x0, y0, x1, y1 = bounds(c, k)
    S = 1000
    s = min(S * ratio / (x1 - x0), S * ratio / (y1 - y0))
    tx = (S - (x1 - x0) * s) / 2 - x0 * s
    ty = (S - (y1 - y0) * s) / 2 + y1 * s
    sym = (f'<g transform="translate({tx:.1f} {ty:.1f}) scale({s:.4f} {-s:.4f})">'
           f'<path fill="{cfill}" d="{d(c)}"/><path fill="{kfill}" d="{d(k)}"/></g>')
    if surf == "mono":
        return (f'<svg viewBox="0 0 {S} {S}" {attrs}><defs><mask id="bm"><rect width="{S}" height="{S}" fill="#fff"/>'
                f'{sym.replace("currentColor", "#000")}</mask></defs>'
                f'<rect width="{S}" height="{S}" rx="{S * .23:.0f}" fill="currentColor" mask="url(#bm)"/></svg>')
    return f'<svg viewBox="0 0 {S} {S}" {attrs}><rect width="{S}" height="{S}" rx="{S * .23:.0f}" fill="{bg}"/>{sym}</svg>'


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for surf in ("paper", "night", "mono"):
        sfx = "" if surf == "mono" else f"-{surf}"
        (OUT / f"wordmark{sfx}.svg").write_text(wordmark_svg(surf, x) + "\n", encoding="utf-8")
        (OUT / f"wordmark-lig{sfx}.svg").write_text(wordmark_svg(surf, x, lig=True) + "\n", encoding="utf-8")
        (OUT / f"symbol{sfx}.svg").write_text(symbol_svg(surf, x) + "\n", encoding="utf-8")
        (OUT / f"badge{sfx}.svg").write_text(badge_svg(surf, x) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def anatomy_svg():
    """Wordmark with the 45° system highlighted."""
    b = build()
    x0, y0, x1, y1 = bounds(b["c"], b["caret"], b["rest"])
    guides = "".join(f'<line x1="{x0 - 60}" x2="{x1 + 60}" y1="{-y}" y2="{-y}" stroke="#72E3AD" stroke-width="3" '
                     f'stroke-dasharray="14 10"/>' for y in (0, 486, 706))
    return (f'<svg viewBox="{_vb((x0, y0, x1, y1), 90)}" aria-hidden="true">{guides}<g transform="scale(1 -1)">'
            f'<path fill="{INK}" fill-opacity=".9" d="{d(b["rest"])}"/><path fill="{DEEP}" d="{d(union(b["c"], b["caret"]))}"/></g></svg>')


def page():
    A = 'aria-hidden="true"'
    sizes = "".join(f'<span style="width:{s}px;height:{s}px">{badge_svg("paper", A)}</span>' for s in (16, 24, 32, 48, 64, 96))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — identidad</title>
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
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }} .deep {{ background:{DEEP}; }}
.hero {{ border:1px solid var(--hair); margin-top:32px; display:grid; place-items:center; padding:clamp(56px,10vw,120px) 20px; }}
.hero svg {{ width:min(680px,90%); height:auto; }}
.intro {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:32px; padding:40px 0 8px; }}
@media (max-width:780px) {{ .intro {{ grid-template-columns:1fr; }} }}
h1 {{ font-size:clamp(30px,4.6vw,46px); font-weight:700; letter-spacing:-.03em; line-height:1.05; }}
.intro p {{ color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; }}
h2 {{ font-size:clamp(24px,3.4vw,32px); font-weight:700; letter-spacing:-.02em; margin-bottom:8px; }}
.part {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:48px; }}
.lead {{ color:var(--muted); line-height:1.6; max-width:66ch; margin-bottom:24px; }}
.eyebrow {{ font-size:12px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; color:var(--acc); margin-bottom:10px; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; }}
.pair div {{ display:grid; place-items:center; padding:34px 16px; }} .pair svg {{ width:min(300px,84%); height:auto; }}
.anat {{ border:1px solid var(--hair); background:{PAPER}; padding:24px; }} .anat svg {{ width:100%; height:auto; display:block; }}
.notes {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-top:12px; }}
.notes div {{ border:1px solid var(--hair); background:var(--card); padding:18px; }}
.notes b {{ display:block; font-weight:600; margin-bottom:4px; }} .notes p {{ color:var(--muted); font-size:14.5px; line-height:1.55; }}
.kit {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
figure {{ border:1px solid var(--hair); }}
.box {{ aspect-ratio:1; display:grid; place-items:center; }} .box svg {{ width:auto; height:56%; max-width:80%; }}
figcaption {{ padding:12px 14px; font-size:13.5px; color:var(--muted); border-top:1px solid var(--hair); background:var(--card); line-height:1.45; }}
figcaption b {{ display:block; color:var(--fg); font-weight:600; font-size:15px; }}
.sizes {{ display:flex; gap:20px; align-items:flex-end; flex-wrap:wrap; border:1px solid var(--hair); padding:24px; background:var(--card); margin-top:12px; }}
.sizes svg {{ width:100%; height:100%; display:block; }}
.gh {{ display:grid; grid-template-columns:auto 1fr; gap:18px; align-items:center; border:1px solid var(--hair); background:var(--card); padding:20px; margin-top:12px; }}
.gh .av {{ width:96px; height:96px; }} .gh .av svg {{ width:100%; height:100%; display:block; }}
.gh b {{ font-size:24px; font-weight:700; display:block; }} .gh small {{ color:var(--muted); font-size:14px; }}
.gh .wm {{ height:22px; width:auto; margin-top:8px; display:block; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · identidad</span><button id="t">Claro / oscuro</button></div>
  <div class="hero paper">{wordmark_svg("paper", A)}</div>
  <div class="pair"><div class="night">{wordmark_svg("night", A)}</div><div class="deep">{wordmark_svg("deep", A)}</div></div>
  <section class="intro">
    <h1>La «C» manda.<br>Todo lo demás la sigue.</h1>
    <p>Un solo ángulo para todo el nombre: 45°, el mismo con que Outfit corta su «C». La «C» principal es un
    anillo geométrico con una cola de mensaje a 45°; la «C» de CRM es el mismo anillo sin cola; la R, la M,
    la h, la t y el cursor llevan el mismo corte. Las letras salen de Outfit, la fuente del frontend.</p>
  </section>

  <section class="part"><div class="eyebrow">Anatomía</div><h2>Un ángulo, un sistema</h2>
    <div class="anat">{anatomy_svg()}</div>
    <div class="notes">
      <div><b>C principal</b><p>Anillo de trazo 180 (más pesado que las demás letras), apertura con cortes exactos
        a 45° y cola de mensaje en la misma diagonal. Es el símbolo.</p></div>
      <div><b>C de CRM</b><p>El mismo anillo sin cola: las dos «C» son hermanas y el nombre rima consigo mismo.</p></div>
      <div><b>R y M</b><p>Corte a 45° en las esquinas superiores exteriores; la M de forma simétrica.</p></div>
      <div><b>h, t y cursor</b><p>El corte a 45° arriba de las astas. El cursor termina en punta como una pluma.</p></div>
    </div>
  </section>

  <section class="part"><div class="eyebrow">Opción</div><h2>Con ligadura «at»</h2>
    <p class="lead">La misma pieza con la barra de la «t» unida a la «a». Elige con o sin.</p>
    <div class="hero paper" style="margin-top:0">{wordmark_svg("paper", A, lig=True)}</div>
    <code>v10/wordmark-lig.svg · wordmark-lig-paper.svg · wordmark-lig-night.svg</code>
  </section>

  <section class="part"><div class="eyebrow">Para GitHub</div><h2>Símbolo e insignia</h2>
    <p class="lead">El símbolo es la «C» principal con su cursor. La insignia lo lleva al avatar de
    <b>chat-crm-suite</b>, al favicon y al ícono de la app.</p>
    <div class="kit">
      <figure><div class="box paper">{symbol_svg("paper", A)}</div><figcaption><b>Símbolo</b>symbol.svg</figcaption></figure>
      <figure><div class="box paper">{badge_svg("paper", A)}</div><figcaption><b>Insignia</b>badge.svg · avatar de GitHub</figcaption></figure>
      <figure><div class="box night">{badge_svg("night", A)}</div><figcaption><b>Insignia sobre oscuro</b>badge-night.svg</figcaption></figure>
      <figure><div class="box night">{symbol_svg("night", A)}</div><figcaption><b>Símbolo sobre oscuro</b>symbol-night.svg</figcaption></figure>
    </div>
    <div class="sizes">{sizes}</div>
    <div class="gh"><span class="av">{badge_svg("paper", A)}</span>
      <div><b>chat-crm-suite</b><small>Conversaciones de WhatsApp que se convierten en clientes</small>
      {wordmark_svg("paper", 'class="wm" ' + A, pad=0)}</div></div>
  </section>

  <p class="foot">Archivos en <code style="display:inline">brand/v10/</code>. Si te convence, el siguiente paso es cerrar:
  PNG 1024 px, favicon.ico, avatar 500×500 y banner social 1280×640.</p>
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
    (ROOT / "showcase-v10.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
