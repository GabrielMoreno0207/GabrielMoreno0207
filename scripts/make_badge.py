"""Gera o badge em SVG. Edite o bloco CONFIG e rode: python3 make_badge.py [foto.jpg]"""
import sys, base64, io, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np

CONFIG = {
    "nome": "GABRIEL MORENO",
    "titulo": "DEVELOPER",
    "iniciais": "GM",
    "cargo": "Data Comm. Analyst &amp; Dev",
    "stack": ["Data", "Analytics", "Dev"],
    "local": "Osvaldo Cruz, SP",
    "saida": "badge.svg",
}
PHOTO = sys.argv[1] if len(sys.argv) > 1 else None

W, H = 340, 650
out = []
a = out.append

# ---------- fonte do meio-tom (halftone) ----------
HX0, HY0, HX1, HY1, STEP = 38, 82, 302, 288, 3.2
cols = int((HX1 - HX0) / STEP)
rows = int((HY1 - HY0) / STEP)

def placeholder_bust(w, h):
    s = 8
    W_, H_ = w * s, h * s
    im = Image.new("L", (W_, H_), 0)
    d = ImageDraw.Draw(im)
    cx = W_ / 2
    # ombros / tronco
    d.ellipse([cx - 0.30 * W_, 0.58 * H_, cx + 0.30 * W_, 1.30 * H_], fill=150)
    # pescoço
    d.rectangle([cx - 0.05 * W_, 0.48 * H_, cx + 0.05 * W_, 0.64 * H_], fill=170)
    # cabeça
    d.ellipse([cx - 0.115 * W_, 0.10 * H_, cx + 0.115 * W_, 0.56 * H_], fill=235)
    # cabelo
    d.chord([cx - 0.125 * W_, 0.06 * H_, cx + 0.125 * W_, 0.40 * H_], 180, 360, fill=110)
    d.ellipse([cx - 0.125 * W_, 0.06 * H_, cx + 0.125 * W_, 0.24 * H_], fill=110)
    # olhos e sorriso
    for ex in (-0.045, 0.045):
        d.ellipse([cx + ex * W_ - 0.014 * W_, 0.31 * H_, cx + ex * W_ + 0.014 * W_, 0.35 * H_], fill=60)
    d.arc([cx - 0.04 * W_, 0.36 * H_, cx + 0.04 * W_, 0.45 * H_], 20, 160, fill=80, width=int(0.012 * W_))
    # fones de ouvido
    d.arc([cx - 0.14 * W_, 0.05 * H_, cx + 0.14 * W_, 0.50 * H_], 190, 350, fill=255, width=int(0.022 * W_))
    for ex in (-0.135, 0.135):
        d.rounded_rectangle([cx + ex * W_ - 0.03 * W_, 0.24 * H_, cx + ex * W_ + 0.03 * W_, 0.38 * H_], radius=int(0.02 * W_), fill=255)
    # notebook na frente
    d.polygon([(cx - 0.30 * W_, 0.70 * H_), (cx + 0.30 * W_, 0.70 * H_), (cx + 0.26 * W_, 1.0 * H_), (cx - 0.26 * W_, 1.0 * H_)], fill=255)
    d.rectangle([cx - 0.36 * W_, 0.97 * H_, cx + 0.36 * W_, 1.0 * H_], fill=255)
    # "</>" na tampa
    lw = int(0.018 * W_)
    d.line([(cx - 0.07 * W_, 0.79 * H_), (cx - 0.11 * W_, 0.85 * H_), (cx - 0.07 * W_, 0.91 * H_)], fill=90, width=lw)
    d.line([(cx + 0.07 * W_, 0.79 * H_), (cx + 0.11 * W_, 0.85 * H_), (cx + 0.07 * W_, 0.91 * H_)], fill=90, width=lw)
    d.line([(cx + 0.02 * W_, 0.78 * H_), (cx - 0.02 * W_, 0.92 * H_)], fill=90, width=lw)
    im = im.filter(ImageFilter.GaussianBlur(0.9 * s))
    return im.resize((w, h), Image.LANCZOS)

