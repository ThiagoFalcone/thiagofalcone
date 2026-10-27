"""Gera os badges e as etiquetas de categoria (assets/badges/*.svg) no estilo do jogo: fundo escuro, borda na cor da categoria e icone.

Uso: python scripts/make_badges.py   (baixa os icones do Iconify uma vez; os SVGs gerados ficam no repositorio)
Icones: pixelarticons (MIT), simple-icons (CC0). Paleta do Akuma: azul, roxo, vermelho.
"""
import os
import re
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "badges")
H, ICON, FONT = 32, 16, 12
BG = "#14102e"
FONT_FAMILY = "Segoe UI,Helvetica,Arial,sans-serif"

DEV, DEVOPS, SECOPS, AI, BIZ = "#3b6fd1", "#3a9ad9", "#c01824", "#a85a32", "#c9822a"

# arquivo, texto, cor da borda, icone, cor do icone
BADGES = [
    # Desenvolvimento
    ("java", "JAVA", DEV, "simple-icons/openjdk", "#ED8B00"),
    ("spring", "SPRING", DEV, "simple-icons/spring", "#6DB33F"),
    ("angular", "ANGULAR", DEV, "simple-icons/angular", "#DD0031"),
    ("ts", "TYPESCRIPT", DEV, "simple-icons/typescript", "#3178C6"),
    ("js", "JAVASCRIPT", DEV, "simple-icons/javascript", "#F7DF1E"),
    ("python", "PYTHON", DEV, "simple-icons/python", "#4B8BBE"),
    ("flutter", "FLUTTER", DEV, "simple-icons/flutter", "#54C5F8"),
    ("dart", "DART", DEV, "simple-icons/dart", "#40C4FF"),
    ("html", "HTML5", DEV, "simple-icons/html5", "#E34F26"),
    ("css", "CSS3", DEV, "simple-icons/css3", "#2D9CDB"),
    # DevOps e Cloud
    ("aws", "AWS", DEVOPS, "simple-icons/amazonaws", "#FF9900"),
    ("docker", "DOCKER", DEVOPS, "simple-icons/docker", "#2496ED"),
    ("actions", "GITHUB ACTIONS", DEVOPS, "simple-icons/githubactions", "#2088FF"),
    ("cicd", "CI/CD", DEVOPS, "simple-icons/jenkins", "#D24939"),
    ("vercel", "VERCEL", DEVOPS, "simple-icons/vercel", "#ffffff"),
    ("supabase", "SUPABASE", DEVOPS, "simple-icons/supabase", "#3ECF8E"),
    ("git", "GIT", DEVOPS, "simple-icons/git", "#F05032"),
    ("github", "GITHUB", DEVOPS, "simple-icons/github", "#ffffff"),
    ("postgres", "POSTGRESQL", DEVOPS, "simple-icons/postgresql", "#4F8CC9"),
    # SecOps
    ("devsecops", "DEVSECOPS", SECOPS, "simple-icons/owasp", "#ffffff"),
    ("secure", "SECURE BY DESIGN", SECOPS, "simple-icons/bitwarden", "#6ea8ff"),
    ("access", "ACCESS CONTROL", SECOPS, "simple-icons/keycloak", "#ffffff"),
    # IA e automacao
    ("openai", "OPENAI", AI, "simple-icons/openai", "#ffffff"),
    ("claude", "CLAUDE", AI, "simple-icons/anthropic", "#d97757"),
    ("agents", "AI AGENTS", AI, "simple-icons/langchain", "#7fd1b9"),
    ("rag", "RAG", AI, "simple-icons/huggingface", "#FFD21E"),
    ("prompt", "PROMPT ENGINEERING", AI, "simple-icons/githubcopilot", "#ffffff"),
    ("n8n", "N8N", AI, "simple-icons/n8n", "#EA4B71"),
    # Negocios e produto
    ("entrepreneur", "ENTREPRENEURSHIP", BIZ, "simple-icons/ycombinator", "#FF6600"),
    ("product", "PRODUCT ENGINEERING", BIZ, "simple-icons/producthunt", "#FF6154"),
    ("leadership", "TECH LEADERSHIP", BIZ, "simple-icons/linear", "#8f9bff"),
    ("innovation", "INNOVATION", BIZ, "simple-icons/spacex", "#ffffff"),
    # Links do perfil
    ("portfolio", "PORTFOLIO", "#c01824", "pixelarticons/external-link", "#ffffff"),
]

