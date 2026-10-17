"""Brand draft 14 — variant 04 (Chat 600 + CRM 800 green), the caret question.

    python brand-source/build_v14.py

With CRM already split by weight and colour, the caret between the words reads as an extra letter.
Options: no caret / caret at the end (typing) / thin light caret between.
"""
from pathlib import Path

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER
from build_v11 import s_link
from build_v12 import pill, rounded
from build_v13 import ROUND, STEMS, TRACK, run

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v14"
WC, WR = 600, 800
CARET_TOP, CARET_BOT = 742, -70

MODES = [
    ("none", "Sin cursor", "ChatCRM a secas. El peso y el color ya separan las dos palabras; el nombre queda "
     "limpio y compacto, y el cursor vive solo en la interfaz del producto."),
    ("end", "Cursor al final", "El cursor pasa al final, como si el nombre se estuviera escribiendo: ChatCRM│. "
     "Conserva la idea de «escribir al cliente» sin cortar el nombre."),
    ("thin", "Cursor fino entre palabras", "Si quieres mantenerlo en medio: más fino, más corto (altura de "
     "mayúscula) y en menta, para que se lea como cursor y no como letra."),
]

_cache = {}


def parts(mode):
    """(chat_d, crm_d, caret_d | None, caret_is_light, bounds) in font units, y up."""
    if mode in _cache:
        return _cache[mode]
    chat, adv = run("Chat", WC, 0)
    caret, light = None, False
    if mode == "none":
        x = adv + 6                                   # t → C: tracking already applied, tiny optical air
    elif mode == "thin":
        w, gap = 40, 34
        cx = adv - TRACK * 1000 + gap
        caret, light = pill(cx, -20, w, 726), True
        x = cx + w + gap
    else:
        x = adv + 6
    crm, crm_adv = run("CRM", WR, x)
    if mode == "end":
        w, gap = 72, 46
        cx = x + crm_adv - TRACK * 1000 + gap
        caret = pill(cx, CARET_BOT, w, CARET_TOP)
    chat_d = rounded(chat, STEMS[WC] * ROUND)
    crm_d = rounded(crm, STEMS[WR] * ROUND)
    b1, b2 = chat.bounds, crm.bounds
    x1 = b2[2] if mode != "end" else cx + 72
    lo = CARET_BOT if mode == "end" else min(b1[1], b2[1])
    hi = CARET_TOP if mode == "end" else max(b1[3], b2[3])
    _cache[mode] = (chat_d, crm_d, caret, light, (b1[0], lo, x1, hi))
    return _cache[mode]


# surface -> (ink, green, light caret, symbol a, symbol b, badge bg, badge a, badge b)
SURF = {
    "paper": (INK, DEEP, "#2FA36B", DEEP, MINT, DEEP, PAPER, MINT),
    "night": (FROST, MINT, "#2FA36B", MINT, "#2FA36B", DEEP, PAPER, MINT),
    "mono":  ("currentColor",) * 8,
}


def word_g(mode, surf):
    ink, green, light = SURF[surf][:3]
    chat, crm, caret, is_light, _ = parts(mode)
    c = f'<path fill="{light if is_light else green}" d="{caret}"/>' if caret else ""
    return (f'<g transform="scale(1 -1)"><path fill="{ink}" d="{chat}"/>'
            f'<path fill="{green}" d="{crm}"/>{c}</g>')


def wordmark_svg(mode, surf, attrs='aria-hidden="true"', pad=40):
    x0, y0, x1, y1 = parts(mode)[4]
    return (f'<svg viewBox="{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}" {attrs}>'
            f'{word_g(mode, surf)}</svg>')


def lockup_svg(mode, surf, attrs='aria-hidden="true"', badge=False):
    *_, a, b, bg, ba, bb = SURF[surf]
    cap = 706
    x0, y0, x1, y1 = parts(mode)[4]
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
            f'<g transform="translate({gx:.1f} 0)">{word_g(mode, surf)}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for mode, *_ in MODES:
        for surf in ("paper", "night", "mono"):
            sfx = "" if surf == "mono" else f"-{surf}"
            (OUT / f"wordmark-{mode}{sfx}.svg").write_text(wordmark_svg(mode, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-{mode}{sfx}.svg").write_text(lockup_svg(mode, surf, x) + "\n", encoding="utf-8")
            (OUT / f"lockup-badge-{mode}{sfx}.svg").write_text(lockup_svg(mode, surf, x, badge=True) + "\n", encoding="utf-8")


def page():
    secs = "".join(f"""
    <article class="v" id="{k}">
      <div class="cap"><span class="idx">{chr(65 + i)}</span><h3>{t}</h3></div>
      <p>{desc}</p>
      <div class="grid">
        <div class="paper big">{lockup_svg(k, "paper")}</div>
        <div class="night big">{lockup_svg(k, "night")}</div>
        <div class="paper">{lockup_svg(k, "paper", badge=True)}</div>
        <div class="night">{lockup_svg(k, "night", badge=True)}</div>
        <div class="paper">{wordmark_svg(k, "paper")}</div>
        <div class="night">{wordmark_svg(k, "night")}</div>
      </div>
      <code>v14/wordmark-{k}.svg · lockup-{k}.svg · lockup-badge-{k}.svg (+ -paper / -night)</code>
    </article>""" for i, (k, t, desc) in enumerate(MODES))
    side = "".join(f'<div class="row"><span>{chr(65 + i)}</span>{wordmark_svg(k, "paper")}</div>'
                   for i, (k, *_) in enumerate(MODES))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — draft 14</title>
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
.intro {{ padding:56px 0 8px; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:700; letter-spacing:-.03em; line-height:1.05; }}
.intro p {{ margin-top:16px; color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; max-width:66ch; }}
.side {{ border:1px solid var(--hair); border-radius:18px; background:{PAPER}; margin-top:28px; padding:10px 24px; }}
.row {{ display:flex; align-items:center; gap:22px; padding:18px 0; border-bottom:1px solid rgba(23,23,23,.08); }}
.row:last-child {{ border-bottom:0; }} .row span {{ color:#8a8f8c; font-size:13px; width:22px; }}
.row svg {{ height:clamp(40px,7vw,70px); width:auto; }}
.v {{ border-top:1px solid var(--hair); margin-top:48px; padding-top:40px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; }}
.idx {{ font-size:13px; color:var(--muted); font-weight:600; }}
h3 {{ font-size:28px; font-weight:700; letter-spacing:-.02em; }}
.v > p {{ color:var(--muted); line-height:1.6; max-width:70ch; margin:8px 0 18px; font-size:16px; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
@media (max-width:640px) {{ .grid {{ grid-template-columns:1fr; }} }}
.grid div {{ border:1px solid var(--hair); border-radius:18px; display:grid; place-items:center; padding:30px 16px; }}
.grid .big {{ padding:56px 16px; }} .grid svg {{ width:min(300px,86%); height:auto; }} .grid .big svg {{ width:min(400px,88%); }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · draft 14</span><button id="t">Claro / oscuro</button></div>
  <section class="intro">
    <h1>Variante 04,<br>¿y el cursor?</h1>
    <p>Chat en 600, CRM en 800 y en verde, como elegiste. Con esa diferencia, el cursor en medio sobra y se lee
    como una letra más. Tres salidas:</p>
    <div class="side">{side}</div>
  </section>
  {secs}
  <p class="foot">Elige A, B o C y genero el paquete final.</p>
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
    (ROOT / "showcase-v14.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
