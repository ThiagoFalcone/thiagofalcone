"""Converte a imagem da capela (fundo do banner) em pixel-art: scripts/chapel_data.py.

Uso: python scripts/make_chapel_data.py capela.png [altura_em_celulas=107] [cores=48]
"""
import os
import string
import sys

import numpy as np
from PIL import Image, ImageEnhance


def main(src, rows=107, ncolors=48):
    im = Image.open(src).convert("RGB")
    cols = round(im.width * rows / im.height)
    im = im.resize((cols, rows), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    q = im.quantize(colors=ncolors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[: ncolors * 3]
    idx = np.array(q)
    used = sorted({int(i) for i in idx.flatten()})
    remap = {o: n for n, o in enumerate(used)}
    hexs = ["#%02x%02x%02x" % tuple(pal[o * 3:o * 3 + 3]) for o in used]
    lines = ["".join(string.ascii_letters[remap[int(idx[r, c])]] for c in range(cols)) for r in range(rows)]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chapel_data.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""Capela do Castlevania em pixel-art (convertida da imagem de referencia). Gerado por make_chapel_data.py."""\n')
        f.write(f"W, H = {cols}, {rows}\nPALETTE = {hexs!r}\nROWS = {lines!r}\n")
    print(cols, rows, len(hexs), "cores")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 107, int(sys.argv[3]) if len(sys.argv) > 3 else 48)
