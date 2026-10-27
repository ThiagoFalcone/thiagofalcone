"""Mapa de Goiania em estilo de selecao de fase (Stage Select): ruas reais (OpenStreetMap) em azul e roxo, marcador vermelho na Praca Civica."""
import base64
import math
import os

import goiania_data as G

RED, BLUE, PURPLE = "#c01824", "#3b6fd1", "#4a2a8a"
Y0 = 80                                                         # faixa central recortada em make_goiania_png.py
H = 260


def _proj(lat, lon):
    lat0, lat1, lon0, lon1 = G.BBOX
    return (lon - lon0) / (lon1 - lon0) * G.W, (lat1 - lat) / (lat1 - lat0) * G.H - Y0


def _route(cx, cy):
    """Via principal que passa mais perto do centro: vira a rota tracejada."""
    best = None
    for seg in G.MAJOR.split("M")[1:]:
        pts = [(float(a), float(b) - Y0) for a, b in (p.split() for p in seg.split("L"))]
        if len(pts) < 6:
            continue
        d = min(math.hypot(x - cx, y - cy) for x, y in pts)
        length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
        score = d - length * 0.02
        if best is None or score < best[0]:
            best = (score, pts)
    return best[1]


def map_svg(text, text_w, frame):
    W = G.W
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "goiania_map.png"), "rb") as f:
        img = base64.b64encode(f.read()).decode()
    b = f'<image href="data:image/png;base64,{img}" width="{W}" height="{H}" image-rendering="pixelated" style="image-rendering:pixelated"/>'
    cx, cy = _proj(-16.6788, -49.2539)
    pts = _route(cx, cy)
    d = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    b += (f'<path d="{d}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="9 7" stroke-linecap="round" opacity="0.9">'
          f'<animate attributeName="stroke-dashoffset" from="0" to="-32" dur="1.6s" repeatCount="indefinite"/></path>')
    b += (f'<g shape-rendering="auto"><circle cx="{cx:.0f}" cy="{cy:.0f}" r="16" fill="none" stroke="{RED}" stroke-width="2">'
          f'<animate attributeName="r" values="10;38" dur="2.4s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/></circle>'
          f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="7" fill="{RED}" stroke="#ffffff" stroke-width="2"/></g>')
    lab = "PRAÇA CÍVICA"
    lw = text_w(lab, 2) + 20
    b += (f'<rect x="{cx - lw / 2:.0f}" y="{cy + 16:.0f}" width="{lw}" height="22" fill="#0b0612" stroke="{RED}" stroke-width="2"/>'
          + text(int(cx - lw / 2 + 10), int(cy + 21), lab, 2, "#ffffff"))
    tt = "STAGE SELECT"
    tw = text_w(tt, 4) + 60
    tx = (W - tw) // 2
    b += (f'<rect x="{tx}" y="30" width="{tw}" height="44" fill="{RED}" stroke="{BLUE}" stroke-width="3"/>'
          f'<rect x="{tx + 5}" y="35" width="{tw - 10}" height="34" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="1"/>')
    b += text(tx + 30, 40, tt, 4, "#ffffff", "#2a0a10")
    sub = "GOIÂNIA, BRASIL"
    b += text((W - text_w(sub, 3)) // 2, 84, sub, 3, "#fff7d6", "#000000")
    b += text(40, H - 54, "LAT 16.68 S, LON 49.25 W", 2, "#8fb4ff")
    cr = "MAP DATA: OPENSTREETMAP CONTRIBUTORS"
    b += text(W - 40 - text_w(cr, 2), H - 54, cr, 2, "#6a78b8")
    b += frame(W, H)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Stage select map of Goiânia, Goiás, Brazil">{b}</svg>')
