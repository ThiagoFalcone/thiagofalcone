"""Converte a foto de referencia da Stratocaster (fundo branco) em pixel-art: scripts/strat_data.py.

Uso: python scripts/make_strat_data.py foto.webp [colunas=150] [cores=40]
"""
import os
import string
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def main(src, cols=150, ncolors=40):
    im = Image.open(src).convert("RGB")
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    a = np.array(im)
    mask = a.min(axis=2) < 238
    ys, xs = np.where(mask)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    a = a[y0:y1, x0:x1].astype("float32")
    m = mask[y0:y1, x0:x1].astype("float32")
    h, w = m.shape
    rows = max(1, round(cols * h / w))

    def box(arr, flt=Image.BOX):
        return np.array(Image.fromarray(arr, mode="F").resize((cols, rows), flt))

    alpha = box(m)
    chans = [box(a[:, :, i] * m, Image.LANCZOS) / np.maximum(box(m, Image.LANCZOS), 1e-6) for i in range(3)]
    rgb = np.stack(chans, axis=2).clip(0, 255).astype("uint8")
    opaque = alpha >= 0.5
    rgb[~opaque] = (255, 255, 255)
    img = Image.fromarray(rgb)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Color(img).enhance(1.1)
    q = img.quantize(colors=ncolors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[: ncolors * 3]
    idx = np.array(q)
    used = sorted({int(i) for i in idx[opaque]})
    remap = {old: n for n, old in enumerate(used)}
    hexs = ["#%02x%02x%02x" % tuple(pal[o * 3:o * 3 + 3]) for o in used]
    lines = []
    for r in range(rows):
        out, c = [], 0
        while c < cols:
            ch = "." if not opaque[r, c] else string.ascii_letters[remap[int(idx[r, c])]]
            n = 1
            while c + n < cols and (("." if not opaque[r, c + n] else string.ascii_letters[remap[int(idx[r, c + n])]]) == ch):
                n += 1
            out.append(f"{ch}{n}")
            c += n
        lines.append("".join(out))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strat_data.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""Pixel-art da Stratocaster (convertido da foto de referencia). Gerado por make_strat_data.py."""\n')
        f.write(f"W, H = {cols}, {rows}\nPALETTE = {hexs!r}\nROWS = {lines!r}\n")
    print(cols, rows, len(hexs), "cores;", sum(len(r) for r in lines), "bytes de dados")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 150, int(sys.argv[3]) if len(sys.argv) > 3 else 40)
