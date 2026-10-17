"""Brand draft 06: marks with depth (weave, extrusion, orbit) for chat-crm suite.

`python brand-source/build_v6.py` writes standalone SVGs to v6/ and the page showcase-v6.html.
Marks are drawn on a 100x100 grid and take a paint dict:
  main / accent / shade  -> fills or strokes (may be url(#gradient))
  mono                   -> True when everything is one colour (cuts replace tone changes)
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v6"

# Palette mapped from chat-crm-app/src/styles/theme.css (OKLCH -> sRGB)
DEEP, MINT, VIVID, EMERALD = "#006239", "#72E3AD", "#4ADE80", "#10B981"
INK, NIGHT, PAPER, FROST = "#171717", "#121212", "#FAFAFA", "#E2E8F0"

GAP = 3.2  # width of every cut between overlapping strands


def rrect(x, y, w, h, r):
    return (f"M {x+r} {y} H {x+w-r} A {r} {r} 0 0 1 {x+w} {y+r} V {y+h-r} "
            f"A {r} {r} 0 0 1 {x+w-r} {y+h} H {x+r} A {r} {r} 0 0 1 {x} {y+h-r} "
            f"V {y+r} A {r} {r} 0 0 1 {x+r} {y} Z")


def pt(cx, cy, r, ang):
    a = math.radians(ang)
    return round(cx + r * math.cos(a), 2), round(cy + r * math.sin(a), 2)


def mask(mid, content):
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-10" y="-10" width="120" height="120">'
            f'<rect x="-10" y="-10" width="120" height="120" fill="#fff"/>{content}</mask>')


# ---------------------------------------------------------------- marks

def m_link(p, u):
    """Enlace — the chat and the customer record woven together, each passing over the other once."""
    a = rrect(12, 18, 48, 44, 15)                    # chat (with tail)
    b = rrect(40, 38, 48, 44, 15)                    # record
    sw = 11
    tail = "M 14 52 L 7.5 77 Q 7 80.5 10.4 78.8 L 31 61 Z"
    over = sw + 2 * GAP
    defs = (f'<clipPath id="{u}c1"><circle cx="60" cy="38" r="13"/></clipPath>'
            f'<clipPath id="{u}c2"><circle cx="40" cy="62" r="13"/></clipPath>'
            + mask(f"{u}mb", f'<g clip-path="url(#{u}c1)"><path d="{a}" fill="none" stroke="#000" stroke-width="{over}"/></g>')
            + mask(f"{u}ma", f'<g clip-path="url(#{u}c2)"><path d="{b}" fill="none" stroke="#000" stroke-width="{over}"/></g>'))
    return (defs, f'<g mask="url(#{u}ma)"><path d="{a}" fill="none" stroke="{p["main"]}" stroke-width="{sw}"/>'
                  f'<path d="{tail}" fill="{p["main"]}"/></g>'
                  f'<path d="{b}" fill="none" stroke="{p["accent"]}" stroke-width="{sw}" mask="url(#{u}mb)"/>')


def _lemniscate(t, a=37, sy=1.7, cx=50, cy=46):
    d = 1 + math.sin(t) ** 2
    return cx + a * math.cos(t) / d, cy + sy * a * math.sin(t) * math.cos(t) / d


def _poly(t0, t1, n=160):
    pts = [_lemniscate(t0 + (t1 - t0) * i / n) for i in range(n + 1)]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def m_loop(p, u):
    """Infinito — the customer loop: two conversations that never end, one strand crossing over."""
    sw = 11.5
    full = _poly(0, 2 * math.pi, 320) + " Z"
    over = _poly(math.pi / 2 - 0.55, math.pi / 2 + 0.55, 60)
    tail = "M 25.5 60 L 15 82 Q 13.8 85.4 17.3 84.2 L 37 66.5 Z"
    defs = mask(f"{u}m", f'<path d="{over}" fill="none" stroke="#000" stroke-width="{sw + 2 * GAP}" stroke-linecap="butt"/>')
    return (defs, f'<g mask="url(#{u}m)"><path d="{full}" fill="none" stroke="{p["main"]}" stroke-width="{sw}" '
                  f'stroke-linejoin="round"/><path d="{tail}" fill="{p["main"]}"/></g>'
                  f'<path d="{over}" fill="none" stroke="{p["main"]}" stroke-width="{sw}"/>')


def _bubble_front():
    body = rrect(15, 13, 60, 48, 16)
    tail = "M 23 52 L 17.5 73 Q 17 76.6 20.3 75 L 43 60 Z"
    return body, tail


def m_block(p, u):
    """Bloque — a solid, extruded chat bubble with the c monogram carved through its face."""
    body, tail = _bubble_front()
    depth = 9
    ext = "".join(f'<path d="{body}" transform="translate({k} {k})"/><path d="{tail}" transform="translate({k} {k})"/>'
                  for k in range(1, depth + 1))
    s, e = pt(41, 37, 10.5, -50), pt(41, 37, 10.5, 50)
    glyph = (f'<path d="M {s[0]} {s[1]} A 10.5 10.5 0 1 0 {e[0]} {e[1]}" fill="none" stroke="#000" '
             f'stroke-width="7.5" stroke-linecap="round"/><circle cx="57.5" cy="37" r="4.6" fill="#000"/>')
    front_cut = (f'<path d="{body}" fill="#000" stroke="#000" stroke-width="{2 * GAP}"/>'
                 f'<path d="{tail}" fill="#000" stroke="#000" stroke-width="{2 * GAP}" stroke-linejoin="round"/>')
    defs = mask(f"{u}e", front_cut) + mask(f"{u}f", glyph)
    face = f'<g mask="url(#{u}f)" fill="{p["accent"]}"><path d="{body}"/><path d="{tail}"/></g>'
    if not p["mono"]:
        # glyph shows the dark body through the face
        face = (f'<g fill="{p["shade"]}"><path d="{body}"/><path d="{tail}"/></g>' + face)
        return defs, f'<g fill="{p["shade"]}">{ext}</g>{face}'
    return defs, f'<g fill="{p["shade"]}" mask="url(#{u}e)">{ext}</g>{face}'


def m_orbit(p, u):
    """Órbita — the suite turns around the conversation: a ring in front of the bubble, one behind."""
    rx, ry, rot, sw = 44, 13, -22, 5.5
    bubble = '<circle cx="50" cy="46" r="24"/><path d="M 33.5 60 L 25 79 Q 24 82.5 27.4 81 L 46 69.6 Z"/>'
    ell = f'<ellipse cx="50" cy="46" rx="{rx}" ry="{ry}"/>'
    front = f'<path d="M {50-rx} 46 A {rx} {ry} 0 0 0 {50+rx} 46"/>'
    sat = pt(50, 46, 1, 32)
    sx, sy = 50 + rx * math.cos(math.radians(32)), 46 + ry * math.sin(math.radians(32))
    rotg = f'transform="rotate({rot} 50 46)"'
    defs = (mask(f"{u}o", f'<g fill="#000" stroke="#000" stroke-width="{2 * GAP}" stroke-linejoin="round">{bubble}</g>')
            + mask(f"{u}b", f'<g {rotg} fill="none" stroke="#000" stroke-width="{sw + 2 * GAP}">{front}'
                            f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{6.5 + GAP}" fill="#000" stroke="none"/></g>'))
    return (defs,
            f'<g mask="url(#{u}o)"><g {rotg} fill="none" stroke="{p["accent"]}" stroke-width="{sw}">{ell}</g></g>'
            f'<g mask="url(#{u}b)" fill="{p["main"]}">{bubble}</g>'
            f'<g {rotg}><g fill="none" stroke="{p["accent"]}" stroke-width="{sw}" stroke-linecap="round">{front}</g>'
            f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="6.5" fill="{p["accent"]}"/></g>')


def m_fold(p, u):
    """Pliegue — the c monogram as a folded ribbon: its base folds under and becomes the speech tail."""
    cx, cy, rm, sw = 50, 46, 25, 17
    s, e = pt(cx, cy, rm, -44), pt(cx, cy, rm, 44)
    o1, o2 = pt(cx, cy, rm + sw / 2, 150), pt(cx, cy, rm - sw / 2, 112)
    i1 = pt(cx, cy, rm - sw / 2, 150)
    tail = f"M {o1[0]} {o1[1]} L 12 88 Q 10.8 91 14.2 90 L {o2[0]} {o2[1]} L {i1[0]} {i1[1]} Z"
    ring = (f'<path d="M {s[0]} {s[1]} A {rm} {rm} 0 1 0 {e[0]} {e[1]}" fill="none" stroke="{p["main"]}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>')
    dot = f'<circle cx="82.5" cy="{cy}" r="8" fill="{p["accent"]}"/>'
    if p["mono"]:
        # fold edge becomes a cut so the flap still reads in one colour
        crease = f'<path d="M {o1[0]} {o1[1]} L {o2[0]} {o2[1]}" stroke="#000" stroke-width="{GAP}"/>'
        defs = mask(f"{u}k", crease)
        return defs, f'<path d="{tail}" fill="{p["shade"]}"/><g mask="url(#{u}k)">{ring}</g>{dot}'
    return "", f'<path d="{tail}" fill="{p["shade"]}"/>{ring}{dot}'


MARKS = [
    ("fold", "Pliegue", m_fold,
     "El monograma «c» hecho cinta: su base se dobla por debajo y sale como la cola del mensaje. El doblez "
     "en verde profundo le da volumen real; el punto es el mensaje que se envía. Es una letra, no un ícono "
     "de chat: se puede registrar y nadie lo confunde.", "Marca principal"),
    ("link", "Enlace", m_link,
     "La conversación y la ficha del cliente entrelazadas: cada una pasa por encima de la otra una vez. "
     "Es literalmente lo que hace el producto: unir el chat con el CRM.", "Org · producto"),
    ("loop", "Infinito", m_loop,
     "Un lazo continuo con cola de mensaje: el ciclo del cliente que nunca se corta. Un solo trazo con "
     "cruce por encima; el degradado recorre todo el tema.", "Marketing · landing"),
    ("block", "Bloque", m_block,
     "Una burbuja sólida, extruida, con la «c» tallada en la cara. Tiene presencia de objeto: funciona "
     "como sticker, como merch y como ícono de app.", "App · merch · redes"),
    ("orbit", "Órbita", m_orbit,
     "La suite gira alrededor de la conversación: un anillo pasa por delante de la burbuja y otro por "
     "detrás, con un satélite. Para cuando la suite tenga varios módulos.", "Suite · módulos"),
]


def grad(gid, stops, x1=12, y1=10, x2=88, y2=92):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'{s}</linearGradient>')


THEMES = {
    "mono":  lambda u: ("", dict(main="currentColor", accent="currentColor", shade="currentColor", mono=True)),
    "light": lambda u: (grad(f"{u}g", [(0, VIVID), (0.55, "#0E8A50"), (1, DEEP)]),
                        dict(main=f"url(#{u}g)", accent=MINT, shade=DEEP, mono=False)),
    "dark":  lambda u: (grad(f"{u}g", [(0, MINT), (1, EMERALD)]),
                        dict(main=f"url(#{u}g)", accent=FROST, shade=DEEP, mono=False)),
    "icon":  lambda u: ("", dict(main="#FFFFFF", accent=MINT, shade=MINT, mono=False)),
}


def render(fn, theme, u):
    gdefs, paint = THEMES[theme](u)
    defs, body = fn(paint, u)
    return f"<defs>{gdefs}{defs}</defs>{body}"


def app_icon(fn, u, size=100):
    """Rounded-square app icon: theme gradient background, mark in white + mint."""
    bg = grad(f"{u}bg", [(0, "#0B8A52"), (1, "#003D24")], 0, 0, 100, 100)
    hl = grad(f"{u}hl", [(0, "rgba(255,255,255,0.18)"), (0.5, "rgba(255,255,255,0)")], 0, 0, 0, 100)
    return (f'<defs>{bg}{hl}</defs><rect width="100" height="100" rx="23" fill="url(#{u}bg)"/>'
            f'<rect width="100" height="100" rx="23" fill="url(#{u}hl)"/>'
            f'<g transform="translate(17 17) scale(.66)">{render(fn, "icon", u + "i")}</g>')


def svg_file(inner, title):
    return (f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="chat-crm suite — {title}"><title>{title}</title>{inner}</svg>\n')


def write_files():
    OUT.mkdir(exist_ok=True)
    for key, title, fn, *_ in MARKS:
        (OUT / f"{key}.svg").write_text(svg_file(render(fn, "mono", key), title), encoding="utf-8")
        (OUT / f"{key}-light.svg").write_text(svg_file(render(fn, "light", key), title), encoding="utf-8")
        (OUT / f"{key}-dark.svg").write_text(svg_file(render(fn, "dark", key), title), encoding="utf-8")
        (OUT / f"{key}-app.svg").write_text(svg_file(app_icon(fn, key), title), encoding="utf-8")


# ---------------------------------------------------------------- page

_n = 0


def uid():
    global _n
    _n += 1
    return f"x{_n}"


def show(fn, theme, cls=""):
    u = uid()
    inner = app_icon(fn, u) if theme == "app" else render(fn, theme, u)
    return f'<svg viewBox="0 0 100 100" class="{cls}" aria-hidden="true">{inner}</svg>'


def word(theme):
    return ('<div class="word"><span class="wm">chat<i></i>crm</span>'
            '<span class="sub">suite</span></div>')


def section(i, key, title, fn, desc, use):
    sizes = "".join(f'<div class="sz"><div style="width:{s}px;height:{s}px">{show(fn, "app")}</div><small>{s}</small></div>'
                    for s in (16, 24, 32, 48, 64))
    return f"""
