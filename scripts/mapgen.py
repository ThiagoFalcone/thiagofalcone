"""Mapa medieval de Goiania: pergaminho com as ruas reais (OpenStreetMap) a tinta, rosa dos ventos, castelo na Praca Civica."""
import base64
import math
import os
import re

import goiania_data as G

INK = "#3b2410"


def _proj(lat, lon):
    lat0, lat1, lon0, lon1 = G.BBOX
    return (lon - lon0) / (lon1 - lon0) * G.W, (lat1 - lat) / (lat1 - lat0) * G.H


def _route(cx, cy):
    """Via principal que passa mais perto do centro: vira a rota tracejada em vermelho."""
    best = None
    for seg in G.MAJOR.split("M")[1:]:
        pts = [tuple(float(v) for v in p.split()) for p in seg.split("L")]
        if len(pts) < 6:
            continue
        d = min(math.hypot(x - cx, y - cy) for x, y in pts)
        length = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
        score = d - length * 0.02
        if best is None or score < best[0]:
            best = (score, pts)
    return best[1]


def _castle_inner():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "..", "assets", "icon-castle.svg"), encoding="utf-8") as f:
        raw = f.read()
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    return vb, re.sub(r"</?svg[^>]*>", "", raw).replace("#c8a24a", INK)


def map_svg(text, text_w, frame):
    W, H = G.W, G.H
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "goiania_map.jpg"), "rb") as f:
        img = base64.b64encode(f.read()).decode()
    b = f'<image href="data:image/jpeg;base64,{img}" width="{W}" height="{H}"/>'
    cx, cy = _proj(-16.6788, -49.2539)
    # rota tracejada ate o castelo
    pts = _route(cx, cy)
    d = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    b += (f'<path d="{d}" fill="none" stroke="#a31621" stroke-width="3" stroke-dasharray="9 7" stroke-linecap="round" opacity="0.9">'
          f'<animate attributeName="stroke-dashoffset" from="0" to="-32" dur="1.4s" repeatCount="indefinite"/></path>')
    # castelo marcando a Praca Civica
    b += (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="14" fill="none" stroke="#a31621" stroke-width="2">'
          f'<animate attributeName="r" values="12;40" dur="2.4s" repeatCount="indefinite"/>'
          f'<animate attributeName="opacity" values="0.9;0" dur="2.4s" repeatCount="indefinite"/></circle>')
    vb, inner = _castle_inner()
    b += f'<g shape-rendering="auto"><ellipse cx="{cx:.0f}" cy="{cy + 20:.0f}" rx="22" ry="5" fill="#000" opacity="0.25"/>'
    b += f'<svg x="{cx - 24:.0f}" y="{cy - 28:.0f}" width="48" height="48" viewBox="{vb}">{inner}</svg></g>'
    lab = "PRAÇA CÍVICA"
    lw = text_w(lab, 2) + 20
    b += (f'<rect x="{cx - lw / 2:.0f}" y="{cy + 26:.0f}" width="{lw}" height="22" fill="#e9d7a8" stroke="{INK}" stroke-width="2"/>'
          + text(int(cx - lw / 2 + 10), int(cy + 31), lab, 2, INK))
    # titulo em fita
    tw = text_w("REINO DE GOIÁS", 4) + 70
    tx = (W - tw) // 2
    b += (f'<polygon points="{tx - 34},{44} {tx + 6},{44} {tx + 6},{86} {tx - 34},{86} {tx - 20},{65}" fill="#5a1620" stroke="#c8a24a" stroke-width="2"/>'
          f'<polygon points="{tx + tw + 34},{44} {tx + tw - 6},{44} {tx + tw - 6},{86} {tx + tw + 34},{86} {tx + tw + 20},{65}" fill="#5a1620" stroke="#c8a24a" stroke-width="2"/>'
          f'<rect x="{tx}" y="36" width="{tw}" height="46" fill="#7a1f2a" stroke="#c8a24a" stroke-width="3"/>'
          f'<rect x="{tx + 5}" y="41" width="{tw - 10}" height="36" fill="none" stroke="#c8a24a" stroke-width="1"/>')
    b += text(tx + 35, 46, "REINO DE GOIÁS", 4, "#f6e7b8", "#2a0a10")
    # rosa dos ventos
    rx, ry, r = 150, 306, 50
    star = ""
    for k in range(8):
        ang = math.radians(k * 45 - 90)
        long_ = r if k % 2 == 0 else r * 0.62
        a1, a2 = ang - math.radians(11), ang + math.radians(11)
        pts = f"{rx},{ry} {rx + math.cos(a1) * r * 0.22:.1f},{ry + math.sin(a1) * r * 0.22:.1f} {rx + math.cos(ang) * long_:.1f},{ry + math.sin(ang) * long_:.1f} {rx + math.cos(a2) * r * 0.22:.1f},{ry + math.sin(a2) * r * 0.22:.1f}"
        col = "#a31621" if k == 0 else INK
        star += f'<polygon points="{pts}" fill="{col}" stroke="{INK}" stroke-width="1"/>'
    b += (f'<g shape-rendering="auto"><circle cx="{rx}" cy="{ry}" r="{r + 8}" fill="#e9d7a8" opacity="0.55" stroke="{INK}" stroke-width="2"/>'
          f'<circle cx="{rx}" cy="{ry}" r="{r - 6}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>'
          f'<g><animateTransform attributeName="transform" type="rotate" values="0 {rx} {ry};4 {rx} {ry};0 {rx} {ry};-4 {rx} {ry};0 {rx} {ry}" dur="6s" repeatCount="indefinite"/>{star}</g></g>')
    for lbl, ox, oy in (("N", -6, -r - 30), ("S", -6, r + 18), ("E", r + 18, -8), ("W", -r - 32, -8)):
        b += text(rx + ox, ry + oy, lbl, 3, INK)
    # legenda
    lx, ly = W - 300, 290
    b += f'<rect x="{lx}" y="{ly}" width="252" height="80" fill="#e9d7a8" opacity="0.8" stroke="{INK}" stroke-width="2"/>'
    for i, (lab, w) in enumerate((("ESTRADA REAL", 3.4), ("CAMINHO", 2.0), ("TRILHA", 1.0))):
        yy = ly + 14 + i * 22
        b += f'<line x1="{lx + 12}" y1="{yy + 6}" x2="{lx + 60}" y2="{yy + 6}" stroke="{INK}" stroke-width="{w}"/>' + text(lx + 72, yy, lab, 2, INK)
    # dragoes, coordenadas e credito
    b += text(W - 56 - text_w("AQUI HÁ DRAGÕES", 3), 100, "AQUI HÁ DRAGÕES", 3, "#6b4a2a", None, 'opacity="0.75"')
    b += text(52, 100, "LAT 16.68 S, LON 49.25 W", 2, "#6b4a2a", None, 'opacity="0.8"')
    cr = "DADOS: OPENSTREETMAP CONTRIBUTORS"
    b += text((W - text_w(cr, 2)) // 2, H - 54, cr, 2, "#6b4a2a", None, 'opacity="0.8"')
    b += frame(W, H)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Medieval map of Goiânia, Goiás, Brazil">{b}</svg>')
