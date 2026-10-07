# -*- coding: utf-8 -*-
"""
Transforma uma foto (e/ou um texto) em arte ASCII que se "digita" linha a linha.

  # retrato claro sobre fundo escuro (ex.: avatar do GitHub) + legenda embaixo
  python scripts/make_ascii_svg.py --image _src/avatar.png --on-dark
         --black-point 0.2 --caption "ANALISTA E|DESENVOLVEDOR"

  # retrato com fundo claro (saida do prep_photo.py)
  python scripts/make_ascii_svg.py --image source-prepped.png

  # so um banner de texto
  python scripts/make_ascii_svg.py --caption "GABRIEL|MORENO"

Saida: ascii-art.svg (840x880 - mesmo tamanho do stats.svg).
STATIC=1 gera sem animacao.
"""
import argparse
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from config import ASCII_CAPTION, ASCII_TITLE, MONO, SHELL_USER, THEME

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ascii-art.svg"

W, H = 840, 880
PAD_X, TOP, BOT = 26, 76, 38
COLS = 110
RAMP = " .`:-~=+*csS%#@"        # vazio -> cheio
STATIC = os.environ.get("STATIC") == "1"

CANVAS_W = 1100                 # largura de trabalho, em pixels
FONTS = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def metrics():
    """Geometria da grade de caracteres dentro do cartao."""
    adv = (W - 2 * PAD_X) / COLS          # largura de 1 caractere
    size = adv / 0.6                      # monospace: avanco ~ 0.6 * font-size
    lh = size * 1.02                      # entrelinha apertada => arte densa
    rows = int((H - TOP - BOT) // lh)
    return adv, size, lh, rows


def load_font(px):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def caption_image(words, width, ink, max_h):
    """Texto em bloco, centralizado: o maior que couber em `width` x `max_h`."""
    lines = [w.strip() for w in words.upper().split("|") if w.strip()]
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))

    def layout(px):
        f = load_font(px)
        bx = [probe.textbbox((0, 0), line, font=f) for line in lines]
        gap = int(px * 0.38)
        return f, bx, gap, sum(b[3] - b[1] for b in bx) + gap * (len(lines) - 1)

    font = load_font(200)
    widest = max(probe.textlength(line, font=font) for line in lines)
    px = max(24, int(200 * (width * 0.92) / widest))          # cabe na largura
    font, boxes, gap, total_h = layout(px)
    if total_h > max_h:                                        # ...e na altura
        font, boxes, gap, total_h = layout(max(24, int(px * max_h / total_h)))

    img = Image.new("L", (width, total_h), 255 - ink)
    d = ImageDraw.Draw(img)
    y = 0
    for line, b in zip(lines, boxes):
        d.text(((width - (b[2] - b[0])) // 2 - b[0], y - b[1]), line, font=font, fill=ink)
        y += (b[3] - b[1]) + gap
    return img


def prepare_photo(img, on_dark, black_point, gamma):
    """-> imagem onde claro = tinta (caractere cheio)."""
    g = ImageOps.autocontrast(ImageOps.exif_transpose(img).convert("L"), cutoff=(1, 1))
    v = np.asarray(g, dtype=np.float32) / 255.0
    if not on_dark:                       # foto clara: o escuro e que vira tinta
        v = 1.0 - v
    if black_point > 0:                   # faz o fundo sumir de vez
        v = np.clip((v - black_point) / (1.0 - black_point), 0.0, 1.0)
    if gamma != 1.0:
        v = v ** gamma
    return Image.fromarray((v * 255).astype(np.uint8))


def compose(photo, title, caption, adv, lh, rows):
    """Foto / titulo / legenda num canvas com a proporcao exata da grade.

    Convencao do canvas: claro = tinta (caractere cheio), preto = vazio.
    """
    target_h = int(CANVAS_W * (rows * lh) / (COLS * adv))
    canvas = Image.new("L", (CANVAS_W, target_h), 0)
    gap = int(target_h * 0.035)

    # sem foto o bloco de texto e o protagonista, entao pode ser maior
    cap_max = 0.26 if photo is None else 0.16
    cap = caption_image(caption, CANVAS_W, 255, int(target_h * cap_max)) if caption else None

    # --- so texto: titulo grande + legenda, tudo centralizado na vertical
    if photo is None:
        ttl = caption_image(title, CANVAS_W, 255, int(target_h * 0.44)) if title else None
        stack = [b for b in (ttl, rule_image(CANVAS_W, int(target_h * 0.012)), cap) if b]
        total = sum(b.height for b in stack) + gap * (len(stack) - 1)
        y = (target_h - total) // 2
        for block in stack:
            canvas.paste(block, (0, y))
            y += block.height + gap
        return canvas

    # --- foto em cima, legenda embaixo
    avail = target_h - (cap.height + gap if cap else 0)
    # resize (e nao thumbnail) pra tambem AMPLIAR imagens pequenas
    k = min(CANVAS_W / photo.width, avail / photo.height)
    ph = photo.resize((max(1, int(photo.width * k)), max(1, int(photo.height * k))),
                      Image.LANCZOS)

    canvas.paste(ph, ((CANVAS_W - ph.width) // 2, max(0, (avail - ph.height) // 2)))
    if cap:
        canvas.paste(cap, (0, target_h - cap.height))
    return canvas


def rule_image(width, thickness):
    """Uma regua horizontal fina, pra separar titulo e legenda."""
    img = Image.new("L", (width, max(2, thickness)), 0)
    ImageDraw.Draw(img).rectangle([int(width * 0.06), 0, int(width * 0.94), img.height], fill=255)
    return img


def to_ascii(canvas, rows):
    small = np.asarray(canvas.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    idx = np.clip((small * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    art = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    while art and not art[0].strip():
        art.pop(0)
    while art and not art[-1].strip():
        art.pop()
    return [""] * max(0, (rows - len(art)) // 2) + art


def render(art, size, lh, adv, label):
    o = []
    a = o.append
    last = max((i for i, r in enumerate(art) if r.strip()), default=0)

    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
      'role="img" aria-label="Retrato em ASCII">' % (W, H, W, H))

    anim = "" if STATIC else """
    @keyframes typ{from{width:0} to{width:%dpx}}
    @keyframes blink{0%%,49%%{opacity:1} 50%%,100%%{opacity:0}}
    .r{animation:typ .40s steps(%d,end) forwards}
    .car{opacity:0;animation:blink 1.05s step-end infinite;animation-delay:%.2fs}
    """ % (W - PAD_X, COLS, 0.1 + last * 0.036)

    a('<style>%s .mono{font-family:%s;white-space:pre}'
      '.a{font-size:%.2fpx;fill:%s}'
      '.ttl{font-size:24px;fill:%s;font-family:%s}'
      '</style>' % (anim, MONO, size, THEME["ascii"], THEME["dim"], MONO))

    a('<rect x="2" y="2" width="%d" height="%d" rx="18" fill="%s" stroke="%s" stroke-width="2"/>'
      % (W - 4, H - 4, THEME["bg"], THEME["border"]))
    a('<path d="M2 20a18 18 0 0 1 18-18h%d a18 18 0 0 1 18 18v36H2z" fill="%s"/>'
      % (W - 40, THEME["panel"]))
    a('<line x1="2" y1="56" x2="%d" y2="56" stroke="%s" stroke-width="2"/>'
      % (W - 2, THEME["border"]))
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        a('<circle cx="%d" cy="29" r="9" fill="%s"/>' % (34 + i * 32, c))
    a('<text class="ttl" x="152" y="38">%s</text>' % esc(label))

    for i, row in enumerate(art):
        if not row.strip():
            continue
        y = TOP + i * lh + size
        delay = "" if STATIC else ' style="animation-delay:%.3fs"' % (i * 0.036)
        a('<clipPath id="l%d"><rect class="r" x="%d" y="%.2f" width="%s" height="%.2f"%s/></clipPath>'
          % (i, PAD_X, y - size, (W - PAD_X) if STATIC else 0, lh + 2, delay))
        a('<text class="mono a" clip-path="url(#l%d)" x="%d" y="%.2f" xml:space="preserve">%s</text>'
          % (i, PAD_X, y, esc(row)))

    if not STATIC:
        a('<rect class="car" x="%d" y="%.2f" width="%.1f" height="%.1f" fill="%s"/>'
          % (PAD_X, TOP + (last + 1) * lh, adv * 1.2, size * .92, THEME["accent"]))
    a('</svg>')
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image")
    ap.add_argument("--title", default=None,
                    help="texto grande; use | para quebrar linha (padrao: config.ASCII_TITLE)")
    ap.add_argument("--caption", default=None,
                    help="texto menor embaixo (padrao: config.ASCII_CAPTION)")
    ap.add_argument("--on-dark", action="store_true",
                    help="a foto ja e clara sobre fundo escuro (avatar do GitHub)")
    ap.add_argument("--black-point", type=float, default=0.0, help="0..0.6 - apaga o fundo")
    ap.add_argument("--gamma", type=float, default=1.0, help="<1 engrossa, >1 afina")
    ap.add_argument("--label", default=None)
    args = ap.parse_args()

    adv, size, lh, rows = metrics()
    photo = None
    if args.image:
        photo = prepare_photo(Image.open(args.image), args.on_dark,
                              args.black_point, args.gamma)

    title = args.title if args.title is not None else (None if args.image else ASCII_TITLE)
    caption = args.caption if args.caption is not None else ASCII_CAPTION
    if photo is None and not (title or caption):
        ap.error("informe --image e/ou --title/--caption")

    label = args.label or ("%s@github: ~ $ whoami" % SHELL_USER)
    art = to_ascii(compose(photo, title, caption, adv, lh, rows), rows)
    OUT.write_text(render(art, size, lh, adv, label), encoding="utf-8")
    print("ok  %s  (%d/%d linhas, fonte %.1fpx, %.1f KB)"
          % (OUT.name, len([r for r in art if r.strip()]), rows, size,
             OUT.stat().st_size / 1024))


if __name__ == "__main__":
    main()
