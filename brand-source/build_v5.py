"""Builds brand draft 05: standalone SVGs in v5/ and the comparison page showcase-v5.html.

Run from anywhere: `python brand-source/build_v5.py`. Every mark is drawn on a 100x100 grid.
Marks take two paints: `a` (main) and `b` (second tone; equals `a` in mono files).
"""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "v5"

# Palette mapped from chat-crm-app/src/styles/theme.css (OKLCH -> sRGB)
DEEP, MINT, VIVID = "#006239", "#72E3AD", "#4ADE80"
INK, NIGHT, PAPER = "#171717", "#121212", "#FAFAFA"
BLUE, VIOLET, AMBER = "#3B82F6", "#8B5CF6", "#F59E0B"          # chart-2..4 light
BLUE_D, VIOLET_D, AMBER_D = "#60A5FA", "#A78BFA", "#FBBF24"    # chart-2..4 dark


def rrect(x, y, w, h, r, sharp=()):
    """Rounded rect path; corners named tl/tr/br/bl listed in `sharp` stay square."""
    def rad(c):
        return 0 if c in sharp else r
    tl, tr, br, bl = rad("tl"), rad("tr"), rad("br"), rad("bl")
    return (f"M {x+tl} {y} H {x+w-tr} " + (f"A {tr} {tr} 0 0 1 {x+w} {y+tr} " if tr else "")
            + f"V {y+h-br} " + (f"A {br} {br} 0 0 1 {x+w-br} {y+h} " if br else "")
            + f"H {x+bl} " + (f"A {bl} {bl} 0 0 1 {x} {y+h-bl} " if bl else "")
            + f"V {y+tl} " + (f"A {tl} {tl} 0 0 1 {x+tl} {y} " if tl else "") + "Z")


# Shared chat bubble: body 18..82 x 20..72, tail out of the bottom-left.
BODY = rrect(18, 20, 64, 52, 17)
TAIL = "M 25 62 L 20.5 84.5 Q 20 88 23.2 86.4 L 45 71 Z"


def cut(uid, shapes, body):
    """Single-colour shape with `shapes` (black-filled SVG) carved out of it."""
    return (f'<defs><mask id="{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100">'
            f'<rect width="100" height="100" fill="#fff"/>{shapes}</mask></defs>'
            f'<g mask="url(#{uid})">{body}</g>')


def m_pulse(a, b, uid):
    # Typing dots that rise like a bar chart: the conversation and its numbers.
    dots = "".join(f'<circle cx="{cx}" cy="{55-r}" r="{r}" fill="#000"/>'
                   for cx, r in ((32, 3.6), (48, 5.6), (66.5, 7.8)))
    return cut(uid, dots, f'<path d="{BODY}" fill="{a}"/><path d="{TAIL}" fill="{a}"/>')


def m_funnel(a, b, uid):
    # Three message lines narrowing into a sales funnel.
    bars = "".join(f'<rect x="{50-w/2}" y="{y}" width="{w}" height="7" rx="3.5" fill="#000"/>'
                   for y, w in ((32, 38), (43.5, 26), (55, 13)))
    return cut(uid, bars, f'<path d="{BODY}" fill="{a}"/><path d="{TAIL}" fill="{a}"/>')


def m_contact(a, b, uid):
    # A contact card that talks: the person cut out of the bubble.
    person = ('<circle cx="50" cy="38.5" r="8.5" fill="#000"/>'
              '<path d="M 33 64 C 33 54 40.5 50.5 50 50.5 C 59.5 50.5 67 54 67 64 Z" fill="#000"/>')
    return cut(uid, person, f'<path d="{BODY}" fill="{a}"/><path d="{TAIL}" fill="{a}"/>')


