"""Brand draft 13 — rounded Outfit, Chat and CRM differentiated, tighter set.

    python brand-source/build_v13.py

Built on draft 12 "round": every convex corner rounded at 38 % of the stem of its own weight, so
mixed weights stay equally soft. Tighter tracking and a narrower caret gap. Variants differ in how
Chat and CRM are told apart (weight / stronger contrast / colour).
"""
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.transformPen import TransformPen

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER, _font
from build_v9 import union
from build_v11 import s_link
from build_v12 import pill, rounded

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v13"

STEMS = {400: 90, 500: 110, 600: 131, 700: 153, 800: 174}
ROUND = 0.38                         # radius / stem (draft 12 "round": 58 / 153)
TRACK = -0.038                       # em, tighter than v12 (-0.03)
CARET_W, CARET_GAP, CARET_TOP, CARET_BOT = 72, 40, 742, -70

# key, title, chat weight, crm weight, crm in green?, description
VARIANTS = [
    ("base", "Base (v12, más junto)", 700, 700, False,
     "El redondo de v12 con el espaciado más apretado y el cursor más cerca de las dos palabras. Para comparar."),
    ("weight", "Peso en CRM", 600, 800, False,
     "Tu sugerencia: «Chat» en 600 y «CRM» en 800. La diferencia se nota sin gritar; el nombre sigue siendo "
     "una sola pieza."),
    ("contrast", "Contraste", 400, 800, False,
     "«Chat» en 400 y «CRM» en 800: la conversación ligera y el sistema sólido. Es la diferencia más clara "
     "y la más elegante de lejos."),
    ("color", "Peso + color", 600, 800, True,
     "Como «Peso en CRM», pero «CRM» además en verde profundo. Diferencia máxima; el cursor se vuelve parte "
     "de «CRM»."),
]


def run(text, weight, x0):
    """Shape `text` at `weight`, return (pathops path, advance) starting at x0 (font units, y up)."""
    static, hbfont = _font("Outfit.ttf", {"wght": weight})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": False})
    order, gs = static.getGlyphOrder(), static.getGlyphSet()
    x, parts = x0, []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        p = pathops.Path()
        gs[order[info.codepoint]].draw(TransformPen(p.getPen(), (1, 0, 0, 1, x + pos.x_offset, 0)))
        parts.append(p)
        x += pos.x_advance + TRACK * 1000
    return union(*parts), x - x0


_cache = {}


def parts(key):
    if key in _cache:
        return _cache[key]
    _, _, wc, wr, green, _ = next(v for v in VARIANTS if v[0] == key)
    chat, adv = run("Chat", wc, 0)
    cx = adv - TRACK * 1000 + CARET_GAP          # drop the trailing tracking before the caret
    crm, _ = run("CRM", wr, cx + CARET_W + CARET_GAP)
    chat_d = rounded(chat, STEMS[wc] * ROUND)
    crm_d = rounded(crm, STEMS[wr] * ROUND)
    b1, b2 = chat.bounds, crm.bounds
    bounds = (b1[0], min(b1[1], b2[1], CARET_BOT), b2[2], max(b1[3], b2[3], CARET_TOP))
    _cache[key] = (chat_d, pill(cx, CARET_BOT, CARET_W, CARET_TOP), crm_d, green, bounds)
    return _cache[key]


# surface -> (word ink, green, symbol a, symbol b, badge bg, badge a, badge b)
SURF = {
    "paper": (INK, DEEP, DEEP, MINT, DEEP, PAPER, MINT),
    "night": (FROST, MINT, MINT, "#2FA36B", DEEP, PAPER, MINT),
    "mono":  ("currentColor",) * 7,
}


def word_g(key, surf):
    ink, acc = SURF[surf][:2]
    chat, caret, crm, green, _ = parts(key)
    return (f'<g transform="scale(1 -1)"><path fill="{ink}" d="{chat}"/><path fill="{acc}" d="{caret}"/>'
            f'<path fill="{acc if green else ink}" d="{crm}"/></g>')


def wordmark_svg(key, surf, attrs='aria-hidden="true"', pad=40):
    x0, y0, x1, y1 = parts(key)[4]
    return (f'<svg viewBox="{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}" {attrs}>'
            f'{word_g(key, surf)}</svg>')


