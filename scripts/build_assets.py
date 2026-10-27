"""Gera os SVGs pixel-art do README: banner, rodape, divisor, icones, ficha e citacao semanal.

Tudo e desenhado com retangulos (sem fontes externas), entao funciona dentro de <img> no GitHub.
"""
import glob
import math
import os
import random
import re
import string
import sys
import textwrap
import unicodedata
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ---------------------------------------------------------------- fonte 5x7
_F = {
    "A": "01110,10001,10001,11111,10001,10001,10001", "B": "11110,10001,10001,11110,10001,10001,11110",
    "C": "01110,10001,10000,10000,10000,10001,01110", "D": "11110,10001,10001,10001,10001,10001,11110",
    "E": "11111,10000,10000,11110,10000,10000,11111", "F": "11111,10000,10000,11110,10000,10000,10000",
    "G": "01110,10001,10000,10111,10001,10001,01110", "H": "10001,10001,10001,11111,10001,10001,10001",
    "I": "01110,00100,00100,00100,00100,00100,01110", "J": "00111,00010,00010,00010,00010,10010,01100",
    "K": "10001,10010,10100,11000,10100,10010,10001", "L": "10000,10000,10000,10000,10000,10000,11111",
    "M": "10001,11011,10101,10101,10001,10001,10001", "N": "10001,11001,10101,10011,10001,10001,10001",
    "O": "01110,10001,10001,10001,10001,10001,01110", "P": "11110,10001,10001,11110,10000,10000,10000",
    "Q": "01110,10001,10001,10001,10101,10010,01101", "R": "11110,10001,10001,11110,10100,10010,10001",
    "S": "01111,10000,10000,01110,00001,00001,11110", "T": "11111,00100,00100,00100,00100,00100,00100",
    "U": "10001,10001,10001,10001,10001,10001,01110", "V": "10001,10001,10001,10001,10001,01010,00100",
    "W": "10001,10001,10001,10101,10101,11011,10001", "X": "10001,10001,01010,00100,01010,10001,10001",
    "Y": "10001,10001,01010,00100,00100,00100,00100", "Z": "11111,00001,00010,00100,01000,10000,11111",
    "0": "01110,10001,10011,10101,11001,10001,01110", "1": "00100,01100,00100,00100,00100,00100,01110",
    "2": "01110,10001,00001,00110,01000,10000,11111", "3": "11110,00001,00001,01110,00001,00001,11110",
    "4": "00010,00110,01010,10010,11111,00010,00010", "5": "11111,10000,11110,00001,00001,10001,01110",
    "6": "00110,01000,10000,11110,10001,10001,01110", "7": "11111,00001,00010,00100,01000,01000,01000",
    "8": "01110,10001,10001,01110,10001,10001,01110", "9": "01110,10001,10001,01111,00001,00010,01100",
    " ": "00000,00000,00000,00000,00000,00000,00000", "-": "00000,00000,00000,11111,00000,00000,00000",
    "&": "01100,10010,10100,01000,10101,10010,01101", ".": "00000,00000,00000,00000,00000,01100,01100",
    "!": "00100,00100,00100,00100,00100,00000,00100", "/": "00001,00010,00010,00100,01000,01000,10000",
    ":": "00000,01100,01100,00000,01100,01100,00000", ",": "00000,00000,00000,00000,01100,00100,01000",
    "'": "00100,00100,01000,00000,00000,00000,00000", "%": "11001,11010,00010,00100,01000,01011,10011", "(": "00010,00100,01000,01000,01000,00100,00010", ")": "01000,00100,00010,00010,00010,00100,01000", "?": "01110,10001,00001,00110,00100,00000,00100",
}
FONT = {k: v.split(",") for k, v in _F.items()}


MARKS = {"́": [(3, -2), (2, -1)], "̀": [(1, -2), (2, -1)], "̂": [(2, -2), (1, -1), (3, -1)],
         "̃": [(1, -1), (2, -2), (3, -1)], "̧": [(2, 7), (1, 8)]}


