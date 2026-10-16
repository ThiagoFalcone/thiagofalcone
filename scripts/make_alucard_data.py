"""Extrai o sprite do Alucard (imagem redimensionada, ~17,2 px por pixel) para scripts/alucard_data.py.

Uso: python scripts/make_alucard_data.py sprite.png
Passos: acha a grade, pega a cor mediana de cada celula (ignora ruido e a marca d'agua), agrupa cores raras
nas mais proximas e separa o fundo branco (ligado a borda) do branco interno do sprite.
"""
import os
import string
import sys
from collections import Counter, deque

import numpy as np
from PIL import Image

PITCH = 17.2


def best_offset(sig):
    best = None
    for o in np.arange(0, PITCH, 0.1):
        idx = (o + np.arange(0, len(sig) / PITCH) * PITCH).astype(int)
        idx = idx[(idx > 0) & (idx < len(sig))]
        sc = sig[idx].sum()
        if best is None or sc > best[0]:
            best = (sc, o)
    return best[1]


def main(src):
    a = np.array(Image.open(src).convert("RGB")).astype(int)
    dx = np.abs(np.diff(a, axis=1)).sum(2).sum(0)
    dy = np.abs(np.diff(a, axis=0)).sum(2).sum(1)
    ox, oy = best_offset(dx), best_offset(dy)
    cols = int((a.shape[1] - ox) // PITCH)
    rows = int((a.shape[0] - oy) // PITCH)
    cell = np.zeros((rows, cols, 3), dtype=int)
    for r in range(rows):
        for c in range(cols):
            x0, x1 = int(ox + (c + 0.2) * PITCH), int(ox + (c + 0.8) * PITCH)
            y0, y1 = int(oy + (r + 0.2) * PITCH), int(oy + (r + 0.8) * PITCH)
            cell[r, c] = np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)
    # agrupa cores: arredonda e junta as raras na mais proxima
    key = lambda p: tuple(int(round(v / 12) * 12) for v in p)
    cnt = Counter(key(p) for p in cell.reshape(-1, 3))
    main_cols = [c for c, n in cnt.most_common() if n >= 6]

    def near(p):
        return min(main_cols, key=lambda m: sum((m[i] - p[i]) ** 2 for i in range(3)))

    grid = [[near(key(cell[r, c])) for c in range(cols)] for r in range(rows)]
    white = near((255, 252, 252)) if (255, 252, 252) not in main_cols else (255, 252, 252)
    bg = set()
    dq = deque((r, c) for r in range(rows) for c in range(cols) if r in (0, rows - 1) or c in (0, cols - 1))
    while dq:
        r, c = dq.popleft()
        if (r, c) in bg or not (0 <= r < rows and 0 <= c < cols):
            continue
        if sum(grid[r][c]) < 720:      # so branco puro conta como fundo
            continue
        bg.add((r, c))
        dq.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])
    palette = []
    out = []
    for r in range(rows):
        line = []
        for c in range(cols):
            if (r, c) in bg:
                line.append(".")
                continue
            col = grid[r][c]
            if col not in palette:
                palette.append(col)
            line.append(string.ascii_letters[palette.index(col)])
        out.append("".join(line))
    # remove linhas/colunas vazias das bordas
    keep_r = [i for i, l in enumerate(out) if set(l) != {"."}]
    out = out[keep_r[0]:keep_r[-1] + 1]
    keep_c = [i for i in range(cols) if any(l[i] != "." for l in out)]
    out = [l[keep_c[0]:keep_c[-1] + 1] for l in out]
    hexs = ["#%02x%02x%02x" % tuple(min(255, max(0, v)) for v in p) for p in palette]
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alucard_data.py")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write('"""Sprite do Alucard (extraido da imagem de referencia). Gerado por make_alucard_data.py."""\n')
        f.write(f"W, H = {len(out[0])}, {len(out)}\nPALETTE = {hexs!r}\nROWS = {out!r}\n")
    print(len(out[0]), "x", len(out), len(hexs), "cores")
    for l in out:
        print(l)


if __name__ == "__main__":
    main(sys.argv[1])
