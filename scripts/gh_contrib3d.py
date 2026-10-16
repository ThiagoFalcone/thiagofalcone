"""Gera assets/contrib3d.svg: grafico 3D de barras com as contribuicoes publicas do ultimo ano.

Le a pagina publica https://github.com/users/<usuario>/contributions (sem token).
Uso: python scripts/gh_contrib3d.py [usuario]. Se a leitura falhar, o arquivo anterior e mantido.
"""
import math
import os
import re
import sys
import urllib.request
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets as B  # noqa: E402

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
LEVEL = ["#1d1b26", "#6b5a1e", "#a68628", "#d4af37", "#ffe27a"]


def fetch(user):
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    tips = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r"\s*([\d,]+)\s+contribution", m.group(2))
        tips[m.group(1)] = int(n.group(1).replace(",", "")) if n else 0
    days = []
    for m in re.finditer(r'<td[^>]*>', html):
        tag = m.group(0)
        d = re.search(r'data-date="([^"]+)"', tag)
        i = re.search(r'id="(contribution-day-component-(\d+)-(\d+))"', tag)
        lv = re.search(r'data-level="(\d)"', tag)
        if d and i and lv:
            days.append((int(i.group(3)), int(i.group(2)), d.group(1), int(lv.group(1)), tips.get(i.group(1), 0)))
    total = re.search(r"([\d,]+)\s+contributions\s+in\s+the\s+last\s+year", html)
    return days, int(total.group(1).replace(",", "")) if total else sum(d[4] for d in days)


def render(days, total):
    W, H = 1056, 312
    gold = "#c8a24a"
    cs, dx, dy = 18, 8, 9
    x0, yfront = 75, 262
    b = f'<rect width="{W}" height="{H}" fill="#0d0a14"/>'
    b += f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{gold}" stroke-width="8"/>'
    b += f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="#6b5420" stroke-width="4"/>'
    for cx, cy in ((0, 0), (W - 24, 0), (0, H - 24), (W - 24, H - 24)):
        b += f'<rect x="{cx}" y="{cy}" width="24" height="24" fill="{gold}"/><rect x="{cx + 8}" y="{cy + 8}" width="8" height="8" fill="#0d0a14"/>'
    b += B.text(48, 34, "CONTRIBUTIONS", 3, "#f2cf5b", "#000000")
    t = f"{total} IN THE LAST YEAR"
    b += B.text(W - 48 - B.text_w(t, 3), 34, t, 3, "#e8d5a3", "#000000")
    grid = {(c, r): (lv, n) for c, r, _, lv, n in days}
    cols = max(c for c, _ in grid) + 1
    for r in range(7):
        for c in range(cols):
            if (c, r) not in grid:
                continue
            lv, n = grid[(c, r)]
            h = 3 if n == 0 else min(120, 6 + 12 * math.sqrt(n))
            X = x0 + c * cs - (6 - r) * dx
            Y = yfront - (6 - r) * dy
            base = LEVEL[lv]
            top, front, side = B.mix(base, "#ffffff", 0.22), base, B.mix(base, "#000000", 0.42)
            yt = Y - h
            b += f'<polygon points="{X},{yt} {X + cs - 2},{yt} {X + cs - 2 - dx},{yt - dy} {X - dx},{yt - dy}" fill="{top}"/>'
            if h > 3:
                b += f'<rect x="{X}" y="{yt}" width="{cs - 2}" height="{h:.1f}" fill="{front}"/>'
                b += f'<polygon points="{X + cs - 2},{yt} {X + cs - 2 - dx},{yt - dy} {X + cs - 2 - dx},{Y - dy} {X + cs - 2},{Y}" fill="{side}"/>'
    seen = set()
    for c, r, d, lv, n in days:
        y, m, dd = (int(v) for v in d.split("-"))
        if r == 0 and dd <= 7 and m not in seen:
            seen.add(m)
            b += B.text(x0 + c * cs - 6 * dx, yfront + 14, MONTHS[m - 1], 2, "#8a7a4a")
    return B.svg(W, H, b, 'role="img" aria-label="3D contributions graph for the last year"')


def main():
    user = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER") or "thiagofalcone"
    try:
        days, total = fetch(user)
        if len(days) < 300:
            raise RuntimeError(f"so {len(days)} dias lidos")
    except Exception as e:
        print("contrib3d: falhou, mantendo arquivo anterior:", e)
        return
    os.makedirs(B.ASSETS, exist_ok=True)
    with open(os.path.join(B.ASSETS, "contrib3d.svg"), "w", encoding="utf-8", newline="\n") as f:
        f.write(render(days, total))
    print("contrib3d:", len(days), "dias,", total, "contribuicoes")


if __name__ == "__main__":
    main()
