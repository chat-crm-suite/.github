"""Brand draft 11 — compact Outfit wordmark + abstract symbols (friendly SaaS: Slack/Intercom/HubSpot).

    python brand-source/build_v11.py

Wordmark: Outfit 700 (the frontend typeface), compact spacing, the v8 caret in green. No cuts, no tails.
Symbols: drawn on a 100 grid, rounded geometry matched to Outfit's weight (stem/cap ≈ 0.22).
"""
import math
from pathlib import Path

from build_v7 import DEEP, FROST, INK, MINT, NIGHT, PAPER
from build_v9 import d, glyph, poly, shape, union

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v11"

TRACK = -0.03                       # compact spacing (em)
CARET_W, CARET_GAP, CARET_TOP, CARET_BOT = 74, 62, 742, -70
GAP = 4.5                           # cut between overlapping symbol parts


# ---------------------------------------------------------------- wordmark (font units, y up)

def wordmark_parts():
    chat, chat_adv = shape("Chat", TRACK)
    rest = [glyph(n, x) for n, x in chat]
    cx = chat_adv + CARET_GAP
    crm, _ = shape("CRM", TRACK)
    dx = cx + CARET_W + CARET_GAP
    rest += [glyph(n, x + dx) for n, x in crm]
    caret = poly((cx, CARET_BOT), (cx + CARET_W, CARET_BOT), (cx + CARET_W, CARET_TOP), (cx, CARET_TOP))
    return union(*rest), caret


_WM = None


def wm():
    global _WM
    if _WM is None:
        _WM = wordmark_parts()
    return _WM


def wm_bounds():
    a, b = wm()
    ba, bb = a.bounds, b.bounds
    return min(ba[0], bb[0]), min(ba[1], bb[1]), max(ba[2], bb[2]), max(ba[3], bb[3])


def wordmark_g(ink, acc):
    letters, caret = wm()
    return (f'<g transform="scale(1 -1)"><path fill="{ink}" d="{d(letters)}"/>'
            f'<path fill="{acc}" d="{d(caret)}"/></g>')


# ---------------------------------------------------------------- symbols (100 grid, y down)

def leaf(x, y, s, sharp):
    """Rounded square with radius s/2 on three corners; `sharp` corner stays square (tl/tr/br/bl)."""
    r = s / 2
    R = {c: (0 if c == sharp else r) for c in ("tl", "tr", "br", "bl")}
    return (f"M {x + R['tl']} {y} H {x + s - R['tr']} "
            + (f"A {R['tr']} {R['tr']} 0 0 1 {x + s} {y + R['tr']} " if R['tr'] else "")
            + f"V {y + s - R['br']} " + (f"A {R['br']} {R['br']} 0 0 1 {x + s - R['br']} {y + s} " if R['br'] else "")
            + f"H {x + R['bl']} " + (f"A {R['bl']} {R['bl']} 0 0 1 {x} {y + s - R['bl']} " if R['bl'] else "")
            + f"V {y + R['tl']} " + (f"A {R['tl']} {R['tl']} 0 0 1 {x + R['tl']} {y} " if R['tl'] else "") + "Z")


def mask(mid, content):
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<rect width="100" height="100" fill="#fff"/>{content}</mask>')


def s_dialogue(a, b, u):
    """Diálogo — two voices: two forms, each with one sharp corner, overlapping into one conversation."""
    back = leaf(14, 14, 50, "bl")
    front = leaf(36, 36, 50, "br")
    return (mask(f"{u}m", f'<path d="{front}" fill="#000" stroke="#000" stroke-width="{GAP * 2}"/>'),
            f'<path d="{back}" fill="{b}" mask="url(#{u}m)"/><path d="{front}" fill="{a}"/>')


def s_converge(a, b, u):
    """Convergencia — every conversation points to one place: four forms, sharp corners to the centre."""
    s, g, o = 36, 6, 11
    parts = [(o, o, "br", b), (o + s + g, o, "bl", a), (o, o + s + g, "tr", a), (o + s + g, o + s + g, "tl", a)]
    return "", "".join(f'<path d="{leaf(x, y, s, c)}" fill="{p}"/>' for x, y, c, p in parts)


