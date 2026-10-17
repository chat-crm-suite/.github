"""Brand draft 08 — ChatCRM "Cursor" system: W3 wordmark + a symbol cut from the same letter.

    python brand-source/build_v8.py

Reuses the type engine from build_v7.py (fonts in brand/fonts/). Rule of the system: the caret
appears once per composition — when the symbol is present, the wordmark drops its caret.
"""
from pathlib import Path

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER, set_type

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v8"
MANROPE = ("Manrope.ttf", {"wght": 800})
CAP = 60
CARET_GAP, CARET_W, CARET_TOP, CARET_H = 7.5, 6.5, -66, 78     # same caret as wordmark W3

# surface -> (letters, caret, badge fill)
SURF = {
    "paper": (INK, DEEP, DEEP),
    "night": (FROST, MINT, DEEP),
    "deep":  (PAPER, MINT, None),
    "mono":  ("currentColor", "currentColor", "currentColor"),
}
BADGE_INK = {"paper": (PAPER, MINT), "night": (PAPER, MINT), "mono": ("#fff", "#fff")}


def caret(x, paint):
    return f'<rect x="{x:.2f}" y="{CARET_TOP}" width="{CARET_W}" height="{CARET_H}" rx="1.2" fill="{paint}"/>'


def run(text, paint, track=-0.025):
    return set_type([(*MANROPE, text, paint, track)], cap=CAP)


def symbol(ink, acc):
    """The C of the wordmark plus its caret, at the wordmark's own spacing. Baseline y=0."""
    body, (x0, y0, x1, y1), _, adv = run("C", ink)
    cx = adv + CARET_GAP
    return body + caret(cx, acc), (x0, min(y0, CARET_TOP), cx + CARET_W, max(y1, CARET_TOP + CARET_H))


def fit(body, bounds, x, y, w, h):
    """Place `body` (with `bounds`) centred inside box x,y,w,h."""
    bx0, by0, bx1, by1 = bounds
    s = min(w / (bx1 - bx0), h / (by1 - by0))
    tx = x + (w - (bx1 - bx0) * s) / 2 - bx0 * s
    ty = y + (h - (by1 - by0) * s) / 2 - by0 * s
    return f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s:.4f})">{body}</g>'


def badge(surf, x, y, size):
    if surf == "deep":
        ink, acc = PAPER, MINT
        fill = None
    else:
        ink, acc = BADGE_INK[surf]
        fill = SURF[surf][2]
    if surf == "mono":   # one-ink badge: knock the symbol out of the square
        mid = f"m{abs(hash((x, y, size))) % 10**6}"
        b, bb = symbol("#000", "#000")
        return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x}" y="{y}" width="{size}" height="{size}">'
                f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#fff"/>'
                f'{fit(b, bb, x + size * .2, y + size * .2, size * .6, size * .6)}</mask>'
                f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * .23:.2f}" fill="currentColor" mask="url(#{mid})"/>')
    b, bb = symbol(ink, acc)
    bg = (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * .23:.2f}" fill="{fill}"/>' if fill else
          f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * .23:.2f}" fill="none" '
          f'stroke="{MINT}" stroke-opacity=".5" stroke-width="{size * .015:.2f}"/>')
    return bg + fit(b, bb, x + size * .2, y + size * .2, size * .6, size * .6)


def wordmark(ink, acc, with_caret=True, green_c=False):
    if not with_caret:
        body, bd, _, adv = run("ChatCRM", ink)
        return body, bd
    if green_c:
        c, cb, _, cadv = run("C", acc)
        h, hb_, _, hadv = run("hat", ink)
        chat = c + f'<g transform="translate({cadv:.2f} 0)">{h}</g>'
        chat_adv, chat_b = cadv + hadv, (cb[0], min(cb[1], hb_[1]), cadv + hb_[2], max(cb[3], hb_[3]))
    else:
        chat, chat_b, _, chat_adv = run("Chat", ink)
    x0 = chat_adv + CARET_GAP
    crm, crm_b, _, _ = run("CRM", ink, -0.02)
    shift = x0 + CARET_W + CARET_GAP
    body = chat + caret(x0, acc) + f'<g transform="translate({shift:.2f} 0)">{crm}</g>'
    return body, (chat_b[0], min(chat_b[1], CARET_TOP), shift + crm_b[2], max(chat_b[3], CARET_TOP + CARET_H))


