"""Street Fighter em pixel-art: palco do banner, Akuma com aura e cartao de personagem (Character Select).

Usa os helpers de build_assets e o sprite de scripts/akuma_data.py (convertido da foto de referencia).
"""
import random
import re
import string

import build_assets as B


def _akuma_grid():
    import akuma_data as D
    grid = []
    for row in D.ROWS:
        line = []
        for ch, n in re.findall(r"([.A-Za-z])(\d+)", row):
            line += [ch] * int(n)
        grid.append(line)
    H, W = len(grid), len(grid[0])

    def light(ch):
        hx = D.PALETTE[string.ascii_letters.index(ch)]
        r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
        return (r + g + b) / 3 > 170 and max(r, g, b) - min(r, g, b) < 60

    for _ in range(2):                                           # duas passadas: some com o halo claro da foto
        drop = []
        for y in range(H):
            for x in range(W):
                if grid[y][x] != "." and light(grid[y][x]):
                    near = [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
                    if any(not (0 <= ny < H and 0 <= nx < W) or grid[ny][nx] == "." for ny, nx in near):
                        drop.append((y, x))
        for y, x in drop:
            grid[y][x] = "."
    return D, grid


def _akuma_paths():
    D, grid = _akuma_grid()
    paths = {}
    for ry, line in enumerate(grid):
        cx = 0
        while cx < len(line):
            ch, n = line[cx], 1
            while cx + n < len(line) and line[cx + n] == ch:
                n += 1
            if ch != ".":
                paths.setdefault(ch, []).append(f"M{cx} {ry}h{n}v1h-{n}z")
            cx += n
    body = "".join(f'<path fill="{D.PALETTE[string.ascii_letters.index(ch)]}" d="{"".join(ds)}"/>' for ch, ds in paths.items())
    return D, body


def _kanji_cells(D):
    """Celulas vermelhas do logo (kanji) nas costas: vermelho forte no centro da parte alta do corpo (fracoes da grade)."""
    _, grid = _akuma_grid()
    H, W = len(grid), len(grid[0])
    ya, yb, xa, xb = int(15 * H / 83), int(30 * H / 83) + 1, int(12 * W / 52), int(40 * W / 52) + 1
    red = set()
    for i, hx in enumerate(D.PALETTE):
        r, g, b = int(hx[1:3], 16), int(hx[3:5], 16), int(hx[5:7], 16)
        if r > 150 and g < 70 and b < 70 and r - g > 100:
            red.add(i)
    return {(x, y) for y, line in enumerate(grid) for x, ch in enumerate(line)
            if ch != "." and string.ascii_letters.index(ch) in red and ya <= y <= yb and xa <= x <= xb}


def fireflies(rnd, n, x0, x1, y0, y1):
    """Vaga-lumes saindo do kanji: pontos de luz que flutuam em curvas suaves, piscam e somem."""
    out = ""
    for _ in range(n):
        sx, sy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        pts = [(sx, sy)]
        for _ in range(5):
            px, py = pts[-1]
            pts.append((px + rnd.uniform(-20, 20), py - rnd.uniform(9, 22)))
        d = rnd.uniform(5.5, 9)
        vals = ";".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        spl = ";".join(["0.4 0 0.6 1"] * (len(pts) - 1))
        blink = "0;0.9;0.3;1;0.35;0.95;0"
        out += (f'<g opacity="0"><animateTransform attributeName="transform" type="translate" values="{vals}" calcMode="spline" keySplines="{spl}" '
                f'dur="{d:.1f}s" begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="{blink}" dur="{d:.1f}s" begin="-{rnd.uniform(0, d):.1f}s" repeatCount="indefinite"/>'
                f'<circle r="9" fill="url(#ffg)"/><circle r="1.8" fill="#ffd9cf"/></g>')
    return out


def akuma_group(x, ground, scale=3):
    """Akuma de costas na entrada: aura roxa que respira e o logo 天 queimando com brilho suave. O corpo fica parado (sem tremer)."""
    D, body = _akuma_paths()
    w, h = D.W * scale, D.H * scale
    top = ground - h + 6
    rnd = random.Random("akuma")
    cx, cy = x + w / 2, top + h * 0.55
    spl = 'calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"'
    g = ('<defs><radialGradient id="aura"><stop offset="0" stop-color="#c02840" stop-opacity="0.55"/><stop offset="0.6" stop-color="#a01830" stop-opacity="0.22"/>'
         '<stop offset="1" stop-color="#a01830" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="kglow"><stop offset="0" stop-color="#ff1f1f" stop-opacity="0.85"/><stop offset="0.55" stop-color="#e01414" stop-opacity="0.35"/>'
         '<stop offset="1" stop-color="#c00a0a" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="ffg"><stop offset="0" stop-color="#ff4a3a" stop-opacity="0.95"/><stop offset="0.4" stop-color="#ff2a1a" stop-opacity="0.4"/>'
         '<stop offset="1" stop-color="#ff1f1f" stop-opacity="0"/></radialGradient></defs>')
    g += (f'<g shape-rendering="auto"><ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{w * 1.15:.0f}" ry="{h * 0.7:.0f}" fill="url(#aura)" opacity="0.7">'
          f'<animate attributeName="opacity" values="0.45;0.9;0.45" keyTimes="0;0.5;1" {spl} dur="3.2s" repeatCount="indefinite"/></ellipse></g>')
    g += f'<g transform="translate({x},{top}) scale({scale})">{body}</g>'
    K = _kanji_cells(D)
    if K:
        xs = [c for c, _ in K]
        ys = [r for _, r in K]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        mx, my = x + (x0 + x1 + 1) / 2 * scale, top + (y0 + y1 + 1) / 2 * scale
        g += (f'<g shape-rendering="auto"><ellipse cx="{mx:.0f}" cy="{my:.0f}" rx="{(x1 - x0 + 9) * scale * 0.75:.0f}" ry="{(y1 - y0 + 9) * scale * 0.65:.0f}" fill="url(#kglow)" opacity="0.5">'
              f'<animate attributeName="opacity" values="0.35;0.9;0.5;1;0.4;0.35" keyTimes="0;0.22;0.4;0.63;0.8;1" dur="1.3s" repeatCount="indefinite"/></ellipse></g>')
        Ks = sorted(K)

        def rects(cs, dy=0):
            return "".join(f'<rect x="{c}" y="{r + dy}" width="1" height="1"/>' for c, r in cs)

        red = [c for c in Ks]
        hot = [c for c in Ks if (c[0] * 2 + c[1] * 3) % 3 == 0]
        irregular = 'keyTimes="0;0.22;0.4;0.63;0.8;1" values="{v}"'
        base = (f'<g fill="#ff2412" opacity="0.4">{rects(red)}<animate attributeName="opacity" keyTimes="0;0.22;0.4;0.63;0.8;1" '
                f'values="0.35;0.95;0.5;1;0.6;0.35" dur="1.3s" repeatCount="indefinite"/></g>'
                f'<g fill="#ff8a24" opacity="0">{rects(hot)}<animate attributeName="opacity" keyTimes="0;0.3;0.5;0.75;1" '
                f'values="0;0.9;0.25;0.8;0" dur="0.9s" repeatCount="indefinite"/></g>')
        tongues = ""
        occupied = set(Ks)
        for gi in range(6):                                      # linguas de fogo subindo dos tracos (grupos defasados)
            cs = [c for c in Ks if (c[0] * 3 + c[1] * 5) % 6 == gi and (c[0], c[1] - 1) not in occupied]
            if not cs:
                continue
            d = 0.8 + gi * 0.11
            tongues += (f'<g><g fill="#ff7a1a">{rects(cs, -1)}</g><g fill="#ffc93a">{rects(cs, -2)}</g>'
                        f'<animateTransform attributeName="transform" type="translate" values="0,0.6;0,-1.4" keyTimes="0;1" dur="{d:.2f}s" begin="-{gi * 0.17:.2f}s" repeatCount="indefinite"/>'
                        f'<animate attributeName="opacity" values="0;0.95;0.85;0" keyTimes="0;0.2;0.6;1" dur="{d:.2f}s" begin="-{gi * 0.17:.2f}s" repeatCount="indefinite"/></g>')
        g += f'<g transform="translate({x},{top}) scale({scale})">{base}{tongues}</g>'
        g += f'<g shape-rendering="auto">{fireflies(rnd, 8, x + x0 * scale, x + (x1 + 1) * scale, top + y0 * scale, top + (y1 + 1) * scale)}</g>'
    return g


def scene(t, name, W=1056, H=320, G=256):
    """Fundo: cenario do Street Fighter III (scripts/stage.png, 352x107 convertido da imagem de referencia) ampliado em pixels."""
    import base64
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stage.png"), "rb") as f:
        png = base64.b64encode(f.read()).decode()
    b = (f'<image href="data:image/png;base64,{png}" width="{W}" height="{H}" preserveAspectRatio="none" '
         f'image-rendering="pixelated" style="image-rendering:crisp-edges;image-rendering:pixelated"/>')
    b += ('<defs><linearGradient id="vg" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity="0.7"/>'
          '<stop offset="0.45" stop-color="#000" stop-opacity="0.45"/><stop offset="0.62" stop-color="#000" stop-opacity="0"/></linearGradient></defs>'
          f'<rect width="{W}" height="{H}" fill="url(#vg)"/>')
    if name != "fighter":                                      # ocasioes: tinge o cenario com a cor do tema
        b += f'<rect width="{W}" height="{H}" fill="{t["sky"][1]}" opacity="0.2"/>'
    return b


def _portrait_block(x, y, s):
    D, body = _akuma_paths()
    return f'<g transform="translate({x},{y}) scale({s})">{body}</g>', D.W * s, D.H * s


def license_card():
    """Cartao de personagem estilo Character Select: retrato do Akuma, dados e barras (Dev, DevOps, SecOps, Cloud, AI, Business)."""
    W, H = 1056, 360
    gold = BLUE
    b = ('<defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1430"/><stop offset="1" stop-color="#0b0612"/></linearGradient>'
         '<radialGradient id="ag" cx="0.5" cy="0.55" r="0.7"><stop offset="0" stop-color="#a01830" stop-opacity="0.55"/><stop offset="1" stop-color="#a01830" stop-opacity="0"/></radialGradient></defs>'
         f'<rect width="{W}" height="{H}" fill="url(#lg)"/>'
         f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{gold}" stroke-width="8"/>'
         f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="#243a82" stroke-width="3"/>')
    for cx, cy in ((0, 0), (W - 24, 0), (0, H - 24), (W - 24, H - 24)):
        b += f'<rect x="{cx}" y="{cy}" width="24" height="24" fill="#c01824"/><rect x="{cx + 8}" y="{cy + 8}" width="8" height="8" fill="#0b0612"/>'
    b += B.text(48, 38, "CHARACTER SELECT", 4, "#ffffff", "#1a0b3a")
    b += B.text(W - 48 - B.text_w("1P", 4), 38, "1P", 4, "#ff5a4d", "#000000")
    fx, fy, fw, fh = 48, 80, 190, 260
    b += f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="#12081f" stroke="{gold}" stroke-width="4"/><rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="url(#ag)"/>'
    spr, sw, sh = _portrait_block(0, 0, 3)
    b += f'<g transform="translate({fx + (fw - sw) // 2},{fy + (fh - sh) // 2 + 2})">{spr}</g>'
    x0 = 276
    for i, (lab, val) in enumerate((("NAME", "THIAGO FALCONE"), ("CLASS", "SOFTWARE ENGINEER & ENTREPRENEUR"), ("BASE", "GOIANIA, BRASIL"))):
        y = 84 + i * 34
        b += B.text(x0, y, lab, 3, "#8fb4ff") + B.text(x0 + 110, y, val, 3, "#fff7d6")
    stats = [("DEV", "#3b6fd1"), ("DEVOPS", "#3a9ad9"), ("SECOPS", "#c01824"), ("CLOUD", "#5fa8ff"), ("AI", "#a85a32"), ("BUSINESS", "#e0a040")]
    for i, (lab, col) in enumerate(stats):
        colx = x0 + (i // 3) * 372
        y = 220 + (i % 3) * 38
        b += B.text(colx, y + 1, lab, 3, "#ffffff")
        bx, bw = colx + 156, 176
        b += f'<rect x="{bx}" y="{y}" width="{bw}" height="20" fill="#06030c" stroke="#243a82" stroke-width="3"/>'
        b += (f'<rect x="{bx}" y="{y}" width="0" height="20" fill="{col}"><animate attributeName="width" from="0" to="{bw}" dur="1.2s" '
              f'begin="{i * 0.15:.2f}s" fill="freeze"/></rect>')
        for k in range(1, 10):
            b += f'<rect x="{bx + k * 19}" y="{y}" width="2" height="20" fill="#06030c"/>'
    return B.svg(W, H, b, 'role="img" aria-label="Character select card: Thiago Falcone, software engineer and entrepreneur focused on DevOps, SecOps, cloud and AI"')


# ---------------------------------------------------------------- interface Street Fighter ate o rodape
BLUE, PURPLE, RED = "#3b6fd1", "#243a82", "#c01824"
GOLD = BLUE


def sf_frame(W, H, inner=True):
    """Moldura de arcade: borda dourada dupla com quinas, no mesmo estilo do cartao de personagem."""
    b = f'<rect width="{W}" height="{H}" fill="#0b0612"/>' if inner else ""
    b += (f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{GOLD}" stroke-width="8"/>'
          f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="{PURPLE}" stroke-width="3"/>')
    for cx, cy in ((0, 0), (W - 24, 0), (0, H - 24), (W - 24, H - 24)):
        b += f'<rect x="{cx}" y="{cy}" width="24" height="24" fill="{RED}"/><rect x="{cx + 8}" y="{cy + 8}" width="8" height="8" fill="#0b0612"/>'
    return b


def section_bar(n, label):
    """Titulo de secao no estilo SF: etiqueta ROUND n, nome e barra de vida amarela para vermelha."""
    W, H = 1056, 56
    uid = f"lb{n}"
    b = (f'<defs><linearGradient id="{uid}" x1="0" x2="1"><stop offset="0" stop-color="#5f93ff"/><stop offset="0.5" stop-color="#b06a8a"/>'
         f'<stop offset="1" stop-color="#e02a3a"/></linearGradient></defs>'
         f'<rect width="{W}" height="{H}" fill="#0b0612"/>'
         f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="none" stroke="{GOLD}" stroke-width="4"/>'
         f'<rect x="12" y="10" width="164" height="36" fill="{RED}"/>')
    b += B.text(26, 19, f"ROUND {n}", 3, "#ffffff")
    b += B.text(200, 14, label, 4, "#fff7d6", "#000000")
    bx, bw = 640, 336
    b += f'<rect x="{bx}" y="18" width="{bw}" height="20" fill="#06030c" stroke="{PURPLE}" stroke-width="3"/>'
    b += f'<rect x="{bx}" y="18" width="{bw}" height="20" fill="url(#{uid})"/>'
    for k in range(1, 12):
        b += f'<rect x="{bx + k * 28}" y="18" width="2" height="20" fill="#06030c"/>'
    b += B.text(W - 62, 19, "KO", 3, "#ff5a4d", "#000000")
    return B.svg(W, H, b, f'role="img" aria-label="Round {n}: {label.title()}"')


DOTS = {
    "0": [".XXXX.", "X....X", "X...XX", "X..X.X", "X.X..X", "XX...X", "X....X", ".XXXX."],
    "1": ["...XX.", "..XXX.", ".X.XX.", "...XX.", "...XX.", "...XX.", "...XX.", "XXXXXX"],
    "2": [".XXXX.", "X....X", ".....X", "....X.", "...X..", "..X...", ".X....", "XXXXXX"],
    "3": [".XXXX.", "X....X", ".....X", "..XXX.", ".....X", ".....X", "X....X", ".XXXX."],
    "4": ["....X.", "...XX.", "..XXX.", ".X.XX.", "X..XX.", "XXXXXX", "...XX.", "...XX."],
    "5": ["XXXXXX", "X.....", "X.....", "XXXXX.", ".....X", ".....X", "X....X", ".XXXX."],
    "6": [".XXXX.", "X.....", "X.....", "XXXXX.", "X....X", "X....X", "X....X", ".XXXX."],
    "7": ["XXXXXX", ".....X", "....X.", "...X..", "..X...", "..X...", "..X...", "..X..."],
    "8": [".XXXX.", "X....X", "X....X", ".XXXX.", "X....X", "X....X", "X....X", ".XXXX."],
    "9": [".XXXX.", "X....X", "X....X", ".XXXXX", ".....X", ".....X", "X....X", ".XXXX."],
}


def _dot(cx, cy, lit):
    """Bolinha octogonal da contagem: acesa (amarela) ou apagada (vermelho escuro), com bisel."""
    edge, face, hi = ("#c88a00", "#ffe814", "#fff6a0") if lit else ("#2a0505", "#4d0f0f", "#6e1b1b")
    def octa(r):
        k = r * 5 / 12
        return f"{cx - k:.1f},{cy - r} {cx + k:.1f},{cy - r} {cx + r},{cy - k:.1f} {cx + r},{cy + k:.1f} {cx + k:.1f},{cy + r} {cx - k:.1f},{cy + r} {cx - r},{cy + k:.1f} {cx - r},{cy - k:.1f}"
    return (f'<polygon points="{octa(13)}" fill="{edge}"/><polygon points="{octa(10)}" fill="{face}"/>'
            f'<rect x="{cx - 6}" y="{cy - 8}" width="6" height="4" fill="{hi}"/>')


def continue_card():
    """Rodape: tela CONTINUE? do Street Fighter II com a contagem de 9 a 0 em matriz de bolinhas (o Akuma nao participa; falta o elenco)."""
    W, H = 1056, 356
    b = f'<rect width="{W}" height="{H}" fill="#000000"/>'
    b += ('<defs><linearGradient id="cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7be860"/><stop offset="0.5" stop-color="#ffe14a"/>'
          '<stop offset="1" stop-color="#ff5a3a"/></linearGradient>'
          '<radialGradient id="kc"><stop offset="0" stop-color="#ff1f1f" stop-opacity="0.8"/><stop offset="1" stop-color="#c00a0a" stop-opacity="0"/></radialGradient></defs>')
    b += B.text(48, 40, "CONTINUE?", 5, "url(#cg)", "#1a0b00")
    for k in range(10):                                              # numero ao lado do titulo, em sincronia (sombra junto, no mesmo grupo)
        digit = str(9 - k)
        seq = ";".join("1" if j == k else "0" for j in range(11))
        num = B.text(48 + B.text_w("CONTINUE?", 5) + 36, 40, digit, 5, "url(#cg)", "#1a0b00")
        b += (f'<g opacity="{1 if k == 0 else 0}">{num}<animate attributeName="opacity" values="{seq}" calcMode="discrete" dur="11s" repeatCount="indefinite"/></g>')
    # retratos dos personagens do SF2 (um por numero da contagem), sem o Akuma
    from portraits_data import PORTRAITS
    sc, px0, py0 = 3, 230, 92
    for k, (name, pw, ph, rows) in enumerate(PORTRAITS):
        seq = ";".join("1" if j == k else "0" for j in range(11))
        rects = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="{c}"/>' for y, row in enumerate(rows) for x, w, c in row)
        b += (f'<g opacity="{1 if k == 0 else 0}"><g transform="translate({px0},{py0}) scale({sc})" shape-rendering="crispEdges">{rects}</g>'
              f'<animate attributeName="opacity" values="{seq}" calcMode="discrete" dur="11s" repeatCount="indefinite"/></g>')
    # matriz de bolinhas com a contagem
    x0, y0, pitch = 560, 80, 31
    b += '<g shape-rendering="auto">'
    for r in range(8):
        for c in range(6):
            b += _dot(x0 + c * pitch + 15, y0 + r * pitch + 15, False)
    for k in range(10):
        digit = str(9 - k)
        seq = ";".join("1" if j == k else "0" for j in range(11))
        lit = "".join(_dot(x0 + c * pitch + 15, y0 + r * pitch + 15, True) for r, row in enumerate(DOTS[digit]) for c, ch in enumerate(row) if ch == "X")
        b += f'<g opacity="{1 if k == 0 else 0}">{lit}<animate attributeName="opacity" values="{seq}" calcMode="discrete" dur="11s" repeatCount="indefinite"/></g>'
    b += "</g>"
    over = B.text((W - B.text_w("GAME OVER", 9)) // 2, 130, "GAME OVER", 9, "#ff3a2a", "#2a0505")
    seq = ";".join("1" if j == 10 else "0" for j in range(11))
    b += (f'<rect x="20" y="20" width="{W - 40}" height="{H - 40}" fill="#000000" opacity="0">'
          f'<animate attributeName="opacity" values="{seq}" calcMode="discrete" dur="11s" repeatCount="indefinite"/></rect>'
          f'<g opacity="0">{over}<animate attributeName="opacity" values="{seq}" calcMode="discrete" dur="11s" repeatCount="indefinite"/></g>')
    b += sf_frame(W, H, inner=False)
    return B.svg(W, H, b, 'role="img" aria-label="Continue? countdown from 9 to 0"')


def banner_strip(kind):
    """Faixas de marketing: abertura (antes do cartao) e convite final (depois do conteudo), no estilo das telas do SF."""
    W, H = 1056, 104
    if kind == "hook":
        title, sub, tag = "FROM FIRST IDEA TO PRODUCTION", "SECURE, SCALABLE AND SHIPPED FAST", "READY?"
    else:
        title, sub, tag = "READY FOR THE NEXT CHALLENGE?", "LET'S BUILD SOMETHING GREAT TOGETHER", "FIGHT!"
    uid = f"st{kind}"
    b = (f'<defs><linearGradient id="{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe14a"/><stop offset="1" stop-color="#ff5a3a"/></linearGradient></defs>'
         f'<rect width="{W}" height="{H}" fill="#0b0612"/>'
         f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="none" stroke="{GOLD}" stroke-width="4"/>'
         f'<rect x="12" y="12" width="{W - 24}" height="{H - 24}" fill="none" stroke="{PURPLE}" stroke-width="2"/>')
    b += B.text((W - B.text_w(title, 5)) // 2, 24, title, 5, f"url(#{uid})", "#1a0b00")
    b += f'<g>{B.text((W - B.text_w(sub, 3)) // 2, 68, sub, 3, "#8fb4ff", "#000000")}<animate attributeName="opacity" values="1;0.55;1" dur="2s" repeatCount="indefinite"/></g>'
    return B.svg(W, H, b, f'role="img" aria-label="{title.title()}"')