def photo_source(path, w, h):
    im = Image.open(path).convert("L")
    S = 6
    tw, th = w * S, h * S
    side = th
    im = ImageOps.fit(im, (side, side), centering=(0.5, 0.45))
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageOps.equalize(im).point(lambda v: v * 0.55) if False else im
    arr = np.asarray(im, dtype=float) / 255.0
    arr = np.clip((arr - 0.04) / 0.80, 0, 1) ** 0.8          # realça o rosto, apaga o fundo
    im = Image.fromarray((arr * 255).astype("uint8"))
    canvas = Image.new("L", (tw, th), 0)
    canvas.paste(im, ((tw - side) // 2, 0))
    m = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(m).ellipse([(tw - side) / 2 - side * .05, -side * .2, (tw + side) / 2 + side * .05, th * 1.25], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(side * .05))
    canvas = Image.composite(canvas, Image.new("L", canvas.size, 0), m)
    return canvas.resize((w, h), Image.LANCZOS)

src = photo_source(PHOTO, cols, rows) if PHOTO else placeholder_bust(cols, rows)
lum = np.asarray(src, dtype=float) / 255.0

# ---------- defs ----------
a(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="\'Segoe UI\', Helvetica, Arial, sans-serif">')
a("""<defs>
  <linearGradient id="pcb" x1="0" y1="0" x2="0.6" y2="1">
    <stop offset="0" stop-color="#8455de"/><stop offset=".55" stop-color="#6c3fc8"/><stop offset="1" stop-color="#5730ad"/>
  </linearGradient>
  <radialGradient id="pcbGlow" cx=".5" cy=".25" r=".6">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".10"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#fbf0d4"/><stop offset=".5" stop-color="#e6cf9c"/><stop offset="1" stop-color="#bb9c62"/>
  </linearGradient>
  <radialGradient id="goldBtn" cx=".38" cy=".32" r=".75">
    <stop offset="0" stop-color="#fff8e4"/><stop offset=".45" stop-color="#ead5a5"/><stop offset="1" stop-color="#b8975c"/>
  </radialGradient>
  <linearGradient id="acrylic" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".30"/><stop offset=".35" stop-color="#ffffff" stop-opacity=".10"/>
    <stop offset=".7" stop-color="#ffffff" stop-opacity=".06"/><stop offset="1" stop-color="#ffffff" stop-opacity=".22"/>
  </linearGradient>
  <linearGradient id="glare" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".35"/><stop offset=".4" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="screw" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#fafafa"/><stop offset=".6" stop-color="#b9bcc4"/><stop offset="1" stop-color="#7c808a"/>
  </radialGradient>
  <radialGradient id="cap" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#6b6f7a"/><stop offset=".6" stop-color="#3a3d45"/><stop offset="1" stop-color="#1e2026"/>
  </radialGradient>
  <filter id="shadow" x="-20%" y="-10%" width="140%" height="130%">
    <feGaussianBlur stdDeviation="9"/>
  </filter>
  <filter id="soft2" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2"/></filter>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>
  <filter id="lift" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="1.4" stdDeviation="1.1" flood-color="#2a1157" flood-opacity=".55"/>
  </filter>
  <clipPath id="disp"><rect x="52" y="392" width="210" height="190" rx="2"/></clipPath>
  <clipPath id="avatar"><circle cx="157" cy="452" r="40"/></clipPath>
  <style>
    .blink{animation:bl 1.1s steps(1) infinite}
    @keyframes bl{50%{opacity:0}}
    .f1{animation:fl 7s ease-in-out infinite alternate}
    .f2{animation:fl 9s ease-in-out infinite alternate-reverse}
    @keyframes fl{from{transform:translate(0,0)}to{transform:translate(14px,-10px)}}
    .led{animation:pu 2.4s ease-in-out infinite}
    @keyframes pu{50%{opacity:.25}}
  </style>
</defs>""")

# sombra no chão
a(f'<ellipse cx="{W/2}" cy="{H-10}" rx="140" ry="9" fill="#000" opacity=".35" filter="url(#shadow)"/>')

# ---------- placa ----------
a('<rect x="20" y="8" width="300" height="626" rx="16" fill="url(#pcb)"/>')
a('<rect x="20" y="8" width="300" height="626" rx="16" fill="url(#pcbGlow)"/>')
a('<rect x="21" y="9" width="298" height="624" rx="15" fill="none" stroke="#a983ff" stroke-opacity=".35"/>')
# fendas do cordão
for x in (48, 252):
    a(f'<rect x="{x}" y="20" width="40" height="8" rx="4" fill="#2b1259"/>')
    a(f'<rect x="{x}" y="20" width="40" height="8" rx="4" fill="none" stroke="#e6cf9c" stroke-width="1.2"/>')
# fileiras de pontinhos nos cantos
for i in range(9):
    a(f'<circle cx="{38+i*4.2:.1f}" cy="40" r="1" fill="#e6cf9c" opacity=".8"/>')
    a(f'<circle cx="{302-i*4.2:.1f}" cy="40" r="1" fill="#e6cf9c" opacity=".8"/>')

# trilhas de circuito (serigrafia)
a('<g fill="none" stroke="#9c74f0" stroke-opacity=".45" stroke-width="1.1" stroke-linecap="round">')
for d in ["M30 300 H55 L68 313 V352", "M30 312 H48 L58 322 V352", "M310 296 H292 L284 304 V318",
          "M310 342 H285 L272 330 H262", "M200 352 V340 L212 328 H232", "M120 352 V344 L130 334",
          "M150 300 L162 292 H196 L204 300"]:
    a(f'<path d="{d}"/>')
a('</g>')
for (x, y) in [(68, 352), (58, 352), (284, 318), (262, 330), (232, 328), (130, 334), (204, 300), (30, 300)]:
    a(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#5730ad" stroke="#e6cf9c" stroke-width="1"/>')

# ---------- cabeçalho: monograma + nome ----------
_tw = len(CONFIG["titulo"]) * 12.5
_x0 = W/2 - (_tw + 30)/2
a(f'<g filter="url(#lift)"><circle cx="{_x0+11}" cy="62" r="11" fill="url(#gold)"/>'
  f'<text x="{_x0+11}" y="66" text-anchor="middle" font-size="10" font-weight="800" fill="#5730ad">{CONFIG["iniciais"]}</text></g>')
a(f'<text x="{_x0+30}" y="69" font-size="18" font-weight="800" fill="#ffffff" letter-spacing=".3" textLength="{_tw:.0f}" lengthAdjust="spacingAndGlyphs">{CONFIG["titulo"]}</text>')

# ---------- meio-tom ----------
a('<g fill="#efdcb2">')
for r in range(rows):
    for c in range(cols):
        v = lum[r, c]
        rad = 0.3 + 1.32 * (v ** 1.0)  # pontos de fundo pequenos, figura com pontos grandes
        x = HX0 + c * STEP + STEP / 2
        y = HY0 + r * STEP + STEP / 2
        op = 0.35 + 0.65 * min(1, v * 2.2)
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.2f}" opacity="{op:.2f}"/>')
a('</g>')

# ---------- controles ----------
# A / B
a('<g filter="url(#lift)">')
a('<circle cx="88" cy="305" r="18" fill="url(#goldBtn)"/>')
a('<circle cx="88" cy="305" r="18" fill="none" stroke="#a88a50" stroke-width="1"/>')
a('<circle cx="123" cy="331" r="10" fill="url(#goldBtn)"/>')
a('<circle cx="123" cy="331" r="10" fill="none" stroke="#a88a50" stroke-width="1"/>')
# select / start
for cx in (150, 176):
    a(f'<rect x="{cx-11}" y="333" width="22" height="8" rx="4" fill="url(#gold)" transform="rotate(-28 {cx} 337)"/>')
a('</g>')
a('<text x="88" y="331" text-anchor="middle" font-size="6" fill="#e6cf9c" opacity=".7" font-weight="700">A</text>')
a('<text x="139" y="335" text-anchor="middle" font-size="6" fill="#e6cf9c" opacity=".7" font-weight="700">B</text>')
# direcional
a('<g filter="url(#lift)">')
a('<path d="M234 284 h14 a2 2 0 0 1 2 2 v13 h13 a2 2 0 0 1 2 2 v14 a2 2 0 0 1 -2 2 h-13 v13 a2 2 0 0 1 -2 2 h-14 a2 2 0 0 1 -2 -2 v-13 h-13 a2 2 0 0 1 -2 -2 v-14 a2 2 0 0 1 2 -2 h13 v-13 a2 2 0 0 1 2 -2z" fill="url(#gold)" stroke="#a88a50" stroke-width="1"/>')
a('</g>')
a('<g fill="#a88a50" opacity=".8">'
  '<path d="M241 289 l4 5 h-8z"/><path d="M241 333 l4 -5 h-8z"/>'
  '<path d="M219 308 l5 -4 v8z"/><path d="M263 308 l-5 -4 v8z"/>'
  '<circle cx="241" cy="308" r="3.2" fill="none" stroke="#a88a50" stroke-width="1"/></g>')


# ---------- componentes eletrônicos na placa ----------
def smd_r(x, y, vert=False, body="#1c1c1f"):   # resistor 0603
    w, h = (4, 8) if vert else (8, 4)
    a(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx=".6" fill="{body}"/>')
    if vert:
        a(f'<rect x="{x}" y="{y}" width="4" height="2" fill="#d9dce2"/><rect x="{x}" y="{y+6}" width="4" height="2" fill="#d9dce2"/>')
    else:
        a(f'<rect x="{x}" y="{y}" width="2" height="4" fill="#d9dce2"/><rect x="{x+6}" y="{y}" width="2" height="4" fill="#d9dce2"/>')

def smd_c(x, y, vert=False):                   # capacitor cerâmico
    smd_r(x, y, vert, body="#b98d5a")

# microcontrolador (QFN) com pinos
mx, my, ms = 186, 346, 15
for i in range(5):
    o = 2.5 + i * 2.5
    a(f'<rect x="{mx-2}" y="{my+o-.5}" width="2" height="1" fill="#d9dce2"/><rect x="{mx+ms}" y="{my+o-.5}" width="2" height="1" fill="#d9dce2"/>')
    a(f'<rect x="{mx+o-.5}" y="{my-2}" width="1" height="2" fill="#d9dce2"/><rect x="{mx+o-.5}" y="{my+ms}" width="1" height="2" fill="#d9dce2"/>')
a(f'<rect x="{mx}" y="{my}" width="{ms}" height="{ms}" rx="1.2" fill="#18181b"/>')
a(f'<circle cx="{mx+2.6}" cy="{my+2.6}" r=".9" fill="#55555e"/>')
a(f'<text x="{mx+ms/2}" y="{my+9.5}" text-anchor="middle" font-size="3.2" fill="#8a8a94" font-family="Consolas, monospace">RP2040</text>')
# cristal
a('<rect x="214" y="347" width="13" height="6" rx="3" fill="#cfd3da" stroke="#8d929c" stroke-width=".6"/>')
a('<rect x="216" y="349" width="9" height="2" rx="1" fill="#eef0f3"/>')
# flash (SOIC-8)
for i in range(4):
    a(f'<rect x="{150+i*3.2}" y="343" width="1.4" height="2.2" fill="#d9dce2"/><rect x="{150+i*3.2}" y="354.8" width="1.4" height="2.2" fill="#d9dce2"/>')
a('<rect x="148.5" y="345" width="13" height="10" rx=".8" fill="#18181b"/>')
# resistores / capacitores espalhados
for (x, y, v) in [(134, 346, True), (168, 344, False), (168, 352, False), (232, 343, True), (240, 343, True)]:
    smd_r(x, y, v)
for (x, y, v) in [(126, 346, True), (204, 336, False), (248, 343, True), (256, 343, True)]:
    smd_c(x, y, v)
# LED de status
a('<rect x="268" y="345" width="7" height="5" rx="1" fill="#e9eaee"/>')
a('<rect class="led" x="269.5" y="346" width="4" height="3" rx=".8" fill="#5ef08c"/>')
a('<circle class="led" cx="271.5" cy="347.5" r="5" fill="#5ef08c" opacity=".35" filter="url(#soft2)"/>')
a('<text x="271.5" y="358" text-anchor="middle" font-size="3.5" fill="#e6cf9c" opacity=".8">PWR</text>')
# conector de bateria JST (branco)
a('<rect x="76" y="342" width="16" height="10" rx="1" fill="#f1efe8" stroke="#c9c5b8" stroke-width=".6"/>')
a('<rect x="79" y="344.5" width="4" height="5" fill="#d7d2c4"/><rect x="85" y="344.5" width="4" height="5" fill="#d7d2c4"/>')
a('<text x="84" y="358" text-anchor="middle" font-size="3.5" fill="#e6cf9c" opacity=".8">BAT</text>')
# componentes visíveis por baixo do acrílico (faixa à esquerda da tela)
for i, yy in enumerate(range(404, 572, 22)):
    (smd_c if i % 2 else smd_r)(32, yy, True)
# serigrafia (legenda) da placa
a('<text x="100" y="358" font-size="3.6" fill="#e6cf9c" opacity=".75" font-family="Consolas, monospace">U2  C7  R3</text>')

# ---------- case de acrílico ----------
CX0, CY0, CX1, CY1 = 26, 364, 314, 628
a(f'<rect x="{CX0}" y="{CY0}" width="{CX1-CX0}" height="{CY1-CY0}" rx="14" fill="url(#acrylic)"/>')
a(f'<rect x="{CX0}" y="{CY0}" width="{CX1-CX0}" height="{CY1-CY0}" rx="14" fill="none" stroke="#ffffff" stroke-opacity=".7" stroke-width="2"/>')
a(f'<rect x="{CX0+5}" y="{CY0+5}" width="{CX1-CX0-10}" height="{CY1-CY0-10}" rx="10" fill="none" stroke="#ffffff" stroke-opacity=".25"/>')
# espaçadores (latão) + parafusos
for (x, y) in [(38, 376), (302, 376), (38, 616), (302, 616)]:
    hexp = " ".join(f"{x+7.2*math.cos(math.radians(60*k+30)):.1f},{y+7.2*math.sin(math.radians(60*k+30)):.1f}" for k in range(6))
    a(f'<polygon points="{hexp}" fill="#c8a24a" stroke="#8e6f26" stroke-width=".7" opacity=".9"/>')
    a(f'<circle cx="{x}" cy="{y}" r="5" fill="url(#screw)" stroke="#5d606a" stroke-width=".6"/>'
      f'<path d="M{x-2.6} {y} h5.2 M{x} {y-2.6} v5.2" stroke="#5d606a" stroke-width="1.1"/>')

# cabo flat (FPC) âmbar saindo da tela até o conector
a('<path d="M136 588 h42 v8 q0 4 -4 4 h-34 q-4 0 -4 -4z" fill="#d9892b" opacity=".92"/>')
for i in range(9):
    a(f'<line x1="{140+i*4}" y1="589" x2="{140+i*4}" y2="599" stroke="#f6c37a" stroke-width=".7" opacity=".8"/>')
a('<rect x="132" y="599" width="50" height="8" rx="1" fill="#1b1b1f"/>')
a('<rect x="134" y="600.5" width="46" height="2" fill="#3b3b44"/>')
for i in range(12):
    a(f'<rect x="{135+i*3.8}" y="606.5" width="1.4" height="2" fill="#d9dce2"/>')
# moldura metálica do módulo TFT
a('<rect x="41" y="381" width="232" height="212" rx="3" fill="#b9bdc6"/>')
a('<rect x="41" y="381" width="232" height="212" rx="3" fill="none" stroke="#7f848e" stroke-width=".8"/>')
for (x, y) in [(45, 385), (265, 385), (45, 585), (265, 585)]:
    a(f'<rect x="{x}" y="{y}" width="4" height="4" fill="#9a9fa9"/>')
a('<rect x="44" y="384" width="226" height="206" rx="5" fill="#0c0c10"/>')
a('<rect x="44" y="384" width="226" height="206" rx="5" fill="none" stroke="#33343d" stroke-width="1.5"/>')

# ---------- display: cenas animadas ----------
T = 25.0                     # duração do ciclo completo (s)
SCENES = 5
SD = T / SCENES              # duração de cada cena
css = []
_kid = [0]

def appear(scene, delay=0.0, fade=0.25):
    """classe CSS que mostra o elemento da cena `scene` a partir de `delay` s até o fim da cena"""
    _kid[0] += 1
    n = f"k{_kid[0]}"
    t0 = scene * SD + delay
    t1 = (scene + 1) * SD - 0.05
    p = lambda t: max(0, min(100, t / T * 100))
    a0, a1, b0, b1 = p(t0), p(t0 + fade), p(t1 - fade), p(t1)
    frames = [f"0%{{opacity:0}}"]
    if a0 > 0: frames.append(f"{a0:.3f}%{{opacity:0}}")
    frames += [f"{a1:.3f}%{{opacity:1}}", f"{b0:.3f}%{{opacity:1}}", f"{b1:.3f}%{{opacity:0}}", "100%{opacity:0}"]
    css.append(f"@keyframes {n}{{{''.join(frames)}}}.{n}{{opacity:0;animation:{n} {T}s linear infinite}}")
    return n

MONO = 'font-family="Consolas, \'Courier New\', monospace"'
G = "#7ee787"   # verde do prompt
TX, TY = 60, 424

a('<g clip-path="url(#disp)">')
a('<rect x="52" y="392" width="210" height="190" fill="#140b2b"/>')

# ===== CENA 0: foto + nome (fundo colorido) =====
c0 = appear(0, 0, 0.4)
a(f'<g class="{c0}">')
a('<rect x="52" y="392" width="210" height="190" fill="#fdf3e7"/>')
a('<g filter="url(#soft)">'
  '<circle class="f1" cx="70" cy="410" r="55" fill="#ff8fc7"/>'
  '<circle class="f2" cx="250" cy="420" r="60" fill="#ffd56b"/>'
  '<circle class="f1" cx="250" cy="560" r="60" fill="#7fd6ff"/>'
  '<circle class="f2" cx="60" cy="570" r="55" fill="#b69bff"/>'
  '<circle cx="157" cy="465" r="50" fill="#ffffff"/></g>')
a('<circle cx="157" cy="460" r="46" fill="#ffffff"/>')
a('<circle cx="157" cy="460" r="46" fill="none" stroke="#6c3fc8" stroke-width="2.5"/>')
if PHOTO:
    im = ImageOps.fit(Image.open(PHOTO).convert("RGB"), (260, 260), centering=(0.5, 0.42))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=82)
    b64 = base64.b64encode(buf.getvalue()).decode()
    a('<clipPath id="av0"><circle cx="157" cy="460" r="42"/></clipPath>')
    a(f'<image x="115" y="418" width="84" height="84" clip-path="url(#av0)" href="data:image/jpeg;base64,{b64}" xlink:href="data:image/jpeg;base64,{b64}"/>')
else:
    a('<circle cx="157" cy="460" r="42" fill="#6c3fc8"/>')
    a(f'<text x="157" y="473" text-anchor="middle" font-size="36" font-weight="800" fill="#fff">{CONFIG["iniciais"]}</text>')
a(f'<text x="157" y="527" text-anchor="middle" font-size="16" font-weight="800" fill="#24124a" class="{appear(0, .5)}">{CONFIG["nome"].title()}</text>')
a(f'<text x="157" y="543" text-anchor="middle" font-size="9.5" fill="#4b3a6e" class="{appear(0, .9)}">Data Communication Analyst</text>')
a(f'<g class="{appear(0, 1.2)}"><rect x="117" y="551" width="80" height="16" rx="8" fill="#6c3fc8"/>'
  '<text x="157" y="562" text-anchor="middle" font-size="9" font-weight="700" fill="#fff">&amp; Developer</text></g>')
a('</g>')

def prompt(scene, y, cmd, d):
    a(f'<text x="{TX}" y="{y}" font-size="10" {MONO} class="{appear(scene, d)}"><tspan fill="{G}">gabriel</tspan><tspan fill="#8b7fb0"> ~ $</tspan> <tspan fill="#fff">{cmd}</tspan></text>')

def line(scene, y, txt, d, fill="#d9ccff", size=10, weight="400"):
    a(f'<text x="{TX}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" {MONO} class="{appear(scene, d)}">{txt}</text>')

def cursor(scene, x, y, d):
    a(f'<g class="{appear(scene, d)}"><rect class="blink" x="{x}" y="{y-8}" width="6" height="10" fill="{G}"/></g>')

# ===== CENA 1: whoami =====
c1 = appear(1, 0)
a(f'<g class="{c1}"><rect x="52" y="392" width="210" height="190" fill="#140b2b"/></g>')
prompt(1, TY, "whoami", .2)
line(1, TY + 20, "Gabriel Moreno", .8, "#ffffff", 12, "700")
line(1, TY + 38, "Data Communication", 1.2)
line(1, TY + 52, "Analyst &amp; Developer", 1.5)
prompt(1, TY + 78, "cat local.txt", 2.1)
a(f'<g class="{appear(1, 2.7)}">'
  f'<path d="M{TX+3.4} {TY+90} a3.4 3.4 0 0 1 6.8 0 c0 2.6 -3.4 6 -3.4 6 s-3.4 -3.4 -3.4 -6z" transform="translate(-3.4 0)" fill="#ff7ab6"/>'
  f'<text x="{TX+9}" y="{TY+97}" font-size="10" fill="#d9ccff" {MONO}>Osvaldo Cruz, SP · BR</text></g>')
prompt(1, TY + 122, "", 3.2)
cursor(1, TX + 66, TY + 122, 3.2)

# ===== CENA 2: contribuições =====
c2 = appear(2, 0)
a(f'<g class="{c2}"><rect x="52" y="392" width="210" height="190" fill="#140b2b"/></g>')
prompt(2, TY, "./contributions.sh", .2)
import random
random.seed(7)
greens = ["#1f2a44", "#0e4429", "#006d32", "#26a641", "#39d353"]
gx0, gy0, cell, gap = TX, TY + 12, 9, 2.2
COLS = 17
for c in range(COLS):
    cls = appear(2, .7 + c * .09, .15)
    a(f'<g class="{cls}">')
    for r in range(7):
        lvl = random.choices(range(5), weights=[1, 3, 3, 3, 2])[0]
        a(f'<rect x="{gx0 + c*(cell+gap):.1f}" y="{gy0 + r*(cell+gap):.1f}" width="{cell}" height="{cell}" rx="2" fill="{greens[lvl]}"/>')
    a('</g>')
line(2, TY + 104, "&#9650; constância nos commits", 2.6, "#39d353")
line(2, TY + 120, "&#9733; sempre aprendendo", 3.0, "#ffd56b")
line(2, TY + 136, "&#8635; atualizado todo dia", 3.4, "#8bd5ff", 9)

# ===== CENA 3: foco + status =====
c3 = appear(3, 0)
a(f'<g class="{c3}"><rect x="52" y="392" width="210" height="190" fill="#140b2b"/></g>')
prompt(3, TY, "ls ~/foco", .2)
_chips = [[("comunicação de dados", "#a371f7"), ("dev", "#79c0ff")],
          [("automação", "#7ee787"), ("aprendizado contínuo", "#ff7ab6")]]
for ri, row in enumerate(_chips):
    cx = TX
    for k, (lab, col) in enumerate(row):
        w = len(lab) * 5.4 + 12
        a(f'<g class="{appear(3, .7 + ri*.35 + k*.18)}"><rect x="{cx:.1f}" y="{TY + 9 + ri*20}" width="{w:.1f}" height="15" rx="7.5" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-opacity=".7"/>'
          f'<text x="{cx + w/2:.1f}" y="{TY + 19.5 + ri*20}" text-anchor="middle" font-size="9" fill="{col}" {MONO}>{lab}</text></g>')
        cx += w + 6
prompt(3, TY + 68, "./status.sh", 1.8)
line(3, TY + 86, '<tspan fill="#7ee787">●</tspan> perfil atualizado todo dia', 2.3, "#d9ccff", 9.5)
line(3, TY + 102, '<tspan fill="#e3b341">●</tspan> stats e streak no README', 2.6, "#d9ccff", 9.5)
line(3, TY + 118, '<tspan fill="#ff7ab6">●</tspan> aberto a novos projetos', 2.9, "#d9ccff", 9.5)
prompt(3, TY + 140, "", 3.4)
cursor(3, TX + 66, TY + 140, 3.4)

# ===== CENA 4: links =====
c3 = appear(4, 0)
a(f'<g class="{c3}"><rect x="52" y="392" width="210" height="190" fill="#140b2b"/></g>')
prompt(4, TY, "./links.sh", .2)
a(f'<g class="{appear(4, .8)}"><rect x="{TX}" y="{TY+12}" width="190" height="24" rx="5" fill="#0A66C2"/>'
  f'<rect x="{TX+6}" y="{TY+17}" width="14" height="14" rx="2.5" fill="#fff"/>'
  f'<text x="{TX+13}" y="{TY+28}" text-anchor="middle" font-size="9.5" font-weight="800" fill="#0A66C2" font-family="Arial, sans-serif">in</text>'
  f'<text x="{TX+26}" y="{TY+28}" font-size="10" font-weight="700" fill="#fff" {MONO}>gabriel-morenodev</text></g>')
a(f'<g class="{appear(4, 1.3)}"><rect x="{TX}" y="{TY+42}" width="190" height="24" rx="5" fill="#0078D4"/>'
  f'<rect x="{TX+6}" y="{TY+49}" width="14" height="10" rx="1.5" fill="#fff"/>'
  f'<path d="M{TX+6} {TY+49} l7 5.5 l7 -5.5" fill="none" stroke="#0078D4" stroke-width="1.3"/>'
  f'<text x="{TX+26}" y="{TY+57.5}" font-size="8.4" font-weight="700" fill="#fff" {MONO}>gabrielmfrontend@hotmail.com</text></g>')
prompt(4, TY + 88, "echo \"bora conversar?\"", 2.0)
line(4, TY + 106, "bora conversar? :)", 2.6, "#ff9bd2", 10, "700")
prompt(4, TY + 130, "", 3.2)
cursor(4, TX + 66, TY + 130, 3.2)

# barra de status (fixa, por cima de tudo)
a('<rect x="52" y="392" width="210" height="15" fill="#1d1235" opacity=".92"/>')
a('<text x="58" y="403" font-size="8" fill="#ffffff" font-family="Consolas, monospace">gabriel@github</text>')
a('<circle class="led" cx="214" cy="399.5" r="2.4" fill="#5ef08c"/>')
a('<rect x="223" y="396" width="16" height="7" rx="1.5" fill="none" stroke="#fff" stroke-width=".9"/>'
  '<rect x="225" y="398" width="11" height="3" fill="#5ef08c"/><rect x="239.5" y="398" width="1.6" height="3" fill="#fff"/>')
a('<text x="256" y="403" text-anchor="end" font-size="8" fill="#fff">&#9829;</text>')
# indicador de cena (bolinhas)
for i in range(SCENES):
    a(f'<circle cx="{137 + i*10}" cy="576" r="2.2" fill="#ffffff" opacity=".3"/>')
    a(f'<circle cx="{137 + i*10}" cy="576" r="2.2" fill="#ffffff" class="{appear(i, 0, .2)}"/>')
a('</g>')
a('<style>' + ''.join(css) + '</style>')

# reflexo no vidro
a('<path d="M52 392 h120 l-80 190 h-40z" fill="url(#glare)" opacity=".55"/>')

# botões laterais
icons = ["▲", "▼", "●", "■"]
def tact(x, y, ic, fs):
    # pernas metálicas
    for dx in (-8.5, 6.5):
        for dy in (-6, 4.5):
            a(f'<rect x="{x+dx}" y="{y+dy}" width="2" height="1.5" fill="#d9dce2"/>')
    # corpo + moldura metálica
    a(f'<rect x="{x-7.5}" y="{y-7.5}" width="15" height="15" rx="1.2" fill="#202126"/>')
    a(f'<rect x="{x-7.5}" y="{y-7.5}" width="15" height="15" rx="1.2" fill="none" stroke="#a9adb6" stroke-width="1"/>')
    for (cx, cy) in [(-5.6, -5.6), (5.6, -5.6), (-5.6, 5.6), (5.6, 5.6)]:
        a(f'<circle cx="{x+cx}" cy="{y+cy}" r=".9" fill="#5b5e66"/>')
    # botão
    a(f'<circle cx="{x}" cy="{y}" r="5.4" fill="url(#cap)"/><circle cx="{x}" cy="{y}" r="5.4" fill="none" stroke="#000" stroke-opacity=".6"/>')
    a(f'<text x="{x}" y="{y+fs*.36}" text-anchor="middle" font-size="{fs}" fill="#c9ccd6">{ic}</text>')

for i, y in enumerate((406, 442, 478, 514)):
    tact(291, y, icons[i], 5)
# botões inferiores
for x, ic in [(76, "✕"), (108, "◁"), (206, "▷"), (238, "○")]:
    tact(x, 608, ic, 6)
a('<text x="157" y="620" text-anchor="middle" font-size="4" fill="#ffffff" opacity=".7" font-family="Consolas, monospace">TFT 2.0in · FPC</text>')
# reflexo no acrílico
a(f'<path d="M{CX0+4} {CY0+40} q0 -32 30 -34 h60" fill="none" stroke="#ffffff" stroke-opacity=".6" stroke-width="2" stroke-linecap="round"/>')

a('</svg>')

# ---------- moldura (vitrine) em volta do badge ----------
FW, FH = 560, 760
DX, DY = (FW - W) / 2, (FH - H) / 2 - 4
inner = "\n".join(out[1:-1])
fr = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{FW}" height="{FH}" viewBox="0 0 {FW} {FH}" font-family="\'Segoe UI\', Helvetica, Arial, sans-serif">',
      '''<defs>
  <pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="8" cy="8" r=".9" fill="#30363d"/></pattern>
  <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#8455de" stop-opacity=".55"/><stop offset=".6" stop-color="#8455de" stop-opacity=".12"/><stop offset="1" stop-color="#8455de" stop-opacity="0"/></radialGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#a371f7"/><stop offset=".5" stop-color="#ff7ab6"/><stop offset="1" stop-color="#79c0ff"/></linearGradient>
  <style>.spin{animation:hue 8s linear infinite}@keyframes hue{0%,100%{opacity:.9}50%{opacity:.45}}</style>
</defs>''',
      f'<rect x="2" y="2" width="{FW-4}" height="{FH-4}" rx="22" fill="#0d1117"/>',
      f'<rect x="2" y="2" width="{FW-4}" height="{FH-4}" rx="22" fill="url(#grid)"/>',
      f'<ellipse cx="{FW/2}" cy="{FH/2}" rx="250" ry="330" fill="url(#halo)"/>',
      f'<rect class="spin" x="2" y="2" width="{FW-4}" height="{FH-4}" rx="22" fill="none" stroke="url(#edge)" stroke-width="2.5"/>',
      f'<rect x="12" y="12" width="{FW-24}" height="{FH-24}" rx="15" fill="none" stroke="#30363d" stroke-width="1"/>']
L = 26
for (x, y, sx, sy) in [(24, 24, 1, 1), (FW-24, 24, -1, 1), (24, FH-24, 1, -1), (FW-24, FH-24, -1, -1)]:
    fr.append(f'<path d="M{x} {y+sy*L} V{y} H{x+sx*L}" fill="none" stroke="#a371f7" stroke-width="3" stroke-linecap="round"/>')
fr.append(f'<g transform="translate({DX} {DY})">{inner}</g>')
fr.append('</svg>')
out[:] = fr
open(CONFIG["saida"], "w", encoding="utf-8").write("\n".join(out))
print("ok", CONFIG["saida"])