def m_dialogue(a, b, uid):
    # Business and customer: two bubbles facing each other, a clean gap between them.
    back = rrect(38, 16, 48, 40, 14)
    back_tail = "M 76 48 L 82.5 63.5 Q 83.5 66.5 80.6 65.2 L 64 55.5 Z"
    front = rrect(14, 36, 50, 40, 14)
    front_tail = "M 24 68 L 18 84 Q 17.2 87 20.2 85.6 L 38 75.5 Z"
    gap = (f'<path d="{front}" fill="none" stroke="#000" stroke-width="9"/>'
           f'<path d="{front_tail}" fill="none" stroke="#000" stroke-width="9" stroke-linejoin="round"/>')
    return (cut(uid, gap, f'<path d="{back}" fill="{b}"/><path d="{back_tail}" fill="{b}"/>')
            + f'<path d="{front}" fill="{a}"/><path d="{front_tail}" fill="{a}"/>')


def m_monogram(a, b, uid):
    # A heavy "c" whose lower stroke becomes the speech tail; the dot is the message going out.
    cx, cy, rm, sw, gap = 50, 48, 24.5, 15, 46
    p = lambda ang, r=rm: (round(cx + r * math.cos(math.radians(ang)), 2),
                           round(cy + r * math.sin(math.radians(ang)), 2))
    s, e = p(-gap), p(gap)
    o1, o2 = p(152, 32), p(112, 32)
    return (f'<path d="M {s[0]} {s[1]} A {rm} {rm} 0 1 0 {e[0]} {e[1]}" fill="none" stroke="{a}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path d="M {o1[0]} {o1[1]} L 14.5 85 Q 13.6 88.4 16.8 87.2 L {o2[0]} {o2[1]} Z" fill="{a}"/>'
            f'<circle cx="80" cy="{cy}" r="7.5" fill="{b}"/>')


def m_suite(a, b, uid, c=None, d=None):
    # The suite: four modules, the chat one keeps a sharp corner, a speech bubble in square form.
    c, d = c or a, d or a
    return (f'<path d="{rrect(17, 17, 30, 30, 9)}" fill="{b}"/>'
            f'<path d="{rrect(53, 17, 30, 30, 9)}" fill="{c}"/>'
            f'<path d="{rrect(17, 53, 30, 30, 9, sharp=("bl",))}" fill="{a}"/>'
            f'<path d="{rrect(53, 53, 30, 30, 15)}" fill="{d}"/>')


MARKS = [
    ("pulse", "Pulso", m_pulse,
     "Los tres puntos de «escribiendo…» crecen como una gráfica: la conversación y sus métricas en "
     "un solo gesto. El más legible a 16 px.", "Favicon · app · avatar"),
    ("funnel", "Embudo", m_funnel,
     "Tres líneas de mensaje que se estrechan hasta formar un embudo de ventas. Lo que entra por chat "
     "termina en cliente: es la frase del CRM.", "Ventas · pitch · docs"),
    ("contact", "Contacto", m_contact,
     "La ficha del contacto dentro de la burbuja: cada chat es una persona con historial. El más "
     "explícito sobre «CRM».", "Producto · onboarding"),
    ("dialogue", "Diálogo", m_dialogue,
     "Negocio y cliente, dos burbujas enfrentadas con un corte limpio. En dos tonos (menta detrás, "
     "verde profundo delante) es la versión más cálida.", "Marketing · landing"),
    ("monogram", "Monograma c", m_monogram,
     "Una «c» gruesa cuya base se convierte en la cola del mensaje; el punto es el mensaje que sale. "
     "El más propio: no se confunde con ninguna app de chat.", "Marca principal · org GitHub"),
    ("suite", "Suite", m_suite,
     "Cuatro módulos de la suite; el de chat conserva una esquina recta, una burbuja cuadrada. "
     "La versión color usa los colores de las gráficas del frontend.", "Org chat-crm-suite · repos"),
]


