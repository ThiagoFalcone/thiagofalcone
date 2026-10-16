"""Troca o bloco de tema do README conforme a data (rock / halloween / natal / ano novo).

Uso: python scripts/seasonal.py [README.md] [--force tema] [--date AAAA-MM-DD]
"""
import os
import re
import sys
from datetime import date
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_assets  # noqa: E402

START, END = "<!--THEME:START-->", "<!--THEME:END-->"

THEMES = {
    "rock": {
        "colors": "000000,5c0000,b30000,5c0000,000000",
        "title": "THIAGO FALCONE",
        "sub": "Code. Riffs. Rock n' Roll.",
        "accent": "ff2a2a",
        "lines": [
            "🎸 Les Paul on my back, code on my screen",
            "🤘 Heavy Metal runs in my veins",
            "🧠 AI Solutions • Software Architecture",
            "⚔️ Rise, Tarnished — Dark Fantasy no sangue",
        ],
        "tagline": "🎸 *\"The crowd is the sea, the code is the setlist.\"* 🤘",
    },
    "halloween": {
        "colors": "000000,2b0a3d,ff6a00,2b0a3d,000000",
        "title": "HAPPY HALLOWEEN",
        "sub": "Thiago Falcone • Trick or Riff 🎃",
        "accent": "ff6a00",
        "lines": [
            "🎃 Bugs are the real monsters",
            "🦇 Ozzy would be proud of this night",
            "👻 Shipping code at midnight",
            "🕸️ Heavy Metal & Halloween: a perfect pair",
        ],
        "tagline": "🎃 *\"Prince of Darkness mode: ON.\"* 🦇",
    },
    "natal": {
        "colors": "0b3d0b,c1121f,0b3d0b,c1121f,0b3d0b",
        "title": "FELIZ NATAL",
        "sub": "Thiago Falcone • Metal Christmas 🎄🎸",
        "accent": "ff4d4d",
        "lines": [
            "🎄 Jingle Bells... but with distortion",
            "🎅 Santa plays a Les Paul",
            "❄️ Deploying joy this Christmas",
            "🎁 Pull requests are the best gifts",
        ],
        "tagline": "🎄 *\"Silent night? Not with a Marshall stack.\"* 🎸",
    },
    "criancas": {
        "colors": "0b1d51,e63946,ffd60a,2a9d8f,0b1d51",
        "title": "DIA DAS CRIANCAS",
        "sub": "Thiago Falcone • Player 1 is still a kid 🎮",
        "accent": "ffd60a",
        "lines": ["🎮 Todo dev é uma criança com um joystick", "🕹️ Insert coin to continue", "🥋 Hadouken, commit e deploy", "🎸 Rock também é brincadeira"],
        "tagline": "🎮 *\"Never stop playing.\"* 🕹️",
    },
    "blackfriday": {
        "colors": "000000,1a1a1a,ffd400,1a1a1a,000000",
        "title": "BLACK FRIDAY",
        "sub": "Thiago Falcone • Steam wishlist em chamas 🔥",
        "accent": "ffd400",
        "lines": ["🔥 Steam sale: carteira em perigo", "🖤 Black Friday, Black Sabbath", "🛒 Compre menos, shippe mais", "💻 Upgrade do PC aprovado?"],
        "tagline": "🖤 *\"Descontos passam, riffs são eternos.\"* 🎸",
    },
    "carnaval": {
        "colors": "6a00f4,f72585,ffd60a,06d6a0,6a00f4",
        "title": "CARNAVAL",
        "sub": "Thiago Falcone • Bloco do Heavy Metal 🎭",
        "accent": "f72585",
        "lines": ["🎭 Carnaval com guitarra distorcida", "🥁 Bateria de escola de samba ou de metal?", "🎉 Deploy em dia de folia", "🤘 Bloco do Maiden"],
        "tagline": "🎭 *\"Quem disse que metal não tem folia?\"* 🥁",
    },
    "pascoa": {
        "colors": "5e2b97,ffb3c6,ffd60a,8ecae6,5e2b97",
        "title": "FELIZ PASCOA",
        "sub": "Thiago Falcone • Ovos, código e riffs 🐰",
        "accent": "ffb3c6",
        "lines": ["🐰 Easter eggs no código e nos games", "🥚 Elden Ring tem os melhores segredos", "🍫 Commit de chocolate", "🎸 Aleluia em power chords"],
        "tagline": "🐰 *\"Procurando easter eggs desde o primeiro jogo.\"* 🥚",
    },
    "maes": {
        "colors": "3a0ca3,f72585,ffb3c6,f72585,3a0ca3",
        "title": "FELIZ DIA DAS MAES",
        "sub": "Thiago Falcone • Gratidão sempre 💐",
        "accent": "f72585",
        "lines": ["💐 Tudo começou com o apoio dela", "❤️ Mãe é o melhor backup", "🎸 Até no metal tem balada para ela", "🌹 Obrigado por tudo"],
        "tagline": "💐 *\"Mãe: a primeira e maior fã.\"* ❤️",
    },
    "pais": {
        "colors": "0b132b,1c2541,3a86ff,1c2541,0b132b",
        "title": "FELIZ DIA DOS PAIS",
        "sub": "Thiago Falcone • Herança: bom gosto musical 🎸",
        "accent": "3a86ff",
        "lines": ["👨‍👦 Pai é o primeiro mentor", "🎸 Riffs passados de geração em geração", "🛠️ Aprendi a construir com os melhores", "🤘 Honra e respeito"],
        "tagline": "🎸 *\"Todo herói tem uma playlist.\"* 🤘",
    },
    "junina": {
        "colors": "7f4f24,e63946,ffb703,2a9d8f,7f4f24",
        "title": "FESTA JUNINA",
        "sub": "Thiago Falcone • Arraiá do Rock 🌽🔥",
        "accent": "ffb703",
        "lines": ["🌽 Milho, fogueira e distorção", "🔥 Quadrilha ou mosh pit?", "🎪 Arraiá do Falcone", "🎸 Sanfona e Les Paul no mesmo palco"],
        "tagline": "🌽 *\"Anarriê do heavy metal!\"* 🔥",
    },
    "dia_do_rock": {
        "colors": "000000,3d0000,ff1e1e,3d0000,000000",
        "title": "DIA MUNDIAL DO ROCK",
        "sub": "Thiago Falcone • 13 de julho: Live Aid forever 🤘",
        "accent": "ff1e1e",
        "lines": ["🤘 Hoje é dia de volume 11", "🎸 Les Paul no talo", "🐴 Up the Irons!", "🐉 Dio: Holy Diver, sempre"],
        "tagline": "🤘 *\"Rock n' Roll never dies.\"* 🎸",
    },
    "programador": {
        "colors": "0d1117,0a3d1f,00ff41,0a3d1f,0d1117",
        "title": "DIA DO PROGRAMADOR",
        "sub": "Thiago Falcone • 256º dia do ano 💻",
        "accent": "00ff41",
        "lines": ["💻 while(alive) { code(); riff(); }", "🐛 Bug de sexta às 17h? Sempre.", "☕ Café + distorção = produtividade", "🚀 Ship it."],
        "tagline": "💻 *\"Hello, World! — com um solo de guitarra.\"* 🎸",
    },
    "anonovo": {
        "colors": "000000,3a2a00,d4af37,3a2a00,000000",
        "title": "FELIZ ANO NOVO",
        "sub": "Thiago Falcone • New Year, New Riffs 🎆",
        "accent": "ffd700",
        "lines": [
            "🎆 New year, new commits",
            "🥂 Cheers to bigger products",
            "🚀 Ship more, worry less",
            "🎸 Next solo starts now",
        ],
        "tagline": "🎆 *\"Same fire, bigger stage.\"* 🎸",
    },
}


def easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    j, k = c // 4, c % 4
    m = (a + 11 * h) // 319
    r = (2 * e + 2 * j - k - h + m + 32) % 7
    month = (h - m + r + 90) // 25
    return date(year, month, (h - m + r + month + 19) % 32)


def second_sunday(year: int, month: int) -> date:
    first = date(year, month, 1)
    return date(year, month, 1 + (6 - first.weekday()) % 7 + 7)


def pick(today: date) -> str:
    """Primeira regra que casar vence. Para criar uma ocasião: adicione em THEMES e uma linha aqui."""
    y, md = today.year, (today.month, today.day)
    pascoa = easter(y)
    rules = [
        ("anonovo", md >= (12, 27) or md <= (1, 5)),
        ("natal", (12, 1) <= md <= (12, 26)),
        ("halloween", (10, 25) <= md <= (11, 2)),
        ("criancas", (10, 8) <= md <= (10, 12)),
        ("blackfriday", (11, 20) <= md <= (11, 30)),
        ("carnaval", pascoa.toordinal() - 51 <= today.toordinal() <= pascoa.toordinal() - 46),
        ("pascoa", pascoa.toordinal() - 7 <= today.toordinal() <= pascoa.toordinal() + 1),
        ("maes", abs(today.toordinal() - second_sunday(y, 5).toordinal()) <= 3),
        ("pais", abs(today.toordinal() - second_sunday(y, 8).toordinal()) <= 3),
        ("junina", (6, 10) <= md <= (6, 30)),
        ("dia_do_rock", (7, 11) <= md <= (7, 14)),
        ("programador", (9, 11) <= md <= (9, 15)),
        # aniversario: ("aniversario", md == (MES, DIA)) -- adicione o tema e descomente
    ]
    for name, ok in rules:
        if ok and name in THEMES:
            return name
    return "rock"


def block(name: str, files: dict) -> str:
    return (
        f"{START}\n"
        f'<div align="center">\n\n'
        f'<img src="{files["banner"]}" width="100%" alt="Banner"/>\n\n'
        f"</div>\n"
        f"{END}"
    )


def apply(text: str, name: str, files: dict) -> str:
    text = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block(name, files), text, flags=re.S)
    text = re.sub(r"(<!--FOOTER:START-->).*?(<!--FOOTER:END-->)",
                  lambda m: f'{m.group(1)}\n<img src="{files["footer"]}" width="100%" alt="Footer"/>\n{m.group(2)}', text, flags=re.S)
    text = re.sub(r"(<!--QUOTE:START-->).*?(<!--QUOTE:END-->)",
                  lambda m: f'{m.group(1)}\n<img src="{files["quote"]}" width="100%" alt="David Gilmour Stratocaster on a medieval frame"/>\n{m.group(2)}', text, flags=re.S)
    return text


def main() -> None:
    args = sys.argv[1:]
    path = "README.md"
    force = None
    today = date.today()
    i = 0
    while i < len(args):
        if args[i] == "--force":
            force = args[i + 1]; i += 2
        elif args[i] == "--date":
            today = date.fromisoformat(args[i + 1]); i += 2
        else:
            path = args[i]; i += 1
    name = force or pick(today)
    with open(path, encoding="utf-8") as f:
        old = f.read()
    files = build_assets.build_all(name, today)
    new = apply(old, name, files)
    if new != old:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    print(f"tema: {name}")


if __name__ == "__main__":
    main()
