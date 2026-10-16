"""Converte o JSON do Overpass (ruas de Goiania) em caminhos SVG simplificados: scripts/goiania_data.py.

Uso: python scripts/make_goiania_data.py roads.json
Dados: (c) OpenStreetMap contributors, ODbL.
"""
import json
import sys

LON0, LON1, LAT0, LAT1 = -49.32, -49.20, -16.7018, -16.6558
W, H = 1056, 420


def proj(lat, lon):
    return (lon - LON0) / (LON1 - LON0) * W, (LAT1 - lat) / (LAT1 - LAT0) * H


def dp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = (dx * dx + dy * dy) ** 0.5 or 1e-9
    idx, dmax = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            idx, dmax = i, d
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    groups = {"major": [], "secondary": [], "tertiary": []}
    for el in data["elements"]:
        if el.get("type") != "way" or "geometry" not in el:
            continue
        hw = el["tags"].get("highway", "")
        key = "major" if hw in ("motorway", "trunk", "primary") else "secondary" if hw == "secondary" else "tertiary"
        pts = dp([proj(p["lat"], p["lon"]) for p in el["geometry"]], 0.6)
        if len(pts) < 2:
            continue
        if all(x < -20 or x > W + 20 for x, _ in pts) or all(y < -20 or y > H + 20 for _, y in pts):
            continue
        groups[key].append("M" + "L".join(f"{x:.0f} {y:.0f}" if abs(x - round(x)) < .25 and abs(y - round(y)) < .25 else f"{x:.1f} {y:.1f}" for x, y in pts))
    out = '"""Ruas de Goiania (c) OpenStreetMap contributors, ODbL. Gerado por make_goiania_data.py."""\n'
    out += f"W, H = {W}, {H}\nBBOX = {(LAT0, LAT1, LON0, LON1)!r}\n"
    for k, v in groups.items():
        out += f"{k.upper()} = {''.join(v)!r}\n"
    open("scripts/goiania_data.py", "w", encoding="utf-8", newline="\n").write(out)
    print({k: len(v) for k, v in groups.items()}, len(out) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