def svg(body, bounds, attrs, pad=6):
    x0, y0, x1, y1 = bounds
    return (f'<svg viewBox="{x0 - pad:.1f} {y0 - pad:.1f} {x1 - x0 + 2 * pad:.1f} {y1 - y0 + 2 * pad:.1f}" {attrs}>'
            f'{body}</svg>')


# ---------------------------------------------------------------- compositions

def comp_symbol(surf):
    ink, acc, _ = SURF[surf]
    return symbol(ink, acc)


def comp_badge(surf):
    return badge(surf, 0, 0, 100), (0, 0, 100, 100)


def comp_wordmark(surf):
    ink, acc, _ = SURF[surf]
    return wordmark(ink, acc)


def comp_fusion(surf):
    ink, acc, _ = SURF[surf]
    return wordmark(ink, acc, green_c=True)


def comp_horizontal(surf):
    """Badge + wordmark without caret. Badge height = 1.55 cap, centred on the cap height."""
    ink, _, _ = SURF[surf]
    size = CAP * 1.55
    y = -CAP / 2 - size / 2
    body, (x0, y0, x1, y1) = wordmark(ink, None, with_caret=False)
    gx = size + CAP * 0.42 - x0
    return (badge(surf, 0, y, size) + f'<g transform="translate({gx:.2f} 0)">{body}</g>',
            (0, min(y, y0), gx + x1, max(y + size, y1)))


def comp_open(surf):
    """Bare symbol + wordmark without caret, split by a hairline: no container."""
    ink, acc, _ = SURF[surf]
    sb, (sx0, sy0, sx1, sy1) = symbol(ink, acc)
    body, (x0, y0, x1, y1) = wordmark(ink, None, with_caret=False)
    rule_x = sx1 - sx0 + CAP * 0.5
    gx = rule_x + CAP * 0.5 - x0
    rule = (f'<rect x="{rule_x:.2f}" y="{CARET_TOP}" width="1.6" height="{CARET_H}" fill="{ink}" '
            f'fill-opacity=".28"/>')
    return (f'<g transform="translate({-sx0:.2f} 0)">{sb}</g>{rule}<g transform="translate({gx:.2f} 0)">{body}</g>',
            (0, min(sy0, y0), gx + x1, max(sy1, y1)))


def comp_stacked(surf):
    ink, _, _ = SURF[surf]
    body, (x0, y0, x1, y1) = wordmark(ink, None, with_caret=False)
    size = CAP * 2.3
    w = x1 - x0
    bx = x0 + w / 2 - size / 2
    by = y0 - CAP * 0.62 - size
    return badge(surf, bx, by, size) + body, (min(x0, bx), by, max(x1, bx + size), y1)


