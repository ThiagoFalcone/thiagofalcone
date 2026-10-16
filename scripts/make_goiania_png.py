"""Gera scripts/goiania_map.jpg: pergaminho envelhecido com as ruas de Goiania desenhadas a tinta (fundo estatico do mapa medieval).

Usa as ruas de scripts/goiania_data.py (OpenStreetMap contributors, ODbL). Requer Pillow e numpy so para gerar a imagem.
"""
import os

import numpy as np
from PIL import Image, ImageFilter, ImageDraw

import goiania_data as G

W, H, SS = G.W, G.H, 3
rng = np.random.default_rng(11)


def noise(scale):
    small = rng.random((H // scale + 3, W // scale + 3))
    img = Image.fromarray((small * 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    return np.asarray(img, dtype="float32") / 255.0


# pergaminho: cor base + manchas em varias escalas + vinheta queimada + dobras
n = noise(120) * 1.0 + noise(48) * 0.6 + noise(16) * 0.35 + noise(4) * 0.12
n = (n - n.mean()) / n.std()
base = np.zeros((H, W, 3), dtype="float32")
base[:] = (226, 204, 158)
base += n[..., None] * np.array([11, 11, 14], dtype="float32")
stain = np.asarray(Image.fromarray((np.clip(noise(70) - 0.62, 0, 1) * 255 * 3).astype("uint8")).filter(ImageFilter.GaussianBlur(6)), dtype="float32") / 255.0
base -= stain[..., None] * np.array([60, 70, 80], dtype="float32")
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
burn = np.clip((d - 0.62) / 0.55, 0, 1) ** 1.6
base *= (1 - 0.55 * burn)[..., None] * np.array([1.0, 0.93, 0.82])[None, None, :] + (1 - burn)[..., None] * 0 + 0 * 1
base = np.clip(base, 0, 255)
for fx in (W // 3, 2 * W // 3):                       # dobras do papel
    base[:, fx - 1:fx + 1] *= 0.93
    base[:, fx + 1:fx + 3] *= 1.04
base[H // 2 - 1:H // 2 + 1, :] *= 0.94
base = np.clip(base, 0, 255)

# ruas a tinta (supersampling para suavizar)
ink = Image.new("L", (W * SS, H * SS), 0)
dr = ImageDraw.Draw(ink)


def draw(paths, width, gray):
    for seg in paths.split("M")[1:]:
        pts = [tuple(float(v) * SS for v in p.split()) for p in seg.split("L")]
        dr.line(pts, fill=gray, width=max(1, int(width * SS)), joint="curve")


draw(G.TERTIARY, 0.9, 120)
draw(G.SECONDARY, 1.5, 190)
draw(G.MAJOR, 2.6, 255)
ink = ink.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.45))
a = np.asarray(ink, dtype="float32")[..., None] / 255.0
ink_col = np.array([58, 36, 18], dtype="float32")
base = base * (1 - a * 0.88) + ink_col * a * 0.88
out = Image.fromarray(np.clip(base, 0, 255).astype("uint8"))
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "goiania_map.jpg")
out.save(path, quality=82, optimize=True)
print(path, os.path.getsize(path) // 1024, "KB")