def svg(inner, title, size=100):
    return (f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="chat-crm — {title}"><title>{title}</title>{inner}</svg>')


def write_files():
    OUT.mkdir(exist_ok=True)
    for key, title, fn, *_ in MARKS:
        (OUT / f"{key}.svg").write_text(svg(fn("currentColor", "currentColor", f"{key}-m"), title) + "\n",
                                        encoding="utf-8")
    two = {
        "dialogue-duo": lambda u: m_dialogue(DEEP, MINT, u),
        "monogram-duo": lambda u: m_monogram(DEEP, MINT, u),
        "suite-color": lambda u: m_suite(DEEP, MINT, u, BLUE, AMBER),
        "suite-color-night": lambda u: m_suite(VIVID, MINT, u, BLUE_D, AMBER_D),
    }
    for key, fn in two.items():
        (OUT / f"{key}.svg").write_text(svg(fn(key), key) + "\n", encoding="utf-8")


# ---------- showcase page ----------
_n = 0


def inline(fn, a="var(--mk)", b=None, cls="", **kw):
    global _n
    _n += 1
    inner = fn(a, b or a, f"u{_n}", **kw)
    return f'<svg viewBox="0 0 100 100" class="{cls}" aria-hidden="true">{inner}</svg>'


def lockup(fn, b=None, extra=None):
    kw = extra or {}
    return (f'<div class="lockup">{inline(fn, b=b, **kw)}'
            f'<span class="word">chat-crm<em>suite</em></span></div>')


def section(i, key, title, fn, desc, use):
    duo = None
    extra = None
    if key in ("dialogue", "monogram"):
        duo = "var(--mk2)"
    if key == "suite":
        duo, extra = "var(--mk2)", {"c": "var(--c-blue)", "d": "var(--c-amber)"}
    tiles = (
        f'<div class="tile paper">{inline(fn)}<span>papel</span></div>'
        f'<div class="tile night">{inline(fn)}<span>noche</span></div>'
        f'<div class="tile mint">{inline(fn)}<span>menta</span></div>'
    )
    if duo:
        tiles += (f'<div class="tile paper">{inline(fn, b=duo, **(extra or {}))}<span>color · papel</span></div>'
                  f'<div class="tile night">{inline(fn, b=duo, **(extra or {}))}<span>color · noche</span></div>')
    sizes = "".join(f'<div class="sz"><div style="width:{s}px;height:{s}px">{inline(fn)}</div><small>{s}</small></div>'
                    for s in (16, 24, 32, 48))
    avatar = f'<div class="avatar">{inline(fn)}</div><div class="avatar dark">{inline(fn)}</div>'
    return f"""
<section class="mark" id="{key}">
  <header><span class="num">0{i}</span><h2>{title}</h2><span class="use">{use}</span></header>
  <p class="desc">{desc}</p>
  <div class="tiles">{tiles}</div>
  <div class="row">
    <div class="cell lock-cell"><div class="lk paper">{lockup(fn, b=duo, extra=extra)}</div>
      <div class="lk night">{lockup(fn, b=duo, extra=extra)}</div></div>
    <div class="cell"><div class="label">Avatar GitHub</div><div class="avatars">{avatar}</div>
      <div class="label">Tamaños</div><div class="sizes">{sizes}</div></div>
  </div>
  <code>v5/{key}.svg</code>
</section>"""


def page():
    sections = "".join(section(i + 1, *m) for i, m in enumerate(MARKS))
    compare = "".join(
        f'<a class="cmp" href="#{k}">{inline(fn)}<span>{t}</span></a>' for k, t, fn, *_ in MARKS)
    org = "".join(
        f'<div class="gh"><div class="gh-av">{inline(fn)}</div><div><b>chat-crm-suite</b>'
        f'<small>{t}</small></div></div>' for k, t, fn, *_ in MARKS)
    swatches = "".join(
        f'<div class="sw"><i style="background:{h}"></i><b>{n}</b><small>{h} · {r}</small></div>'
        for n, h, r in [("Deep", DEEP, "marca en claro"), ("Mint", MINT, "primary del front"),
                        ("Vivid", VIVID, "marca en oscuro"), ("Blue", BLUE, "chart-2"),
                        ("Amber", AMBER, "chart-4"), ("Ink", INK, "texto"),
                        ("Night", NIGHT, "fondo oscuro"), ("Paper", PAPER, "fondo claro")])
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>chat-crm suite — draft 05</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{ --bg:{PAPER}; --fg:{INK}; --muted:rgba(23,23,23,.62); --hair:rgba(23,23,23,.12); --card:#fff;
  --mk:{DEEP}; --mk2:{MINT}; --c-blue:{BLUE}; --c-amber:{AMBER}; color-scheme:light; }}
