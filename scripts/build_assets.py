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
            f'shape-rendering="crispEdges" {extra}>{body}</svg>')


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


def castle(c0, ground_row, color, win, rnd):
    S, g = set(), ground_row - 1

    def rect(a, b, c, d):
        S.update((x, y) for x in range(a, c + 1) for y in range(b, d + 1))

    def roof(cx, base, hw):
        for i in range(hw):
            wd = hw - 1 - i
            S.update((x, base - i) for x in range(cx - wd, cx + wd + 1))

    rect(c0, g - 9, c0 + 23, g)
    S.update((c, g - 10) for c in range(c0, c0 + 24, 2))
    rect(c0 - 3, g - 15, c0 + 3, g)
    roof(c0, g - 16, 4)
    rect(c0 + 9, g - 20, c0 + 15, g)
    roof(c0 + 12, g - 21, 5)
    rect(c0 + 21, g - 14, c0 + 27, g)
    roof(c0 + 24, g - 15, 4)
    out = cells(S, color)
    # bandeira
    px = (c0 + 12) * 8 + 4
    top = (g - 26) * 8
    out += (f'<rect x="{px}" y="{top}" width="4" height="40" fill="{color}"/>'
            f'<rect x="{px + 4}" y="{top}" width="16" height="12" fill="{win}"><animate attributeName="width" values="16;24;16" dur="1.6s" repeatCount="indefinite"/></rect>')
    wins = [(c0 - 1, g - 9), (c0 + 1, g - 9), (c0 + 11, g - 14), (c0 + 13, g - 14), (c0 + 12, g - 6),
            (c0 + 5, g - 6), (c0 + 18, g - 6), (c0 + 23, g - 9), (c0 + 25, g - 9), (c0 + 11, g - 3)]
    for (c, r) in wins:
        d = rnd.uniform(1.2, 3)
        out += (f'<rect x="{c * 8}" y="{r * 8}" width="8" height="16" fill="{win}">'
                f'<animate attributeName="opacity" values="1;0.45;1;0.8;1" dur="{d:.1f}s" begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/></rect>')
    out += f'<rect x="{(c0 + 11) * 8}" y="{(g - 1) * 8}" width="24" height="24" fill="{win}" opacity="0.55"/>'
    return out


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
SKATER = [
    ".....kkkk.....", "...kkkkkkk....", "..kkkkkkkk....", ".kk.kkkkk.....", "k....kkkk.....",
    ".....kkkkkkk..", ".....kkkk..kk.", "....kkkkk...k.", "....kkkkkk....", ".....kkkkk....",
    "....kkk.kkk...", "...kkk...kkk..", "..kkk.....kk..", "..kk......kkk.", ".ssssssssssss.", "..ww......ww..",
]


def skater(x, y, s, deck, dur, delay, w, back=False):
    spr = sprite(SKATER, {"k": "#08050d", "s": deck, "w": "#d9d9d9"}, 0, 0, s)
    return (f'<g><animateTransform attributeName="transform" type="translate" values="{-20 * s},{y};{w + 20 * s},{y}" '
            f'dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>{spr}</g>')


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


DRACULA_TOWERS = [(0, 4, 9), (5, 3, 13), (9, 5, 11), (15, 6, 19), (23, 4, 14), (28, 5, 17), (34, 4, 10), (39, 4, 13)]


