# -*- coding: utf-8 -*-
"""
Limpa uma ilustracao vetorial: apaga o fundo e os elementos soltos, deixando so
a figura principal. Serve pra icone/clipart com fundo chapado.

   python scripts/clean_art.py _src/coder.avif
   -> _src/coder-clean.png   (fundo transparente, so o desenho)

Como funciona: separa a imagem em pedacos conectados, mantem o(s) maior(es) e
joga o resto fora. Buracos internos (olho, lente de oculos, dente) sao
preservados, nao viram furo.

Opcoes:
   --keep 1        quantos pedacos manter (do maior pro menor)
   --min-area 500  tambem mantem qualquer pedaco com pelo menos essa area
   --bg none       'none' = transparente | 'white' | 'black'
   --level 720     soma R+G+B abaixo da qual o pixel conta como desenho (0..765)
   --crop          corta a sobra de fundo em volta do desenho
   --inspect       so lista os pedacos e sai, sem gravar nada
"""
import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def components(rgb, level):
    ink = (rgb.astype(np.int32).sum(2) < level).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(ink, connectivity=8)
    order = [i for i in np.argsort(-stats[1:, cv2.CC_STAT_AREA]) + 1]
    return lab, stats, order


def fill_holes(mask):
    """Fecha os vazios internos (so os que nao encostam na borda)."""
    h, w = mask.shape
    outside = (1 - mask).astype(np.uint8)
    seed = np.zeros((h + 2, w + 2), np.uint8)
    # inunda a partir de toda a moldura: o que sobrar branco e buraco interno
    for pt in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if outside[pt[1], pt[0]]:
            cv2.floodFill(outside, seed, pt, 0)
    return (mask | outside).astype(bool)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--out", default=None)
    ap.add_argument("--keep", type=int, default=1)
    ap.add_argument("--min-area", type=int, default=0)
    ap.add_argument("--bg", choices=("none", "white", "black"), default="none")
    ap.add_argument("--level", type=int, default=720)
    ap.add_argument("--crop", action="store_true",
                    help="corta a sobra de fundo em volta do desenho")
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args()

    src = Path(args.image)
    if not src.exists():
        raise SystemExit("nao achei o arquivo: %s" % src)

    img = Image.open(src).convert("RGB")
    rgb = np.asarray(img)
    lab, stats, order = components(rgb, args.level)

    if args.inspect:
        print("pedacos encontrados (maior primeiro):")
        for i in order:
            a = stats[i, cv2.CC_STAT_AREA]
            if a < 40:
                break
            x, y, w, h = stats[i, :4]
            print("  #%-3d area=%-7d bbox=(%d,%d) %dx%d" % (i, a, x, y, w, h))
        return

    keep = set(order[:args.keep])
    if args.min_area:
        keep |= {i for i in order if stats[i, cv2.CC_STAT_AREA] >= args.min_area}

    mask = np.isin(lab, list(keep)).astype(np.uint8)
    mask = fill_holes(mask)
    print("  mantidos %d de %d pedacos (%d px)" % (len(keep), len(order), mask.sum()))

    ys, xs = np.nonzero(mask)
    if args.crop:
        box = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgb, mask = rgb[box], mask[box]

    out = Path(args.out) if args.out else src.with_name(src.stem + "-clean.png")
    if args.bg == "none":
        rgba = np.dstack([rgb, (mask * 255).astype(np.uint8)])
        Image.fromarray(rgba, "RGBA").save(out)
    else:
        flat = 255 if args.bg == "white" else 0
        clean = np.where(mask[..., None], rgb, flat).astype(np.uint8)
        Image.fromarray(clean, "RGB").save(out)

    print("ok  %s  (%dx%d)" % (out.name, mask.shape[1], mask.shape[0]))


if __name__ == "__main__":
    main()