body.night {{ --bg:{NIGHT}; --fg:#E2E8F0; --muted:rgba(226,232,240,.6); --hair:rgba(226,232,240,.14); --card:#1a1a1a;
  --mk:{VIVID}; --mk2:{MINT}; --c-blue:{BLUE_D}; --c-amber:{AMBER_D}; color-scheme:dark; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:Outfit,system-ui,sans-serif; background:var(--bg); color:var(--fg); -webkit-font-smoothing:antialiased;
  transition:background-color .3s, color .3s; }}
.page {{ max-width:1120px; margin:0 auto; padding:0 16px 96px; }}
.top {{ display:flex; justify-content:space-between; align-items:center; padding:24px 0; }}
.top b {{ font-weight:600; }}
button {{ font:inherit; font-size:13px; color:var(--fg); background:none; border:1px solid var(--hair); border-radius:99px;
  padding:7px 16px; cursor:pointer; }}
button:hover {{ border-color:var(--mk); color:var(--mk); }}
h1 {{ font-size:clamp(34px,6vw,60px); font-weight:700; letter-spacing:-.02em; margin:40px 0 12px; line-height:1.05; }}
h1 em {{ font-style:normal; font-weight:300; color:var(--mk); }}
.lede {{ font-size:17px; font-weight:300; color:var(--muted); max-width:60ch; line-height:1.6; }}
.compare {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:40px 0 72px; }}
.cmp {{ display:flex; flex-direction:column; align-items:center; gap:10px; padding:22px 10px 14px; border:1px solid var(--hair);
  border-radius:16px; color:var(--fg); text-decoration:none; background:var(--card); transition:border-color .2s, transform .2s; }}