<section class="mark" id="{key}">
  <div class="hero">
    <div class="hero-in">
      {show(fn, "dark", "hero-mark")}
      <div class="lock">{show(fn, "dark", "lock-mark")}{word("dark")}</div>
    </div>
    <span class="tag">{use}</span>
  </div>
  <div class="meta"><span class="num">0{i}</span><h2>{title}</h2></div>
  <p class="desc">{desc}</p>
  <div class="grid">
    <div class="t paper">{show(fn, "light")}<span>color · claro</span></div>
    <div class="t night">{show(fn, "dark")}<span>color · oscuro</span></div>
    <div class="t paper mono-l">{show(fn, "mono")}<span>una tinta</span></div>
    <div class="t mint">{show(fn, "mono")}<span>sobre menta</span></div>
    <div class="t appbg">{show(fn, "app", "app")}<span>ícono de app</span></div>
  </div>
  <div class="row">
    <div class="lk paper"><div class="lock">{show(fn, "light", "lock-mark")}{word("light")}</div></div>
    <div class="cell">
      <div class="label">Avatar GitHub · favicon</div>
      <div class="avs"><div class="av">{show(fn, "app")}</div><div class="av round">{show(fn, "app")}</div></div>
      <div class="sizes">{sizes}</div>
    </div>
  </div>
  <code>v6/{key}.svg · {key}-light.svg · {key}-dark.svg · {key}-app.svg</code>
