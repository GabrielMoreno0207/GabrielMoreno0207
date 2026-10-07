# -*- coding: utf-8 -*-
"""
Prepara uma foto pra virar arte ASCII: recorta o fundo com `rembg`, enquadra
o recorte num quadrado, reforca o contraste local (CLAHE) e joga sobre branco.

   python scripts/prep_photo.py "C:\\caminho\\foto.jpg"
   -> source-prepped.png

   python scripts/make_ascii_svg.py --image source-prepped.png --caption "..."

Opcoes:
   --no-cut      pula o recorte de fundo (foto ja tem fundo limpo)
   --margin 0.12 folga ao redor do recorte
   --clahe 2.4   forca do contraste local (0 desliga)
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"
MAX_SIDE = 1600


def cut_background(img: Image.Image) -> Image.Image:
    """-> RGBA com o fundo transparente."""
    try:
        from rembg import new_session, remove
    except ImportError:
        raise SystemExit("rembg nao instalado. Rode:  python -m pip install --user rembg onnxruntime\n"
                         "(ou use --no-cut se a foto ja tiver fundo limpo)")
    print("  recortando o fundo (a 1a vez baixa o modelo, ~176 MB)...")
    return remove(img.convert("RGBA"), session=new_session("u2net_human_seg"),
                  alpha_matting=True, alpha_matting_foreground_threshold=250,
                  alpha_matting_background_threshold=15, alpha_matting_erode_size=8)


def square_crop(img: Image.Image, margin: float, zoom: float) -> Image.Image:
    """Quadrado ancorado na cabeca: `zoom` e a fracao da largura do assunto."""
    box = None
    if img.mode == "RGBA":
        box = img.split()[-1].point(lambda v: 255 if v > 12 else 0).getbbox()
    if box is None:
        box = (0, 0, img.width, img.height)

    x0, y0, x1, y1 = box
    side = (x1 - x0) * zoom * (1 + margin)
    cx = (x0 + x1) / 2
    top = y0 - (y1 - y0) * margin * 0.5          # um respiro acima da cabeca
    return img.crop((int(cx - side / 2), int(top), int(cx + side / 2), int(top + side)))


def on_flat(img: Image.Image, bg: str) -> Image.Image:
    if img.mode != "RGBA":
        return img.convert("RGB")
    v = 255 if bg == "white" else 0
    flat = Image.new("RGBA", img.size, (v, v, v, 255))
    return Image.alpha_composite(flat, img).convert("RGB")


def local_contrast(img: Image.Image, clip: float) -> Image.Image:
    """CLAHE no canal L: puxa detalhe de sombra e luz sem estourar."""
    if clip <= 0:
        return img
    import cv2
    lab = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2LAB)
    lab[:, :, 0] = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(lab[:, :, 0])
    return Image.fromarray(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--no-cut", action="store_true")
    ap.add_argument("--margin", type=float, default=0.10)
    ap.add_argument("--zoom", type=float, default=0.85,
                    help="<1 aproxima no rosto, >1 afasta")
    ap.add_argument("--clahe", type=float, default=2.4)
    ap.add_argument("--bg", choices=("white", "black"), default="white")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    src = Path(args.photo)
    if not src.exists():
        raise SystemExit("nao achei o arquivo: %s" % src)

    img = ImageOps.exif_transpose(Image.open(src))
    img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    print("  entrada: %dx%d" % img.size)

    if not args.no_cut:
        img = cut_background(img)
    img = square_crop(img, args.margin, args.zoom)
    img = on_flat(img, args.bg)
    img = local_contrast(img, args.clahe)
    img = ImageOps.autocontrast(img.convert("L"), cutoff=(0, 1)).convert("RGB")

    out = Path(args.out) if args.out else OUT
    img.save(out)
    print("ok  %s  (%dx%d)" % (out.name, img.width, img.height))


if __name__ == "__main__":
    main()