def s_flow(a, b, u):
    """Flujo — a conversation flowing into the record: a rounded square split by one soft curve."""
    sq = "M 36 12 H 64 A 24 24 0 0 1 88 36 V 64 A 24 24 0 0 1 64 88 H 36 A 24 24 0 0 1 12 64 V 36 A 24 24 0 0 1 36 12 Z"
    curve = "M 70 4 C 70 40 30 60 30 96"
    left = "M 0 0 H 70 C 70 40 30 60 30 100 H 0 Z"
    right = "M 70 0 H 100 V 100 H 30 C 30 60 70 40 70 0 Z"
    cut = f'<path d="{curve}" fill="none" stroke="#000" stroke-width="{GAP * 1.6}"/>'
    return ((f'<clipPath id="{u}l"><path d="{left}"/></clipPath><clipPath id="{u}r"><path d="{right}"/></clipPath>'
             + mask(f"{u}m", cut)),
            f'<g mask="url(#{u}m)"><path d="{sq}" fill="{a}" clip-path="url(#{u}l)"/>'
            f'<path d="{sq}" fill="{b}" clip-path="url(#{u}r)"/></g>')


def s_link(a, b, u):
    """Monograma CC — two C's, one turned 180°, closing a circle: the back-and-forth of a conversation."""
    r, sw = 27, 16

    def arc(start, end):
        p = lambda t: (50 + r * math.cos(math.radians(t)), 50 + r * math.sin(math.radians(t)))
        (x1, y1), (x2, y2) = p(start), p(end)
        return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 0 1 {x2:.2f} {y2:.2f}"
    return "", (f'<path d="{arc(165, 285)}" fill="none" stroke="{b}" stroke-width="{sw}" stroke-linecap="round"/>'
                f'<path d="{arc(-15, 105)}" fill="none" stroke="{a}" stroke-width="{sw}" stroke-linecap="round"/>')


SYMBOLS = [
    ("dialogue", "Diálogo", s_dialogue,
     "Dos formas, cada una con una esquina recta, que se superponen: dos voces (tu negocio y tu cliente) "
     "en una sola conversación. Amigable y muy reconocible, en la línea de Intercom o Notion."),
    ("converge", "Convergencia", s_converge,
     "Cuatro formas con su esquina recta apuntando al centro: todas las conversaciones llegan a un mismo "
     "lugar, el CRM. Modular y de «suite», en la línea de Slack."),
    ("flow", "Flujo", s_flow,
     "Un cuadrado redondeado partido por una curva suave: la conversación (menta) fluye hacia el registro "
     "del cliente (verde). Sólido y corporativo, en la línea de HubSpot o Zendesk."),
    ("link", "Monograma CC", s_link,
     "La C de Chat y la C de CRM, una girada 180° respecto de la otra, cierran un círculo con dos aberturas: "
     "el ida y vuelta de una conversación. La variante de monograma que pediste ver."),
]

# surface -> (symbol a, symbol b, word ink, caret, badge bg, badge a, badge b)
SURF = {
    "paper": (DEEP, MINT, INK, DEEP, DEEP, PAPER, MINT),
    "night": (MINT, "#2FA36B", FROST, MINT, DEEP, PAPER, MINT),
    "mono":  ("currentColor",) * 7,
}

_n = 0


def uid():
    global _n
    _n += 1
    return f"q{_n}"


def symbol_svg(fn, surf="paper", attrs='aria-hidden="true"', u=None, mono=False):
    a, b = SURF[surf][:2]
    if mono:
        b = a
    defs, body = fn(a, b, u or uid())
    return f'<svg viewBox="0 0 100 100" {attrs}><defs>{defs}</defs>{body}</svg>'


def badge_svg(fn, surf="paper", attrs='aria-hidden="true"', u=None):
    *_, bg, a, b = SURF[surf]
    defs, body = fn(a, b, u or uid())
    return (f'<svg viewBox="0 0 100 100" {attrs}><defs>{defs}</defs><rect width="100" height="100" rx="23" fill="{bg}"/>'
            f'<g transform="translate(19 19) scale(.62)">{body}</g></svg>')