def _split(s):
    out = []
    for ch in unicodedata.normalize("NFD", s.upper()):
        if unicodedata.combining(ch) and out:
            out[-1][1].append(ch)
        else:
            out.append([ch, []])
    return out


def text_w(s, p):
    return (len(_split(s)) * 6 - 1) * p


def text(x, y, s, p, color, shadow=None, attrs=""):
    runs = []
    for i, (ch, marks) in enumerate(_split(s)):
        g = FONT.get(ch, FONT[" "])
        for ry, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == "1":
                    c2 = c
                    while c2 < 5 and row[c2] == "1":
                        c2 += 1
                    runs.append(f'<rect x="{i * 6 * p + c * p}" y="{ry * p}" width="{(c2 - c) * p}" height="{p}"/>')
                    c = c2
                else:
                    c += 1
        for m in marks:
            for cc, rr in MARKS.get(m, []):
                runs.append(f'<rect x="{i * 6 * p + cc * p}" y="{rr * p}" width="{p}" height="{p}"/>')
    body = "".join(runs)
    out = ""
    if shadow:
        out += f'<g fill="{shadow}" transform="translate({x + p},{y + p})">{body}</g>'
    return out + f'<g fill="{color}" transform="translate({x},{y})" {attrs}>{body}</g>'


# ---------------------------------------------------------------- utilidades
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, rb = hex2rgb(a), hex2rgb(b)
    return "#%02x%02x%02x" % tuple(round(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def grad(stops, t):
    t = min(max(t, 0), 1) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return mix(stops[i], stops[i + 1], t - i)


def sprite(rows, pal, x, y, s, attrs=""):
    w = max(len(r) for r in rows)
    out = []
    for ry, row in enumerate(rows):
        row = row.ljust(w, ".")
        c = 0
        while c < w:
            ch = row[c]
            if ch != "." and ch in pal:
                c2 = c
                while c2 < w and row[c2] == ch:
                    c2 += 1
                out.append(f'<rect x="{c * s}" y="{ry * s}" width="{(c2 - c) * s}" height="{s}" fill="{pal[ch]}"/>')
                c = c2
            else:
                c += 1
    return f'<g transform="translate({x},{y})" {attrs}>{"".join(out)}</g>'


def cells(cellset, color, cell=8):
    rows = {}
    for c, r in cellset:
        rows.setdefault(r, []).append(c)
    out = []
    for r, cs in sorted(rows.items()):
        cs.sort()
        start = prev = cs[0]
        for c in cs[1:] + [None]:
            if c is None or c != prev + 1:
                out.append(f'<rect x="{start * cell}" y="{r * cell}" width="{(prev - start + 1) * cell}" height="{cell}"/>')
                if c is not None:
                    start = c
            prev = c if c is not None else prev
    return f'<g fill="{color}">{"".join(out)}</g>'


def svg(w, h, body, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" {extra}><metadata>(c) 2026 Thiago Falcone. All rights reserved. github.com/ThiagoFalcone</metadata>{body}</svg>')


def sky(stops, y0, y1, w, bands):
    bh = (y1 - y0) / bands
    return "".join(
        f'<rect x="0" y="{y0 + i * bh:.0f}" width="{w}" height="{bh + 1:.0f}" fill="{grad(stops, i / (bands - 1))}"/>'
        for i in range(bands))


def stars(rnd, n, w, ymax, color):
    out = []
    for _ in range(n):
        x, y = rnd.randrange(0, w, 8), rnd.randrange(0, ymax, 8)
        sz = rnd.choice([4, 4, 8])
        d = rnd.uniform(1.5, 4)
        out.append(f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{color}">'
                   f'<animate attributeName="opacity" values="1;0.2;1" dur="{d:.1f}s" begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/></rect>')
    return "".join(out)


def moon(cx, cy, r, col, glow):
    def disc(rr):
        return {(c, rw) for rw in range(cy - rr, cy + rr + 1) for c in range(cx - rr, cx + rr + 1)
                if (c - cx) ** 2 + (rw - cy) ** 2 <= rr * rr + 1}
    out = f'<g opacity="0.10">{cells(disc(r + 4), glow)}</g><g opacity="0.18">{cells(disc(r + 2), glow)}</g>'
    out += cells(disc(r), col)
    dark = mix(col, "#000000", 0.18)
    out += cells({(cx - 2, cy - 1), (cx - 1, cy - 1), (cx + 2, cy + 1), (cx + 1, cy + 2), (cx - 2, cy + 2)}, dark)
    return out


def hills(w, base_y, color, amp, freq, phase, minh):
    cs = set()
    for c in range(w // 8 + 1):
        h = int(minh + amp * (1 + math.sin(c / freq + phase)) / 2 + (amp / 3) * math.sin(c / (freq / 2.3) + phase * 2))
        for r in range(base_y // 8 - h, base_y // 8):
            cs.add((c, r))
    return cells(cs, color)


def falling(rnd, n, w, h, colors, sizes, rise=False, dur=(6, 12), drift=40, tall=None):
    out = []
    for _ in range(n):
        x, d = rnd.randrange(0, w), rnd.uniform(*dur)
        sz = rnd.choice(sizes)
        y0, y1 = (h + 10, -30) if rise else (-30, h + 10)
        dx = rnd.randint(-drift, drift)
        out.append(f'<rect x="{x}" y="0" width="{sz}" height="{tall or sz}" fill="{rnd.choice(colors)}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0,{y0};{dx},{y1}" dur="{d:.1f}s" '
                   f'begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/></rect>')
    return "".join(out)


BAT = ["k.....k", "kk.k.kk", ".kkkkk.", "..k.k.."]
def bats(rnd, w, color):
    out = []
    for i in range(5):
        y, d = rnd.randrange(30, 170), rnd.uniform(9, 16)
        spr = sprite(BAT, {"k": color}, 0, 0, 4)
        out.append(f'<g><animateTransform attributeName="transform" type="translate" values="-40,{y};{w + 40},{y}" dur="{d:.1f}s" '
                   f'begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/>'
                   f'<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-12;0,0" dur="0.9s" repeatCount="indefinite"/>{spr}</g></g>')
    return "".join(out)


# ---------------------------------------------------------------- temas
def T(title, sub, skyc, moon_c, far, near, castle_c, win, ground, text_c, sub_c, fx="", fxc=None, deck="#ff2a2a"):
    return dict(title=title, sub=sub, sky=skyc, moon=moon_c, far=far, near=near, castle=castle_c, win=win,
                ground=ground, text=text_c, subc=sub_c, fx=fx, fxc=fxc or ["#ffffff"], deck=deck)


TH = {
    "fighter": T("THIAGO FALCONE", "SOFTWARE ENGINEER & ENTREPRENEUR", ["#12061f", "#3a0f3f", "#8a1a3a", "#e2512b"], "#ff3b2f", "#2a0f35",
                 "#1a0a24", "#0d0612", "#ffb347", ("#3a2a3f", "#241a2c", "#4e3a58"), "#ffffff", "#ff5a4d"),
    "rock": T("THIAGO FALCONE", "SOFTWARE ENGINEER", ["#0b0614", "#2a0a2e", "#7a1020", "#e0551c"],
              "#f2e9d0", "#3a1238", "#1d0b24", "#0a0612", "#ffb347", ("#4a2418", "#2c140f", "#6b3a22"),
              "#fff3d6", "#ff4d3d", "sparks", ["#ff7a1a", "#ffb347"]),
    "halloween": T("HAPPY HALLOWEEN", "THIAGO FALCONE: TRICK OR RIFF", ["#08000f", "#2b0a3d", "#7a2a00", "#ff6a00"],
                   "#ffb347", "#3b1050", "#1b0826", "#0a0412", "#ff9a1a", ("#3a1a0a", "#22100a", "#5a2c10"),
                   "#ffd9a0", "#ff6a00", "bats", ["#0a0412"], "#ff6a00"),
    "natal": T("FELIZ NATAL", "THIAGO FALCONE: METAL CHRISTMAS", ["#04210f", "#0b3d22", "#7a1520", "#c1121f"],
               "#fffbe6", "#14532d", "#0b3d22", "#05140a", "#ffd166", ("#eef6f9", "#b8cbd6", "#ffffff"),
               "#ffffff", "#ff6b6b", "snow", ["#ffffff", "#dff1ff"], "#c1121f"),
    "anonovo": T("FELIZ ANO NOVO", "THIAGO FALCONE: NEW RIFFS", ["#000000", "#1a1033", "#4a3600", "#d4af37"],
                 "#fff4c2", "#2a2036", "#140f1e", "#07050c", "#ffd700", ("#2a2236", "#18121f", "#3a3048"),
                 "#ffe27a", "#ffffff", "confetti", ["#ffd700", "#ffffff", "#ff4d6d"], "#d4af37"),
    "criancas": T("DIA DAS CRIANÇAS", "THIAGO FALCONE: PLAYER ONE", ["#0b1d51", "#6a4c93", "#e63946", "#ffd60a"],
                  "#fff7c2", "#4a2c6b", "#2a1a45", "#120a24", "#ffd60a", ("#3a2a5a", "#241940", "#5a4480"),
                  "#ffffff", "#ffd60a", "confetti", ["#ffd60a", "#2a9d8f", "#e63946", "#4cc9f0"], "#ffd60a"),
    "blackfriday": T("BLACK FRIDAY", "THIAGO FALCONE: BLACK SABBATH", ["#000000", "#0d0d0d", "#2b2400", "#ffd400"],
                     "#ffd400", "#1a1a1a", "#0d0d0d", "#000000", "#ffd400", ("#222222", "#111111", "#333333"),
                     "#ffd400", "#ffffff", "sparks", ["#ffd400"], "#ffd400"),
    "carnaval": T("CARNAVAL", "THIAGO FALCONE: BLOCO DO METAL", ["#3a0ca3", "#7209b7", "#f72585", "#ffd60a"],
                  "#fff7c2", "#5a1a8a", "#2d0b55", "#14052b", "#ffd60a", ("#3a1a60", "#25103f", "#5a2a8a"),
                  "#ffffff", "#ffd60a", "confetti", ["#f72585", "#ffd60a", "#06d6a0", "#4cc9f0"], "#f72585"),
    "pascoa": T("FELIZ PÁSCOA", "THIAGO FALCONE: EASTER EGGS", ["#3d2c6b", "#8d6bb8", "#ffb3c6", "#fff1c1"],
                "#fffbe6", "#6a5a9a", "#4a3a7a", "#2a2050", "#ffe27a", ("#4f9d5a", "#3a7d44", "#6cc07a"),
                "#ffffff", "#ffe27a", "confetti", ["#ffb3c6", "#ffe27a", "#b8f2e6"], "#ffb3c6"),
    "maes": T("FELIZ DIA DAS MÃES", "THIAGO FALCONE: OBRIGADO MÃE", ["#2a0a3d", "#7b2a6f", "#f72585", "#ffb3c6"],
              "#fff0f5", "#5a1a60", "#3a0f45", "#1a0524", "#ffd1e0", ("#4a1a50", "#2e0f36", "#6a2a70"),
              "#ffffff", "#ffb3c6", "confetti", ["#ffb3c6", "#ff4d8d", "#ffffff"], "#f72585"),
    "pais": T("FELIZ DIA DOS PAIS", "THIAGO FALCONE: HERANÇA ROCK", ["#050a1a", "#12234d", "#3a86ff", "#9ad0ff"],
              "#eaf4ff", "#1a2f66", "#0f1c40", "#050a1a", "#ffd166", ("#1a2a50", "#0f1a38", "#2a3f70"),
              "#ffffff", "#9ad0ff", "", None, "#3a86ff"),
    "junina": T("FESTA JUNINA", "THIAGO FALCONE: ARRAIÁ DO ROCK", ["#2b1408", "#7f3a14", "#e63946", "#ffb703"],
                "#ffe9a8", "#5a2a10", "#2e1608", "#120804", "#ffb703", ("#4a2a14", "#2e1a0c", "#6a3a1c"),
                "#fff0c8", "#ffb703", "sparks", ["#ffb703", "#ff6a00", "#e63946"], "#e63946"),
    "dia_do_rock": T("DIA DO ROCK", "THIAGO FALCONE: 13 DE JULHO", ["#050005", "#3d0000", "#9a0f0f", "#ff3b1e"],
                     "#ffffff", "#3a0a0a", "#1c0505", "#080000", "#ffcc33", ("#4a1a14", "#2c0e0a", "#6b2a1c"),
                     "#ffffff", "#ff2a2a", "sparks", ["#ff3b1e", "#ffcc33"], "#ff2a2a"),
    "programador": T("DIA DO PROGRAMADOR", "THIAGO FALCONE: 256TH DAY", ["#000000", "#001a0a", "#003d14", "#00aa2e"],
                     "#b8ffcb", "#0a2a14", "#051a0a", "#000a04", "#00ff41", ("#0a2a14", "#051a0a", "#0f3a1c"),
                     "#00ff41", "#b8ffcb", "matrix", ["#00ff41", "#00aa2e"], "#00ff41"),
}


# ---------------------------------------------------------------- icones
# ---------------------------------------------------------------- ficha
# ---------------------------------------------------------------- citacao
def banner(name):
    """Banner: mundo de Hunter x Hunter (Arvore do Mundo, dirigivel, nuvens) com um Hunter correndo."""
    import sf
    t = TH[name]
    rnd = random.Random(name)
    W, H = 1056, 320
    p = min(8, 800 // (len(t["title"]) * 6 - 1))
    b = sf.scene(t, name)
    fx = t["fx"]
    if fx == "bats":
        b += bats(rnd, W, t["fxc"][0])
    elif fx == "snow":
        b += falling(rnd, 32, W, H, t["fxc"], [4, 8], dur=(6, 12))
    elif fx == "confetti":
        b += falling(rnd, 28, W, H, t["fxc"], [4, 8], dur=(5, 10), drift=60)
    elif fx == "sparks":
        b += falling(rnd, 16, W, H, t["fxc"], [4], rise=True, dur=(4, 9), drift=30)
    elif fx == "matrix":
        b += falling(rnd, 20, W, H, t["fxc"], [4], dur=(3, 7), drift=0, tall=28)
    sp = 4 if text_w(t["sub"], 4) <= 700 else 3
    ys = 44 + 7 * p + 22
    b += text(56, 44, t["title"], p, t["text"], "#000000")
    b += text(56, ys, t["sub"], sp, t["subc"], "#000000")
    b += text(56, ys + 7 * sp + 16, "DEVOPS / SECOPS / AWS / AI", 3, t["text"], "#000000")
    b += sf.akuma_group(790, 302, 3)
    return svg(W, H, b, 'role="img" aria-label="Banner"')


# ---------------------------------------------------------------- saida
def _write(name, content):
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def build_all(theme, today=None):
    import mapgen
    import sf
    _write(f"banner-{theme}.svg", banner(theme))
    _write("license.svg", sf.license_card())
    _write("map-goiania.svg", mapgen.map_svg(text, text_w, lambda w, h: sf.sf_frame(w, h, inner=False)))
    for n, lab in ((1, "FOCUS"), (2, "ACTIVITY"), (3, "STAGE SELECT")):
        _write(f"bar-{n}.svg", sf.section_bar(n, lab))
    _write("hook.svg", sf.banner_strip("hook"))
    _write("cta.svg", sf.banner_strip("cta"))
    _write("continue.svg", sf.continue_card())
    for f in glob.glob(os.path.join(ASSETS, "banner-*.svg")):
        if os.path.basename(f) != f"banner-{theme}.svg":
            os.remove(f)
    return {"banner": f"assets/banner-{theme}.svg", "footer": "", "quote": ""}


if __name__ == "__main__":
    import sys
    print(build_all(sys.argv[1] if len(sys.argv) > 1 else "fighter"))