# etiquetas de categoria (largura fixa para alinhar): arquivo, texto, cor, icone
TAGS = [
    ("tag-dev", "DEVELOPMENT", DEV, "pixelarticons/code"),
    ("tag-devops", "DEVOPS AND CLOUD", DEVOPS, "pixelarticons/cloud-server"),
    ("tag-secops", "SECOPS", SECOPS, "pixelarticons/shield"),
    ("tag-ai", "AI AND AUTOMATION", AI, "pixelarticons/robot"),
    ("tag-business", "BUSINESS AND PRODUCT", BIZ, "pixelarticons/briefcase"),
]


def icon(path, color):
    url = f"https://api.iconify.design/{path}.svg?color={color.replace('#', '%23')}"
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-badges"})
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
            break
        except OSError:
            if attempt == 3:
                raise
    vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
    return vb, re.sub(r"</?svg[^>]*>", "", raw)


def esc(s):
    return s.replace("&", "&amp;")


def badge(label, border, ic, ic_col):
    vb, inner = icon(ic, ic_col)
    tw = round(len(label) * 8.7)
    w = 14 + ICON + 9 + tw + 16
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{esc(label)}">'
            f'<rect width="{w}" height="{H}" rx="4" fill="{BG}"/>'
            f'<rect x="1" y="1" width="{w - 2}" height="{H - 2}" rx="3" fill="none" stroke="{border}" stroke-width="2"/>'
            f'<svg x="14" y="{(H - ICON) // 2}" width="{ICON}" height="{ICON}" viewBox="{vb}">{inner}</svg>'
            f'<text x="{14 + ICON + 9}" y="{H // 2 + 4}" fill="#ffffff" font-family="{FONT_FAMILY}" font-size="{FONT}" font-weight="700" '
            f'letter-spacing="0.8" textLength="{tw}" lengthAdjust="spacingAndGlyphs">{esc(label)}</text></svg>')


def linkedin():
    vb, inner = icon("simple-icons/linkedin", "#ffffff")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="124" height="{H}" viewBox="0 0 124 {H}" role="img" aria-label="LinkedIn">'
            f'<rect width="124" height="{H}" rx="4" fill="#0A66C2"/>'
            f'<svg x="14" y="{(H - ICON) // 2}" width="{ICON}" height="{ICON}" viewBox="{vb}">{inner}</svg>'
            f'<text x="38" y="{H // 2 + 4}" fill="#ffffff" font-family="{FONT_FAMILY}" font-size="13" font-weight="700" letter-spacing="0.3">LinkedIn</text></svg>')


def tag(label, color, ic):
    vb, inner = icon(ic, "#ffffff")
    w, h = 300, 36
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">'
            f'<rect width="{w}" height="{h}" fill="{color}"/>'
            f'<rect width="46" height="{h}" fill="#000000" fill-opacity="0.28"/>'
            f'<svg x="13" y="8" width="20" height="20" viewBox="{vb}">{inner}</svg>'
            f'<text x="60" y="{h // 2 + 5}" fill="#ffffff" font-family="{FONT_FAMILY}" font-size="14" font-weight="800" letter-spacing="1.2">{esc(label)}</text>'
            f'<rect x="0" y="{h - 3}" width="{w}" height="3" fill="#000000" fill-opacity="0.35"/></svg>')


def main():
    os.makedirs(ROOT, exist_ok=True)

    def w(name, svg):
        with open(os.path.join(ROOT, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(name)

    w("linkedin", linkedin())
    for name, label, border, ic, col in BADGES:
        w(name, badge(label, border, ic, col))
    for name, label, color, ic in TAGS:
        w(name, tag(label, color, ic))


if __name__ == "__main__":
    main()