</section>"""


def page():
    nav = "".join(f'<a href="#{k}">{show(fn, "app")}<span>{t}</span></a>' for k, t, fn, *_ in MARKS)
    secs = "".join(section(i + 1, *m) for i, m in enumerate(MARKS))
    gh = "".join(f'<div class="gh"><div class="gh-av">{show(fn, "app")}</div><div><b>chat-crm-suite</b>'
                 f'<small>{t} · 6 repositories</small></div></div>' for k, t, fn, *_ in MARKS)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>chat-crm suite — draft 06</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:rgba(23,23,23,.62); --hair:rgba(23,23,23,.12); --card:#fff; --acc:{DEEP}; color-scheme:light; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:{NIGHT}; --fg:{FROST};
  --muted:rgba(226,232,240,.6); --hair:rgba(226,232,240,.13); --card:#191919; --acc:{VIVID}; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:{NIGHT}; --fg:{FROST}; --muted:rgba(226,232,240,.6); --hair:rgba(226,232,240,.13);
  --card:#191919; --acc:{VIVID}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:Outfit,system-ui,sans-serif; background:var(--bg); color:var(--fg); -webkit-font-smoothing:antialiased; }}
.page {{ max-width:1160px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:22px 0; font-weight:600; }}
button {{ font:inherit; font-size:13px; font-weight:500; color:var(--fg); background:none; border:1px solid var(--hair);
  border-radius:99px; padding:7px 16px; cursor:pointer; }}
button:hover {{ border-color:var(--acc); color:var(--acc); }}
.intro {{ margin:36px 0 28px; }}
.intro h1 {{ font-size:clamp(38px,7vw,76px); font-weight:800; letter-spacing:-.04em; line-height:.98; }}
.intro h1 span {{ background:linear-gradient(120deg,{MINT},{VIVID} 45%,{EMERALD}); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.intro p {{ margin-top:18px; font-size:18px; font-weight:300; color:var(--muted); max-width:62ch; line-height:1.6; }}
.nav {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:64px; }}
.nav a {{ display:flex; align-items:center; gap:12px; padding:12px; border:1px solid var(--hair); border-radius:16px;
  background:var(--card); color:var(--fg); text-decoration:none; font-weight:600; transition:border-color .2s,transform .2s; }}
.nav a:hover {{ border-color:var(--acc); transform:translateY(-2px); }}
.nav svg {{ width:44px; height:44px; flex:none; }}
.mark {{ padding:0 0 88px; }}
.hero {{ position:relative; border-radius:28px; overflow:hidden; background:
  radial-gradient(60% 90% at 18% 30%, rgba(74,222,128,.22), transparent 70%),
  radial-gradient(50% 80% at 90% 100%, rgba(16,185,129,.18), transparent 70%), #0C0F0D;
  min-height:340px; display:grid; place-items:center; padding:48px 24px; }}
.hero::after {{ content:""; position:absolute; inset:0; background-image:radial-gradient(rgba(255,255,255,.06) 1px, transparent 1px);
  background-size:22px 22px; mask-image:linear-gradient(to bottom, #000, transparent); pointer-events:none; }}
.hero-in {{ position:relative; z-index:1; display:flex; align-items:center; gap:clamp(24px,6vw,72px); flex-wrap:wrap; justify-content:center; }}
.hero-mark {{ width:clamp(130px,22vw,210px); height:auto; filter:drop-shadow(0 18px 40px rgba(74,222,128,.25)); }}
.hero .lock .word {{ color:{FROST}; }}
.tag {{ position:absolute; z-index:1; top:18px; right:18px; font-size:12px; color:{MINT}; border:1px solid rgba(114,227,173,.35);
  border-radius:99px; padding:5px 12px; }}
.lock {{ display:flex; align-items:center; gap:14px; }}
.lock-mark {{ width:clamp(54px,8vw,76px); height:auto; flex:none; }}
.word {{ display:flex; flex-direction:column; line-height:.9; }}
.wm {{ font-size:clamp(34px,6vw,58px); font-weight:800; letter-spacing:-.045em; }}
.wm i {{ display:inline-block; width:.2em; height:.2em; border-radius:50%; background:{VIVID}; margin:0 .07em; vertical-align:.12em; }}
.paper .wm i {{ background:{DEEP}; }}
.sub {{ font-size:clamp(11px,1.4vw,14px); font-weight:600; letter-spacing:.62em; text-transform:uppercase; margin-top:.75em;
  color:{MINT}; padding-left:.12em; }}
.paper .sub {{ color:{DEEP}; }}
.meta {{ display:flex; align-items:baseline; gap:14px; margin-top:28px; }}
.num {{ color:var(--muted); font-size:14px; font-variant-numeric:tabular-nums; }}
h2 {{ font-size:34px; font-weight:700; letter-spacing:-.02em; }}
.desc {{ margin:8px 0 22px; color:var(--muted); font-weight:300; font-size:16.5px; max-width:72ch; line-height:1.6; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }}
.t {{ position:relative; aspect-ratio:1; border-radius:20px; display:grid; place-items:center; border:1px solid var(--hair); }}
.t svg {{ width:60%; height:60%; }} .t svg.app {{ width:56%; height:56%; filter:drop-shadow(0 10px 18px rgba(0,61,36,.35)); }}
.t span {{ position:absolute; left:12px; bottom:10px; font-size:11px; opacity:.6; }}
.paper {{ background:{PAPER}; color:{INK}; }} .night {{ background:{NIGHT}; color:{FROST}; }}
.mono-l {{ color:{DEEP}; }} .mint {{ background:{MINT}; color:{DEEP}; border-color:transparent; }}
.appbg {{ background:linear-gradient(160deg,#eef8f2,#dcefe5); color:{INK}; }}
.row {{ display:grid; grid-template-columns:minmax(0,1.45fr) minmax(0,1fr); gap:10px; margin-top:10px; }}
@media (max-width:760px) {{ .row {{ grid-template-columns:1fr; }} }}
.lk {{ border-radius:20px; border:1px solid var(--hair); padding:32px 28px; display:flex; align-items:center; }}
.cell {{ border:1px solid var(--hair); border-radius:20px; padding:20px; background:var(--card); }}
.label {{ font-size:12px; color:var(--muted); margin-bottom:12px; }}
.avs {{ display:flex; gap:14px; margin-bottom:20px; }}
.av {{ width:84px; height:84px; }} .av svg {{ width:100%; height:100%; display:block; }}
.av.round svg {{ clip-path:circle(50%); }}
.sizes {{ display:flex; gap:16px; align-items:flex-end; flex-wrap:wrap; }}
.sz {{ display:flex; flex-direction:column; align-items:center; gap:6px; }} .sz svg {{ width:100%; height:100%; display:block; }}
.sz small {{ font-size:11px; color:var(--muted); }}
code {{ display:inline-block; margin-top:14px; font-size:12px; color:var(--muted); }}
.ctx h3 {{ font-size:24px; font-weight:700; margin-bottom:16px; }}
.ghs {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:10px; }}
.gh {{ display:flex; gap:14px; align-items:center; border:1px solid var(--hair); border-radius:14px; padding:14px; background:var(--card); }}
.gh-av {{ width:52px; height:52px; flex:none; }} .gh-av svg {{ width:100%; height:100%; }}
.gh b {{ display:block; font-weight:700; }} .gh small {{ color:var(--muted); font-size:12px; }}
.foot {{ margin-top:56px; color:var(--muted); font-weight:300; border-top:1px solid var(--hair); padding-top:26px; line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><span>chat-crm-suite · brand</span><button id="t">Cambiar tema</button></div>
  <div class="intro">
    <h1>chat-crm <span>suite</span><br>draft 06</h1>
    <p>Cinco marcas con volumen: cintas que se doblan, trazos que se cruzan por encima y por debajo, un
    objeto extruido, una órbita. Usan el degradado del tema (menta → verde vivo → verde profundo) y un
    wordmark más pesado. Cada una se muestra en grande sobre oscuro, en claro, a una tinta, como ícono
    de app y como avatar de GitHub.</p>
  </div>
  <div class="nav">{nav}</div>
  {secs}
  <section class="ctx"><h3>En la organización de GitHub</h3><div class="ghs">{gh}</div></section>
  <p class="foot">Dime cuál (o qué mezcla) y la llevo a versión final: ajuste óptico de grosores y cortes, wordmark
  convertido a curvas, PNG 1024 px, favicon.ico, avatar 500×500 y banner social 1280×640.</p>
</div>
<script>
const r=document.documentElement, b=document.getElementById('t');
b.onclick=()=>{{const dark=r.dataset.theme? r.dataset.theme==='dark' : matchMedia('(prefers-color-scheme: dark)').matches;
r.dataset.theme=dark?'light':'dark';}};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    write_files()
    (ROOT / "showcase-v6.html").write_text(page(), encoding="utf-8")
    print("ok:", len(list(OUT.iterdir())), "files")
