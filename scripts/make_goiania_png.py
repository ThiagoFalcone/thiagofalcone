"""Gera scripts/goiania_map.png: mapa de Goiania em estilo de selecao de fase (fundo escuro, ruas em azul e roxo, brilho nas vias principais).

Usa as ruas de scripts/goiania_data.py (OpenStreetMap contributors, ODbL). Recorta a faixa central (y 80..340) para ficar compacto.
Requer Pillow e numpy so para gerar a imagem.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import goiania_data as G

W, H, SS = G.W, G.H, 3
Y0, Y1 = 80, 340
bg = Image.new("RGB", (W * SS, H * SS), (11, 6, 18))
d = ImageDraw.Draw(bg)
for x in range(0, W, 66):
    d.line([(x * SS, 0), (x * SS, H * SS)], fill=(26, 18, 56), width=SS)
for y in range(0, H, 60):
    d.line([(0, y * SS), (W * SS, y * SS)], fill=(26, 18, 56), width=SS)


def draw(paths, width, color, glow=None):
    for seg in paths.split("M")[1:]:
        pts = [tuple(float(v) * SS for v in p.split()) for p in seg.split("L")]
        if glow:
            d.line(pts, fill=glow, width=int(width * 3 * SS), joint="curve")
        d.line(pts, fill=color, width=max(1, int(width * SS)), joint="curve")


draw(G.TERTIARY, 0.9, (58, 47, 122))
draw(G.SECONDARY, 1.5, (59, 111, 209))
draw(G.MAJOR, 2.6, (143, 180, 255), glow=(30, 42, 110))
img = bg.resize((W, H), Image.LANCZOS).crop((0, Y0, W, Y1))
arr = np.asarray(img, dtype="float32")
yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
v = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - arr.shape[0] / 2) / (arr.shape[0] / 2)) ** 2)
arr *= (1 - 0.5 * np.clip((v - 0.55) / 0.6, 0, 1))[..., None]
out = Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "goiania_map.png")
out.save(path, optimize=True)
print(path, os.path.getsize(path) // 1024, "KB")
