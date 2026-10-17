"""Gera os badges do topo (assets/badges/*.svg): mesma altura, icone e estilo, sem depender de servicos externos.

Uso: python scripts/make_badges.py   (baixa os icones do Iconify uma vez; os SVGs gerados ficam no repositorio)
"""
import os
import re
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "badges")
H, ICON, FONT = 32, 16, 12

# arquivo, texto, cor do fundo, cor do texto, icone (conjunto/nome), cor do icone
BADGES = [
    ("linkedin", "LinkedIn", "#0A66C2", "#ffffff", "simple-icons/linkedin", "#ffffff", False),
    ("rock", "ROCK & ROLL", "#0b0b0e", "#ffffff", "game-icons/guitar", "#ff2a2a", True),
    ("eldenring", "ELDEN RING", "#C8A951", "#1a1205", "game-icons/ring", "#1a1205", True),
    ("pc", "PC MASTER RACE", "#1B2838", "#ffffff", "simple-icons/steam", "#ffffff", True),
    ("darkfantasy", "DARK FANTASY", "#3A0CA3", "#ffffff", "game-icons/horned-skull", "#ffffff", True),
    ("anime", "ANIME", "#E63946", "#ffffff", "game-icons/dragon-orb", "#ffffff", True),
    ("openai", "OPENAI", "#412991", "#ffffff", "simple-icons/openai", "#ffffff", True),
    ("claude", "CLAUDE", "#1a1a1e", "#ffffff", "simple-icons/anthropic", "#d97757", True),
    ("agents", "AI AGENTS", "#4A90E2", "#ffffff", "game-icons/robot-golem", "#ffffff", True),
    ("rag", "RAG", "#FF6B35", "#ffffff", "game-icons/magnifying-glass", "#ffffff", True),
    ("prompt", "PROMPT ENGINEERING", "#8A2BE2", "#ffffff", "game-icons/scroll-quill", "#ffffff", True),
    ("n8n", "N8N", "#EA4B71", "#ffffff", "simple-icons/n8n", "#ffffff", True),
    ("aws", "AWS", "#232F3E", "#ffffff", "simple-icons/amazonaws", "#FF9900", True),
    ("vercel", "VERCEL", "#000000", "#ffffff", "simple-icons/vercel", "#ffffff", True),
    ("supabase", "SUPABASE", "#3ECF8E", "#0b1f16", "simple-icons/supabase", "#0b1f16", True),
    ("docker", "DOCKER", "#2496ED", "#ffffff", "simple-icons/docker", "#ffffff", True),
    ("actions", "GITHUB ACTIONS", "#2088FF", "#ffffff", "simple-icons/githubactions", "#ffffff", True),

]


def icon(path, color):
    url = f"https://api.iconify.design/{path}.svg?color={color.replace('#', '%23')}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-badges"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    return vb, re.sub(r"</?svg[^>]*>", "", raw)


def build(name, label, bg, fg, ic, ic_col, upper):
    vb, inner = icon(ic, ic_col)
    safe = label.replace("&", "&amp;")
    tw = round(len(label) * (8.7 if upper else 7.9))
    w = 14 + ICON + 9 + tw + 16
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{safe}">'
            f'<rect width="{w}" height="{H}" rx="5" fill="{bg}"/>'
            f'<rect x="0.5" y="0.5" width="{w - 1}" height="{H - 1}" rx="4.5" fill="none" stroke="#ffffff" stroke-opacity="0.12"/>'
            f'<svg x="14" y="{(H - ICON) // 2}" width="{ICON}" height="{ICON}" viewBox="{vb}">{inner}</svg>'
            f'<text x="{14 + ICON + 9}" y="{H // 2 + 4}" fill="{fg}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="{FONT}" '
            f'font-weight="700" letter-spacing="0.8" textLength="{tw}" lengthAdjust="spacingAndGlyphs">{safe}</text></svg>')


def main():
    os.makedirs(ROOT, exist_ok=True)
    for b in BADGES:
        with open(os.path.join(ROOT, b[0] + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(build(*b))
        print(b[0])


if __name__ == "__main__":
    main()