COMPS = [
    ("horizontal", "Horizontal con insignia", comp_horizontal,
     "El símbolo dentro de una insignia de verde profundo y, al lado, el nombre sin cursor. La insignia hace "
     "de «ícono de app» y el nombre queda limpio. Es la combinación principal recomendada."),
    ("open", "Horizontal abierta", comp_open,
     "El símbolo sin contenedor, una línea fina y el nombre. Más editorial; para documentos, firma de correo "
     "y presentaciones."),
    ("stacked", "Apilada", comp_stacked,
     "Insignia arriba y nombre debajo, centrados. Para portadas, splash de la app, login y banners cuadrados."),
    ("fusion", "Fusión (sin símbolo aparte)", comp_fusion,
     "El wordmark W3 con la «C» y el cursor en verde: muestra de dónde sale el símbolo. Es el logo y el "
     "símbolo en una sola pieza; úsalo cuando solo cabe una cosa."),
]


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    items = [("symbol", comp_symbol), ("badge", comp_badge), ("wordmark", comp_wordmark)] + \
            [(k, fn) for k, _, fn, _ in COMPS]
    for key, fn in items:
        for surf in ("paper", "night", "mono"):
            name = key if surf == "mono" else f"{key}-{surf}"
            body, bd = fn(surf)
            (OUT / f"{name}.svg").write_text(svg(body, bd, x, pad=0 if key == "badge" else 6) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def show(fn, surf, cls=""):
    body, bd = fn(surf)
    return svg(body, bd, f'class="{cls}" aria-hidden="true"', pad=0 if fn is comp_badge else 6)


def page():
    comps = "".join(f"""
    <article class="comp" id="{k}">
      <div class="cap"><span class="idx">L{i + 1}</span><h3>{t}</h3></div>
      <p>{d}</p>
      <div class="stage paper">{show(fn, "paper", "lg")}</div>
      <div class="pair"><div class="night">{show(fn, "night")}</div><div class="deep">{show(fn, "deep")}</div></div>
      <code>v8/{k}.svg · {k}-paper.svg · {k}-night.svg</code>
    </article>""" for i, (k, t, fn, d) in enumerate(COMPS))
    sizes = "".join(f'<span style="width:{s}px;height:{s}px">{show(comp_badge, "paper")}</span>' for s in (16, 24, 32, 48, 64, 96))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — sistema Cursor</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:#5f6360; --hair:rgba(23,23,23,.12); --card:#fff; --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d;
  --hair:rgba(226,232,240,.12); --card:#161616; --acc:{MINT}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#0f0f0f; --fg:{FROST}; --muted:#9aa19d; --hair:rgba(226,232,240,.12); --card:#161616;
  --acc:{MINT}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:var(--bg); color:var(--fg); font-family:Manrope,system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1080px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; border-bottom:1px solid var(--hair);
  font-size:13px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; }}
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:6px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.hero {{ padding:72px 0 40px; }}
.hero svg {{ width:min(520px,90%); height:auto; }}
.hero p {{ margin-top:28px; color:var(--muted); font-size:17px; line-height:1.65; max-width:62ch; }}
h2 {{ font-size:clamp(26px,3.6vw,36px); font-weight:800; letter-spacing:-.03em; margin-bottom:8px; }}
.part {{ border-top:1px solid var(--hair); padding:56px 0 16px; }}
.lead {{ color:var(--muted); line-height:1.6; max-width:66ch; margin-bottom:32px; }}
.eyebrow {{ font-size:12px; font-weight:700; letter-spacing:.14em; text-transform:uppercase; color:var(--acc); margin-bottom:12px; }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }} .deep {{ background:{DEEP}; }}
.parts {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }}
.parts figure {{ border:1px solid var(--hair); }}
.parts .box {{ aspect-ratio:4/3; display:grid; place-items:center; }}
.parts .box svg {{ width:auto; height:44%; max-width:80%; }}
.parts .box.wide svg {{ width:78%; height:auto; }}
figcaption {{ padding:12px 14px; font-size:13px; color:var(--muted); line-height:1.5; border-top:1px solid var(--hair); background:var(--card); }}
figcaption b {{ color:var(--fg); display:block; font-size:14px; }}
.rule {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px; }}
@media (max-width:700px) {{ .rule {{ grid-template-columns:1fr; }} }}
.rule div {{ border:1px solid var(--hair); padding:22px; background:var(--card); }}
.rule b {{ display:block; margin-bottom:6px; }} .rule .no b {{ color:#b42318; }} .rule .yes b {{ color:var(--acc); }}
.rule p {{ color:var(--muted); font-size:14px; line-height:1.55; }}
.comps {{ display:grid; gap:64px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; }}
.idx {{ font-size:12px; color:var(--muted); font-weight:700; letter-spacing:.08em; }}
h3 {{ font-size:24px; font-weight:800; letter-spacing:-.02em; }}
.comp p {{ color:var(--muted); line-height:1.6; max-width:66ch; margin:6px 0 18px; }}
.stage {{ border:1px solid var(--hair); display:grid; place-items:center; padding:clamp(40px,8vw,84px) 20px; }}
.stage svg {{ width:min(520px,84%); height:auto; max-height:260px; }}
.pair {{ display:grid; grid-template-columns:1fr 1fr; }}
.pair div {{ display:grid; place-items:center; padding:30px 16px; }} .pair svg {{ width:min(260px,82%); height:auto; max-height:130px; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.sizes {{ display:flex; gap:22px; align-items:flex-end; flex-wrap:wrap; border:1px solid var(--hair); padding:26px; background:var(--card); }}
.sizes svg {{ width:100%; height:100%; display:block; }}
.ctx {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; margin-top:12px; }}
.gh, .appbar {{ border:1px solid var(--hair); background:var(--card); padding:16px; display:flex; align-items:center; gap:14px; }}
.gh .av {{ width:56px; height:56px; flex:none; }} .gh b {{ font-size:18px; font-weight:800; display:block; }}
.gh small {{ color:var(--muted); }}
.appbar {{ background:{NIGHT}; }} .appbar svg {{ height:30px; width:auto; }}
.appbar span {{ margin-left:auto; color:#9aa19d; font-size:13px; }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · sistema Cursor</span><button id="t">Claro / oscuro</button></div>
  <section class="hero">
    {show(comp_wordmark, "paper", "")}
    <p>W3 + S4, rehechos como un solo sistema. El símbolo ya no es un dibujo aparte: es la misma «C» de
    Manrope 800 del wordmark y el mismo cursor, con el mismo espaciado. Por eso combinan.</p>
  </section>

  <section class="part"><div class="eyebrow">Las piezas</div><h2>Tres piezas, una sola letra</h2>
    <p class="lead">El wordmark sigue igual que te gustó. El símbolo sale de él y la insignia lo lleva a ícono.</p>
    <div class="parts">
      <figure><div class="box wide paper">{show(comp_wordmark, "paper")}</div>
        <figcaption><b>Wordmark</b>El nombre solo. Cabeceras, README, documentos.</figcaption></figure>
      <figure><div class="box paper">{show(comp_symbol, "paper")}</div>
        <figcaption><b>Símbolo</b>«C» + cursor, recortados del wordmark.</figcaption></figure>
      <figure><div class="box paper">{show(comp_badge, "paper")}</div>
        <figcaption><b>Insignia</b>Avatar de GitHub, favicon, ícono de la app.</figcaption></figure>
    </div>
    <div class="rule">
      <div class="no"><b>Por qué no quedaba bien antes</b><p>«C│ Chat│CRM»: la C y el cursor se repetían dos veces seguidas
        y el símbolo tenía otro grosor y otra curva que las letras.</p></div>
      <div class="yes"><b>La regla nueva</b><p>El cursor aparece <b style="display:inline">una sola vez</b> por composición.
        Si está el símbolo, el nombre va sin cursor; si va el nombre solo, lleva su cursor.</p></div>
    </div>
  </section>

  <section class="part"><div class="eyebrow">Combinaciones</div><h2>Cuatro formas de juntarlos</h2>
    <p class="lead">Elige la principal; las demás quedan como variantes para otros espacios.</p>
    <div class="comps">{comps}</div></section>

  <section class="part"><div class="eyebrow">En uso</div><h2>Insignia en tamaños reales</h2>
    <p class="lead">16 px es el favicon; 32–64 px, avatar de GitHub y apps.</p>
    <div class="sizes">{sizes}</div>
    <div class="ctx">
      <div class="gh"><span class="av">{show(comp_badge, "paper")}</span><div><b>chat-crm-suite</b><small>ChatCRM · conversaciones que se convierten en clientes</small></div></div>
      <div class="appbar">{show(comp_horizontal, "night")}<span>Panel</span></div>
    </div>
  </section>

  <p class="foot">Dime qué combinación es la principal (L1–L4). Después cierro: PNG en varios tamaños, favicon.ico,
  avatar 500×500 para la organización y banner social 1280×640.</p>
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
    (ROOT / "showcase-v8.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