def lockup_svg(key, surf, attrs='aria-hidden="true"', badge=False):
    _, _, a, b, bg, ba, bb = SURF[surf]
    cap = 706
    x0, y0, x1, y1 = parts(key)[4]
    size = cap * (1.42 if badge else 1.36)
    sy = -cap / 2 - size / 2
    if badge:
        _, body = s_link(ba, bb, "l")
        sym = (f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})"><rect width="100" height="100" rx="23" '
               f'fill="{bg}"/><g transform="translate(18 18) scale(.64)">{body}</g></g>')
        left = 0
    else:
        _, body = s_link(a, b, "l")
        sym = f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})">{body}</g>'
        left = size * 0.15
    gx = size - left + cap * 0.32 - x0
    vx0, vy0 = left - 30, min(sy, -y1) - 30
    w, h = gx + x1 + 30 - vx0, max(sy + size, -y0) - vy0 + 30
    return (f'<svg viewBox="{vx0:.0f} {vy0:.0f} {w:.0f} {h:.0f}" {attrs}>{sym}'
            f'<g transform="translate({gx:.1f} 0)">{word_g(key, surf)}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for key, *_ in VARIANTS:
        for surf in ("paper", "night", "mono"):
            sfx = "" if surf == "mono" else f"-{surf}"
            (OUT / f"wordmark-{key}{sfx}.svg").write_text(wordmark_svg(key, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-{key}{sfx}.svg").write_text(lockup_svg(key, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-badge-{key}{sfx}.svg").write_text(lockup_svg(key, surf, x, badge=True) + "\n", encoding="utf-8")


def page():
    secs = "".join(f"""
    <article class="v" id="{k}">
      <div class="cap"><span class="idx">0{i + 1}</span><h3>{t}</h3><span class="spec">Chat {wc} · CRM {wr}{' · verde' if g else ''}</span></div>
      <p>{desc}</p>
      <div class="stage paper">{wordmark_svg(k, "paper")}</div>
      <div class="grid">
        <div class="paper">{lockup_svg(k, "paper")}</div>
        <div class="night">{lockup_svg(k, "night")}</div>
        <div class="paper">{lockup_svg(k, "paper", badge=True)}</div>
        <div class="night">{wordmark_svg(k, "night")}</div>
      </div>
      <code>v13/wordmark-{k}.svg · lockup-{k}.svg · lockup-badge-{k}.svg (+ -paper / -night)</code>
    </article>""" for i, (k, t, wc, wr, g, desc) in enumerate(VARIANTS))
    side = "".join(f'<div class="row"><span>0{i + 1}</span>{wordmark_svg(k, "paper")}</div>'
                   for i, (k, *_) in enumerate(VARIANTS))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — draft 13</title>
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
.intro {{ padding:56px 0 8px; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:700; letter-spacing:-.03em; line-height:1.05; }}
.intro p {{ margin-top:16px; color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; max-width:66ch; }}
.side {{ border:1px solid var(--hair); border-radius:18px; background:{PAPER}; margin-top:28px; padding:10px 24px; }}
.row {{ display:flex; align-items:center; gap:22px; padding:16px 0; border-bottom:1px solid rgba(23,23,23,.08); }}
.row:last-child {{ border-bottom:0; }} .row span {{ color:#8a8f8c; font-size:13px; width:22px; }}
.row svg {{ height:clamp(40px,7vw,66px); width:auto; }}
.v {{ border-top:1px solid var(--hair); margin-top:48px; padding-top:40px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; }}
.idx {{ font-size:13px; color:var(--muted); font-weight:600; }}
h3 {{ font-size:28px; font-weight:700; letter-spacing:-.02em; }}
.spec {{ margin-left:auto; font-size:13px; color:var(--muted); }}
.v > p {{ color:var(--muted); line-height:1.6; max-width:70ch; margin:8px 0 18px; font-size:16px; }}
.stage {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:clamp(40px,7vw,80px) 20px; }}
.stage svg {{ width:min(520px,86%); height:auto; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }}
@media (max-width:640px) {{ .grid {{ grid-template-columns:1fr; }} }}
.grid div {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:30px 16px; }}
.grid svg {{ width:min(300px,86%); height:auto; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · draft 13</span><button id="t">Claro / oscuro</button></div>
  <section class="intro">
    <h1>Chat y CRM,<br>juntos pero distintos</h1>
    <p>Sobre el redondo de v12: espaciado más apretado y el cursor más pegado a las dos palabras. Tres formas de
    diferenciar «Chat» de «CRM». El redondeo se ajusta al grosor de cada peso, así las letras finas y las
    gruesas se ven igual de suaves.</p>
    <div class="side">{side}</div>
  </section>
  {secs}
  <p class="foot">Elige la variante (01–04). Con eso genero el paquete final: PNG, favicon.ico, avatar 500×500 y banner.</p>
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
    (ROOT / "showcase-v13.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
