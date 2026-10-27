"""Converte o cenario do Street Fighter III (imagem de referencia) em pixel-art nitido: scripts/stage.png.

Uso: python scripts/make_stage_data.py cenario.webp [y_topo=215] [altura=272] [linhas=160] [cores=72]
Recorta uma faixa horizontal (mesma proporcao do banner 1056x320), reduz com realce de nitidez e quantiza as cores.
O banner amplia o PNG em pixels (cada pixel vira 2x2), sem suavizar.
"""
import os
import sys

from PIL import Image, ImageEnhance, ImageFilter


def main(src, y0=215, h=272, rows=160, ncolors=72):
    im = Image.open(src).convert("RGB")
    im = im.crop((0, y0, im.width, min(im.height, y0 + h)))
    cols = round(im.width * rows / im.height)
    im = im.resize((cols, rows), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120, threshold=2))
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.1)).enhance(1.1)
    q = im.quantize(colors=ncolors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage.png")
    q.save(path, optimize=True)
    print(cols, rows, ncolors, "cores,", os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], int(a[2]) if len(a) > 2 else 215, int(a[3]) if len(a) > 3 else 272, int(a[4]) if len(a) > 4 else 160, int(a[5]) if len(a) > 5 else 72)