.cmp:hover {{ border-color:var(--mk); transform:translateY(-2px); }}
.cmp svg {{ width:72px; height:72px; }} .cmp span {{ font-size:14px; font-weight:500; }}
.mark {{ border-top:1px solid var(--hair); padding:48px 0 56px; }}
.mark header {{ display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }}
.num {{ font-size:13px; color:var(--muted); font-variant-numeric:tabular-nums; }}
h2 {{ font-size:30px; font-weight:600; letter-spacing:-.01em; }}
.use {{ margin-left:auto; font-size:12px; color:var(--mk); border:1px solid var(--hair); border-radius:99px; padding:4px 12px; }}
.desc {{ margin:10px 0 24px; color:var(--muted); font-weight:300; max-width:68ch; line-height:1.6; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }}
.tile {{ position:relative; aspect-ratio:1; border-radius:18px; display:grid; place-items:center; border:1px solid var(--hair); }}
.tile svg {{ width:58%; height:58%; }}
.tile span {{ position:absolute; left:12px; bottom:10px; font-size:11px; opacity:.6; }}
.paper {{ background:{PAPER}; color:{INK}; --mk:{DEEP}; --mk2:{MINT}; --c-blue:{BLUE}; --c-amber:{AMBER}; }}
.night {{ background:{NIGHT}; color:#E2E8F0; --mk:{VIVID}; --mk2:{MINT}; --c-blue:{BLUE_D}; --c-amber:{AMBER_D}; }}
.mint {{ background:{MINT}; color:{DEEP}; --mk:{DEEP}; border-color:transparent; }}
.row {{ display:grid; grid-template-columns:minmax(0,1.5fr) minmax(0,1fr); gap:10px; margin-top:10px; }}
@media (max-width:760px) {{ .row {{ grid-template-columns:1fr; }} }}
.cell {{ border:1px solid var(--hair); border-radius:18px; padding:20px; background:var(--card); }}
.lock-cell {{ display:grid; gap:10px; padding:10px; }}
.lk {{ border-radius:12px; padding:26px 22px; display:flex; align-items:center; }}
.lockup {{ display:flex; align-items:center; gap:12px; }}
.lockup svg {{ width:54px; height:54px; flex:none; }}
.word {{ font-size:clamp(26px,4.4vw,38px); font-weight:700; letter-spacing:-.025em; color:currentColor; }}
.word em {{ font-style:normal; font-weight:300; color:var(--mk); margin-left:.22em; letter-spacing:0; }}
.label {{ font-size:12px; color:var(--muted); margin-bottom:10px; }}
.avatars {{ display:flex; gap:12px; margin-bottom:22px; }}
.avatar {{ width:76px; height:76px; border-radius:50%; background:{MINT}; --mk:{DEEP}; display:grid; place-items:center; }}
.avatar.dark {{ background:{NIGHT}; --mk:{VIVID}; --mk2:{MINT}; }}
.avatar svg {{ width:64%; height:64%; }}
.sizes {{ display:flex; gap:20px; align-items:flex-end; }}
.sz {{ display:flex; flex-direction:column; align-items:center; gap:6px; }}
.sz svg {{ width:100%; height:100%; display:block; }} .sz small {{ font-size:11px; color:var(--muted); }}
code {{ display:inline-block; margin-top:14px; font-size:12px; color:var(--muted); }}
h3 {{ font-size:22px; font-weight:600; margin:0 0 6px; }}
.ctx {{ border-top:1px solid var(--hair); padding:48px 0; }}
.ghs {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:10px; margin-top:20px; }}
.gh {{ display:flex; gap:14px; align-items:center; border:1px solid var(--hair); border-radius:12px; padding:14px; background:var(--card); }}
.gh-av {{ width:48px; height:48px; border-radius:10px; background:{MINT}; --mk:{DEEP}; display:grid; place-items:center; flex:none; }}
body.night .gh-av {{ background:#0d2a1c; --mk:{VIVID}; }}
.gh-av svg {{ width:70%; height:70%; }} .gh b {{ display:block; font-weight:600; }} .gh small {{ color:var(--muted); font-size:12px; }}
.sws {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:10px; margin-top:20px; }}
.sw i {{ display:block; height:64px; border-radius:12px; border:1px solid var(--hair); margin-bottom:8px; }}
.sw b {{ font-weight:600; font-size:14px; display:block; }} .sw small {{ font-size:11px; color:var(--muted); }}
.foot {{ color:var(--muted); font-weight:300; border-top:1px solid var(--hair); padding-top:28px; line-height:1.6; }}
</style>
</head>
<body>
<div class="page">
  <div class="top"><b>chat-crm-suite · brand</b><button id="t">Modo noche</button></div>
  <h1>chat-crm <em>suite</em><br>draft 05</h1>
  <p class="lede">Seis direcciones nuevas. Todas con la misma paleta del frontend (el verde menta de los
  botones primary y su verde profundo), el mismo peso y la misma regla: recortar formas en vez de dibujar
  líneas. Cada una incluye lockup con el nombre, avatar de GitHub y tamaños de favicon.</p>
  <div class="compare">{compare}</div>
  {sections}
  <section class="ctx"><h3>Así se vería en GitHub</h3>
    <p class="desc">Avatar de la organización junto al nombre, al tamaño real de la lista de repos.</p>
    <div class="ghs">{org}</div></section>
  <section class="ctx"><h3>Paleta</h3>
    <p class="desc">Tomada 1:1 de <code style="margin:0">chat-crm-app/src/styles/theme.css</code>. Azul y ámbar
    (colores de gráficas) solo aparecen en la variante color de «Suite».</p>
    <div class="sws">{swatches}</div></section>
  <p class="foot">Elige una o dos (por número o nombre) y la refinamos: grosor, radios, cola, espaciado del
  lockup. Después: wordmark en curvas, PNG 1024 px, favicon.ico y avatar 500×500 para GitHub.</p>
</div>
<script>
const b=document.getElementById('t');
b.onclick=()=>{{const n=document.body.classList.toggle('night');b.textContent=n?'Modo día':'Modo noche';}};
</script>
</body>
</html>
"""


if __name__ == "__main__":
    write_files()
    (ROOT / "showcase-v5.html").write_text(page(), encoding="utf-8")
    print("ok:", sorted(p.name for p in OUT.iterdir()))