def dracula_castle(c0, ground_row, color, win, rnd):
    """Castelo do Dracula (Castlevania): muralha com ameias, torres com agulhas, torre do relogio e janelas goticas acesas."""
    base = ground_row - 1
    S, wins = set(), []
    for c in range(44):
        for r in range(base - 6, base + 1):
            S.add((c0 + c, r))
        if c % 2 == 0:
            S.add((c0 + c, base - 7))
        if c % 5 == 2:
            S.update({(c0 + c, base - 8), (c0 + c, base - 9)})
    for i, (xo, w, h) in enumerate(DRACULA_TOWERS):
        top = base - h + 1
        for c in range(xo, xo + w):
            for r in range(top, base + 1):
                S.add((c0 + c, r))
        for c in range(xo, xo + w, 2):
            S.add((c0 + c, top - 1))
        for k in range(w + 1):                                   # agulha cônica
            left, right = xo - 1 + (k + 1) // 2, xo + w - k // 2
            for c in range(left, right + 1):
                S.add((c0 + c, top - 2 - k))
        for j in range(5):                                       # ponta fina
            S.add((c0 + xo + w // 2, top - 2 - (w + 1) - j))
        if h >= 10:
            wins.append((c0 + xo + w // 2, top + 2, 1, 2))
        if h >= 15:
            wins.append((c0 + xo + w // 2, top + 7, 1, 2))
    big = DRACULA_TOWERS[3]                                      # salao principal: rosacea
    wins.append((c0 + big[0] + 2, base - big[2] + 11, 2, 2))
    clock = DRACULA_TOWERS[4]                                    # torre do relogio
    wins.append((c0 + clock[0] + 1, base - clock[2] + 4, 2, 2))
    for c in range(3, 42, 5):
        wins.append((c0 + c, base - 4, 1, 2))
    wins.append((c0 + 21, base - 1, 2, 2))                       # portao
    out = cells(S, color)
    for (c, r, w, h) in wins:
        d = rnd.uniform(1.4, 3.2)
        out += (f'<rect x="{c * 8}" y="{r * 8}" width="{w * 8}" height="{h * 8}" fill="{win}">'
                f'<animate attributeName="opacity" values="1;0.5;1;0.8;1" dur="{d:.1f}s" begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/></rect>')
    return out


def alucard_group(w, delay=0, scale=4, ground=316):
    """Alucard (sprite de referencia em scripts/alucard_data.py) andando: 4 quadros com balanco do corpo e passada das pernas/capa."""
    import alucard_data as D
    grid = []
    for row in D.ROWS:
        line = []
        for ch, n in re.findall(r"(.)\1*", row) and [(m.group(1), len(m.group(0))) for m in re.finditer(r"(.)\1*", row)]:
            line += [ch] * n
        grid.append(line)
    split = round(D.H * 0.56)                                 # quadril: abaixo daqui andam pernas e capa
    steps = [(0, 0), (1, -1), (0, 0), (-1, -1)]               # (deslocamento da parte de baixo, subida do corpo)
    frames = ""
    for k, (dx, bob) in enumerate(steps):
        by = {}
        for r, line in enumerate(grid):
            for c, ch in enumerate(line):
                if ch == ".":
                    continue
                cc = c + (dx if r >= split else 0)
                by.setdefault(ch, []).append((cc, r + bob))
        g = ""
        for ch, cs in by.items():
            rows = {}
            for c, r in cs:
                rows.setdefault(r, []).append(c)
            d = ""
            for r, cl in sorted(rows.items()):
                cl.sort()
                st = pv = cl[0]
                for c in cl[1:] + [None]:
                    if c is None or c != pv + 1:
                        d += f"M{st} {r}h{pv - st + 1}v1h-{pv - st + 1}z"
                        st = c
                    pv = c if c is not None else pv
            g += f'<path fill="{D.PALETTE[string.ascii_letters.index(ch)]}" d="{d}"/>'
        vals = ";".join("1" if j == k else "0" for j in range(4))
        frames += f'<g opacity="{1 if k == 0 else 0}">{g}<animate attributeName="opacity" values="{vals}" calcMode="discrete" dur="0.64s" repeatCount="indefinite"/></g>'
    top = ground - D.H * scale
    return (f'<g><animateTransform attributeName="transform" type="translate" values="-110,{top};{w + 110},{top}" dur="22s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<g transform="scale({scale})">{frames}</g></g>')


def chapel_background(W, H, cell=3):
    """Fundo: capela do Castlevania (imagem de referencia). A parede de pedra da esquerda e repetida com <use> (arquivo leve)."""
    import chapel_data as D

    def paths_of(rows):
        paths = {}
        for r, row in enumerate(rows):
            c = 0
            while c < len(row):
                ch, n = row[c], 1
                while c + n < len(row) and row[c + n] == ch:
                    n += 1
                paths.setdefault(ch, []).append(f"M{c} {r}h{n}v1h-{n}z")
                c += n
        return "".join(f'<path fill="{D.PALETTE[string.ascii_letters.index(ch)]}" d="{"".join(ds)}"/>' for ch, ds in paths.items())

    total, right, tw = W // cell, 9, 17
    left = total - D.W - right
    tile = paths_of([r[:tw] for r in D.ROWS])
    defs = (f'<defs><g id="wl">{tile}</g><g id="wm" transform="translate({tw},0) scale(-1,1)">{tile}</g></defs>')
    body = "".join(f'<use href="#{"wl" if k % 2 == 0 else "wm"}" x="{k * tw}"/>' for k in range(-(-left // tw)))
    body += f'<g transform="translate({left},0)">{paths_of(D.ROWS)}</g>'
    body += f'<g transform="translate({left + D.W},0)">{paths_of([r[-right:] for r in D.ROWS])}</g>'
    return f'{defs}<g transform="scale({cell})">{body}</g>'


def banner(name):
    t = TH[name]
    rnd = random.Random(name)
    W, H = 1056, 320
    p = min(8, 800 // (len(t["title"]) * 6 - 1))
    b = chapel_background(W, H)
    b += (f'<defs><linearGradient id="vg" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity="0.72"/>'
          f'<stop offset="0.5" stop-color="#000" stop-opacity="0.55"/><stop offset="0.66" stop-color="#000" stop-opacity="0"/></linearGradient></defs>'
          f'<rect width="{W}" height="{H}" fill="url(#vg)"/>'
          f'<rect width="{W}" height="{H}" fill="{t["sky"][1]}" opacity="0.16"/>')
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
    b += text(56, 44, t["title"], p, t["text"], "#000000")
    sp = 4 if text_w(t["sub"], 4) <= 700 else 3
    b += text(56, 44 + 7 * p + 22, t["sub"], sp, t["subc"], "#000000")
    b += alucard_group(W)
    return svg(W, H, b, 'role="img" aria-label="Banner"')


FLAME = {
    "r": ["...rr...", "..rrrr..", ".rrrrrr.", "rrrrrrrr", "rrrrrrrr", "rrrrrrrr", ".rrrrrr."],
    "o": ["...oo...", "..oooo..", ".oooooo.", ".oooooo.", "..oooo.."],
    "y": ["..yy..", ".yyyy.", ".yyyy.", "..yy.."],
}
FLAME_COL = {"r": "#d6361a", "o": "#ff8a1f", "y": "#ffe27a"}


def footer(name):
    """Fogueira (estilo Dark Souls): cenario escuro com ruinas, nevoa e chama animada."""
    t = TH[name]
    rnd = random.Random(name + "f")
    W, H, G = 1056, 220, 184
    cx, by = W // 2, G
    dark = ["#04030a", mix(t["sky"][1], "#000000", 0.55), mix(t["sky"][2], "#000000", 0.7)]
    b = sky(dark, 0, G, W, 10) + stars(rnd, 14, W, 90, "#ffffff")
    for px, hh in ((70, 120), (150, 80), (W - 150, 100), (W - 230, 70), (260, 54), (W - 330, 60)):
        top = G - hh
        b += f'<rect x="{px}" y="{top}" width="26" height="{hh}" fill="#0b0810"/><rect x="{px - 4}" y="{top}" width="34" height="8" fill="#14101c"/>'
        b += f'<rect x="{px + 4}" y="{top - 8}" width="8" height="8" fill="#0b0810"/>'
    b += f'<rect x="0" y="{G}" width="{W}" height="{H - G}" fill="#100c12"/><rect x="0" y="{G}" width="{W}" height="8" fill="#1d1722"/>'
    for _ in range(18):
        b += f'<rect x="{rnd.randrange(0, W, 8)}" y="{rnd.randrange(G + 14, H, 8)}" width="{rnd.choice([8, 16])}" height="8" fill="#1a141d"/>'
    b += (f'<circle cx="{cx}" cy="{G - 30}" r="150" fill="#ff7a1a" opacity="0.10"><animate attributeName="opacity" '
          f'values="0.06;0.2;0.08;0.18;0.06" dur="1.8s" repeatCount="indefinite"/></circle>'
          f'<circle cx="{cx}" cy="{G - 24}" r="70" fill="#ff5a14" opacity="0.14"/>')
    b += (f'<rect x="{cx - 3}" y="{by - 72}" width="6" height="62" fill="#b8c0ca"/><rect x="{cx - 1}" y="{by - 72}" width="2" height="62" fill="#eef3f8"/>'
          f'<rect x="{cx - 14}" y="{by - 78}" width="28" height="7" fill="#6f6f78"/><rect x="{cx - 4}" y="{by - 98}" width="8" height="20" fill="#5a3a1e"/>'
          f'<rect x="{cx - 6}" y="{by - 104}" width="12" height="7" fill="#8a8a94"/>')
    for key, rows in FLAME.items():
        w = len(rows[0]) * 8
        flame = sprite(rows, {key: FLAME_COL[key]}, -w // 2, -len(rows) * 8, 8)
        b += (f'<g transform="translate({cx},{by - 4})" shape-rendering="auto"><g><animateTransform attributeName="transform" type="scale" '
              f'values="1,1;1.07,1.18;0.95,0.9;1.04,1.1;1,1" dur="{0.9 + 0.2 * "ryo".index(key) if False else 0.8 + 0.15 * "roy".index(key):.2f}s" repeatCount="indefinite"/>{flame}</g></g>')
    for sx in range(-6, 7):
        b += f'<rect x="{cx + sx * 12 - 6}" y="{by - 2}" width="12" height="10" fill="{"#2c2831" if sx % 2 else "#3a3540"}"/>'
    b += fire(rnd, 16, cx - 60, cx + 60, by - 20, by - 170, ["#ff7a1a", "#ffb347", "#ffd23a"], [4, 4, 6], (3, 6))
    b += (f'<g opacity="0.07" shape-rendering="auto"><rect x="-200" y="{G - 50}" width="900" height="34" fill="#fff" rx="17">'
          f'<animateTransform attributeName="transform" type="translate" values="0,0;240,0;0,0" dur="22s" repeatCount="indefinite"/></rect>'
          f'<rect x="500" y="{G - 28}" width="800" height="28" fill="#fff" rx="14"><animateTransform attributeName="transform" type="translate" values="0,0;-260,0;0,0" dur="28s" repeatCount="indefinite"/></rect></g>')
    msg, sub = "BONFIRE LIT", "REST HERE, WANDERER"
    b += text((W - text_w(msg, 5)) // 2, 12, msg, 5, t["text"], "#000000")
    b += text((W - text_w(sub, 3)) // 2, 54, sub, 3, t["subc"], "#000000",
              attrs='><animate attributeName="opacity" values="1;1;0.35;1;1" keyTimes="0;0.4;0.6;0.8;1" dur="2.4s" repeatCount="indefinite"/')
    return svg(W, H, b, 'role="img" aria-label="Footer"')


# ---------------------------------------------------------------- icones
SPR = {
    "sword": (["..............ss", ".............sss", "............sss.", "...........sss..", "..........sss...",
               ".........sss....", "..h.....sss.....", "...h...sss......", "....h.sss.......", ".....hhs........",
               "....hhhh........", "...bhhh.........", "..bb.h..........", ".bb.............", "pb..............", "pp.............."],
              {"s": "#dfe8f2", "h": "#d4af37", "b": "#7a4a21", "p": "#f2cf5b"}),
    "guitar": (["..............kk", ".............kkk", "............kk..", "...........nn...", "..........nn....",
                ".........nn.....", "........nn......", "....bbbbnnb.....", "...bBBBBBbb.....", "..bBBBBBBBBb....",
                "..bBBpBBBBBb....", ".bBBBBBBBBBb....", ".bBBBBpBBBb.....", "..bBBBBBBBb.....", "...bbBBBbb......", ".....bbb........"],
               {"k": "#2a1a10", "n": "#d9b98a", "b": "#5a1608", "B": "#d9541a", "p": "#111111"}),
    "castle": (["................", "....k..kk..k....", "..k.kk.kk.kk.k..", "..kkkk.kk.kkkk..", "..kkkkkkkkkkkk..",
                "..kkwkkkkkkwkk..", "..kkkkkkkkkkkk..", "..kkkkkkkkkkkk..", "..kkkkkddkkkkk..", "..kkkwkddkwkkk..",
                "..kkkkkddkkkkk..", "..kkkkkddkkkkk.."],
               {"k": "#8b94a8", "w": "#ffb347", "d": "#2a2236"}),
    "chest": (["................", "................", "................", "....bbbbbbbb....", "...bBBBBBBBBb...",
               "..bBBBBBBBBBBb..", "..bbbbbbbbbbbb..", "..bGGGGGGGGGGb..", "..bBBBBggBBBBb..", "..bBBBBggBBBBb..",
               "..bBBBBBBBBBBb..", "..bbbbbbbbbbbb.."],
              {"b": "#4a2a12", "B": "#8a5a2a", "G": "#d4af37", "g": "#f2cf5b"}),
    "scroll": (["................", "..yyyyyyyyyyyy..", ".yYYYYYYYYYYYYy.", ".yY..........Yy.", "..yYtttttttttY..",
                "...YYYYYYYYYY...", "...YtttttttttY..", "...YYYYYYYYYY...", "...YtttttttY....", "...YYYYYYYYYY...",
                "..yYYYYYYYYYYy..", ".yYYYYYYYYYYYYy.", "..yyyyyyyyyyyy.."],
               {"y": "#a67c3d", "Y": "#e8d5a3", "t": "#5a3d1a"}),
}


def divider(name):
    t = TH[name]
    W, H = 1056, 40
    b = ""
    for i in range(14):
        for side in (0, 1):
            x = 96 + i * 26 if side == 0 else W - 96 - i * 26 - 8
            b += (f'<rect x="{x}" y="16" width="8" height="8" fill="#c8a24a" opacity="0.9">'
                  f'<animate attributeName="opacity" values="0.3;1;0.3" dur="2.4s" begin="{i * 0.12:.2f}s" repeatCount="indefinite"/></rect>')
    with open(os.path.join(ASSETS, "icon-sword.svg"), encoding="utf-8") as f:
        inner = re.sub(r"</?svg[^>]*>", "", f.read())
    b += f'<g transform="translate({W // 2 - 16},4) scale(0.0625)" shape-rendering="auto">{inner}</g>'
    return svg(W, H, b)


# ---------------------------------------------------------------- ficha
def fire(rnd, n, x0, x1, y0, y1, colors, sizes, dur):
    """Particulas que sobem (ou caem) e somem."""
    out = []
    for _ in range(n):
        x, d, sz = rnd.randrange(x0, x1), rnd.uniform(*dur), rnd.choice(sizes)
        dx, b = rnd.randint(-14, 14), f"-{rnd.uniform(0, d):.1f}s"
        out.append(f'<rect x="{x}" y="0" width="{sz}" height="{sz}" fill="{rnd.choice(colors)}" opacity="0" shape-rendering="auto">'
                   f'<animateTransform attributeName="transform" type="translate" values="0,{y0};{dx},{y1}" dur="{d:.1f}s" begin="{b}" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;0.9;0.7;0" dur="{d:.1f}s" begin="{b}" repeatCount="indefinite"/></rect>')
    return "".join(out)


def lich_scene(x, y, s=2.5):
    """Ainz Ooal Gown: pixel-art da imagem de referencia (scripts/ainz_data.py) com raios do orbe piscando."""
    import ainz_data as D
    paths = {}
    for ry, row in enumerate(D.ROWS):
        cx = 0
        for ch, n in re.findall(r"([.A-Za-z])(\d+)", row):
            n = int(n)
            if ch != ".":
                paths.setdefault(ch, []).append(f"M{cx} {ry}h{n}v1h-{n}z")
            cx += n
    grid = []
    for row in D.ROWS:
        line = []
        for ch, n in re.findall(r"([.A-Za-z])(\d+)", row):
            line += [ch] * int(n)
        grid.append(line)
    seen, stack = set(), [(cx, cy) for cy in range(D.H) for cx in range(D.W) if cx in (0, D.W - 1) or cy in (0, D.H - 1)]
    while stack:                                 # vazios ligados a borda = fora do personagem
        cx, cy = stack.pop()
        if (cx, cy) in seen or not (0 <= cx < D.W and 0 <= cy < D.H) or grid[cy][cx] != ".":
            continue
        seen.add((cx, cy))
        stack += [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
    inner = "".join(f"M{cx} {cy}h1v1h-1z" for cy in range(D.H) for cx in range(D.W)
                    if grid[cy][cx] == "." and (cx, cy) not in seen)
    inner_path = f'<path fill="#0a0a08" d="{inner}"/>'
    body = "".join(f'<path fill="{D.PALETTE[string.ascii_letters.index(ch)]}" d="{"".join(ds)}"/>' for ch, ds in paths.items())
    groups = [[], [], []]
    for lx, ly, ci in D.LIGHT:
        groups[(lx + ly) % 3].append(f'<rect x="{lx}" y="{ly}" width="1" height="1" fill="{D.PALETTE[ci]}"/>')
    flick = ""
    for i, g in enumerate(groups):
        flick += (f'<g>{"".join(g)}<animate attributeName="opacity" values="1;0.25;1;0.6;1" dur="{0.9 + i * 0.35:.2f}s" '
                  f'begin="-{i * 0.4:.1f}s" repeatCount="indefinite"/></g>')
    out = '<defs><clipPath id="pc"><rect x="0" y="0" width="280" height="320"/></clipPath></defs>'
    out += f'<g transform="translate({x},{y})" clip-path="url(#pc)"><rect width="280" height="320" fill="#0a0a08"/>'
    eyes = ""
    rnd = random.Random("buff")
    ease = 'calcMode="spline" keySplines="0.45 0 0.55 1;0.45 0 0.55 1"'
    out += f'<g><animate attributeName="opacity" values="0.55;1;0.55" keyTimes="0;0.5;1" {ease} dur="3.2s" repeatCount="indefinite"/>'
    for rx, ry, col, op in ((135, 160, "#7c3aed", 0.16), (105, 128, "#c084fc", 0.16), (72, 92, "#f2cf5b", 0.12)):
        out += f'<ellipse cx="140" cy="165" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}"/>'
    out += "</g>"
    for i, col in enumerate(("#c084fc", "#f2cf5b", "#7dd3fc")):
        out += (f'<g transform="translate(140 165)" shape-rendering="auto"><ellipse rx="40" ry="48" fill="none" stroke="{col}" stroke-width="3" '
                f'vector-effect="non-scaling-stroke" opacity="0">'
                f'<animateTransform attributeName="transform" type="scale" values="1;3.3" keyTimes="0;1" calcMode="spline" keySplines="0.2 0.6 0.4 1" dur="3.6s" begin="-{i * 1.2:.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0.7;0" keyTimes="0;0.2;1" dur="3.6s" begin="-{i * 1.2:.1f}s" repeatCount="indefinite"/></ellipse></g>')
    out += fire(rnd, 14, 8, 270, 320, -10, ["#f2cf5b", "#c084fc", "#7dd3fc"], [4, 4, 6], (4, 8))
    out += (f'<g transform="translate({(280 - D.W * s) / 2:g},8)"><g transform="scale({s})">{inner_path}{body}{flick}{eyes}</g></g>')
    return out + "</g>"


LESPAUL = [
    "......kkk......", ".....kkkkk.....", ".....kkkkk.....", "......nnn......", "......nnn......", "......nnn......",
    "......nnn......", "......nnn......", "......nnn......", "......nnn......", "...bbbbnbbbb...", "..bBBBBnBBBBb..",
    ".bBBBBpppBBBBb.", ".bBBBBBBBBBBBb.", "..bBBBBBBBBBb..", "..bBBBBBBBBBb..", ".bBBBBBBBBBBBb.", "bBBBBBpppBBBBBb",
    "bBBBBBBBBBBBBBb", "bBBBBBBBBBBBBBb", "bBBBBBBBBBBBBBb", ".bBBBBBBBBBBBb.", "..bBBBBBBBBBb..", "....bbbbbbb....",
]
def sheet():
    W, H = 1056, 400
    gold, bg, panel = "#c8a24a", "#0d0a14", "#1a1226"
    b = f'<rect width="{W}" height="{H}" fill="{bg}"/>'
    b += f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{gold}" stroke-width="8"/>'
    b += f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="#6b5420" stroke-width="4"/>'
    for cx, cy in ((0, 0), (W - 24, 0), (0, H - 24), (W - 24, H - 24)):
        b += f'<rect x="{cx}" y="{cy}" width="24" height="24" fill="{gold}"/><rect x="{cx + 8}" y="{cy + 8}" width="8" height="8" fill="{bg}"/>'
    b += lich_scene(44, 44)
    b += f'<rect x="44" y="44" width="280" height="320" fill="none" stroke="{gold}" stroke-width="4"/>'
    b += text(184 - text_w("LV 100", 3) // 2, 336, "LV 100", 3, gold, "#000000")
    x0 = 360
    b += text(x0, 52, "THIAGO FALCONE", 6, "#f2cf5b", "#000000")
    b += text(x0, 112, "CLASS: SOFTWARE ENGINEER", 3, "#e8d5a3")
    b += text(x0, 140, "GUILD: TECH LEADERSHIP", 3, "#e8d5a3")
    b += text(x0, 168, "ARMS: LES PAUL, SKATE, PC", 3, "#e8d5a3")
    stats = [("AI", 100, "#7c5cff"), ("CODE", 100, "#3ddc97"), ("CLOUD", 100, "#3a86ff"), ("LEAD", 100, "#ffb703"), ("ROCK", 100, "#ff2a2a")]
    y = 208
    for i, (lab, val, col) in enumerate(stats):
        b += text(x0, y + 1, lab, 3, "#ffffff")
        bx, bw = 480, 440
        b += f'<rect x="{bx}" y="{y}" width="{bw}" height="22" fill="#000000" stroke="#4a3a1a" stroke-width="3"/>'
        b += (f'<rect x="{bx}" y="{y}" width="0" height="22" fill="{col}"><animate attributeName="width" from="0" to="{bw * val // 100}" '
              f'dur="1.4s" begin="{i * 0.2:.1f}s" fill="freeze"/></rect>')
        for k in range(1, 20):
            b += f'<rect x="{bx + k * 22}" y="{y}" width="3" height="22" fill="#000000"/>'
        b += text(936, y + 1, str(val), 3, "#f2cf5b")
        y += 36
    return svg(W, H, b, 'role="img" aria-label="Character sheet"')


QUESTS = [
    ("guitar", "GUITAR", ["GIBSON LES PAUL", "SUNBURST", "SUSTAIN FOREVER"]),
    ("metal", "ROCK & METAL", ["OZZY OSBOURNE", "IRON MAIDEN", "DIO"]),
    ("fantasy", "DARK FANTASY", ["PATH OF EXILE", "DIABLO", "ELDEN RING", "DARK SOULS"]),
    ("fight", "FIGHTING", ["STREET FIGHTER", "HADOUKEN!"]),
    ("anime", "ANIME", ["DRAGON BALL", "AND PLENTY MORE"]),
    ("pc", "PC GAMING", ["WHERE ALL OF IT", "HAPPENS"]),
    ("skate", "SKATE", ["WHEELS DOWN", "VOLUME UP"]),
]


def _icon_inner(name):
    with open(os.path.join(ASSETS, f"q-{name}.svg"), encoding="utf-8") as f:
        raw = f.read()
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    return vb, re.sub(r"</?svg[^>]*>", "", raw)


def sidequests():
    """Quadro de missoes secundarias: cartoes com icone, titulo e lista (substitui a lista simples)."""
    W, CW, CH, GAP = 1056, 252, 206, 16
    gold = "#c8a24a"
    b = ""
    positions = [(i * (CW + GAP), 0) for i in range(4)]
    off = (W - 3 * CW - 2 * GAP) // 2
    positions += [(off + i * (CW + GAP), CH + GAP) for i in range(3)]
    for (key, title, lines), (x, y) in zip(QUESTS, positions):
        fav = key == "fantasy"
        b += f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="#120d1c"/>'
        stroke = f'<rect x="{x + 2}" y="{y + 2}" width="{CW - 4}" height="{CH - 4}" fill="none" stroke="{gold}" stroke-width="4"'
        if fav:
            b += stroke + '><animate attributeName="stroke" values="#c8a24a;#ffe08a;#c8a24a" dur="2.2s" repeatCount="indefinite"/></rect>'
            b += f'<rect x="{x + 2}" y="{y + 2}" width="{CW - 4}" height="{CH - 4}" fill="#7c3aed" opacity="0"><animate attributeName="opacity" values="0;0.12;0" dur="2.2s" repeatCount="indefinite"/></rect>'
        else:
            b += stroke + "/>"
        b += f'<rect x="{x + 10}" y="{y + 10}" width="{CW - 20}" height="{CH - 20}" fill="none" stroke="#4a3a1a" stroke-width="2"/>'
        for cx, cy in ((x, y), (x + CW - 12, y), (x, y + CH - 12), (x + CW - 12, y + CH - 12)):
            b += f'<rect x="{cx}" y="{cy}" width="12" height="12" fill="{gold}"/>'
        vb, inner = _icon_inner(key)
        b += f'<svg x="{x + CW // 2 - 28}" y="{y + 20}" width="56" height="56" viewBox="{vb}" shape-rendering="auto">{inner}</svg>'
        b += text(x + (CW - text_w(title, 3)) // 2, y + 90, title, 3, "#f2cf5b", "#000000")
        ly = y + 124
        for ln in lines:
            b += text(x + (CW - text_w(ln, 2)) // 2, ly, ln, 2, "#e8d5a3")
            ly += 18
        if fav:
            vb2, inner2 = _icon_inner("star")
            b += f'<svg x="{x + CW - 36}" y="{y + 18}" width="20" height="20" viewBox="{vb2}" shape-rendering="auto">{inner2}</svg>'
            b += text(x + 18, y + 20, "FAVORITE", 2, "#ffe08a")
    H = 2 * CH + GAP
    return svg(W, H, b, 'role="img" aria-label="Side quests: guitar, rock and metal, dark fantasy, fighting games, anime, PC gaming, skate"')


# ---------------------------------------------------------------- citacao
QUOTES = [
    ("UP THE IRONS!", "IRON MAIDEN BATTLE CRY"),
    ("RISE, TARNISHED.", "ELDEN RING (2022)"),
    ("PRAISE THE SUN!", "DARK SOULS (2011)"),
    ("STAY A WHILE AND LISTEN.", "DIABLO II (2000)"),
    ("HADOUKEN!", "RYU - STREET FIGHTER"),
    ("IT'S OVER 9000!", "VEGETA - DRAGON BALL Z"),
    ("TALK IS CHEAP. SHOW ME THE CODE.", "LINUS TORVALDS"),
    ("YOU DIED", "DARK SOULS"),
]


def _inside(x, y, poly):
    ins = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def _raster(poly, w=120, h=50):
    return {(c, r) for r in range(h) for c in range(w) if _inside(c + 0.5, r + 0.5, poly)}


def _line(x0, y0, x1, y1):
    cells, n = [], max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        t = i / n if n else 0
        cells.append((round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)))
    return cells


STRAT_BODY = [(57, 14), (62, 10), (70, 9), (78, 11), (84, 9), (92, 5), (102, 4), (109, 8), (112, 15), (113, 24), (112, 33), (109, 40),
              (102, 44), (92, 44), (84, 40), (78, 37), (70, 39), (62, 38), (57, 34), (63, 30), (64, 28), (64, 20), (63, 18)]
STRAT_GUARD = [(70, 15), (80, 13), (94, 12), (104, 15), (108, 22), (108, 30), (104, 36), (94, 38), (82, 38), (74, 34), (70, 28), (70, 20)]
STRAT_HEAD = [(22, 20), (18, 16), (10, 13), (3, 13), (0, 16), (1, 21), (5, 25), (12, 28), (22, 28)]
STRAT_NECK = [(22, 20), (72, 17), (72, 31), (22, 28)]
NOTE1 = ["...#....", "...##...", "...#.#..", "...#..#.", "...#....", "...#....", "...#....", ".###....", "#####...", "#####...", ".###...."]
NOTE2 = ["..########..", "..########..", "..#......#..", "..#......#..", "..#......#..", "..#......#..", "..#......#..",
         ".###....###.", "####...####.", "####...####.", ".###....###."]


def strat_group(rnd):
    """David Gilmour Signature Stratocaster (pixel-art da foto de referencia): cordas vibrando e notas subindo."""
    import strat_data as D
    paths = {}
    for ry, row in enumerate(D.ROWS):
        cx = 0
        for ch, n in re.findall(r"([.A-Za-z])(\d+)", row):
            n = int(n)
            if ch != ".":
                paths.setdefault(ch, []).append(f"M{cx} {ry}h{n}v1h-{n}z")
            cx += n
    g = "".join(f'<path fill="{D.PALETTE[string.ascii_letters.index(ch)]}" d="{"".join(ds)}"/>' for ch, ds in paths.items())
    f = D.W / 150.0                                       # coordenadas medidas na grade de 150 colunas
    for i in range(6):
        yb, yn = (18.55 + i * 1.66) * f, (18.7 + i * 1.18) * f
        x0, n = round(21 * f), round(100 * f)
        segs = "".join(f'<rect x="{x0 + k}" y="{round((yb + (yn - yb) * k / n) * 2) / 2 - 0.25:g}" width="1" height="0.5"/>' for k in range(n))
        dur = 0.13 + i * 0.017
        g += (f'<g fill="#e9edf2" opacity="0.95">{segs}<animateTransform attributeName="transform" type="translate" '
              f'values="0,0;0,-0.6;0,0;0,0.6;0,0" calcMode="discrete" dur="{dur:.3f}s" repeatCount="indefinite"/></g>')
    cols = ["#f2cf5b", "#c084fc", "#7dd3fc", "#ff8a5b", "#f2cf5b", "#c084fc", "#7dd3fc"]
    for i, c in enumerate(cols):
        sx, sy = (26 + (i * 7) % 26) * f, (6 + (i * 3) % 4) * f
        dx, dy = rnd.randint(-6, 18) * f, -rnd.randint(8, 12) * f
        d = 4.4 + (i % 3) * 0.8
        glyph = sprite(NOTE2 if i % 3 == 0 else NOTE1, {"#": c}, 0, 0, max(1, round(4 / (630 / D.W))))
        g += (f'<g opacity="0"><animateTransform attributeName="transform" type="translate" values="{sx:g},{sy:g};{sx + dx:g},{sy + dy:g}" '
              f'dur="{d:.1f}s" begin="-{i * 0.7:.1f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.7;1" dur="{d:.1f}s" begin="-{i * 0.7:.1f}s" repeatCount="indefinite"/>'
              f'<g><animateTransform attributeName="transform" type="translate" values="0,0;1,0;0,0;-1,0;0,0" calcMode="discrete" dur="1.2s" begin="-{i * 0.3:.1f}s" repeatCount="indefinite"/>{glyph}</g></g>')
    return f'<g transform="scale({630 / D.W:g})">{g}</g>'


def medieval_frame(W, H, rnd, inner=True, crest=True):
    """Moldura medieval: blocos de pedra, friso dourado, placas de ferro com rebites nos cantos e tochas animadas."""
    T = 28
    if inner:
        g = f'<rect width="{W}" height="{H}" fill="#17120f"/>'
    else:
        g = (f'<rect width="{W}" height="{T}" fill="#17120f"/><rect y="{H - T}" width="{W}" height="{T}" fill="#17120f"/>'
             f'<rect width="{T}" height="{H}" fill="#17120f"/><rect x="{W - T}" width="{T}" height="{H}" fill="#17120f"/>')
    tones = ["#4b413a", "#3f3631", "#574b43", "#362e2a", "#4a4038"]
    y, row = 0, 0
    while y < H:
        x = -(row % 2) * 22
        while x < W:
            bw = rnd.choice((34, 40, 48, 56))
            inside = x > T and x + bw < W - T and y > T and y + 14 < H - T
            if not inside:
                tone = rnd.choice(tones)
                g += (f'<rect x="{x + 1}" y="{y + 1}" width="{bw - 2}" height="12" fill="{tone}"/>'
                      f'<rect x="{x + 1}" y="{y + 1}" width="{bw - 2}" height="2" fill="#6a5d53" opacity="0.7"/>'
                      f'<rect x="{x + 1}" y="{y + 11}" width="{bw - 2}" height="2" fill="#1d1713" opacity="0.8"/>')
            x += bw
        y += 14
        row += 1
    g += f'<rect x="{T}" y="{T}" width="{W - 2 * T}" height="{H - 2 * T}" fill="{"#1d140d" if inner else "none"}" stroke="#c8a24a" stroke-width="4"/>'
    g += f'<rect x="{T + 8}" y="{T + 8}" width="{W - 2 * T - 16}" height="{H - 2 * T - 16}" fill="none" stroke="#5a4020" stroke-width="2"/>'
    for x in range(120, W - 100, 120):                      # rebites ao longo da pedra
        for yy in (11, H - 17):
            g += f'<rect x="{x}" y="{yy}" width="8" height="8" fill="#8a8f98"/><rect x="{x}" y="{yy}" width="3" height="3" fill="#d6d9de"/>'
    for yy in range(70, H - 60, 70):
        for xx in (10, W - 18):
            g += f'<rect x="{xx}" y="{yy}" width="8" height="8" fill="#8a8f98"/><rect x="{xx}" y="{yy}" width="3" height="3" fill="#d6d9de"/>'
    for cx, cy in ((0, 0), (W - 44, 0), (0, H - 44), (W - 44, H - 44)):   # placas de ferro nos cantos
        g += (f'<rect x="{cx}" y="{cy}" width="44" height="44" fill="#5b5d66" stroke="#26272c" stroke-width="3"/>'
              f'<rect x="{cx + 4}" y="{cy + 4}" width="36" height="36" fill="none" stroke="#c8a24a" stroke-width="2"/>'
              f'<rect x="{cx + 19}" y="{cy + 10}" width="6" height="24" fill="#c8a24a"/><rect x="{cx + 10}" y="{cy + 19}" width="24" height="6" fill="#c8a24a"/>')
        for ox, oy in ((7, 7), (33, 7), (7, 33), (33, 33)):
            g += f'<rect x="{cx + ox}" y="{cy + oy}" width="4" height="4" fill="#d6d9de"/>'
    if crest:
        with open(os.path.join(ASSETS, "icon-sword.svg"), encoding="utf-8") as f:   # brasao no topo
            sw = re.sub(r"</?svg[^>]*>", "", f.read())
        g += (f'<path d="M{W // 2 - 30} 0 h60 v26 l-30 22 l-30 -22 z" fill="#c8a24a" stroke="#6b5420" stroke-width="3"/>'
              f'<path d="M{W // 2 - 24} 4 h48 v20 l-24 17 l-24 -17 z" fill="#1d140d"/>'
              f'<g transform="translate({W // 2 - 16},6) scale(0.0625)" shape-rendering="auto">{sw}</g>')
    return g


def torch(x, y):
    fl = ""
    for key, rows in FLAME.items():
        w = len(rows[0]) * 3
        flame = sprite(rows, {key: FLAME_COL[key]}, -w // 2, -len(rows) * 3, 3)
        fl += (f'<g transform="translate({x + 12},{y + 22})" shape-rendering="auto"><g><animateTransform attributeName="transform" type="scale" '
               f'values="1,1;1.08,1.2;0.94,0.9;1.04,1.1;1,1" dur="{0.7 + 0.12 * "roy".index(key):.2f}s" repeatCount="indefinite"/>{flame}</g></g>')
    return (f'<circle cx="{x + 12}" cy="{y + 12}" r="26" fill="#ff7a1a" opacity="0.12"><animate attributeName="opacity" values="0.07;0.2;0.09;0.18;0.07" dur="1.6s" repeatCount="indefinite"/></circle>'
            f'<rect x="{x + 9}" y="{y + 28}" width="6" height="16" fill="#3a3a42"/><path d="M{x + 1} {y + 22} h22 l-4 8 h-14 z" fill="#4a4a52" stroke="#1d1d22" stroke-width="2"/>' + fl)


def quote(today):
    """Palco: moldura medieval com a Strato do Gilmour (cordas vibrando e notas subindo). Sem texto."""
    W, H = 1056, 264
    b = medieval_frame(W, H, random.Random("frame"))
    b += f'<g transform="translate({(W - 630) // 2},34)">{strat_group(random.Random("strat"))}</g>'
    b += torch(40, 36) + torch(W - 64, 36) + torch(40, H - 86) + torch(W - 64, H - 86)
    return svg(W, H, b, 'role="img" aria-label="David Gilmour Stratocaster on a medieval frame, strings vibrating and music notes rising"'), "stage.svg"


NOW_PLAYING = ["OZZY OSBOURNE: CRAZY TRAIN", "IRON MAIDEN: THE TROOPER", "DIO: HOLY DIVER", "PATH OF EXILE: WRAECLAST AWAITS",
               "ELDEN RING: RISE, TARNISHED", "DRAGON BALL: KAMEHAMEHA"]


def nowplaying():
    """Frase digitada em loop (substitui o readme-typing-svg): cada linha e escrita letra a letra, fica parada e apaga."""
    W, H = 1056, 70
    n = len(NOW_PLAYING)
    D = n * 4.6
    b = ""
    lab = "NOW PLAYING"
    b += text((W - text_w(lab, 2)) // 2, 4, lab, 2, "#8a7a4a")
    for i, line in enumerate(NOW_PLAYING):
        L = len(line.upper())
        w = text_w(line, 3)
        x0 = (W - w) // 2
        slot = 1 / n
        t0 = i * slot
        type_end = t0 + slot * 0.42
        hold_end = t0 + slot * 0.92
        pts = [(0.0, 0.0), (t0, 0.0)] if t0 > 0 else [(0.0, 0.0)]
        for k in range(1, L + 1):
            pts.append((t0 + (type_end - t0) * k / L, min(w, k * 18 - (3 if k == L else 0))))
        pts.append((hold_end, 0.0))
        if hold_end < 1.0:
            pts.append((1.0, 0.0))
        # remove tempos repetidos para manter keyTimes crescentes
        clean, last = [], -1.0
        for t, v in pts:
            t = round(t, 5)
            if t <= last:
                t = last + 0.00001
            clean.append((t, v))
            last = t
        clean[-1] = (1.0, clean[-1][1]) if clean[-1][0] >= 1.0 else clean[-1]
        if clean[-1][0] < 1.0:
            clean.append((1.0, 0.0))
        kt = ";".join(f"{t:.5f}" for t, _ in clean)
        wv = ";".join(f"{v:g}" for _, v in clean)
        xv = ";".join(f"{x0 + v:g}" for _, v in clean)
        b += (f'<defs><clipPath id="np{i}"><rect x="{x0 - 4}" y="14" width="0" height="40"><animate attributeName="width" values="{wv}" keyTimes="{kt}" '
              f'calcMode="discrete" dur="{D:g}s" repeatCount="indefinite"/></rect></clipPath></defs>')
        b += f'<g clip-path="url(#np{i})">{text(x0, 24, line, 3, "#f2cf5b", "#000000")}</g>'
        vis = f"0;0;1;1;0;0"
        b += (f'<rect x="{x0}" y="22" width="4" height="25" fill="#f2cf5b" opacity="0"><animate attributeName="x" values="{xv}" keyTimes="{kt}" calcMode="discrete" dur="{D:g}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{(t0 + slot * 0.01):.5f};1" calcMode="discrete" dur="{D:g}s" repeatCount="indefinite" begin="0s"/></rect>')
    return svg(W, H, b, 'role="img" aria-label="Now playing: Ozzy Osbourne, Iron Maiden, Dio, Path of Exile, Elden Ring, Dragon Ball"')


# ---------------------------------------------------------------- saida
def _write(name, content):
    os.makedirs(ASSETS, exist_ok=True)
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def build_all(theme, today=None):
    today = today or date.today()
    keep = {f"banner-{theme}.svg", f"footer-{theme}.svg"}
    _write(f"banner-{theme}.svg", banner(theme))
    _write(f"footer-{theme}.svg", footer(theme))
    q, qname = quote(today)
    _write(qname, q)
    keep.add(qname)
    _write("divider.svg", divider(theme))
    _write("sheet.svg", sheet())
    _write("nowplaying.svg", nowplaying())
    _write("sidequests.svg", sidequests())
    import mapgen
    _write("map-goiania.svg", mapgen.map_svg(text, text_w, lambda w, h: medieval_frame(w, h, random.Random("mapframe"), inner=False, crest=False)))
    for pat in ("banner-*.svg", "footer-*.svg", "quote-*.svg"):
        for f in glob.glob(os.path.join(ASSETS, pat)):
            if os.path.basename(f) not in keep:
                os.remove(f)
    return {"banner": f"assets/banner-{theme}.svg", "footer": f"assets/footer-{theme}.svg", "quote": f"assets/{qname}"}


if __name__ == "__main__":
    import sys
    print(build_all(sys.argv[1] if len(sys.argv) > 1 else "rock"))
