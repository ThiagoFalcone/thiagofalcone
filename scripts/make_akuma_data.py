"""Converte a foto do Akuma em miçangas (metade de cima da imagem) em pixel-art nitido: scripts/akuma_data.py.

Uso: python scripts/make_akuma_data.py foto.png [colunas=40] [cores=26]
- fundo cinza removido pela cor (pouca saturacao e claro), ficando so com o maior componente conectado (ignora a moeda);
- uma cor por pixel = MEDIANA do centro da celula (sem misturar cores como a media faria);
- a grade fica perto do tamanho real das miçangas, entao cada pixel sai chunky e limpo;
- pixels isolados (ruido do furo das miçangas) sao removidos.
"""
import os
import string
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageEnhance


def largest_component(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = []
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                comp, dq = [], deque([(y, x)])
                seen[y, x] = True
                while dq:
                    cy, cx = dq.popleft()
                    comp.append((cy, cx))
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            dq.append((ny, nx))
                if len(comp) > len(best):
                    best = comp
    out = np.zeros_like(mask)
    for y, x in best:
        out[y, x] = True
    return out


def main(src, cols=40, ncolors=26, top_rows=298):
    full = Image.open(src).convert("RGB")
    im = full.crop((0, 0, full.width, top_rows))
    a = np.array(im).astype("float32")
    sat = a.max(axis=2) - a.min(axis=2)
    lum = a.mean(axis=2)
    mask = (sat >= 38) | (lum < 135)
    small = np.array(Image.fromarray((mask * 255).astype("uint8")).resize((im.width // 3, im.height // 3), Image.BOX)) > 100
    comp = largest_component(small)
    big = np.array(Image.fromarray((comp * 255).astype("uint8")).resize((im.width, im.height), Image.NEAREST)) > 0
    ys, xs = np.where(big)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    a, m = a[y0:y1, x0:x1], big[y0:y1, x0:x1]
    h, w = m.shape
    cw = w / cols
    rows = max(1, round(h / cw))
    ch = h / rows
    cell = np.zeros((rows, cols, 3), dtype="float32")
    opaque = np.zeros((rows, cols), dtype=bool)
    for r in range(rows):
        for c in range(cols):
            ya, yb = int(r * ch + ch * 0.2), max(int(r * ch + ch * 0.8), int(r * ch + ch * 0.2) + 1)
            xa, xb = int(c * cw + cw * 0.2), max(int(c * cw + cw * 0.8), int(c * cw + cw * 0.2) + 1)
            mm = m[int(r * ch):int((r + 1) * ch) + 1, int(c * cw):int((c + 1) * cw) + 1]
            if mm.size and mm.mean() >= 0.5:
                px = a[ya:yb, xa:xb][m[ya:yb, xa:xb]]
                if len(px):
                    cell[r, c] = np.median(px, axis=0)
                    opaque[r, c] = True
    for _ in range(2):                                            # tira pixels isolados (ruido)
        drop = []
        for r in range(rows):
            for c in range(cols):
                if opaque[r, c]:
                    n = sum(1 for rr, cc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if 0 <= rr < rows and 0 <= cc < cols and opaque[rr, cc])
                    if n <= 1:
                        drop.append((r, c))
        for r, c in drop:
            opaque[r, c] = False
    rgb = cell.clip(0, 255).astype("uint8")
    rgb[~opaque] = (255, 255, 255)
    pil = ImageEnhance.Color(ImageEnhance.Contrast(Image.fromarray(rgb)).enhance(1.12)).enhance(1.35)   # cores mais vivas
    q = pil.quantize(colors=ncolors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    pal = q.getpalette()[: ncolors * 3]
    idx = np.array(q)
    for _ in range(1):                                            # filtro de maioria 3x3: manchas de cor chapadas, sem granulado
        out = idx.copy()
        for r in range(rows):
            for c in range(cols):
                if not opaque[r, c]:
                    continue
                win = [int(idx[rr, cc]) for rr in range(max(0, r - 1), min(rows, r + 2)) for cc in range(max(0, c - 1), min(cols, c + 2)) if opaque[rr, cc]]
                top = max(set(win), key=win.count)
                if win.count(top) >= 6 and top != idx[r, c]:
                    out[r, c] = top
        idx = out
    used = sorted({int(i) for i in idx[opaque]})
    remap = {o: n for n, o in enumerate(used)}
    hexs = ["#%02x%02x%02x" % tuple(pal[o * 3:o * 3 + 3]) for o in used]
    lines = []
    for r in range(rows):
        line = "".join("." if not opaque[r, c] else string.ascii_letters[remap[int(idx[r, c])]] for c in range(cols))
        out, c = [], 0
        while c < cols:
            chh, n = line[c], 1
            while c + n < cols and line[c + n] == chh:
                n += 1
            out.append(f"{chh}{n}")
            c += n
        lines.append("".join(out))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "akuma_data.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""Pixel-art do Akuma (convertido da foto de referencia). Gerado por make_akuma_data.py."""\n')
        f.write(f"W, H = {cols}, {rows}\nPALETTE = {hexs!r}\nROWS = {lines!r}\n")
    print(cols, rows, len(hexs), "cores")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40, int(sys.argv[3]) if len(sys.argv) > 3 else 26)