def wordmark_svg(surf, attrs='aria-hidden="true"', pad=40):
    _, _, ink, acc, *_ = SURF[surf]
    x0, y0, x1, y1 = wm_bounds()
    return (f'<svg viewBox="{x0 - pad:.0f} {-y1 - pad:.0f} {x1 - x0 + 2 * pad:.0f} {y1 - y0 + 2 * pad:.0f}" {attrs}>'
            f'{wordmark_g(ink, acc)}</svg>')


def lockup_svg(fn, surf, attrs='aria-hidden="true"', u=None, badge=False):
    """Symbol height = 1.3 x cap height (706), centred on the caps; gap = 0.36 cap."""
    a, b, ink, acc, bg, ba, bb = SURF[surf]
    cap, x0, y0, x1, y1 = 706, *wm_bounds()
    size = cap * (1.42 if badge else 1.3)
    sy = -(cap / 2) - size / 2                 # y-down coordinates for the symbol box
    u = u or uid()
    if badge:
        defs, body = fn(ba, bb, u)
        sym = (f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})"><rect width="100" height="100" rx="23" '
               f'fill="{bg}"/><g transform="translate(19 19) scale(.62)">{body}</g></g>')
    else:
        defs, body = fn(a, b, u)
        sym = f'<g transform="translate(0 {sy:.1f}) scale({size / 100:.3f})">{body}</g>'
    gx = size + cap * 0.36 - x0
    vx0, vy0 = -30, min(sy, -y1) - 30
    w, h = gx + x1 + 60, max(sy + size, -y0) - vy0 + 30
    return (f'<svg viewBox="{vx0} {vy0:.0f} {w:.0f} {h:.0f}" {attrs}><defs>{defs}</defs>{sym}'
            f'<g transform="translate({gx:.1f} 0)">{wordmark_g(ink, acc)}</g></svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    x = 'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ChatCRM"'
    for surf in ("paper", "night", "mono"):
        sfx = "" if surf == "mono" else f"-{surf}"
        (OUT / f"wordmark{sfx}.svg").write_text(wordmark_svg(surf, x) + "\n", encoding="utf-8")
        for key, _, fn, _ in SYMBOLS:
            (OUT / f"{key}-symbol{sfx}.svg").write_text(symbol_svg(fn, surf, x, key, mono=surf == "mono") + "\n", encoding="utf-8")
            (OUT / f"{key}-badge{sfx}.svg").write_text(badge_svg(fn, surf, x, key) + "\n", encoding="utf-8")
            (OUT / f"{key}-lockup{sfx}.svg").write_text(lockup_svg(fn, surf, x, key) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- page

def page():
    nav = "".join(f'<a href="#{k}">{badge_svg(fn)}<span>{t}</span></a>' for k, t, fn, _ in SYMBOLS)

    def sec(i, k, t, fn, desc):
        sizes = "".join(f'<span style="width:{s}px;height:{s}px">{badge_svg(fn)}</span>' for s in (16, 24, 32, 48, 64))
        return f"""
    <article class="sym" id="{k}">
      <div class="cap"><span class="idx">0{i}</span><h3>{t}</h3></div>
      <p>{desc}</p>
      <div class="row3">
        <div class="tile paper">{symbol_svg(fn, "paper")}<span>símbolo</span></div>
        <div class="tile paper">{badge_svg(fn, "paper")}<span>insignia · GitHub</span></div>
        <div class="tile night">{badge_svg(fn, "night")}<span>insignia · oscuro</span></div>
        <div class="tile paper">{symbol_svg(fn, "paper", mono=True)}<span>una tinta</span></div>
      </div>
      <div class="lk paper">{lockup_svg(fn, "paper")}</div>
      <div class="lk2">
        <div class="night">{lockup_svg(fn, "night")}</div>
        <div class="paper">{lockup_svg(fn, "paper", badge=True)}</div>
      </div>
      <div class="sizes">{sizes}<div class="gh"><span class="av">{badge_svg(fn)}</span><b>chat-crm-suite</b></div></div>
      <code>v11/{k}-symbol.svg · {k}-badge.svg · {k}-lockup.svg (+ -paper / -night)</code>
    </article>"""
    secs = "".join(sec(i + 1, *s) for i, s in enumerate(SYMBOLS))
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatCRM — draft 11</title>
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
button {{ font:inherit; font-size:12px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:8px;
  padding:7px 14px; cursor:pointer; text-transform:uppercase; letter-spacing:.06em; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.paper {{ background:{PAPER}; }} .night {{ background:{NIGHT}; }}
.intro {{ padding:56px 0 28px; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:700; letter-spacing:-.03em; line-height:1.05; }}
.intro p {{ margin-top:16px; color:var(--muted); font-size:17px; font-weight:300; line-height:1.65; max-width:66ch; }}
.wmstage {{ border:1px solid var(--hair); border-radius:16px; display:grid; place-items:center; padding:clamp(44px,8vw,88px) 20px; margin-top:28px; }}
.wmstage svg {{ width:min(520px,86%); height:auto; }}
.nav {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:28px 0 8px; }}
.nav a {{ display:flex; gap:12px; align-items:center; padding:12px; border:1px solid var(--hair); border-radius:14px;
  background:var(--card); color:var(--fg); text-decoration:none; font-weight:600; }}
.nav a:hover {{ border-color:var(--acc); }} .nav svg {{ width:44px; height:44px; flex:none; }}
.sym {{ border-top:1px solid var(--hair); margin-top:48px; padding-top:44px; }}
.cap {{ display:flex; gap:12px; align-items:baseline; }}
.idx {{ font-size:13px; color:var(--muted); font-weight:600; }}
h3 {{ font-size:30px; font-weight:700; letter-spacing:-.02em; }}
.sym > p {{ color:var(--muted); line-height:1.6; max-width:68ch; margin:8px 0 20px; font-size:16.5px; }}
.row3 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:10px; }}
.tile {{ position:relative; aspect-ratio:1; border:1px solid var(--hair); border-radius:16px; display:grid; place-items:center; }}
.tile svg {{ width:52%; height:52%; }}
.tile span {{ position:absolute; left:12px; bottom:10px; font-size:11px; color:#8a8f8c; }}
.lk {{ border:1px solid var(--hair); border-radius:16px; display:grid; place-items:center; padding:clamp(36px,6vw,64px) 20px; margin-top:10px; }}
.lk svg {{ width:min(470px,86%); height:auto; }}
.lk2 {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px; }}
@media (max-width:640px) {{ .lk2 {{ grid-template-columns:1fr; }} }}
.lk2 div {{ border:1px solid var(--hair); border-radius:16px; display:grid; place-items:center; padding:30px 16px; }}
.lk2 svg {{ width:min(280px,86%); height:auto; }}
.sizes {{ display:flex; gap:18px; align-items:flex-end; flex-wrap:wrap; border:1px solid var(--hair); border-radius:16px;
  padding:20px; margin-top:10px; background:var(--card); }}
.sizes > span svg {{ width:100%; height:100%; display:block; }}
.gh {{ margin-left:auto; display:flex; gap:12px; align-items:center; }} .gh .av {{ width:52px; height:52px; }}
.gh .av svg {{ width:100%; height:100%; display:block; }} .gh b {{ font-size:18px; }}
code {{ display:block; margin-top:10px; font-size:12px; color:var(--muted); }}
.foot {{ border-top:1px solid var(--hair); margin-top:56px; padding-top:24px; color:var(--muted); line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>ChatCRM · draft 11</span><button id="t">Claro / oscuro</button></div>
  <section class="intro">
    <h1>Outfit compacta,<br>símbolo abstracto</h1>
    <p>De vuelta al sistema que te gustó (v8): <b>Chat│CRM</b> con el cursor. Ahora en Outfit 700, la tipografía
    del frontend, sin adornos, con el espaciado apretado para que el nombre se vea compacto y sólido. Los
    símbolos son formas redondeadas con el mismo peso visual que las letras, para que el conjunto se vea como
    una sola pieza.</p>
    <div class="wmstage paper">{wordmark_svg("paper")}</div>
    <div class="nav">{nav}</div>
  </section>
  {secs}
  <p class="foot">Dime cuál te convence (o qué cambiarías de alguna). Con eso ajusto proporciones finas y cierro
  los archivos finales.</p>
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
    (ROOT / "showcase-v11.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
