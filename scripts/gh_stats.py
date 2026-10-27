"""Gera assets/stats.svg (cartao de status em pixel-art) a partir da API do GitHub.

Uso: python scripts/gh_stats.py [usuario]     (token opcional em GITHUB_TOKEN)
Se a API falhar, o arquivo anterior e mantido.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets as B  # noqa: E402

LANG_COLORS = {"TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Dart": "#00b4ab", "Python": "#3572a5", "Java": "#b07219",
               "HTML": "#e34c26", "CSS": "#663399", "SCSS": "#c6538c", "Shell": "#89e051", "Kotlin": "#a97bff", "Go": "#00add8",
               "Rust": "#dea584", "C": "#888888", "C++": "#f34b7d", "C#": "#178600", "PHP": "#4f5d95", "Swift": "#f05138",
               "PLpgSQL": "#336790", "Dockerfile": "#384d54"}


def api(path, token=None):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-readme-stats"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect(user, token):
    repos, page = [], 1
    while True:
        chunk = api(f"/users/{user}/repos?per_page=100&type=owner&page={page}", token)
        repos += chunk
        if len(chunk) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = {}
    for r in own[:60]:
        try:
            for k, v in api(f"/repos/{user}/{r['name']}/languages", token).items():
                langs[k] = langs.get(k, 0) + v
        except Exception:
            pass
    since = (date.today() - timedelta(days=365)).isoformat()
    q = lambda s: urllib.parse.quote(s, safe=":+><=")

    def count(kind, extra=""):
        return api(f"/search/{kind}?q={q(extra)}&per_page=1", token)["total_count"]

    try:
        commits = count("commits", f"author:{user} author-date:>={since}")
    except Exception:
        commits = None
    prs = count("issues", f"author:{user} type:pr")
    issues = count("issues", f"author:{user} type:issue")
    return {"stars": stars, "commits": commits, "prs": prs, "issues": issues, "repos": len(own), "langs": langs}


def render(user, d):
    W, H = 1056, 300
    gold = "#3b6fd1"
    b = f'<rect width="{W}" height="{H}" fill="#0b0612"/>'
    b += f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="none" stroke="{gold}" stroke-width="8"/>'
    b += f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" stroke="#243a82" stroke-width="4"/>'
    for cx, cy in ((0, 0), (W - 24, 0), (0, H - 24), (W - 24, H - 24)):
        b += f'<rect x="{cx}" y="{cy}" width="24" height="24" fill="#c01824"/><rect x="{cx + 8}" y="{cy + 8}" width="8" height="8" fill="#0b0612"/>'
    b += B.text(48, 40, f"STATUS: {user.upper()}", 4, "#ffffff", "#1a0b3a")
    rows = [("STARS", d["stars"], "#5fa8ff"), ("COMMITS 12M", d["commits"], "#3b6fd1"), ("PULL REQUESTS", d["prs"], "#3a9ad9"),
            ("ISSUES", d["issues"], "#c01824"), ("REPOS", d["repos"], "#a85a32")]
    y = 100
    for lab, val, col in rows:
        b += f'<rect x="48" y="{y + 2}" width="18" height="18" fill="{col}"/>'
        b += B.text(80, y, lab, 3, "#ffffff")
        v = "-" if val is None else str(val)
        b += B.text(440 - B.text_w(v, 3), y, v, 3, "#fff7d6")
        y += 36
    b += B.text(520, 100, "TOP LANGUAGES", 3, "#e8d5a3")
    total = sum(d["langs"].values()) or 1
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    y = 140
    for i, (name, n) in enumerate(top):
        pct = n * 100 / total
        col = LANG_COLORS.get(name, "#9aa4b2")
        b += B.text(520, y, name[:11], 2, "#ffffff")
        b += f'<rect x="680" y="{y - 2}" width="280" height="16" fill="#000000" stroke="#243a82" stroke-width="2"/>'
        b += (f'<rect x="680" y="{y - 2}" width="0" height="16" fill="{col}"><animate attributeName="width" from="0" to="{max(4, int(280 * pct / 100))}" '
              f'dur="1.2s" begin="{i * 0.15:.2f}s" fill="freeze"/></rect>')
        t = f"{pct:.1f}%"
        b += B.text(1000 - B.text_w(t, 2) + 20, y, t, 2, "#fff7d6")
        y += 24
    return B.svg(W, H, b, 'role="img" aria-label="GitHub stats"')


def main():
    user = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_USER") or "thiagofalcone")
    token = os.environ.get("GITHUB_TOKEN")
    try:
        data = collect(user, token)
    except Exception as e:  # mantem o arquivo anterior
        print("stats: falhou, mantendo arquivo anterior:", e)
        return
    out = os.path.join(B.ASSETS, "stats.svg")
    os.makedirs(B.ASSETS, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(user, data))
    print("stats:", {k: v for k, v in data.items() if k != "langs"}, list(data["langs"])[:6])


if __name__ == "__main__":
    main()
